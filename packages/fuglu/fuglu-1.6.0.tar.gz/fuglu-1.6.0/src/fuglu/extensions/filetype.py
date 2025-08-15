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
# This content has been extracted from attachment.py and refactored
#

import threading
import sys

MAGIC_AVAILABLE = 0
MAGIC_PYTHON_MAGIC = 1

STATUS = "not loaded"
ENABLED = False

# try to detect which magic version is installed
try:
    # python-magic (https://github.com/ahupp/python-magic)
    import magic
    MAGIC_AVAILABLE = MAGIC_PYTHON_MAGIC
    STATUS = "available, using python magic"
except ImportError:
    # unsupported version, for example 'filemagic' (outdated, never tested)
    # https://github.com/aliles/filemagic
    # or 'python-file' (outdate, broken as of 2025)
    # http://www.darwinsys.com/file/
    STATUS = 'Python Magic not installed'

ENABLED = MAGIC_AVAILABLE > 0


class MIME_types_base(object):
    """
    Base class for mime file type magic
    """

    def __init__(self):
        self.magic = None

    def get_filetype(self, path):
        return None

    def get_buffertype(self, buffercontent):
        return None

    def available(self):
        """
        Return if there's a mime filetype module available to be used.

        All the implementations of this class should actually allocate
        something for self.magic and therefore it will not be None anymore. It
        would also be possible to check for "MAGIC_AVAILABLE > 0" but this would
        be a less object-oriented approach...

        Returns:
            (bool) True if there's a file type module available to be used

        """
        return (self.magic is not None)


class Typemagic_MIME_pythonmagic(MIME_types_base):
    """
    MIME file type magic using magic module python magic

    python-magic (https://github.com/ahupp/python-magic)
    """

    def __init__(self):
        super(Typemagic_MIME_pythonmagic, self).__init__()
        self.magic = magic

    def get_filetype(self, path):
        return magic.from_file(path, mime=True)

    def get_buffertype(self, buffercontent):
        btype = magic.from_buffer(buffercontent, mime=True)
        if isinstance(btype, bytes):
            btype = btype.decode('UTF-8', 'ignore')
        return btype


class ThreadLocalMagic(threading.local):

    def __init__(self, **kw):

        self._magicversion = MAGIC_AVAILABLE

        if MAGIC_AVAILABLE == MAGIC_PYTHON_MAGIC:
            self._typemagic = Typemagic_MIME_pythonmagic()
        else:
            self._typemagic = MIME_types_base()

    def __getattr__(self, name):
        """
        Passing all requests for attributes/methods to actual implementation

        Args:
            name (str): Name of attribute/method

        Returns:
            the answer fo the actual implementation

        """
        return getattr(self._typemagic, name)

    def lint(self):
        """
        Info about module printed on screen(lint)

        Returns:
            (bool) True if there's a mime type magic module available to be used
        """
        lint_string = "not available"
        if MAGIC_AVAILABLE == 0:
            if 'magic' in sys.modules:  # unsupported version
                lint_string = "The installed version of the magic module is not supported. Content/File type analysis only works with python-file from http://www.darwinsys.com/file/ or python-magic from https://github.com/ahupp/python-magic"
            else:
                lint_string = "Python libmagic bindings (python-file or python-magic) not available. No Content/File type analysis."
            return False, lint_string
        elif MAGIC_AVAILABLE == MAGIC_PYTHON_MAGIC:
            lint_string = "Found python-magic (https://github.com/ahupp/python-magic)"
        return True, lint_string


filetype_handler = ThreadLocalMagic()
