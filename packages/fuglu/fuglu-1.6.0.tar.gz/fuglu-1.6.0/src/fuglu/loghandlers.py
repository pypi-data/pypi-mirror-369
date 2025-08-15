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


# additional loggers
# source:
# http://stackoverflow.com/questions/1407474/does-python-logging-handlers-rotatingfilehandler-allow-creation-of-a-group-writa

import os
import sys
import logging.handlers
from fuglu.stringencode import force_uString, force_bString


HAVE_FLUENT = False
try:
    from fluent import handler as fluenthandler
    HAVE_FLUENT = True
except ModuleNotFoundError:
    fluenthandler = None


class GroupReadableRotatingFileHandler(logging.handlers.RotatingFileHandler):

    def _open(self):
        prevumask = os.umask(0o137)
        rtv = logging.handlers.RotatingFileHandler._open(self)
        os.umask(prevumask)
        return rtv


class GroupWritableRotatingFileHandler(logging.handlers.RotatingFileHandler):

    def _open(self):
        prevumask = os.umask(0o117)
        rtv = logging.handlers.RotatingFileHandler._open(self)
        os.umask(prevumask)
        return rtv


class GroupReadableTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):

    def _open(self):
        prevumask = os.umask(0o137)
        rtv = logging.handlers.TimedRotatingFileHandler._open(self)
        os.umask(prevumask)
        return rtv


class GroupWritableTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):

    def _open(self):
        prevumask = os.umask(0o117)
        rtv = logging.handlers.TimedRotatingFileHandler._open(self)
        os.umask(prevumask)
        return rtv


class StreamHandlerNEOL(logging.StreamHandler):
    """Stream Handler removing all end of line characters"""
    def __init__(self, stream=None, eolchars=""):
        super().__init__(stream=stream)
        self.eolchars = eolchars

    def emit(self, record: logging.LogRecord) -> None:
        if isinstance(record.msg, str):
                record.msg = record.msg.replace("\r\n", self.eolchars).replace("\n", self.eolchars)
        elif isinstance(record.msg, bytes):
                msg = force_uString(record.msg)
                msg = msg.replace("\r\n", self.eolchars).replace("\n", self.eolchars)
                record.msg = force_bString(msg)
        super().emit(record)


if HAVE_FLUENT:
    class FluentFugluHandler(fluenthandler.FluentHandler):
        """
        A Fluent handler

        Sturctured data sent to fluent will contain hostname in `Node_Hostname`, a `log` entry in the format below,
        a `message` entry with the log message and a timestamp.
        """
        def __init__(self, tag, host='localhost', port=24224, timeout=3, verbose=False, buffer_overflow_handler=None, msgpack_kwargs=None, nanosecond_precision=False, eolchars="", **kwargs):
            super().__init__(tag, host, port, timeout, verbose, buffer_overflow_handler, msgpack_kwargs, nanosecond_precision, **kwargs)
            self.eolchars = eolchars
            fugluformat = {
                'Node_Hostname': '%(hostname)s',
                'log': '%(name)-12s: %(levelname)s %(message)s',
            }
            fluentformatter = fluenthandler.FluentRecordFormatter(fugluformat)
            self.setFormatter(fluentformatter)

    def emit(self, record: logging.LogRecord) -> None:
        if isinstance(record.msg, str):
                record.msg = record.msg.replace("\r\n", self.eolchars).replace("\n", self.eolchars)
        elif isinstance(record.msg, bytes):
                msg = force_uString(record.msg)
                msg = msg.replace("\r\n", self.eolchars).replace("\n", self.eolchars)
                record.msg = force_bString(msg)
        super().emit(record)

else:
    class FluentFugluHandler(logging.StreamHandler):
        """Dummy handler in case there's not fluentd library"""
        def __init__(self, tag, host='localhost', port=24224, timeout=3, verbose=False, buffer_overflow_handler=None, msgpack_kwargs=None, nanosecond_precision=False, eolchars="", **kwargs):
            super().__init__(stream=sys.stderr)

        def emit(self, record: logging.LogRecord) -> None:
            print(f"WARNING: No fluent library found, FluentFugluHandler can not work! Dumping output to stderr!")
            super().emit(record)

