# -*- coding: utf-8 -*-
#   Copyright Oli Schacher, Fumail Project
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
from fuglu.shared import ScannerPlugin, DUNNO, SuspectFilter
import os


class BACN(ScannerPlugin):
    """
    Mark message as Bacn/Bulk
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'bacn_filter': {
                'default': '${confdir}/bacn_filter.regex',
                'description': 'filterfile containing rules to mark message as bacn',
            },

            'add_datatags': {
                'default': 'True',
                'description': "add from/to header data tags. may be needed for some filter matches.",
            },

            'subjecttag': {
                'default': '',
                'description': "tag to prepend in subject, e.g. [ADVERT] - will break DKIM",
            },

            'addheader': {
                'default': '',
                'description': "name of header to add, e.g. X-Fuglu-Bulk - will only be added if message is bacn",
            },
            
            'tagname': {
                'default': 'bacn',
                'description': "name of subject tag to add. will be boolean True/False",
            },
            
            'addsaheader': {
                'default': 'X-Fuglu-BACN',
                'description': "name of spamassassin pseudo header to add - will only be added if message is bacn",
            },
            
        }
        self.bacn_filter = None

    def _init_bacn_filter(self):
        """checks if there is a bacn filter file and initializes it. """
        if self.bacn_filter is None:
            filename = self.config.get(self.section, 'bacn_filter')
            if filename and os.path.exists(filename):
                self.bacn_filter = SuspectFilter(filename)

    def _add_data_tag(self, suspect, hdr):
        parsed_headers = suspect.parse_from_type_header(hdr)
        if parsed_headers and parsed_headers[0]:
            address = parsed_headers[0][1]
            suspect.set_tag(f'bacn.hdr_{hdr.lower()}', address)

    def _update_subject(self, suspect):
        tag = self.config.get(self.section, 'subjecttag')
        if tag:
            oldsubj = suspect.get_header('subject')
            newsubj = f'{tag} {oldsubj}'
            suspect.update_subject(lambda oldsubj: newsubj)

    def examine(self, suspect):
        self._init_bacn_filter()
        if self.bacn_filter is None:
            return DUNNO

        if self.config.getboolean(self.section, 'add_datatags'):
            self._add_data_tag(suspect, 'From')
            self._add_data_tag(suspect, 'Reply-To')
        
        tagname = self.config.get(self.section, 'tagname')
        match, arg = self.bacn_filter.matches(suspect)
        if match:
            reason = arg or ''
            self.logger.debug(f'{suspect.id} message marked as bacn {reason}')
            suspect.set_tag(tagname, True)
            saheader = self.config.get(self.section, 'addsaheader')
            if saheader:
                suspect.write_sa_temp_header(saheader, 'yes')
            if reason:
                suspect.set_tag(f'{tagname}.reason', reason)
            header = self.config.get(self.section, 'addheader')
            if header:
                suspect.add_header(header, arg or 'Yes')
        else:
            suspect.set_tag(tagname, False)
        return DUNNO

    def lint(self):
        if not self.check_config():
            return False
        self._init_bacn_filter()
        if not self.bacn_filter:
            print('ERROR: bacn filter was not initialised')
            return False
        return True
