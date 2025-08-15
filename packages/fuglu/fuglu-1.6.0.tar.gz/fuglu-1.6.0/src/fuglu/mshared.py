# -*- coding: utf-8 -*-
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
import time
try:
    #from contextlib import AbstractAsyncContextManager
    from contextlib import AbstractContextManager
except ImportError:
    #AbstractAsyncContextManager = object
    AbstractContextManager = object
import typing as tp
from typing import Tuple, Union
from types import TracebackType

import fuglu.connectors.milterconnector as sm
import fuglu.connectors.asyncmilterconnector as asm
from fuglu.scansession import TrackTimings
from fuglu.mixins import ReturnOverrideMixin

from fuglu.connectors.milterconnector import (
    CONNECT,
    HELO,
    MAILFROM,
    RCPT,
    HEADER,
    EOH,
    EOB,
    ACCEPT,
    CONTINUE,
    DISCARD,
    TEMPFAIL,
    REJECT,
    STR2RETCODE,
)
import fuglu.shared as fs

EOM = "eom"  # end-of-message state for non-milter-call

# conversion return code to Milter return code
retcode2milter = {
    fs.DUNNO: CONTINUE,
    fs.ACCEPT: ACCEPT,
    fs.DELETE: DISCARD,
    fs.REJECT: REJECT,
    fs.DEFER: TEMPFAIL,
}


def convert_return2milter(ret: tp.Union[int, tp.Tuple[int, str]]) \
        -> tp.Union[bytes, tp.Tuple[bytes, str]]:
    """Convert return code (simple or tuple with message string) to milter return code"""
    if isinstance(ret, tuple):
        return retcode2milter[ret[0]], ret[1]
    elif isinstance(ret, int):
        return retcode2milter[ret]
    else:
        raise ValueError(f"ret type should be tuple(int, str) or int -> but is {type(ret)}")


class SumAsyncTime(AbstractContextManager):
    """Async context manager to additionally sum async await calls"""

    def __init__(self, timer: TrackTimings, key: tp.Optional[str] = None, logid: tp.Optional[str] = None):
        self.timer = timer
        self.asyncstart = None
        self.asyncend = None
        self.key = key
        self.logid = logid
        self.logger = logging.getLogger('fuglu.SumAsyncTime')

    def __enter__(self):
        self.asyncstart = time.time()
        #self.logger.debug(f"{self.logid} ({self.key}) -> enter with time {self.asyncstart}")

    def __exit__(self, exc_type: tp.Optional[tp.Type[BaseException]], exc_value: tp.Optional[BaseException], traceback: tp.Optional[TracebackType]):
        self.asyncend = time.time()
        #self.logger.debug(f"{self.logid} ({self.key}) -> exit with time {self.asyncend}")
        self.timer.sum_asynctime(self.asyncend - self.asyncstart, self.key, logid=self.logid)


class BMPConnectMixin:
    """Basic Milter Plugin Mixing to implement plugin for connect state which can be a coroutine"""

    def examine_connect(self, sess: Union[sm.MilterSession, asm.MilterSession], host: bytes, addr: bytes) -> Union[bytes, Tuple[bytes, str]]:
        """(async) Examine connect state, return action code or tuple with action code and message"""
        raise NotImplementedError()


class BMPHeloMixin:
    """Basic Milter Plugin Mixing to implement plugin for helo state which can be a coroutine"""

    def examine_helo(self, sess: Union[sm.MilterSession, asm.MilterSession], helo: bytes) -> Union[bytes, Tuple[bytes, str]]:
        """(async) Examine helo state, return action code or tuple with action code and message"""
        raise NotImplementedError()


class BMPMailFromMixin:
    """Basic Milter Plugin Mixing to implement plugin for mailfrom state which can be a coroutine"""

    def examine_mailfrom(self, sess: Union[sm.MilterSession, asm.MilterSession], sender: bytes) -> Union[bytes, Tuple[bytes, str]]:
        """(async) Examine mailfrom state, return action code or tuple with action code and message"""
        raise NotImplementedError()


class BMPRCPTMixin:
    """Basic Milter Plugin Mixing to implement plugin for rcpt state which can be a coroutine"""

    def examine_rcpt(self, sess: Union[sm.MilterSession, asm.MilterSession], recipient: bytes) -> Union[bytes, Tuple[bytes, str]]:
        """(async) Examine recipient state, return action code or tuple with action code and message"""
        raise NotImplementedError()


class BMPHeaderMixin:
    """Basic Milter Plugin Mixing to implement plugin for header state which can be a coroutine"""

    def examine_header(self, sess: Union[sm.MilterSession, asm.MilterSession], key: bytes, value: bytes) -> Union[bytes, Tuple[bytes, str]]:
        """(async) Examine header state, return action code or tuple with action code and message"""
        raise NotImplementedError()


class BMPEOHMixin:
    """Basic Milter Plugin Mixing to implement plugin for end-of-headers state which can be a coroutine"""

    def examine_eoh(self, sess: Union[sm.MilterSession, asm.MilterSession]) -> Union[bytes, Tuple[bytes, str]]:
        """(async) Examine eoh state, return action code or tuple with action code and message"""
        raise NotImplementedError()


class BMPEOBMixin(ReturnOverrideMixin):
    """Basic Milter Plugin Mixing to implement plugin for end-of-body state which can be a coroutine"""

    def examine_eob(self, sess: Union[sm.MilterSession, asm.MilterSession]) -> Union[bytes, Tuple[bytes, str]]:
        """(async) Examine eob state, return action code or tuple with action code and message"""
        raise NotImplementedError()


class BasicMilterPlugin(ReturnOverrideMixin, fs.BasicPlugin):
    """Base for milter plugins, derive from BMP***Mixins above to implement states"""

    ALL_STATES = {
        CONNECT: BMPConnectMixin,
        HELO: BMPHeloMixin,
        MAILFROM: BMPMailFromMixin,
        RCPT: BMPRCPTMixin,
        HEADER: BMPHeaderMixin,
        EOH: BMPEOHMixin,
        EOB: BMPEOBMixin,
    }

    def __init__(self, config, section=None):
        super().__init__(config, section=section)
        self.requiredvars.update({
            'state': {
                'default': '',
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        })
        self._state = None
        self.logger = self._logger()

    @property
    def state(self):
        """states list this plugin is active in"""
        if self._state is None:
            self._state = [s.lower() for s in fs.Suspect.getlist_space_comma_separated(self.config.get(self.section, 'state'))]
        return self._state

    def lint(self, **kwargs) -> bool:
        """Basic lint, check if given state exists & implementation of state"""
        if not super().lint():
            return False

        checkstates = kwargs.get('state', self.state)
        if isinstance(checkstates, str):
            checkstates = [checkstates]

        if not all(s in BasicMilterPlugin.ALL_STATES.keys() for s in checkstates):
            print("Error: Not all states are available/implemented")
            print(f"checkstates: {checkstates}")
            print(f"allkeys: {list(BasicMilterPlugin.ALL_STATES.keys())}")
            return False

        for s in checkstates:
            cls = BasicMilterPlugin.ALL_STATES[s]
            if not isinstance(self, cls):
                print(f"ERROR: {self.__class__.__name__} does not implement {cls.__name__}")
                return False

        return True

    def _logger(self):
        """returns the logger for this plugin"""
        myclass = self.__class__.__name__
        loggername = "fuglu.mplugin.%s" % myclass
        return logging.getLogger(loggername)

    def _problemcode(self, configoption='problemaction'):
        """
        safely calculates action code based on problemaction config value
        :return: action code
        """
        retcode = STR2RETCODE.get(self.config.get(self.section, configoption), self.config)
        if retcode is not None:
            return retcode
        else:
            # in case of invalid problem action
            return CONTINUE
