# -*- coding: UTF-8 -*-
#   Copyright Fumail Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

"""
Plugins for misc analysis of suspect/message
"""

from collections import Counter
import math
import typing as tp
import base64
from fuglu.stringencode import force_uString
from fuglu.shared import Suspect, ScannerPlugin, DUNNO
from .uriextract import URIExtract

try:
    import esprima
    HAVE_ESPRIMA = True
except ImportError:
    HAVE_ESPRIMA = False

class CalcEntropy(ScannerPlugin):
    """
    calculate entry of various aspects of the suspect:
    - sender localpart
    """
    
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {}
    
    @staticmethod
    def _calculate_entropy(data:str) -> int:
        # Count the frequency of each character
        data_counter = Counter(data)
        entropy = 0
        for count in data_counter.values():
            probability = count / len(data)
            entropy -= probability * math.log2(probability)
        return entropy
    
    def examine(self, suspect):
        sender = suspect.from_localpart
        en = self._calculate_entropy(sender)
        suspect.set_tag('sender.entropy', en)
        suspect.write_sa_temp_header('X-Fuglu-SenderEntropy', str(en))
        self.logger.debug(f'{suspect.id} entropy of {sender} is {en}')
        
        subject = suspect.get_header('subject')
        en = self._calculate_entropy(subject)
        suspect.set_tag('subject.entropy', en)
        suspect.write_sa_temp_header('X-Fuglu-SubjectEntropy', str(en))
        self.logger.debug(f'{suspect.id} entropy of {subject} is {en}')
        return DUNNO
    

class CheckJavaScript(URIExtract):
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
    
    def _get_javascript_pdf(self, suspect: Suspect) -> str|None:
        for attobj in suspect.att_mgr.get_objectlist(level=0):
            if attobj.is_archive and (attobj.contenttype_mime == 'application/pdf' or attobj.filename.endswith('.pdf')):
                archobj = attobj.get_archive_objlist()
                if archobj.filename.endswith('.js'):
                    return archobj
        return None
    
    def _chek_jawa(self, suspect: Suspect, js_code: str) -> tp.Tuple[tp.List[str], tp.List[str]]:
        suspicious_patterns = ["eval", "document.write", "Function", "setTimeout", "setInterval", "XMLHttpRequest", "appendChild"]
        
        conversions = {
            'atob': base64.b64decode,
        }
        
        strings_found = []
        suspats_found = []
        try:
            tree = esprima.parseScript(js_code)
            if tree.body:
                for node in tree.body:
                    if node.declarations:
                        for decl in node.declarations:
                            conv = conversions.get(decl.init.callee.name)
                            for arg in decl.init.arguments:
                                if conv is not None:
                                    arg = force_uString(conv(arg))
                                    strings_found.append(arg)
                    if node.expression:
                        expr = node.expression.callee.property.name
                        if expr in suspicious_patterns:
                            suspats_found.append(expr)
        except esprima.error_handler.Error as e:
            suspats_found.append(str(e))
        except Exception as e:
            self.logger.debug(f'{suspect.id} failed to parse js code with esprima due to {e.__class__.__name__}: {str(e)}')
        
        return strings_found, suspats_found
    
    
    def examine(self, suspect):
        js_codes = []
        js_code_pdf = self._get_javascript_pdf(suspect)
        if js_code_pdf:
            js_codes.append(js_code_pdf)
            
        strings_found = []
        suspats_found = []
        for js_code in js_codes:
            strf, spf = self._chek_jawa(suspect, js_code)
            strings_found.extend(strf)
            suspats_found.extend(spf)
        
        stringlines = '\n'.join(strings_found)
        uris = self.extractor.extracturis(stringlines)
        uris = self._quickfilter(list(uris))
        self.logger.debug(f'{suspect.id} extracted {len(uris)} URLs from javascript in attachments')
        suspect.set_tag('js.hyperlinks', list(set(uris)))
        
        if uris:
            suspats_found.append('URIVAR')
        self.logger.debug(f'{suspect.id} found {len(suspats_found)} suspcious patterns in javascript')
        
        return DUNNO
        
        