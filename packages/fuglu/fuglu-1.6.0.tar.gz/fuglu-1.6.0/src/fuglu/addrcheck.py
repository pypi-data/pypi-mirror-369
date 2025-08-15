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
import re
import logging


# Singleton implementation for Addrcheck
class Addrcheck:
    """
    Singleton implementation for Addrcheck. Note it is important not
    to initialise "self._method" by creating a "__init__" function
    since this would be called whenever asking for the singleton...
    (Addrcheck() would call __init__).
    """
    __instance = None

    def __new__(cls):
        """
        Returns Singleton of Addrcheck (create if not yet existing)

        Returns:
            (Addrcheck) The singleton of Addrcheck
        """
        if Addrcheck.__instance is None:
            Addrcheck.__instance = object.__new__(cls)
            Addrcheck.__instance.set("Default")
        return Addrcheck.__instance

    def set(self, name: str, maxsize: int = 64) -> None:
        """
        Sets method to be used in valid - function to validate an address
        Args:
            name (String): String with name of validator
            maxsize (int): maximum number of characters allowed in localpart (64 according to RFC 3696)
        """
        if name == "Default":
            self._method = Default()
        elif name == "LazyLocalPart":
            self._method = LazyLocalPart()
        elif name == "NoCheck":
            self._method = NoCheck()
        elif name == "AsciiOnly":
            self._method = AsciiOnly(maxsize)
        elif name == "PrintableAsciiOnly":
            self._method = PrintableAsciiOnly(maxsize)
        else:
            logger = logging.getLogger("%s.Addrcheck" % __package__)
            logger.warning(f'Mail address check "{name}" not valid, using default...')
            self._method = Default()

    def valid(self, address: str, allow_postmaster: bool = False) -> bool:
        """

        Args:
            address (String): Address to be checked
            allow_postmaster (Bool):

        Returns:
            (Boolean) True if address is valid using internal validation method

        """
        if allow_postmaster and address and address.lower() == "postmaster":
            # According to RFC5321 (https://tools.ietf.org/html/rfc5321#section-4.1.1.3)
            # postmaster is allowed as recipient without domain
            return True

        return self._method(address)


class Addrcheckint:
    """
    Functor interface for method called by Addrcheck
    """

    def __init__(self, maxsize: int = 64):
        self.maxsize = maxsize

    def __call__(self, mailAddress: str) -> bool:
        raise NotImplementedError()
    
    def check_startsendsdot(self, mailAddress: str) -> bool:
        localpart = mailAddress.rsplit('@',1)[0]
        if localpart.startswith('"') and localpart.endswith('"'):
            localpart = localpart.strip('"')
        return localpart.startswith('.') or localpart.endswith('.')


class Default(Addrcheckint):
    """
    Default implementation (and backward compatible) which does not allow more than one '@'
    """

    def __init__(self, maxsize: int = 64):
        super().__init__(maxsize)
        self._re_at = re.compile(r"[^@]{1,%u}@[^@]+$" % maxsize)

    def __call__(self, mailAddress: str) -> bool:
        return mailAddress != '' \
            and self._re_at.match(mailAddress) \
            and not self.check_startsendsdot(mailAddress)


class LazyLocalPart(Default):
    """
    Allows '@' in local part if quoted
    """

    def __init__(self, maxsize: int = 64):
        super().__init__(maxsize)
        self._re_u00_7f = re.compile(r"^\"[\x00-\x7f]{1,%u}\"@[^@]+$" % maxsize)

    def __call__(self, mailAddress: str) -> bool:
        return mailAddress != '' and \
            (self._re_at.match(mailAddress) or self._re_u00_7f.match(mailAddress)) \
            and not self.check_startsendsdot(mailAddress)


class AsciiOnly(Addrcheckint):
    """
    Allow ascii characters only, "@" in local part has to be quoted, max 64 chars in localpart
    """

    def __init__(self, maxsize: int = 64):
        super().__init__(maxsize)
        self.ascii_noadd = re.compile(r"^[\x00-\x3f\x41-\x7f]{1,%u}@[\x00-\x3f\x41-\x7f]+$" % maxsize, flags=re.IGNORECASE)
        self.ascii_quoted = re.compile(r"^\"[\x00-\x7f]{0,%u}\"@[\x00-\x3f\x41-\x7f]+$" % (maxsize-2), flags=re.IGNORECASE)

    def __call__(self, mailAddress: str) -> bool:
        # there has to be an "@" in the address
        return mailAddress != '' and \
            (self.ascii_noadd.match(mailAddress) or self.ascii_quoted.match(mailAddress)) \
            and not self.check_startsendsdot(mailAddress)


class PrintableAsciiOnly(Addrcheckint):
    """
    Allow ascii printable characters only, "@" in local part has to be quoted, max 64 chars in localpart
    """

    def __init__(self, maxsize: int = 64):
        super().__init__(maxsize)
        self.ascii_noadd = re.compile(r"^[\x20-\x3f\x41-\x7e]{1,%u}@[\x20-\x3e\x41-\x7e]+$" % maxsize, flags=re.IGNORECASE)
        self.ascii_quoted = re.compile(r"^\"[\x20-\x7e]{0,%u}\"@[\x20-\x3f\x41-\x7e]+$" % (maxsize-2), flags=re.IGNORECASE)

    def __call__(self, mailAddress: str) -> bool:
        # there has to be an "@" in the address
        return mailAddress != '' and \
            (self.ascii_noadd.match(mailAddress) or self.ascii_quoted.match(mailAddress)) \
            and not self.check_startsendsdot(mailAddress)


class NoCheck(Addrcheckint):
    """
    Disable check
    """

    def __init__(self, maxsize: int = 64):
        super(NoCheck, self).__init__(maxsize)

    def __call__(self, mailAddress: str) -> bool:
        return True
