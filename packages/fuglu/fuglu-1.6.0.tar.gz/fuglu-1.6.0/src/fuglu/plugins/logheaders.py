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
#
import logging
from typing import Union, Tuple, Optional

import fuglu.connectors.milterconnector as sm
import fuglu.connectors.asyncmilterconnector as asm
from fuglu.shared import ScannerPlugin, DUNNO, Suspect
from fuglu.mshared import (
    BMPHeaderMixin, BMPEOHMixin, BMPEOBMixin,
    BasicMilterPlugin
)
from fuglu.stringencode import force_uString


class LogHeaders(BMPHeaderMixin, BMPEOHMixin, BMPEOBMixin, ScannerPlugin, BasicMilterPlugin):
    """Simple plugin to log headers (milter mode or as normal scanner plugin)"""

    def __init__(self, config, section: Optional[str]=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'state': {
                'default': sm.HEADER,
                'description': f'comma/space separated list of milter states this plugin should be '
                               f'applied ({",".join((sm.HEADER, sm.EOH, sm.EOB))})',
            },
            'loglevel': {
                'default': "DEBUG",
                'description': 'define loglevel in which headers are logged (DEBUG, INFO, WARNING, ERROR)',
            },
        }
        self.loglevel = None
    
    def _set_loglevel(self):
        if self.loglevel is None:
            self.loglevel = logging.getLevelNamesMapping().get(self.config.get(self.section, 'loglevel'), logging.DEBUG)

    def examine_header(self, sess: Union[sm.MilterSession, asm.MilterSession], key: bytes, value: bytes) -> Union[bytes, Tuple[bytes, str]]:
        """Log header"""
        self._set_loglevel()
        try:
            self.logger.log(level=self.loglevel, msg=f"{sess.id} {force_uString(key)}: {force_uString(value)}")
        except Exception as e:
            self.logger.error(f"{sess.id} error logging header(header): ({e.__class__.__name__}) {str(e)}")
        return sm.CONTINUE

    def examine_eoh(self, sess: Union[sm.MilterSession, asm.MilterSession]) -> Union[bytes, Tuple[bytes, str]]:
        """Log all headers"""
        self._set_loglevel()
        try:
            for key, value in sess.original_headers:
                self.logger.log(level=self.loglevel, msg=f"{sess.id} {force_uString(key)}: {force_uString(value)}")
        except Exception as e:
            self.logger.error(f"{sess.id} error logging headers(eoh): ({e.__class__.__name__}) {str(e)}")
        return sm.CONTINUE

    def examine_eob(self, sess: Union[sm.MilterSession, asm.MilterSession]) -> Union[bytes, Tuple[bytes, str]]:
        """Log all headers"""
        self._set_loglevel()
        try:
            for key, value in sess.original_headers:
                self.logger.log(level=self.loglevel, msg=f"{sess.id} {force_uString(key)}: {force_uString(value)}")
        except Exception as e:
            self.logger.error(f"{sess.id} error logging headers(eob): ({e.__class__.__name__}) {str(e)}")
        return sm.CONTINUE

    def examine(self, suspect: Suspect) -> Optional[Union[int, Tuple[int, str]]]:
        """Log all headers"""
        self._set_loglevel()
        try:
            for key, value in suspect.get_message_rep().items():
                self.logger.log(level=self.loglevel, msg=f"{suspect.id} {force_uString(key)}: {force_uString(value)}")
        except Exception as e:
            self.logger.error(f"{suspect.id} error logging headers: ({e.__class__.__name__}) {str(e)}")
        return DUNNO
