# -*- coding: UTF-8 -*-
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
#
#
import copy
import hashlib
import logging
import os
import time
import socket
import uuid
import threading
import email
import re
import configparser
import datetime
import traceback
import operator
import tempfile as tf
import typing as tp
import weakref
import json

from string import Template
from email.header import Header, decode_header
import email.utils
from email.mime.base import MIMEBase
from email.mime.message import MIMEMessage
from email.mime.text import MIMEText
from email.headerregistry import HeaderRegistry, BaseHeader
from email.policy import SMTP
from email.parser import HeaderParser
from collections.abc import Mapping
from html.parser import HTMLParser
from functools import wraps
from io import StringIO
import urllib.parse

from .addrcheck import Addrcheck
from .stringencode import force_uString, force_bString
from .mailattach import Mailattachment_mgr
from .lib.patchedemail import PatchedMessage, PatchedMIMEMultipart
from .funkyconsole import FunkyConsole
from .mixins import DefConfigMixin, SimpleTimeoutMixin, ReturnOverrideMixin

try:
    import bs4 as BeautifulSoup
    HAVE_BEAUTIFULSOUP = True
except ImportError:
    BeautifulSoup = None
    HAVE_BEAUTIFULSOUP = False

try:
    from lxml import etree # this is what's really needed, in some broken installations it may be missing
    HAVE_LXML = True
except ImportError:
    HAVE_LXML = False

try:
    from domainmagic import extractor, tld
except ImportError:
    extractor = None
    tld = None

# constants

DUNNO = 0  # go on
ACCEPT = 1  # accept message, no further tests
DELETE = 2  # blackhole, no further tests
REJECT = 3  # reject, no further tests
DEFER = 4  # defer, no further tests

ALLCODES = {
    'DUNNO': DUNNO,
    'ACCEPT': ACCEPT,
    'DELETE': DELETE,
    'REJECT': REJECT,
    'DEFER': DEFER,
}


headerregistry = HeaderRegistry()

def make_header(header: str, value: str) -> BaseHeader:
    """returns a header object based on class determined by headerregistry"""
    hdrclass = headerregistry[header]
    hdr = hdrclass(header, value)
    return hdr

_re_crlfws = re.compile(r'\r\n(?![ \t])') # CRFL not followed by space or tab (multline header separator)
_re_nocrlf = re.compile(r'(?<!\r)\n') # single LF, not after CR
_re_crnolf = re.compile(r'\r(?!\n)') # single CR, not followed by LF
def fold_header(header: str, value: str, policy=SMTP, value_only: bool = False) -> str:
    """returns a correctly folded and encoded (multiline) header as string"""
    hdr = make_header(header, value)
    hdrval = hdr.fold(policy=policy).strip()
    hdrval = _re_crlfws.sub('=?utf-8?q?=0D=0A?=', hdrval) # replace CRLF
    hdrval = _re_nocrlf.sub('=?utf-8?q?=0A?=', hdrval) # replace single LF
    hdrval = _re_crnolf.sub('=?utf-8?q?=0D?=', hdrval) # replace single CR
    if value_only:
        hdrval = hdrval.split(':',1)[-1].strip()
    else:
        hdrval += policy.linesep
    return hdrval


def actioncode_to_string(actioncode):
    """Return the human-readable string for this code"""
    for key, val in list(ALLCODES.items()):
        if val == actioncode:
            return key
    if actioncode is None:
        return "NULL ACTION CODE"
    return f'INVALID ACTION CODE {actioncode}'


def string_to_actioncode(actionstring, config=None):
    """return the code for this action"""
    upper = actionstring.upper().strip()

    # support DISCARD as alias for DELETE
    if upper == 'DISCARD':
        upper = 'DELETE'

    if config is not None:
        if upper == 'DEFAULTHIGHSPAMACTION':
            confval = config.get('spam', 'defaulthighspamaction').upper()
            if confval not in ALLCODES:
                return None
            return ALLCODES[confval]

        if upper == 'DEFAULTLOWSPAMACTION':
            confval = config.get('spam', 'defaultlowspamaction').upper()
            if confval not in ALLCODES:
                return None
            return ALLCODES[confval]

        if upper == 'DEFAULTVIRUSACTION':
            confval = config.get('virus', 'defaultvirusaction').upper()
            if confval not in ALLCODES:
                return None
            return ALLCODES[confval]

    if upper not in ALLCODES:
        return None
    return ALLCODES[upper]


def utcnow() -> datetime:
    """Return timezone-aware utc-datetime object"""
    return datetime.datetime.now(datetime.timezone.utc)


class FuConfigParser:
    """
    A RawConfigParser with support for comma separated lists of values
    """

    class _Undefined:
        pass

    def __init__(self, *args, **kwargs):
        if not 'strict' in kwargs:
            kwargs['strict'] = False
        self._rawconfigparser = configparser.RawConfigParser(*args, **kwargs)
        self.configpath = None

        # defaults, setup by plugin values
        self._defaultdict = {}

        # Markers with default value, put None as value
        # if there's no default value for a marker
        # Note: markers are for replacements in strings
        self.markers = {
            '${confdir}': "/etc/fuglu"
        }

    def update_defaults(self, section: str, defaults: tp.Dict):
        """Add dictionary to defaults"""
        updatedict = {}
        for k, v in defaults.items():
            active_section = v.get("section", section)
            default = v.get('default', FuConfigParser._Undefined)
            if default is not FuConfigParser._Undefined:
                if active_section not in updatedict:
                    updatedict[active_section] = {}
                updatedict[active_section][k] = default
        for sec, values in updatedict.items():
            if sec not in self._defaultdict:
                self._defaultdict[sec] = values
            else:
                self._defaultdict[sec].update(values)

    def _get_fallback(self, section, option, **kwargs):
        """Extract fallback argument from parameters, set fallback from defaults"""
        if 'fallback' in kwargs:
            fallback = kwargs.pop('fallback')
        else:
            try:
                fallback = self._defaultdict[section][option]
            except KeyError:
                # noinspection PyProtectedMember
                # noinspection PyUnresolvedReferences
                fallback = configparser._UNSET
        return fallback
    
    # noinspection PyProtectedMember
    # noinspection PyUnresolvedReferences
    def getlist(self,  section: str, option: str, separators: str = ',',
                strip: bool = True, lower: bool = False,
                fallback = configparser._UNSET,
                override: tp.Optional[str] = None,
                **kwargs) -> list:
        resolve_env = kwargs.pop("resolve_env", False)
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        if fallback == configparser._UNSET:
            fallback = self._get_fallback(section, option, **kwargs)

        if override is not None:
            # override the value returned by get while still applying all other transformations
            value = override
        else:
            value = self._rawconfigparser.get(section, option, fallback=fallback, **kwargs)
        if resolve_env and value:
            # the whole list could be stored as environment variable
            value = self.resolve_env(value)
        value = self.apply_markers(value)

        if value:
            valuelist = re.split(f'[{re.escape(separators)}]', value)
            if strip:
                valuelist = [v.strip() for v in valuelist]
            if lower:
                valuelist = [v.lower() for v in valuelist]
            valuelist = [v for v in valuelist if v]  # remove empty elements
        else:
            valuelist = []

        if resolve_env and valuelist:
            valuelist = [self.resolve_env(v) for v in valuelist]

        return valuelist
    
    # noinspection PyProtectedMember
    # noinspection PyUnresolvedReferences
    def getint(self, section: str, option: str, fallback=configparser._UNSET,
               override: tp.Optional[tp.Union[str, int]] = None,
               **kwargs):
        """
        Wraps RawConfigParser.getint with default fallback from internal
        class dictionary.
        """
        if override is not None:
            # convert using RawConfigParser method which just uses 'int'
            if isinstance(override, int):
                return override
            else:
                return int(override)

        if fallback == configparser._UNSET:
            fallback = self._get_fallback(section, option, **kwargs)
            if isinstance(fallback, str):
                # convert using RawConfigParser method
                fallback = int(fallback)
        return self._rawconfigparser.getint(section, option, fallback=fallback, **kwargs)


    # noinspection PyProtectedMember
    # noinspection PyUnresolvedReferences
    def getfloat(self, section: str, option: str, fallback=configparser._UNSET,
                 override: tp.Optional[tp.Union[str, float]] = None,
                 **kwargs):
        """
        Wraps RawConfigParser.getfloat with default fallback from internal
        class dictionary.
        """
        if override is not None:
            # convert using RawConfigParser method which just uses 'float'
            if isinstance(override, float):
                return override
            else:
                return float(override)

        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        if fallback == configparser._UNSET:
            fallback = self._get_fallback(section, option, **kwargs)
            if isinstance(fallback, str):
                # convert using RawConfigParser method
                fallback = float(fallback)
        return self._rawconfigparser.getfloat(section, option, fallback=fallback, **kwargs)
    
    # noinspection PyProtectedMember
    # noinspection PyUnresolvedReferences
    def getboolean(self, section: str, option: str, fallback=configparser._UNSET,
                   override: tp.Optional[tp.Union[str, bool]] = None,
                   **kwargs):
        """
        Wraps RawConfigParser.getboolean with default fallback from internal
        class dictionary.
        """
        if override is not None:
            if isinstance(override, bool):
                return override
            else:
                # convert using RawConfigParser method
                return self._rawconfigparser._convert_to_boolean(override)

        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        if fallback == configparser._UNSET:
            fallback = self._get_fallback(section, option, **kwargs)
            if isinstance(fallback, str):
                # convert using RawConfigParser method
                fallback = self._rawconfigparser._convert_to_boolean(fallback)

        return self._rawconfigparser.getboolean(section, option, fallback=fallback, **kwargs)

    def apply_markers(self, inputstring: str) -> str:
        """ Replace markers like ${confdir} """
        outstring = inputstring

        if isinstance(outstring, str):
            for key, value in self.markers.items():
                if value is not None:
                    outstring = outstring.replace(key, value)

        return outstring

    def resolve_env(self, inputstring: str) -> tp.Optional[str]:
        outstring = inputstring
        if outstring and outstring.startswith("$") and len(outstring) > 1:
            # check if variable starts with "$" and if yes, try to get a value
            outstring = os.getenv(outstring[1:], default=outstring)
        return outstring

    def set_configpath_from_configfile(self, configfile: str):
        # Set absolute config path which can be used later in getter
        # -> For example
        path, _ = os.path.split(os.path.abspath(configfile))
        self.markers['${confdir}'] = path

    # noinspection PyProtectedMember
    # noinspection PyUnresolvedReferences
    def get(self, section: str, option: str, fallback=configparser._UNSET,
            override: tp.Optional[str] = None,
            **kwargs) -> str:
        """ Custom get replacing markers like ${confdir} """
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        if fallback == configparser._UNSET:
            fallback = self._get_fallback(section, option, **kwargs)

        resolve_env = kwargs.pop("resolve_env", False)

        if override is not None:
            outstring = override
        else:
            outstring = self._rawconfigparser.get(section, option, fallback=fallback, **kwargs)

        if resolve_env:
            outstring = self.resolve_env(outstring)
        outstring = self.apply_markers(outstring)
        return outstring

    def __getattr__(self, name):
        """
        Delegate to RawConfigParser.
        """
        return getattr(self._rawconfigparser, name)


class _SuspectTemplate(Template):
    delimiter = '$'
    idpattern = r'@?[a-z][_a-z0-9.:]*'


class _SuspectDict(Mapping):
    """Dictionary-like object which fetches SuspectFilter values dynamically"""

    def __init__(self, suspect, values, valuesfunction):
        self.values = values
        self.filter = SuspectFilter(filename=None)
        self.valuesfunction = valuesfunction
        self.suspect = suspect

    def _get_raw(self, item):
        if item in self.values:  # always try the passed dict first
            return self.values[item]
        # get the value from the filter
        fieldlist = self.filter.get_field(self.suspect, item)
        if len(fieldlist):
            # if there are multiple values , just return the first
            return force_uString(str(fieldlist[0]))
        return None

    def __getitem__(self, item):
        val = self._get_raw(item)
        if self.valuesfunction:
            try:
                # valuesfunction expects a dict (backward compatibility)
                val = self.valuesfunction({item: val})[item]
            except KeyError:
                val = None
        if val is not None:
            self.values[item] = val
            return val
        return ''

    def __iter__(self):
        return iter(self.values.copy())

    def __len__(self):
        return len(self.values)


def apply_template(templatecontent, suspect, values=None, valuesfunction=None):
    """Replace templatecontent variables as defined in https://fumail.gitlab.io/fuglu/plugins-index.html#template-variables
    with actual values from suspect
    the calling function can pass additional values by passing a values dict

    if valuesfunction is not none, it is called with the final dict with all built-in and passed values
    and allows further modifications, like SQL escaping etc
    """
    if values is None:
        values = {}

    default_template_values(suspect, values)
    sdict = _SuspectDict(suspect, values, valuesfunction)
    template = _SuspectTemplate(force_uString(templatecontent))
    message = template.safe_substitute(sdict)
    return message


def default_template_values(suspect, values=None):
    """Return a dict with default template variables applicable for this suspect
    if values is not none, fill the values dict instead of returning a new one"""

    if values is None:
        values = {}

    values['id'] = suspect.id
    values['timestamp'] = suspect.timestamp
    values['from_address'] = suspect.from_address
    values['to_address'] = suspect.to_address
    values['from_domain'] = suspect.from_domain
    values['from_localpart'] = suspect.from_localpart
    values['to_domain'] = suspect.to_domain
    values['to_localpart'] = suspect.to_localpart
    values['subject'] = suspect.get_header('subject')
    values['date'] = str(datetime.date.today())
    values['time'] = time.strftime('%X')
    return values


def redact_uri(uri: str, mask: str = '*****') -> str:
    """
    Redact a password in a URI. If no password is found in URI nothing should be changed
    :param uri: string: the URI to redact
    :param mask: string: the replacement for the password
    :return: string: the redacted URI
    """
    p = urllib.parse.urlparse(uri)
    netloc = p.hostname # hostname is mandatory
    if p.port: # add port if it exists
        netloc += ':' + str(p.port)
    userpass = p.username or '' # get username if it exists
    if p.password: # add password if it exists
        userpass += ':' + mask
    if userpass: # add user/pass to host/port
        netloc = userpass + '@' + netloc
    return p._replace(netloc=netloc).geturl() # we have read access to all netloc components, but can only set netloc atomically


HOSTNAME = socket.getfqdn()


def yesno(val):
    """returns the string 'yes' for values that evaluate to True, 'no' otherwise"""
    if val:
        return 'yes'
    else:
        return 'no'


def deprecated(func):
    """
    use this decorator to mark deprecated functions
    """
    @wraps(func)
    def deprecated_wrapper(*args, **kwargs):
        logger = logging.getLogger('fuglu.deprecated')
        logger.error(f'called deprecated function {func.__qualname__}')
        return func(*args, **kwargs)
    return deprecated_wrapper


# Use Class variable to store the outgoing helo globally
# (Similar to the Singleton implementation)
class HeloSingleton:
    _outgoinghelo = None

    @classmethod
    def outgoinghelo(cls, config):
        if cls._outgoinghelo is None:
            if config is None:
                logging.getLogger('fuglu.HeloSingleton').error(
                    "outgoing helo called without config while there's no config defined -> return hostname and don't cache result")
                return HeloSingleton.__get_outgoing(config=config)
            else:
                cls._outgoinghelo = HeloSingleton.__get_outgoing(config=config)
        return cls._outgoinghelo

    @staticmethod
    def __get_outgoing(config=None) -> str:
        outhelo = None
        if config is not None:
            helo = config.get('main', 'outgoinghelo', fallback='')
            if helo.startswith("$"):
                # extract target host from environment variable
                env_helo = os.environ[helo[1:].strip()]
                if not env_helo:
                    raise ValueError(f"Could not extract helo from environment var '{helo}'")
                outhelo = env_helo
            elif helo:
                outhelo = helo

        if outhelo is None:
            outhelo = HOSTNAME
        outhelo = outhelo.lower() # lowercase as some servers (e.g. m365) don't like uppercase hostnames
        return outhelo


def get_outgoing_helo(config=None):
    """Use singleton implementation to store outgoing helo"""
    return HeloSingleton.outgoinghelo(config=config)


class Suspect(SimpleTimeoutMixin):

    """
    The suspect represents the message to be scanned. Each scannerplugin will be presented
    with a suspect and may modify the tags or even the message content itself.
    """

    # tags set by plugins
    _default_tags = {
        'virus': {},
        'blocked': {},
        'spam': {},
        'highspam': {},
        'welcomelisted': {},  # use spamassassin's new wording
        'blocklisted': {},  # use spamassassin's new wording
        'decisions': [],
        'scantimes': []
    }

    def __init__(self, from_address: str, recipients: tp.Union[str, tp.List[str]],
                 tempfile: tp.Optional[str], inbuffer: tp.Optional[bytes] = None,
                 smtp_options: tp.Optional[tp.Set] = None, milter_macros: tp.Optional[tp.Dict] = None,
                 **kwargs):
        super().__init__()

        self.source = None
        """holds the message source if set directly"""

        self._msgrep = None
        """holds a copy of the message representation"""

        # it's possible to pass ID to suspect
        arg_id = kwargs.pop('id', None)
        self.id = arg_id if arg_id else Suspect.generate_id()

        # store additional keyword parameters
        self.kwargs = kwargs

        self.tags = copy.deepcopy(self._default_tags)

        self.logger = logging.getLogger('fuglu.Suspect')

        # temporary file containing the message source
        self._tempfile = tempfile

        # input message buffer
        self.inbuffer = force_bString(inbuffer)

        # stuff set from smtp transaction
        if tempfile:
            self.size = os.path.getsize(tempfile)
        elif inbuffer:
            self.size = len(self.inbuffer)
        else:
            self.size = None
        self.from_address = force_uString(from_address)
        from_address_stripped = self.from_address.strip() if self.from_address else self.from_address
        if from_address_stripped != self.from_address:
            self.logger.info(f"{self.id} Stripped whitespaces from from_adress '{self.from_address}' -> '{from_address_stripped}'")
            self.from_address = from_address_stripped

        # backwards compatibility, recipients can be a single address
        if isinstance(recipients, list):
            recipientlist = [force_uString(rec) for rec in recipients]
        else:
            recipientlist = [force_uString(recipients), ]

        # basic email validitiy check - nothing more than necessary for our internal assumptions
        self.recipients = []
        for rec in recipientlist:
            if rec is None:
                self.logger.warning(f"{self.id} Recipient address can not be None")
                raise ValueError("Recipient address can not be None")
            if not Addrcheck().valid(rec, allow_postmaster=True):
                self.logger.warning(f"{self.id} Invalid recipient address: {rec}")
                raise ValueError(f"Invalid recipient address: {rec}")
            rec_stripped = rec.strip()
            if rec_stripped != rec:
                self.logger.info(f"{self.id} Stripped whitespaces from recipient '{rec}' -> '{rec_stripped}'")
            self.recipients.append(rec_stripped)

        # additional basic information
        self.timestamp = kwargs.get("timestamp", time.time())
        self.timestamp_utc = kwargs.get("timestamp_utc", utcnow().timestamp())

        # headers which are prepended before re-injecting the message
        self.addheaders = {}

        if self.from_address is None:
            self.from_address = ''

        if self.from_address != '' and not Addrcheck().valid(self.from_address):
            self.logger.warning(f"{self.id} Invalid sender address: {self.from_address}")
            raise ValueError(f"Invalid sender address: {self.from_address}")

        """holds client info tuple: helo, ip, reversedns"""
        self.clientinfo = None

        """Attachment manager"""
        self._att_mgr = None

        # ------------- #
        # modifications #
        # ------------- #
        self.modified_headers = {}
        """To keep track of modified headers"""

        self.added_headers = {}
        """To keep track of already added headers (not in self.addheaders)"""

        self.removed_headers = {}
        """To keep track of already removed headers"""

        # keep track of original sender/receivers
        self.original_from_address = self.from_address
        self.original_recipients = self.recipients

        # ------------ #
        # smtp_otpions #
        # ------------ #
        self.smtp_options = set() if smtp_options is None else smtp_options
        self.milter_macros = dict() if milter_macros is None else milter_macros

        # eventually, size was also given in MAIL-FROM command
        mfsize = self.kwargs.get('mfsize', None)
        if self.size and isinstance(mfsize, int) and self.size < int(mfsize*0.9):
            errmsg = f"{self.id} Message size received {self.size} is smaller than 90% of " \
                     f"the proposed size in MAILFROM {mfsize}"

            self.logger.error(errmsg)
            raise Exception(errmsg)

        # log basic line describing filename/buffer and other mail basics
        self._log_incoming_basics(tempfile, inbuffer)
        
        # cache parsed from headers
        self._cache_from_type_headers = {}
        self._header_cache = {}

        # timetracker (reference to session which is derived from TrackTimings)
        self._timetracker = None

        # ------------------------- #
        # Attachment manager limits #
        # ------------------------- #
        # as property directly from kwargs:
        # - self._att_cachelimit
        # - self._att_defaultlimit
        # - self._att_maxlimit
        # - self._att_fdefaultlimit
        # - self._att_fmaxlimit

        # ------------------------ #
        # SASL authentication info #
        # queue id                 #
        # (milter mode only)       #
        # ------------------------ #
        # as property directly from kwargs:
        # - self.sasl_login
        # - self.sasl_sender
        # - self.sasl_method

        # ------------------ #
        # queue id           #
        # (milter mode only) #
        # ------------------ #
        # as property directly from kwargs:
        # self.queue_id

        # ---------- #
        # Assertions #
        # ---------- #
        # note the assertions are at the end because everything below will not be called
        # and variables not set, which is however still required for the HealthCheckSuspect

        # either there is a filename defined or a message buffer given
        # (filename can be /dev/null for an empty suspect)
        assert bool(tempfile) or bool(inbuffer)

        # either filename or buffer, not both...
        assert not (bool(tempfile) and bool(inbuffer))

    def _log_incoming_basics(self, tempfile:str, inbuffer:tp.Optional[bytes]) -> None:
        """Basic logline, ousourced to a separate routine so it can easily be overwritten in healthcheck"""
        self.logger.info(f"{self.id} "
                         f"from={self.from_address}, "
                         f"nrec={len(self.recipients)}, "
                         f"file={tempfile if tempfile else ''}, "
                         f"buffer={bool(inbuffer)}, "
                         f"size={self.size}, "
                         f"mfsize={self.kwargs.get('mfsize', 'N/A')}"
                         )

    @property
    def timetracker(self):
        """
        returns scansession.TrackTimings object or None
        """
        return self._timetracker() if self._timetracker else self._timetracker

    @timetracker.setter
    def timetracker(self, tobj):
        """
        set weakref to scansession.TrackTimings object or remove by sending None
        """
        self._timetracker = weakref.ref(tobj) if tobj is not None else None

    @property
    def tmpdir(self) -> str:
        return self.kwargs.get('queue_id', '/tmp')

    @property
    def tempfile(self) -> tp.Optional[str]:
        if self._tempfile is None:

            (handle, tempfilename) = tf.mkstemp(prefix='fuglu', dir=self.tmpdir)
            if self.inbuffer:
                self._tempfile = tempfilename
                try:
                    fhandle = os.fdopen(handle, 'w+b')
                    fhandle.write(self.inbuffer)
                    fhandle.close()
                    self.logger.debug(f"{self.id} -> tempfile requested, creating file from buffer")
                except Exception as e:
                    self.logger.error(f"{self.id} -> tempfile requested, error creating file from buffer: {str(e)}", exc_info=e)
                    self._tempfile = None
            else:
                self.logger.error(f"{self.id} -> tempfile requested but there's no filename and no buffer!")

        return self._tempfile

    def tempfilename(self) -> str:
        if self._tempfile:
            return self._tempfile
        else:
            return "(buffer-only)"

    @tempfile.setter
    def tempfile(self, val:str) -> None:
        self._tempfile = val

    @property
    def queue_id(self) -> str:
        return self.kwargs.get('queue_id')

    @property
    def _att_cachelimit(self):
        return self.kwargs.get('att_cachelimit')

    @property
    def _att_defaultlimit(self):
        return self.kwargs.get('att_defaultlimit')

    @property
    def _att_maxlimit(self):
        return self.kwargs.get('att_maxlimit')

    @property
    def _att_fdefaultlimit(self):
        return self.kwargs.get('att_fdefaultlimit')

    @property
    def _att_fmaxlimit(self):
        return self.kwargs.get('att_fmaxlimit')

    @property
    def sasl_login(self):
        self.logger.warning(f"{self.id} deprecated suspect.sasl_login: use suspect.milter_macros.get('auth_authen') instead")
        return self.milter_macros.get('auth_authen')

    @property
    def sasl_user(self):
        self.logger.warning(f"{self.id} deprecated suspect.sasl_user: use suspect.milter_macros.get('auth_authen') instead")
        return self.milter_macros.get('auth_authen')

    @property
    def sasl_sender(self):
        self.logger.warning(f"{self.id} deprecated suspect.sasl_sender: use suspect.milter_macros.get('auth_author') instead")
        return self.milter_macros.get('auth_author')

    @property
    def sasl_method(self):
        self.logger.warning(f"{self.id} deprecated suspect.sasl_method: use suspect.milter_macros.get('auth_type') instead")
        return self.milter_macros.get('auth_type')

    def orig_from_address_changed(self) -> bool:
        return self.original_from_address != self.from_address

    def orig_recipients_changed(self) -> bool:
        return self.original_recipients != self.recipients

    @property
    def att_mgr(self) -> Mailattachment_mgr:
        if self._att_mgr is None:
            self._att_mgr = Mailattachment_mgr(self.get_message_rep(), self.id,
                                               cachelimit=self._att_cachelimit,
                                               default_filelimit=self._att_defaultlimit,
                                               max_filelimit=self._att_maxlimit,
                                               default_numfilelimit=self._att_fdefaultlimit,
                                               max_numfilelimit=self._att_fmaxlimit
                                               )
        return self._att_mgr

    @property
    def to_address(self) -> tp.Optional[str]:
        """Returns the first recipient address"""
        try:
            return self.recipients[0]
        except IndexError:
            return None

    @to_address.setter
    def to_address(self, recipient:str):
        """Sets a single recipient for this suspect, removing all others"""
        self.recipients = [recipient, ]

    @property
    def to_localpart(self) -> tp.Optional[str]:
        """Returns the local part of the first recipient"""
        # catch empty and None
        if not self.to_address:
            return ''
        try:
            return self.to_address.rsplit('@', 1)[0]
        except Exception:
            self.logger.error(f'{self.id} could not extract localpart from recipient address {self.to_address}')
            return None

    @property
    def to_domain(self) -> tp.Optional[str]:
        """Returns the local part of the first recipient"""
        # catch empty and None
        if not self.to_address:
            return ''
        try:
            return self.to_address.rsplit('@', 1)[1]
        except Exception:
            self.logger.error(f'{self.id} could not extract domain from recipient address {self.to_address}')
            return None

    @property
    def from_localpart(self) -> tp.Optional[str]:
        # catch empty and None
        if not self.from_address:
            return ''

        else:
            try:
                return self.from_address.rsplit('@', 1)[0]
            except Exception:
                self.logger.error(f'{self.id} could not extract localpart from sender address {self.from_address}')
                return None

    @property
    def from_domain(self) -> tp.Optional[str]:
        # catch empty and None
        if not self.from_address:
            return ''

        else:
            try:
                return self.from_address.rsplit('@', 1)[1]
            except Exception:
                self.logger.error(f'{self.id} could not extract domain from sender address {self.from_address}')
                return None

    @staticmethod
    def generate_id() -> str:
        """
        returns a unique id (a string of 32 hex characters)
        """
        return uuid.uuid4().hex

    _re_fugluid = re.compile('^[a-f0-9]{32}$', re.I)

    def check_id(self, id:str=None) -> bool:
        """
        verify id is a valid fuglu id (a string of 32 hex characters)
        """
        if id is None:
            id = self.id
        return bool(self._re_fugluid.match(id))

    def debug(self, message:str) -> None:
        """Add a line to the debug log if debugging is enabled for this message"""
        if not self.get_tag('debug'):
            return
        isotime = utcnow().isoformat()
        fp = self.get_tag('debugfile')
        try:
            fp.write(f'{isotime} {message}\n')
            fp.flush()
        except Exception as e:
            self.logger.error(f'{self.id} Could not write to logfile: {e.__class__.__name__}: {str(e)}')

    def get_tag(self, key:str, defaultvalue:tp.Any=None) -> tp.Any:
        """returns the tag value. if the tag is not found, return defaultvalue instead (None if no defaultvalue passed)"""
        if key not in self.tags:
            return defaultvalue
        return self.tags[key]

    def set_tag(self, key:str, value:tp.Any) -> None:
        """Set a new tag"""
        if isinstance(value, str) and len(value)>256:
            logvalue = value[:256] + '...'
        elif isinstance(value, bytes) and len(value)>256:
            logvalue = value[:256] + b'...'
        else:
            try:
                logvalue = value.__class__.__name__ + ' ' + str(value)
            except Exception as e:
                logvalue = f'unknown({e.__class__.__name__}: {str(e)}'
            if len(logvalue) > 256:
                logvalue = logvalue[:256] + '...'
        self.logger.debug(f"{self.id} setting tag {key}:{logvalue}")
        self.tags[key] = value

    def __tagsummary(self, tagname:str) -> bool:
        for key in list(self.tags[tagname].keys()):
            val = self.tags[tagname][key]
            if val:
                return True
        return False

    def is_highspam(self) -> bool:
        """Returns True if ANY of the spam engines tagged this suspect as high spam"""
        return self.__tagsummary('highspam')

    def is_spam(self) -> bool:
        """Returns True if ANY of the spam engines tagged this suspect as spam"""
        return self.__tagsummary('spam')

    def is_blocked(self) -> bool:
        """Returns True if ANY plugin tagged this suspect as blocked content"""
        return self.__tagsummary('blocked')

    def is_virus(self) -> bool:
        """Returns True if ANY of the antivirus engines tagged this suspect as infected"""
        return self.__tagsummary('virus')

    def is_welcomelisted(self) -> bool:
        """Returns True if ANY plugin tagged this suspect as 'welcome by recipient'"""
        return self.__tagsummary('welcomelisted')

    def is_blocklisted(self) -> bool:
        """Returns True if ANY plugin tagged this suspect as 'not welcome by recipient'"""
        return self.__tagsummary('blocklisted')

    def is_ham(self) -> bool:
        """Returns True if message is neither considered to be spam, virus, blocked or blocklisted"""
        if self.is_spam() or self.is_virus() or self.is_blocked() or self.is_highspam() or self.is_blocklisted():
            return False
        return True

    _status_funcs = [is_ham, is_spam, is_highspam, is_blocked, is_virus, is_welcomelisted, is_blocklisted]

    def get_status(self) -> tp.Dict[str,bool]:
        status = {}
        for func in self._status_funcs:
            value = func(self)
            status[func.__name__] = value
        return status

    def update_subject(self, subject_cb:tp.Callable, **cb_params) -> bool:
        """
        update/alter the message subject
        :param subject_cb: callback function that alters the subject. must accept a string and return a string
        :param cb_params: additional parameters to be passed to subject_cb
        :return: True if subject was altered, False otherwise
        """
        oldsubj = self.get_header('subject')
        oldsubj_exists = True
        if oldsubj is None:
            oldsubj = ""
            oldsubj_exists = False

        decsubj = self.decode_msg_header(oldsubj, logid=self.id)
        newsubj = subject_cb(decsubj, **cb_params)
        if oldsubj != newsubj:
            foldsubj = fold_header('subject', newsubj, value_only=True)
            self.remove_headers_from_source({'subject'}, track_change=False)  # don't track change because it would add an unnecessary "remove" in milter-mode
            self.set_source(Suspect.prepend_header_to_source('subject', foldsubj, self.get_source(), raw=True), att_mgr_reset=False)
            try:
                del self._header_cache['subject']
            except KeyError:
                pass

            # store as modified header
            if oldsubj_exists:
                self.modified_headers["subject"] = newsubj
            else:
                self.added_headers["subject"] = newsubj

            if self.get_tag('origsubj') is None:
                self.set_tag('origsubj', oldsubj)
            return True
        return False

    def set_header(self, key:str, value:str) -> None:
        """
        Replace existing header or create a new one

        Args:
            key (string): header key
            value (string): header value

        """
        msg = self.get_message_rep()

        # convert inputs if needed
        key = force_uString(key)
        value = force_uString(value)

        oldvalue = msg.get(key, None)
        self.logger.debug(f"{self.id} set_header -> modify '{key}' from '{oldvalue}' to {value}")
        if oldvalue is not None:
            if force_uString(oldvalue) == value:
                self.logger.debug(f"{self.id} set_header -> modify '{key}' unnecessary since oldvalue == newvalue")
                return
            self.remove_headers_from_source({key}, track_change=False)  # don't track change because it would add an unnecessary "remove" in milter mode
            self.modified_headers[key] = value
            self.set_source(Suspect.prepend_header_to_source(key, value, self.get_source()), att_mgr_reset=False)
        else:
            self.logger.debug(f"{self.id} set_header -> add instead of modify '{key}' with '{oldvalue}' because header doesn't exist yet")
            self.add_header(key, value, immediate=True)
            

    def remove_headers(self, key:str) -> bool:
        """
        Remove existing header(s) with given name

        Args:
            key (string): header key

        """
        msg = self.get_message_rep()

        # convert inputs if needed
        key = force_uString(key)
        
        removed = False
        oldvalues = msg.get_all(key, [])
        if oldvalues:
            del msg[key]
            self.logger.debug(f"{self.id} remove_headers -> remove headers '{key}' with '{oldvalues}'")
            if self.removed_headers.get(key):
                self.removed_headers[key].extend(oldvalues)
            else:
                self.removed_headers[key] = oldvalues
            self.set_message_rep(msg, att_mgr_reset=False)
            removed = True
        return removed
    
    
    def remove_headers_from_source(self, headernames:tp.Iterable[str], track_change: bool = True) -> bool:
        """
        removes headers without changing body code e.g. by dumping source from msg rep
        :param headernames: List of header names to remove
        :param track_change: Track changes (to be applied in milter mode later on)
        :return: True if anything was removed, False if no change in source
        """
        deleted = False
        msgrep = self.get_message_rep()
        delhdrs = {h.lower() for h in msgrep.keys()} & {h.lower() for h in headernames} # intersect sets
        if delhdrs:
            delhdrs = tuple({h.encode()+b':' for h in delhdrs})
            source = self.get_source()
            lines = source.splitlines(True) # preserve line endings
            newlines = []
            in_hdr = True
            hdrname = b''
            for line in lines:
                if not line.strip(): # empty line indicates end of headers
                    in_hdr = False
                if in_hdr and (line.lower().startswith(delhdrs) or hdrname and line.startswith((b' ', b'\t'))): # skip header
                    self.logger.debug(f'{self.id} delete header line {force_uString(line)}')
                    deleted = True
                    try:
                        if not line.startswith((b' ', b'\t')):
                            hdrname, value = line.split(b':',1)
                            hdrname = hdrname.decode()
                            value = value.decode()
                            if track_change:
                                try:
                                    self.removed_headers[hdrname].append(value)
                                except KeyError:
                                    self.removed_headers[hdrname] = [value]
                        else:
                            value = line.decode()
                            if track_change:
                                self.removed_headers[hdrname][-1] += value
                    except Exception as e:
                        self.logger.warning(f'{self.id} failed to update removed_headers with {line} due to {e.__class__.__name__}: {str(e)}')
                else: # keep line
                    hdrname = b''
                    newlines.append(line)
            if deleted:
                self.set_source(b''.join(newlines))
        return deleted
    
    @staticmethod
    def decode_msg_header(header: tp.Union[str, bytes, email.header.Header], decode_errors:str="replace", logid='n/a') -> str:
        """
        Decode message header from email.message into unicode string

        Args:
            header (str, email.header.Header): the header to decode
            decode_errors (str): error handling as in standard bytes.decode -> strict, ignore, replace
            logid (str): prefix of log message, usually suspect id
        Returns:
            str
        """
        try:
            PSEUDO_HEADER_NAME = 'header'
            header_unicode = force_uString(header)
            msg = HeaderParser(policy=SMTP).parsestr(f'{PSEUDO_HEADER_NAME}: {header_unicode}')
            headerstring = msg[PSEUDO_HEADER_NAME]
        except Exception as e:
            logger = logging.getLogger('fuglu.Suspect')
            logger.warning(f'{logid} error parsing header value, using legacy fallback due to {e.__class__.__name__}: {str(e)}')
            try:
                headerstring = ''.join([force_uString(x[0], encodingGuess=x[1], errors=decode_errors) for x in decode_header(header)])
            except TypeError:
                # if input is bytes (Py3) we end here
                header_unicode = force_uString(header)
                headerstring = ''.join([force_uString(x[0], encodingGuess=x[1], errors=decode_errors) for x in decode_header(header_unicode)])
            except Exception:
                headerstring = header
        return force_uString(headerstring)

    @staticmethod
    def prepend_header_to_source(key:tp.Union[str,bytes], value:tp.Union[str,bytes], source:bytes, raw: bool = False) -> bytes:
        """
        Prepend a header to the message

        Args:
            key (str): the header key
            value (str): the header value
            source (bytes): the message source
            raw (bool): Just add header raw as 'key: value\r\n', caller is responsible for correct formatting

        Returns:
            bytes: the new message buffer

        """

        b_source = force_bString(source)

        # convert inputs if needed
        u_key = force_uString(key).strip()
        u_value = force_uString(value).strip()
        if raw:
            hdr = f"{u_key}: {u_value}\r\n"
        else:
            hdr = fold_header(u_key, u_value)
        src = force_bString(hdr) + b_source
        return src

    @staticmethod
    def getlist_space_comma_separated(inputstring:str) -> tp.List[str]:
        """Create list from string, splitting at ',' space"""
        BACKSLASH = '{BACKSLASH}'
        SPACE = '{SPACE}'
        COMMA = '{COMMA}'
        finallist = []
        if inputstring:
            inputstring = inputstring.strip()
            # encode escaped spaces/commas to distinguish them from delimiters
            inputstring = inputstring.replace('\\\\', BACKSLASH).replace('\\ ', SPACE).replace('\\,', COMMA)
            if inputstring:
                # check for comma-separated list
                commaseplist = [tag.strip() for tag in inputstring.split(',') if tag.strip()]
                # also handle space-separated list
                for tag in commaseplist:
                    # take elements, split by spac
                    finallist.extend([t.strip() for t in tag.split(' ') if t.strip()])
            rawlist = finallist
            finallist = []
            # decode encoded spaces/commas
            for entry in rawlist:
                finallist.append(entry.replace(SPACE, ' ').replace(COMMA, ',').replace(BACKSLASH, '\\'))

        return finallist
    
    def parse_from_type_header(self, header:str='From', validate_mail:bool=True, recombine:bool=True, use_cache:bool=True) -> tp.List[tp.Tuple[str,str]]:
        """

        Args:
            header (str): name of header to extract, defaults to From
            validate_mail (bool): base checks for valid mail
            recombine (bool): recombine displaypart with mailaddress
            use_cache (bool): do not recalculate if previous result exists

        Returns:
            [(displayname,email), ... ]
                - displayname (str) : display name
                - email (str) : email address

        """
        cachekey = f'{header}-{validate_mail}-{recombine}'
        if use_cache and self._cache_from_type_headers.get(cachekey) is not None:
            return self._cache_from_type_headers.get(cachekey)
        from_headers = self.get_message_rep().get_all(header, [])

        # allow multiple headers
        if len(from_headers) < 1:
            return []

        from_addresses_raw = []
        # replace \r\n by placeholders to allow getaddresses to properly distinguish between mail and display part
        #
        # This seems to be a stable way to overcome issues with encoded and multiline headers, see below
        #
        # Example: encoded display part without quotes
        # =?iso-8859-1?q?alpha=2C_beta?= <alpha.beta@fuglu.org>
        # If decode header:
        # alpha, beta <alpha.beta@fuglu.org>
        # and getaddresses returns
        # [(,alpha), (beta, alpha.beta@fuglu.org)]
        # -> this example works correctly if getaddresses is applied first and then decode_header
        #
        # Example: multiline
        # "=?iso-8859-1?q?alpha=2C?=\r\n =?iso-8859-1?q?beta?=" <alpha.beta@fuglu.org>
        # calling getaddresses returns only the first part
        # [('', '=?iso-8859-1?q?alpha=2C?=')]
        # -> calling decode header and then getaddresses works for this case
        #    (because the display name is surrounded by ", otherwise there's no way
        from_headers = [h.replace('\r', '{{CR}}').replace('\n', '{{LF}}') for h in force_uString(from_headers)]
        try:
            hdr_addresses = email.utils.getaddresses(from_headers, strict=False) # new in 3.11.10 and 3.12.5
        except TypeError:
            hdr_addresses = email.utils.getaddresses(from_headers)
        
        for display, mailaddress in hdr_addresses:

            # after the split, put back the original CR/LF
            if display:
                display = display.replace('{{CR}}', '\r').replace('{{LF}}', '\n')
            if mailaddress:
                mailaddress = mailaddress.replace('{{CR}}', '\r').replace('{{LF}}', '\n')

            # display name eventually needs decoding
            display = self.decode_msg_header(display, logid=self.id)

            # Add if there is a display name or mail address,
            # ignore if both entries are empty
            if display or mailaddress:
                from_addresses_raw.append((display, mailaddress))

        # validate email
        from_addresses_val = []
        for displayname, mailaddress in from_addresses_raw:
            if mailaddress and (not Addrcheck().valid(mailaddress)):
                if displayname:
                    displayname += " "+mailaddress
                else:
                    displayname = mailaddress
                mailaddress = ""
            from_addresses_val.append((displayname, mailaddress))

        # --------- #
        # recombine #
        # --------- #
        #
        # if displaypart and mailaddress are not correctly extracted the might
        # appear in separate tuples, for example:
        # [('Sender', ''), ('', 'sender@fuglu.org')]
        # Recombine tries to merge such entries merging if
        # 1) element has display name but no mail address
        # 2) next consecutive element has no display name but mail address
        if recombine:
            from_addresses_recombined = []
            from collections import deque
            entry_list = deque(from_addresses_val)
            try:
                first = entry_list.popleft()
            except IndexError:
                # empty list
                first = None

            # use a loop counter, so we can check for an infinite loop
            loopcounter = 0
            while first:
                # check if we're in an infinite loop
                loopcounter += 1
                if loopcounter > 2000:
                    raise ValueError("More than 2000 loops in parsing from-type header!")

                display, mailaddress = first
                if mailaddress:
                    from_addresses_recombined.append((display, mailaddress))
                    first = None
                else:
                    # if there's no mail address, check if the next element
                    # has a mail address
                    try:
                        second = entry_list.popleft()
                    except IndexError:
                        # empty list
                        second = None

                    if second:
                        # combine display parts of the elements
                        display2, mailaddress2 = second
                        if display:
                            newdisplay = "{} {}".format(display, display2)
                        else:
                            newdisplay = display2
                        first = (newdisplay.strip(), mailaddress2)
                    else:
                        # if there's no more element, add the current one to the list...
                        from_addresses_recombined.append((display, mailaddress))
                        # set first to None to stop the loop
                        first = None
                if not first:
                    try:
                        first = entry_list.popleft()
                    except IndexError:
                        # empty list
                        first = None
        else:
            from_addresses_recombined = from_addresses_val

        # again decode display part
        from_addresses_decoded = [(self.decode_msg_header(display, logid=self.id), mail.strip())
                                  for display, mail in from_addresses_recombined]

        # validate email
        if validate_mail:
            from_addresses = []
            for displayname, mailaddress in from_addresses_decoded:
                try:
                    isvalid = True
                    if not mailaddress or (not Addrcheck().valid(mailaddress)):
                        isvalid = False
                except Exception as e:
                    isvalid = False
                    self.logger.error(f'{self.id} Parsing error {e.__class__.__name__}: {str(e)}')
                    self.logger.exception(e)

                if isvalid:
                    from_addresses.append((displayname, mailaddress))
                else:
                    self.logger.info(f'{self.id} Mail "{mailaddress}" is not valid, display name is "{displayname}"')
        else:
            from_addresses = from_addresses_decoded
        self._cache_from_type_headers[cachekey] = from_addresses
        return from_addresses

    def add_header(self, key:str, value:str, immediate:bool=False, raw: bool = False) -> None:
        """adds a header to the message. by default, headers will be added when re-injecting the message back to postfix
        if you set immediate=True the message source will be replaced immediately. Only set this to true if a header must be
        visible to later plugins (e.g. for spamassassin rules), otherwise, leave as False which is faster.

        raw: Just add header raw as 'key: value\r\n', caller is responsible for correct formatting, only available if immediate is True
        """

        # convert inputs if needed
        key = force_uString(key)
        value = force_uString(value)

        if immediate:
            # no need to reset the attachment manager when just adding a header
            self.set_source(Suspect.prepend_header_to_source(key, value, self.get_source(), raw=raw), att_mgr_reset=False)
            # keep track of headers already added
            self.added_headers[key] = value
        else:
            if raw:
                self.logger.warning(f"{self.id} (add_header) raw option is only available if immediate is True -> ignoring")
            self.addheaders[key] = value

    @deprecated
    def addheader(self, key, value, immediate=False):
        """old name for add_header"""
        return self.add_header(key, value, immediate)

    def get_current_decision_code(self):
        dectag = self.get_tag('decisions')
        if dectag is None:
            return DUNNO
        try:
            pluginname, code = dectag[-1]
            return code
        except Exception:
            return DUNNO

    def _short_tag_rep(self) -> str:
        """return a tag representation suitable for logging, with some tags stripped, some shortened"""
        skiplist = {'decisions', 'scantimes', 'debugfile'}
        tagscopy = {}

        for k, v in self.tags.items():
            if k in skiplist:
                continue

            try:
                strrep = str(v)
            except Exception:  # Unicodedecode errors and stuff like that
                continue

            therep = v

            maxtaglen = 100
            if len(strrep) > maxtaglen:
                therep = strrep[:maxtaglen] + "..."

            # specialfixes
            if k.endswith('.spamscore') and not isinstance(v, str):
                therep = f"{v:.2f}"

            tagscopy[k] = therep
        return str(tagscopy)

    def log_format(self, template:tp.Optional[str]=None):
        addvals = {
            'size': self.size,
            'spam': yesno(self.is_spam()),
            'highspam': yesno(self.is_highspam()),
            'blocked': yesno(self.is_blocked()),
            'virus': yesno(self.is_virus()),
            'modified': yesno(self.is_modified()),
            'decision': actioncode_to_string(self.get_current_decision_code()),
            'tags': self._short_tag_rep(),
            'fulltags': str(self.tags),
        }
        return apply_template(template, self, addvals)

    def __str__(self):
        """representation good for logging"""
        return self.log_format("Suspect ${id}: from=${from_address} to=${to_address} size=${size} spam=${spam} blocked=${blocked} virus=${virus} modified=${modified} decision=${decision} tags=${tags}")

    def has_message_rep(self) -> bool:
        """returns true if python email api representation of this suspect exists already"""
        return self._msgrep is not None

    def build_headeronly_message_rep(self) -> PatchedMessage:
        """Build a python email representation from headers only"""
        headersource = self.get_headers()
        msgrep = email.message_from_string(headersource, _class=PatchedMessage)
        # noinspection PyTypeChecker
        return msgrep

    def get_message_rep(self) -> PatchedMessage:
        """returns the python email api representation of this suspect"""
        # do we have a cached instance already?
        if self._msgrep is not None:
            return self._msgrep

        if self.source is not None:
            try:
                msgrep = email.message_from_bytes(self.source, _class=PatchedMessage)
            except TypeError:
                msgrep = email.message_from_string(self.source, _class=PatchedMessage)
                self.logger.debug(f'{self.id} get_message_rep: self.source was type string, expected bytes')

            self._msgrep = msgrep
        else:
            # IMPORTANT: It is possible to use email.message_from_file BUT this will automatically replace
            #            '\r\n' in the message (_payload) by '\n' and the endtoend_test.py will fail!
            tmpSource = self.get_original_source()
            msgrep = email.message_from_bytes(tmpSource, _class=PatchedMessage)
            self._msgrep = msgrep
        # noinspection PyTypeChecker
        return msgrep

    @deprecated
    def getMessageRep(self):
        """old name for get_message_rep"""
        return self.get_message_rep()

    def set_message_rep(self, msgrep: PatchedMessage, att_mgr_reset: bool = True) -> None:
        """replace the message content. this must be a standard python email representation
        Warning: setting the source via python email representation seems to break dkim signatures!

        The attachment manager is build based on the python mail representation. If no message
        attachments or content is modified there is no need to recreate the attachment manager.

        Args:
            msgrep (email): standard python email representation
            att_mgr_reset (bool): Reset the attachment manager
        """
        self.logger.debug(f'{self.id} setting new message rep')
        try:
            self.set_source(msgrep.as_bytes(), att_mgr_reset=att_mgr_reset)
        except AttributeError:
            self.set_source(force_bString(msgrep.as_string()), att_mgr_reset=att_mgr_reset)

        # order is important, set_source sets _msgrep to None
        self._msgrep = msgrep

    @deprecated
    def setMessageRep(self, msgrep):
        """old name for set_message_rep"""
        return self.set_message_rep(msgrep)

    def is_modified(self) -> bool:
        """returns true if the message source has been modified"""
        return self.source is not None

    def get_source(self, maxbytes:int=None, newline:tp.Optional[bytes]=None) -> bytes:
        """returns the current message source, possibly changed by plugins"""
        if self.source is not None:
            source = self.source[:maxbytes]
        else:
            source = self.get_original_source(maxbytes)
        if isinstance(newline, bytes):
            source = source.replace(b'\r', b'').replace(b'\n', newline)
        return source

    @deprecated
    def getSource(self, maxbytes=None):
        """old name for get_source"""
        return self.get_source(maxbytes)

    def set_source(self, source:tp.Union[bytes,str], encoding:str='utf-8', att_mgr_reset:bool=True) -> None:
        """ Store message source. This might be modified by plugins later on...

        Args:
            source (bytes,str): new message source
            encoding (str): encoding, default is utf-8
            att_mgr_reset (bool): Reset the attachment manager
        """
        self.source = force_bString(source, encoding=encoding)
        self._msgrep = None
        if att_mgr_reset:
            self._att_mgr = None
        self._header_cache = {}
        self._cache_from_type_headers = {}

    @deprecated
    def setSource(self, source):
        """old name for set_source"""
        return self.set_source(source)

    def get_original_source(self, maxbytes:int=None) -> bytes:
        """returns the original, unmodified message source as bytes"""
        readbytes = -1
        if maxbytes is not None:
            readbytes = maxbytes
        try:
            # check internal filename directly (otherwise file gets created from buffer automatically...)
            if self._tempfile:
                if self.tempfile == "/dev/null":
                    # don't try to read from /dev/null
                    return b""
                else:
                    with open(self.tempfile, 'rb') as fh:
                        source = fh.read(readbytes)
                        #lines = fh.read(readbytes).splitlines(False)
                        #source = b'\r\n'.join(lines)
            else:
                source = bytes(self.inbuffer)
                if readbytes > 0:
                    source = source[:readbytes]
        except Exception as e:
            self.logger.error(f'{self.id} Cannot retrieve original source from tempfile {self.tempfilename()} due to {e.__class__.__name__}: {str(e)}')
            raise e
        return source

    @deprecated
    def getOriginalSource(self, maxbytes=None):
        """old name for get_original_source"""
        return self.get_original_source(maxbytes)

    def get_as_attachment(self, filename:str=None) -> MIMEBase:
        """
        returns message as multipart attachment
        :param filename: filename as which to attach. defaults to suspectid.eml
        :return: mime message object
        """
        if filename is None:
            filename = f'{self.id}.eml'
        p = MIMEBase('message', 'rfc822')
        p.set_payload(self.get_original_source())
        try:
            _ = p.as_bytes()
        except UnicodeEncodeError:
            # set from Python message, this might modify (base64-encode)
            # subparts of the attached message
            p = MIMEMessage(self.get_message_rep())
            self.logger.debug(f"{self.id} -> Failed to attach as MIMEBase, use MIMEMessage")
        p.add_header('Content-Disposition', f"attachment; filename={filename}")
        return p

    def wrap(self, sender:str, recipient:str, subject:str, body:tp.Optional[str]=None, filename:tp.Optional[str]=None, config:tp.Optional[FuConfigParser]=None, hdr_autosub:tp.Optional[str]='auto-generated', hdr_arsupp:tp.Optional[str]='DR, RN, NRN, OOF, AutoReply') -> PatchedMIMEMultipart:
        """
        attach original source to a new multipart email
        https://www.geeksforgeeks.org/send-mail-attachment-gmail-account-using-python/
        :param sender: wrapper From header address
        :param recipient: wrapper To header address
        :param subject: wrapper Subject header
        :param body: additional wrapper body, leave empty to omit
        :param filename: filename as which to attach. defaults to suspectid.eml
        :param config: fuglu config object, needed for proper evaluation of outgoing helo which is used to create message id header
        :param hdr_autosub: add auto-submitted header
        :param hdr_arsupp: add x-auto-response-suppress header
        :return: mime multipart message object
        """
        msg = PatchedMIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg['Date'] = email.utils.formatdate(localtime=True)
        msg['Message-ID'] = email.utils.make_msgid(domain=get_outgoing_helo(config))
        if hdr_autosub:
            msg['Auto-Submitted'] = hdr_autosub
        if hdr_arsupp:
            msg['X-Auto-Response-Suppress'] = hdr_arsupp

        if body:
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
        p = self.get_as_attachment(filename)
        msg.attach(p)
        return msg

    _re_newlines = re.compile(rb'(\n\n|\r\n\r\n)')

    def get_headers(self) -> str:
        """
        Returns the message headers as string type
        :return: string of all headers
        """
        headers = self._re_newlines.split(self.get_source(maxbytes=1048576), 1)[0]
        return force_uString(headers)
    
    
    def get_header(self, headername:str, fallback:tp.Optional[str]=None, use_cache:bool=True) -> tp.Optional[str]:
        """
        Returns content of header. value is cached for fast repeated lookups of header.
        :param headername: name of header
        :param fallback: fallback value in case header is not present, defaults to None
        :param use_cache: set False to get current value. Will update cache with the latest value.
        :return: value of header or fallback value if header not present
        """
        headername = headername.lower()
        if use_cache:
            value = self._header_cache.get(headername)
            if value is not None:
                return value
        msg = self.get_message_rep() if self.has_message_rep() else self.build_headeronly_message_rep()
        value = msg.get(headername, fallback)
        if value:
            # overly eager header folding can lead to the entire value being
            # on a separate line which would be extracted as "\r\n value"
            value = force_uString(value).lstrip()
        self._header_cache[headername] = value
        return value
    

    def get_client_info(self, config:tp.Optional[FuConfigParser]=None) -> tp.Optional[tp.Tuple[str,str,str]]:
        """returns information about the client that submitted this message.
        (helo,ip,reversedns)

        In before-queue mode this info is extracted using the XFORWARD SMTP protocol extension.

        In after-queue mode this information is extracted from the message Received: headers and therefore probably not 100% reliable
        all information is returned as-is, this means for example, that non-fcrdns client will show 'unknown' as reverse dns value.

        if no config object is passed, we use the first parseable Received header. otherwise, we use the config to determine the correct boundary MTA (trustedhostsregex / boundarydistance)
        """
        if self.clientinfo is not None:
            return self.clientinfo

        if config is None:
            self.logger.debug(f"{self.id} Getting client info with no arguments")
            clientinfo = self.client_info_from_rcvd()

        else:
            trustedhostsregex = config.get('environment', 'trustedhostsregex', fallback='')
            boundarydistance = config.getint('environment', 'boundarydistance', fallback=0)
            skiponerror = config.getboolean('environment', 'skiponerror', fallback=False)
            trustedreceivedregex = config.get('environment', 'trustedreceivedregex', fallback='')
            skipsamedomain = config.getboolean('environment', 'skipsamedomain', fallback=False)

            self.logger.debug(f"{self.id} Getting client info with trustedhostsregex: {trustedhostsregex} and boundarydistance: {boundarydistance}")
            clientinfo = self.client_info_from_rcvd(ignoreregex=trustedhostsregex,
                                                    skip=boundarydistance,
                                                    skiponerror=skiponerror,
                                                    ignorelineregex=trustedreceivedregex,
                                                    skipsamedomain=skipsamedomain
                                                    )
        self.clientinfo = clientinfo
        return clientinfo

    def client_info_from_rcvd(self, ignoreregex:str=None, skip:int=0, skiponerror:bool=False, ignorelineregex:str=None, skipsamedomain:bool=False) -> tp.Optional[tp.Tuple[str,str,str]]:
        """returns information about the client that submitted this message.
        (helo,ip,reversedns)

        This information is extracted from the message Received: headers and therefore probably not 100% reliable
        all information is returned as-is, this means for example, that non-fcrdns client will show 'unknown' as reverse dns value.

        if ignoreregex is not None, all results which match this regex in either helo,ip or reversedns will be ignored
        if ignorelineregex is not None, all results which match this regex will be ignored
        if skipsamedomain is True, ignore received lines where from & by domain is in same domain

        By default, this method starts searching at the top Received Header. Set a higher skip value to start searching further down.

        both these arguments can be used to filter received headers from local systems in order to get the information from a boundary MTA

        returns None if the client info can not be found or if all applicable values are filtered by skip/ignoreregex
        """
        ignorere = None
        if ignoreregex is not None and ignoreregex != '':
            ignorere = re.compile(ignoreregex)

        ignorelinere = None
        if ignorelineregex is not None and ignorelineregex != '':
            ignorelinere = re.compile(ignorelineregex)

        unknown = None

        receivedheaders_raw = self.get_message_rep().get_all('Received')
        if receivedheaders_raw is None:
            return unknown
        else:
            # make sure receivedheaders is an array of strings, no Header objects
            receivedheaders = [self.decode_msg_header(h, logid=self.id) for h in receivedheaders_raw]
            self.logger.debug(f"{self.id} (client_info_from_rcvd) Got {len(receivedheaders)} received headers")

        for rcvdline in receivedheaders[skip:]:
            h_rev_ip = self._parse_rcvd_header(rcvdline)
            if h_rev_ip is None:
                self.logger.debug(
                    f"{self.id} (client_info_from_rcvd) Could not parse header line... -> rcv line was: {rcvdline} => {'skip' if skiponerror else 'break'}")
                if skiponerror:
                    continue
                else:
                    return unknown

            helo, revdns, ip, by = h_rev_ip
            self.logger.debug(f"{self.id} (client_info_from_rcvd) Parsed: helo={helo}, revdns={revdns}, ip={ip}, by={by}")

            # check if hostname or ip matches ignore re, try next header if it does
            if ignorere is not None:
                excludematch = ignorere.search(ip)
                if excludematch is not None:
                    self.logger.debug(f"{self.id} (client_info_from_rcvd) -> exclude (ip={ip})")
                    continue

                if revdns:
                    excludematch = ignorere.search(revdns)
                    if excludematch is not None:
                        self.logger.debug(f"{self.id} (client_info_from_rcvd) -> exclude (revdns={revdns})")
                        continue

                if helo:
                    excludematch = ignorere.search(helo)
                    if excludematch is not None:
                        self.logger.debug(f"{self.id} (client_info_from_rcvd) -> exclude (helo={helo})")
                        continue

            # check if line matches ignore re, try next header if it does
            if ignorelinere is not None:
                excludematch = ignorelinere.search(rcvdline)
                if excludematch is not None:
                    self.logger.debug(f"{self.id} (client_info_from_rcvd) -> exclude (line={rcvdline})")
                    continue

            if skipsamedomain:
                tldmagic = tld.TLDMagic()
                try:
                    fqdn = extractor.domain_from_uri(revdns)
                    fromdomain = tldmagic.get_domain(fqdn)
                except Exception:
                    fromdomain = revdns

                try:
                    fqdn = extractor.domain_from_uri(by)
                    bydomain = tldmagic.get_domain(fqdn)
                except Exception:
                    bydomain = by

                try:
                    fqdn = extractor.domain_from_uri(helo)
                    helodomain = tldmagic.get_domain(fqdn)
                except Exception:
                    helodomain = by

                if bydomain and ((fromdomain and (fromdomain == bydomain)) or (helodomain and (helodomain == bydomain))):
                    self.logger.debug(f"{self.id} (client_info_from_rcvd) -> exclude (from/helo-domain == by-domain == {bydomain})")
                    continue

            clientinfo = force_uString(helo), force_uString(ip), force_uString(revdns)
            self.logger.info(f"{self.id} (client_info_from_rcvd) => extracted: helo={helo}, ip={ip}, revdns={revdns}")
            return clientinfo
        # we should only land here if we only have received headers in
        # mynetworks
        self.logger.info(f"{self.id} (client_info_from_rcvd) => Could not extract clientinfo")
        return unknown
    
    _re_receivedpattern = re.compile(
        r"^from\s(?P<helo>\S{3,256})\s{1,8}\((?P<revdns>\S{3,256})?\s?\[(?:IPv6:)?(?P<ip>(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|(?:[0-9a-f:]{3,40}))\]\)", re.MULTILINE)
    _re_receivedbypattern = re.compile(r"\s{1,8}(by\s{1,8}(?P<by>\S{3,64}))")
    
    def _parse_rcvd_header(self, rcvdline:str) -> tp.Optional[tp.Tuple[str, str, str, str]]:
        """return tuple HELO,REVERSEDNS,IP from received Header line, or None, if extraction fails"""
        match = self._re_receivedpattern.search(rcvdline)
        if match is None:
            return None
        h_rev_ip = match.groups()
        helo, revdns, ip = h_rev_ip

        match = self._re_receivedbypattern.search(rcvdline)
        if match is None:
            by = ""
        else:
            by = match.groups()[0]
        return helo, revdns, ip, by

    def source_stripped_attachments(self, content:bytes=None, maxsize:int=None, with_mime_headers:bool=False) -> bytes:
        """
        strip all attachments from multipart mails except for plaintext and html text parts.
        if message is still too long, truncate.

        Args:
            content (string,bytes): message source
            maxsize (integer): maximum message size accepted
            with_mime_headers (boolean): add mime headers from attachments

        Returns:
            bytes: stripped and truncated message content
        """

        if content is None:
            content = self.get_source()
        
        try:
            msgrep = email.message_from_bytes(content, _class=PatchedMessage)
        except TypeError:
            msgrep = email.message_from_string(content, _class=PatchedMessage)
            self.logger.debug(f'{self.id} source_stripped_attachments: self.source was type string, expected bytes')

        if msgrep.is_multipart():
            new_msg = PatchedMIMEMultipart()
            for hdr, val in msgrep.items():
                # convert "val" to "str" since in Py3 it might be of type email.header.Header
                # strip newlines as the MailMessage parser does not like them
                new_msg.add_header(hdr, force_uString(val))
            for part in msgrep.walk():
                # only plaintext and html parts but no text attachments
                if part.get_content_maintype() == 'text' and part.get_filename() is None:
                    new_msg.attach(part)
                elif with_mime_headers:
                    new_part = MIMEBase(part.get_content_maintype(), part.get_content_subtype())
                    for mhdr, mval in part.items():
                        new_part.add_header(mhdr, force_uString(mval))
                        new_part.set_payload("")
                    new_msg.attach(new_part)
            new_src = new_msg.as_bytes()
        else:
            # text only mail - keep full content and truncate later
            new_src = force_bString(content)

        if maxsize and len(new_src) > maxsize:
            # truncate to maxsize
            new_src = new_src[:maxsize]

        return force_bString(new_src)

    def write_sa_temp_header(self, header:str, value:str, plugin:str='SAPlugin') -> None:
        """
        Write a temporary pseudo header. This is used by e.g. SAPlugin to pass extra information to external services
        :param header: pseudo header name
        :param value: pseudo header value
        :param plugin: name of destination plugin. defaults to SAPlugin
        :return: None
        """
        hdr = f'{header}: {value}'
        tag = self.get_tag(f'{plugin}.tempheader')
        if isinstance(tag, list):
            tag.append(hdr)
        elif tag is None:
            tag = [hdr, ]
        else:  # str/unicode
            tag = f'{tag}\r\n{hdr}'
        self.set_tag(f'{plugin}.tempheader', tag)

    def get_sa_temp_headers(self, plugin:str='SAPlugin') -> bytes:
        """
        returns temporary pseude headers as a bytes string.
        :param plugin: name of destination plugin. defaults to SAPlugin
        :return: bytes: temp headers
        """
        headers = b''
        tempheader = self.get_tag(f'{plugin}.tempheader')
        if tempheader is not None:
            if isinstance(tempheader, list):
                tempheader = "\r\n".join(tempheader)
            tempheader = tempheader.strip()
            if tempheader != '':
                headers = force_bString(tempheader + '\r\n')
        return headers


def strip_address(address:str) -> str:
    """
    Strip the leading & trailing <> from an address.  Handy for
    getting FROM: addresses.
    """
    start = address.find('<') + 1
    if start < 1:
        start = address.find(':') + 1
    if start < 1:
        return address
    end = address.find('>')
    if end < 0:
        end = len(address)
    retaddr = address[start:end]
    retaddr = retaddr.strip()
    return retaddr


def extract_domain(address:str, lowercase:bool=True) -> tp.Optional[str]:
    if address is None or address == '':
        return None
    else:
        try:
            user, domain = address.rsplit('@', 1)
            if lowercase:
                domain = domain.lower()
            return domain
        except Exception:
            raise ValueError(f"invalid email address: '{address}'")


class BasicPlugin(DefConfigMixin):

    """Base class for all plugins"""

    def __init__(self, config, section=None):
        super().__init__(config)
        if section is None:
            self.section = self.__class__.__name__
        else:
            self.section = section

        self.config = config
        self.requiredvars = {}

    def _logger(self):
        """returns the logger for this plugin"""
        loggername = f"fuglu.plugin.{self.__class__.__name__}"
        return logging.getLogger(loggername)

    def lint(self):
        return self.check_config()

    @deprecated
    def checkConfig(self):
        """old name for check_config"""
        return self.check_config()

    def check_config(self):
        """Print missing / non-default configuration settings"""
        all_ok = True

        fc = FunkyConsole()
        # old config style
        if isinstance(self.requiredvars, (tuple, list)):
            for configvar in self.requiredvars:
                if isinstance(self.requiredvars, tuple):
                    (section, config) = configvar
                else:
                    config = configvar
                    section = self.section
                try:
                    self.config.get(section, config)
                except configparser.NoOptionError:
                    print(fc.strcolor(f"Missing configuration value without default [{section}] :: {config}", "red"))
                    all_ok = False
                except configparser.NoSectionError:
                    print(fc.strcolor(f"Missing configuration section containing variables without default "
                                      f"value [{section}] :: {config}", "red"))
                    all_ok = False

        # new config style
        if isinstance(self.requiredvars, dict):
            for config, infodic in self.requiredvars.items():
                section = infodic.get("section", self.section)

                try:
                    var = self.config.get(section, config)
                    if 'validator' in infodic:
                        if not infodic["validator"](var):
                            print(fc.strcolor(f"Validation failed for [{section}] :: {config}", "red"))
                            all_ok = False
                except configparser.NoSectionError:
                    print(fc.strcolor(f"Missing configuration section containing variables without default "
                                      f"value [{section}] :: {config}", "red"))
                    all_ok = False
                except configparser.NoOptionError:
                    print(fc.strcolor(f"Missing configuration value without default [{section}] :: {config}", "red"))
                    all_ok = False

        # missing sections -> this is only a warning since section is not required
        # as long as there are no required variables without default values...
        if all_ok:
            missingsections = set()
            for config, infodic in self.requiredvars.items():
                section = infodic.get("section", self.section)
                if section not in missingsections and not self.config.has_section(section):
                    missingsections.add(section)
            for section in missingsections:
                if section is None:
                    print(fc.strcolor(f"Pogramming error: Configuration section is manually None :: "
                                      f"Setup 'section' in requiredvars dict!", "red"))
                    all_ok = False
                else:
                    print(fc.strcolor(f"Missing configuration section [{section}] :: "
                                      f"All variables will use default values", "yellow"))
        return all_ok

    def __str__(self):
        classname = self.__class__.__name__
        if self.section == classname:
            return classname
        else:
            return f'{classname}({self.section})'


class ScannerPlugin(ReturnOverrideMixin, BasicPlugin):
    """Scanner Plugin Base Class"""

    def __init__(self, config, section: tp.Optional[str] = None):
        super().__init__(config, section=section)

    def run_examine(self, suspect: Suspect) -> tp.Optional[tp.Union[int, tp.Tuple[int, str]]]:
        """Run examine method of plugin + additional pre- / post-calculations"""
        out = self.examine(suspect=suspect)
        return self._check_apply_override(out, suspectid=suspect.id)

    def examine(self, suspect: Suspect) -> tp.Optional[tp.Union[int, tp.Tuple[int, str]]]:
        self._logger().warning('Unimplemented examine() method')
        return None

    def _problemcode(self, configoption='problemaction'):
        """
        safely calculates action code based on problemaction config value
        :return: action code
        """
        retcode = string_to_actioncode(self.config.get(self.section, configoption), self.config)
        if retcode is not None:
            return retcode
        else:
            # in case of invalid problem action
            return DEFER

    def _blockreport(self, suspect, blockinfo, enginename=None):
        """
        Tags suspect as blocked and saves block information in parseable tags
        :param suspect: the suspect object
        :param blockinfo: block info dict generated, usually filename -> blockreason
        :param enginename: block engine name. if None uses class name
        """
        if enginename is None:
            enginename = self.__class__.__name__

        if blockinfo is not None:
            self._logger().info(f'{suspect.id} Block reason found in message from {suspect.from_address} : {blockinfo}')
            suspect.tags['blocked'][enginename] = True
            suspect.tags[f'{enginename}.blocked'] = blockinfo
            suspect.debug(f'block reason found in message : {blockinfo}')
        else:
            suspect.tags['blocked'][enginename] = False

    def _spamreport(self, suspect, is_spam, is_highspam, spamreport, spamscore, enginename=None):
        """
        Tags suspect as spam and saves spam report in parseable tags
        :param suspect: the suspect object
        :param is_spam: bool: is the message spam?
        :param is_highspam: bool: des the message have a high spam score?
        :param spamreport: block info dict generated, usually filename -> blockreason
        :param spamscore: spam score
        :param enginename: block engine name. if None uses class name
        """
        if enginename is None:
            enginename = self.__class__.__name__

        suspect.tags['spam'][enginename] = is_spam
        suspect.tags['highspam'][enginename] = is_highspam
        suspect.tags[f'{enginename}.report'] = force_uString(spamreport, errors="replace")
        suspect.tags[f'{enginename}.score'] = spamscore


class AVScannerPlugin(ScannerPlugin):
    """AV Scanner Plugin Base Class - Scanner Plugins that communicate with external AV scanners"""
    enginename = 'generic-av'

    eicar = """Return-Path: sender@unittests.fuglu.org
Date: Mon, 08 Sep 2008 17:33:54 +0200
To: recipient@unittests.fuglu.org
From: sender@unittests.fuglu.org
Subject: test eicar attachment
X-Mailer: swaks v20061116.0 jetmore.org/john/code/#swaks
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="----=_MIME_BOUNDARY_000_12140"

------=_MIME_BOUNDARY_000_12140
Content-Type: text/plain

Eicar test
------=_MIME_BOUNDARY_000_12140
Content-Type: application/octet-stream
Content-Transfer-Encoding: BASE64
Content-Disposition: attachment

UEsDBAoAAAAAAGQ7WyUjS4psRgAAAEYAAAAJAAAAZWljYXIuY29tWDVPIVAlQEFQWzRcUFpYNTQo
UF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCoNClBLAQIU
AAoAAAAAAGQ7WyUjS4psRgAAAEYAAAAJAAAAAAAAAAEAIAD/gQAAAABlaWNhci5jb21QSwUGAAAA
AAEAAQA3AAAAbQAAAAAA

------=_MIME_BOUNDARY_000_12140--"""

    eicar_body = r"""Date: Mon, 08 Sep 2008 17:33:54 +0200
To: oli@unittests.fuglu.org
From: oli@unittests.fuglu.org
Subject: test eicar in body
X-Mailer: swaks v20061116.0 jetmore.org/john/code/#swaks
MIME-Version: 1.0

X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*

"""

    def _logger(self):
        """returns the logger for this plugin"""
        myclass = self.__class__.__name__
        loggername = f"fuglu.plugin.{myclass}({self._get_enginename()})"
        return logging.getLogger(loggername)

    def scan_stream(self, content, suspectid='(N/A)'):
        """
        Scans given byte buffer (file content). May raise an exception on errors.
        :param content: file content as string
        :param suspectid: suspect.id of currently processed suspect
        :return: None if no virus is found, else a dict filename -> virusname
        """
        self._logger().warning('Unimplemented scan_stream() method')

    def _check_too_big(self, suspect):
        """
        Checks if a message is too big for the current antivirus engine. Expects a maxsize configuration directive to be present
        :param suspect: the suspect object to be checked
        :return: boolean
        """
        if suspect.size > self.config.getint(self.section, 'maxsize'):
            self._logger().info(f'{suspect.id} Not scanning - message too big (message {suspect.size} bytes > config {self.config.getint(self.section, "maxsize")} bytes )')
            return True
        return False

    def _get_enginename(self):
        enginename = self.enginename
        if self.config.has_option(self.section, 'enginename'):
            configengine = self.config.get(self.section, 'enginename')
            if configengine:
                enginename = configengine
        return enginename

    def _virusreport(self, suspect, viruses):
        """
        tags suspect, saves virus reports in parseable tags, and returns action code and postfix reply message
        :param suspect: the suspect object
        :param viruses: the virus dict generated by e.g. scan_stream function
        :return: action code, message
        """
        actioncode = DUNNO
        message = None
        enginename = self._get_enginename()
        if viruses is None:
            self._logger().info(f'{suspect.id} No virus found in message from {suspect.from_address}')
            suspect.tags['virus'][enginename] = False
        else:
            self._logger().info(f'{suspect.id} Virus found in message from {suspect.from_address} : {viruses}')
            suspect.tags['virus'][enginename] = True
            suspect.tags[f'{enginename}.virus'] = viruses
            suspect.tags[f'{self.__class__.__name__}.virus'] = viruses  # deprecated, keep for compatibility
            suspect.debug(f'viruses found in message : {viruses}')
            virusaction = self.config.get(self.section, 'virusaction')
            actioncode = string_to_actioncode(virusaction, self.config)
            firstinfected, firstvirusname = list(viruses.items())[0]
            values = dict(infectedfile=firstinfected, virusname=firstvirusname)
            message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, values)
        return actioncode, message

    def lint_eicar(self, scan_function_name='scan_stream'):
        """
        passes an eicar (generic virus test) to the scanner engine
        :param scan_function_name: name of the scan function to be called
        :return: lint success as boolean
        """

        scan_function = getattr(self, scan_function_name)
        bodyeicar = self.config.getboolean(self.section, 'lint_body_eicar', fallback=False)

        eicar = self.eicar_body if bodyeicar else self.eicar
        try:
            result = scan_function(force_bString(eicar))
            if result is None:
                print("EICAR Test virus not found!")
                return False
            print(f"{str(self)} testing eicar in {'body' if bodyeicar else 'zip attachment'}: found virus {result}")
            return True
        except Exception as e:
            print(f'ERROR in {scan_function_name}: {e.__class__.__name__}: {str(e)}')
            #import traceback
            #print(traceback.format_exc())
            return False

    def _skip_on_previous_virus(self, suspect):
        """
        Configurable skip message scan based on previous virus findings.
        Args:
            suspect (fuglu.shared.Suspect):  the suspect 

        Returns:
            str: empty string means "don't skip", otherwise string contains reason to skip
        """
        skiplist = self.config.get(self.section, 'skip_on_previous_virus')
        if skiplist.lower() == "none":
            # don't skip
            return ""
        elif skiplist.lower() == "all":
            # skip if already marked as virus, no matter which scanner did mark
            isvirus = suspect.is_virus()
            if isvirus:
                return "Message is virus and skiplist is 'all' -> skip!"
            else:
                return ""
        else:
            # skip only if scanner from given list has marked message as virus
            scannerlist = [scanner.strip() for scanner in skiplist.split(',')]

            # dict with scanner as key for scanners that found a virus
            scanner_virustags = suspect.tags['virus']
            for scanner in scannerlist:
                if scanner_virustags.get(scanner, False):
                    return f"Scanner {scanner} has already tagged message as virus -> skip"
        return ""

    def lintinfo_skip(self):
        """
        If 'examine' method uses _skip_on_previous_virus to skip scan, this routine can be
        used to print lint info
        """
        skiplist = self.config.get(self.section, 'skip_on_previous_virus')
        if skiplist.lower() == "none":
            print(f"{self.enginename} will always scan, even if message is already marked as virus")
        elif skiplist.lower() == "all":
            print(f"{self.enginename} will skip scan if message is already marked as virus")
        else:
            # skip only if scanner from given list has marked message as virus
            scannerlist = [scanner.strip() for scanner in skiplist.split(',')]
            print(f"{self.enginename} will skip scan if message is already marked as virus by: {','.join(scannerlist)}")
        return True

    def examine(self, suspect):
        if self._check_too_big(suspect):
            return DUNNO

        content = suspect.get_source()
        
        retries = self.config.getint(self.section, 'retries')
        for i in range(0, retries):
            try:
                viruses = self.scan_stream(content, suspect.id)
                actioncode, message = self._virusreport(suspect, viruses)
                return actioncode, message
            except Exception as e:
                self._logger().warning(f"{suspect.id} Error encountered while contacting {self.enginename} server (try {i+1} of {retries}): {e.__class__.__name__}: {str(e)}")
                self._logger().debug(f"{suspect.id} {traceback.format_exc()}")
        self._logger().error(f"{suspect.id} {self.enginename} scan failed after {retries} retries")

        return self._problemcode()

    def __init_socket__(self):
        unixsocket = False
        path_or_port = self.config.get(self.section, 'port')
        timeout = self.config.getfloat(self.section, 'timeout')

        try:
            port = int(path_or_port)
        except ValueError:
            port = 0
            unixsocket = True

        if unixsocket:
            if not os.path.exists(path_or_port):
                raise Exception(f"unix socket {path_or_port} not found")
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            try:
                sock.connect(path_or_port)
            except socket.error as e:
                raise Exception(f'Could not reach {self.enginename} server using unix socket {path_or_port} due to {str(e)}')
        else:
            host = self.config.get(self.section, 'host', resolve_env=True)
            try:
                sock = socket.create_connection((host, port), timeout)
            except socket.error as e:
                raise Exception(f'Could not reach {self.enginename} server using network ({host}, {path_or_port}) due to {str(e)}')

        return sock

    def _close_socket(self, sock):
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except socket.error as e:
            self._logger().warning(f'{self.enginename} Error terminating connection: {str(e)}')
        finally:
            sock.close()


class PrependerPlugin(BasicPlugin):

    """Prepender Plugins - Plugins run before the scanners that can influence
    the list of scanners being run for a certain message"""

    def pluginlist(self, suspect, pluginlist):
        """return the modified pluginlist or None for no change"""
        return None

    def appenderlist(self, suspect, appenderlist):
        """return the modified appenderlist or None for no change"""
        return None


class AppenderPlugin(BasicPlugin):

    """Appender Plugins are run after the scan process (and after the re-injection if the message
    was accepted)"""

    def process(self, suspect, decision):
        self._logger().warning('Unimplemented process() method')


class FileList(object):

    """Map all lines from a textfile into a list. If the file is changed, the list is refreshed automatically
    Each line can be run through a callback filter which can change or remove the content.

    filename: The textfile which should be mapped to a list. This can be changed at runtime. If None, an empty list will be returned.
    strip: remove leading/trailing whitespace from each line. Note that the newline character is always stripped
    skip_empty: skip empty lines (if used in combination with strip: skip all lines with only whitespace)
    skip_comments: skip lines starting with #
    lowercase: lowercase each line
    additional_filters: function or list of functions which will be called for each line on reload.
        Each function accept a single argument and must return a (possibly modified) line or None to skip this line
    minimum_time_between_reloads: number of seconds to cache the list before it will be reloaded if the file changes
    """

    def __init__(self, filename=None, strip=True, skip_empty=True, skip_comments=True, lowercase=False, additional_filters=None, minimum_time_between_reloads=5):
        self._filename = filename
        self.minium_time_between_reloads = minimum_time_between_reloads
        self._lastreload = 0
        self.linefilters = []
        self.content = []
        self.logger = logging.getLogger(f'{__package__ or "fuglu"}.filelist')
        self.lock = threading.Lock()

        # we always strip newline
        self.linefilters.append(lambda x: x.rstrip('\r\n'))

        if strip:
            self.linefilters.append(lambda x: x.strip())

        if skip_empty:
            self.linefilters.append(lambda x: x if x != '' else None)

        if skip_comments:
            self.linefilters.append(lambda x: None if x.strip().startswith('#') else x)

        if lowercase:
            self.linefilters.append(lambda x: x.lower())

        if additional_filters is not None:
            if isinstance(additional_filters, list):
                self.linefilters.extend(additional_filters)
            else:
                self.linefilters.append(additional_filters)

        if filename is not None:
            self._reload_if_necessary()

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        if self._filename != value:
            self._filename = value
            if value is not None:
                self._reload_if_necessary()
            else:
                self.content = []
                self._lastreload = 0

    def _reload_if_necessary(self):
        """Calls _reload if the file has been changed since the last reload"""
        now = time.time()
        # check if reloadinterval has passed
        if now - self._lastreload < self.minium_time_between_reloads:
            return False
        if not self.file_changed():
            return False
        if not self.lock.acquire():
            return False
        try:
            self.content = self._parse_lines(self._reload())
        finally:
            self.lock.release()
        return True

    def _reload(self, retry=1):
        """Reload the file and build the list"""
        self.logger.info(f'Reloading file {self.filename}')
        statinfo = os.stat(self.filename)
        ctime = statinfo.st_ctime
        self._lastreload = ctime
        try:
            with open(self.filename, 'r') as fp:
                lines = fp.readlines()
        except OSError as e:
            if retry > 0:
                self.logger.debug(f'while reading {self.filename}: {e.__class__.__name__}: {str(e)}')
                time.sleep(0.1)
                lines = self._reload(retry=retry-1)
            else:
                self.logger.error(f'while reading {self.filename}: {e.__class__.__name__}: {str(e)}')
                raise
        except Exception as e:
            perm = oct(statinfo.st_mode)[-3:]
            self.logger.error(f'while reading {self.filename} with uid={statinfo.st_uid} and perm={perm}: {e.__class__.__name__}: {str(e)}')
            raise
        return lines

    def _apply_linefilters(self, line):
        for func in self.linefilters:
            line = func(line)
            if line is None:
                break
        return line

    def _parse_lines(self, lines):
        newcontent = []
        for line in lines:
            line = self._apply_linefilters(line)
            if line is not None:
                newcontent.append(line)
        return newcontent

    def file_changed(self):
        """Return True if the file has changed on disks since the last reload"""
        if not os.path.isfile(self.filename):
            return False
        statinfo = os.stat(self.filename)
        ctime = statinfo.st_ctime
        if ctime > self._lastreload:
            return True
        return False

    def get_list(self):
        """Returns the current list. If the file has been changed since the last call, it will rebuild the list automatically."""
        if self.filename is not None:
            self._reload_if_necessary()
        return self.content

    @staticmethod
    def inline_comments_filter(line):
        """
        Convenience function, strips comments from lines (e.g. everything after #)
        Pass to FileList() as additional_filter([FileList.inline_comments_filter])
        :param line: str: input line
        :return:  str or None
        """
        if '#' in line:
            idx = line.index('#')
            line = line[:idx].strip()
            if len(line) == 0:
                line = None
        return line


class SuspectFilterResult(object):
    def __init__(self, fieldname:str, value:str, arg:str, pattern:str):
        self.fieldname = fieldname
        self.value = value
        self.arg = arg
        self.pattern = pattern
    
    def __repr__(self):
        return f'<{self.__class__.__name__} fieldname={self.fieldname} value={self.value} arg={self.arg} pattern={self.pattern}>'


class SuspectFilterRule(object):
    op_map = {
        '<': operator.lt,
        '<=': operator.le,
        '==': operator.eq,
        '=': operator.eq,
        '!=': operator.ne,
        '<>': operator.ne,
        '>': operator.gt,
        '>=': operator.ge,
    }
    
    def _to_num(self, value:str) -> tp.Union[float,int]:
        try:
            num = int(value)
        except ValueError:
            num = float(value)
        return num
    
    def __init__(self, fieldname:str, args:str=None):
        # strip ending : (request AXB)
        if fieldname.endswith(':'):
            fieldname = fieldname[:-1]
        self.fieldname = fieldname
        
        if args is not None and args.strip() == '':
            args = None
        self.args = args
        
        self.pattern = None
        self.op = None
        self.num = None
        self.cmp = None
        
    def __repr__(self):
        return f'<{self.__class__.__name__} fieldname={self.fieldname} args={self.args} pattern={self.pattern} cmp={self.cmp}>'
    
    def set_rgx(self, pattern:str=None, reflags:int=0):
        try:
            self.pattern = re.compile(pattern, reflags)
        except Exception as e:
            raise Exception(f'Could not compile regex {pattern} due to {e.__class__.__name__}: {str(e)}')
    
    def set_cmp(self, cmp:str=None, num:str=None):
        self.op = self.op_map.get(cmp)
        if self.op is None:
            raise ValueError(f'failed to identify operator {cmp} use one of {",".join(self.op_map.keys())}')
        self.num = self._to_num(num)
        self.cmp = f'{cmp}{num}'
        
        

class SuspectFilter(FileList):

    """Allows filtering Suspect based on header/tag/body regexes"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('fuglu.suspectfilter')
    
    _re_numcomp = re.compile(r'^(?P<cmp>!?[=<>]{1,2})(?P<num>[0-9.]{1,16})$')

    def _load_simplestyle_line(self, line:str) -> SuspectFilterRule:
        sp = line.split(None, 2)
        if len(sp) < 2:
            raise Exception(f"Invalid line '{line}' in Rulefile {self.filename}. Ignoring.")

        args = None
        if len(sp) == 3:
            args = sp[2]
        rule = SuspectFilterRule(sp[0], args)

        m = self._re_numcomp.match(sp[1])
        if m and sp[1].startswith(tuple(rule.op_map.keys())):
            rule.set_cmp(m['cmp'], m['num'])
        else:
            reflags = re.IGNORECASE | re.DOTALL
            rule.set_rgx(sp[1], reflags)

        return rule
    
    def _get_regexflags(self, flags:str) -> int:
        reflags = 0
        for flag in flags:
            flag = flag.lower()
            if flag == 'i':
                reflags |= re.I
            elif flag == 'm':
                reflags |= re.M
            else:
                self.logger.debug(f'invalid flag {flag} in {flags}')
        return reflags

    _re_line = re.compile(r"""(?P<fieldname>@?[a-zA-Z0-9\-._:]{1,1024}):?\s+/(?P<regex>(?:\\.|[^/\\]){0,1024})/(?P<flags>[IiMm]{1,10})?((?:\s{0,1024}$)|(?:\s{1,1024}(?P<args>.{0,1024})))$""")

    def _load_perlstyle_line(self, line:str) -> tp.Optional[SuspectFilterRule]:
        m = self._re_line.match(line)
        if m is None:
            return None
        
        flags = m['flags']
        if flags is None:
            flags = ''
        reflags = self._get_regexflags(flags)
        
        rule = SuspectFilterRule(m['fieldname'], m['args'])
        rule.set_rgx(m['regex'], reflags)

        return rule
    
    def _load_jsonlines_line(self, line:str) -> SuspectFilterRule:
        data = json.loads(line)
        if not 'field' in data:
            raise ValueError('must specify field')
        rule = SuspectFilterRule(data['field'], data.get('args'))
        
        if 'regex' in data:
            reflags = self._get_regexflags(data['flags']) if 'flags' in data else 0
            rule.set_rgx(data['regex'], reflags)
        elif 'cmp' in data and 'num' in data:
            rule.set_cmp(data['cmp'], data['num'])
        else:
            raise ValueError('must specify either regex or cmp+num')
            
        return rule
    

    def _parse_lines(self, lines:tp.List[str]) -> tp.List[SuspectFilterRule]:
        newpatterns = []

        for line in lines:
            line = self._apply_linefilters(line)
            if line is None:
                continue
                
            if line.startswith('{'):
                # try to parse jsonline
                # {"field":"<fieldname>", "regex":"regex", "flags":"<flags>", "args":"args"}
                # {"field":"<fieldname>", "cmp":"<op>", "num":"<num>", "args":"args"}
                try:
                    tup = self._load_jsonlines_line(line)
                    if tup is not None:
                        newpatterns.append(tup)
                        continue
                except Exception as e:
                    self.logger.error(f'jsonlines style line failed {line} in file {self.filename} due to {e.__class__.__name__}: {str(e)}')
                    continue

            # try to parse advanced regex line
            # <fieldname> /regex/<flags> <arguments>
            try:
                tup = self._load_perlstyle_line(line)
                if tup is not None:
                    newpatterns.append(tup)
                    continue
            except Exception as e:
                self.logger.error(f'perl style line failed {line} in file {self.filename} due to {e.__class__.__name__}: {str(e)}')
                continue

            # try to parse simple style line
            # <fieldname> regex <arguments>
            # <fieldname> <cmp><val> <comment>
            try:
                tup = self._load_simplestyle_line(line)
                newpatterns.append(tup)
                continue
            except Exception as e:
                self.logger.error(f'perl style line failed {line} in file {self.filename} due to {e.__class__.__name__}: {str(e)}')
                continue

        return newpatterns

    _re_strip = re.compile(r'<[^>]*?>')

    def strip_text(self, content:str, remove_tags:tp.Optional[tp.List[str]]=None, replace_nbsp:bool=True, use_bfs:bool=True, fugluid: str = "<>"):
        """Strip HTML Tags from content, replace newline with space (like Spamassassin)

        Returns:
            (unicode/str) Unicode string (Py3 'str' is unicode string)
        """

        if remove_tags is None:
            remove_tags = ['script', 'style']

        # try to generate string if we receive a header.
        if isinstance(content, Header):
            try:
                content = content.encode()
            except Exception as e:
                self.logger.debug(f'{fugluid} failed to encode header {e.__class__.__name__}: {str(e)}')

        # make sure inputs are unicode, convert if needed
        content = force_uString(content)
        remove_tags = [force_uString(rtag) for rtag in remove_tags]

        content = content.replace("\n", " ")

        if HAVE_BEAUTIFULSOUP and use_bfs:
            try:
                # bs4 prefers filehandles to prevent confusion with file names
                fh = StringIO(content)
                if HAVE_LXML:
                    features = 'lxml'
                elif HAVE_LXML and content.startswith('<?x'):
                    features = 'lxml-xml'
                else:
                    features = 'html.parser'
                soup = BeautifulSoup.BeautifulSoup(fh, features)
            except Exception as e:
                self.logger.warning(f"{fugluid} Problem creating BeautifulSoup object: {e.__class__.__name__}: {str(e)}")
            else:
                for r in remove_tags:
                    [x.extract() for x in soup.find_all(r)]

                stripped = soup.get_text()
                if replace_nbsp:
                    stripped = stripped.replace('\xa0', ' ')
                return force_uString(stripped)

        # no BeautifulSoup available, let's try a modified version of pyzor's
        # html stripper
        stripper = HTMLStripper(strip_tags=remove_tags)

        try:
            # always try to replace nbsp as HTMLStripper would just remove them
            content = content.replace("&nbsp;", " ").replace("&#xa0;", " ").replace("&#160;", " ")
        except Exception:
            pass

        try:
            stripper.feed(content)
            return force_uString(stripper.get_stripped_data())
        except Exception:  # ignore parsing/encoding errors
            pass
        # use regex replace, make sure returned object is unicode string
        return force_uString(re.sub(self._re_strip, '', content))

    def get_decoded_textparts(self, suspect:Suspect, attachment:tp.Optional[bool]=None, inline:tp.Optional[bool]=None) -> tp.List[str]:
        """
        Get all text parts of suspect as a list. Text parts can be limited by the attachment, inline
        keywords which checks the Content-Disposition header:

        attachment: True/False/None
            None: Ignore
            True: attachment or header not present
            False: no attachment

        inline: True/False/None
            None: Ignore
            True: inline attachment
            False: no inline attachment or header present, so attached textparts are included

        Args:
            suspect (Suspect, PatchedMessage): Suspect object
            attachment (bool, NoneType): filter for attachments
            inline (bool, NoneType): filter for inline attachments

        The input should be a Suspect. Due to backward compatibility email.message.Message is still supported
        and passed to the deprecated routine which will however NOT handle the additional keyword parameters
        for filtering attachments and inline attachments.

        Returns:
            list: List containing decoded text parts

        """
        if not isinstance(suspect, Suspect):
            self.logger.warning(f'{suspect.id} "get_decoded_textparts" called with object other than Suspect which is deprecated and will be removed in near future...')
            if attachment is not None or inline is not None:
                raise DeprecationWarning
            suspect: PatchedMessage
            return self.get_decoded_textparts_deprecated(suspect)

        textparts = []
        for attObj in suspect.att_mgr.get_objectlist():
            # filter for attachment attribute
            if attachment is not None and attachment != attObj.is_attachment:
                # skip if we ask for attachments but the object is not an attachment
                # skip if we ask for non-attachments but the object is an attachment (or no Content-Disposition header)
                continue

            if inline is not None and inline != attObj.is_inline:
                # skip if we ask for inline but the object is not inline
                # skip if we ask for non-inline but the object is inline (or no Content-Disposition header)
                continue

            if attObj.content_fname_check(maintype="text", ismultipart=False) \
                    or attObj.content_fname_check(maintype='multipart', subtype='mixed'):
                decoded_buffer = attObj.decoded_buffer_text
                textparts.append(decoded_buffer)

        return textparts

    @deprecated
    def get_decoded_textparts_deprecated(self, messagerep:MIMEMessage) -> tp.List[str]:
        """Returns a list of all text contents"""
        textparts = []
        for part in messagerep.walk():
            payload = None
            if part.get_content_maintype() == 'text' and (not part.is_multipart()):
                payload = part.get_payload(None, True)

            # multipart/mixed are text by default as well
            if part.get_content_maintype() == 'multipart' and part.get_content_subtype() == 'mixed':
                payload = part.get_payload(None, True)

            # payload can be None even if it was returned from part.get_payload()
            if payload is not None:
                # Try to decode using the given char set
                charset = part.get_content_charset("utf-8")
                payload = force_uString(payload, encodingGuess=charset)
                textparts.append(payload)
        return textparts

    def get_field(self, suspect:Suspect, headername:str) -> tp.List[str]:
        """return a list of mail header values or special values. If the value can not be found, an empty list is returned.

        headers:
            just the headername or header:<headername> for standard message headers
            mime:headername for attached mime part headers

        envelope data:
            envelope_from (or from_address)
            envelope_to (or to_address)
            from_domain
            to_domain
            clientip
            clienthostname (fcrdns or 'unknown')
            clienthelo

        tags
            @tagname
            @tagname.fieldname (maps to suspect.tags['tagname']['fieldname'], unless suspect.tags['tagname.fieldname'] exists)

        body source:
            body:full -> (full source, encoded)
            body:stripped (or just 'body') : -> returns text/* bodyparts with tags and newlines stripped
            body:raw -> decoded raw message body parts
        """

        # convert inputs to unicode if needed
        headername = force_uString(headername)

        # builtins
        if headername == 'envelope_from' or headername == 'from_address':
            return force_uString([suspect.from_address, ])
        if headername == 'envelope_to' or headername == 'to_address':
            return force_uString(suspect.recipients)
        if headername == 'from_domain':
            return force_uString([suspect.from_domain, ])
        if headername == 'to_domain':
            return force_uString([suspect.to_domain, ])
        if headername == 'body:full':
            return force_uString([suspect.get_original_source()])

        if headername in ['clientip', 'clienthostname', 'clienthelo']:
            clinfo = suspect.get_client_info()
            if clinfo is None:
                return []
            if headername == 'clienthelo':
                return force_uString([clinfo[0], ])
            if headername == 'clientip':
                return force_uString([clinfo[1], ])
            if headername == 'clienthostname':
                return force_uString([clinfo[2], ])

        # if it starts with a @ we return a tag, not a header
        if headername[0:1] == '@':
            # treat status functions (e.g. is_spam) like tags.
            status = suspect.get_status()
            tagname = headername[1:]
            if tagname in status.keys():
                tagval = status[tagname]
            elif '.' in tagname and tagname not in suspect.tags.keys():
                tagparts = tagname.split('.')
                subtags = suspect.get_tag(tagparts[0], {})
                for tagpart in tagparts[1:-1]:
                    subtags = subtags.get(tagpart, {})
                tagval = subtags.get(tagparts[-1])
            else:
                tagval = suspect.get_tag(tagname)
            if tagval is None:
                return []
            if isinstance(tagval, list):
                return force_uString(tagval)
            return force_uString([tagval])

        messagerep = suspect.get_message_rep()

        # body rules on decoded text parts
        if headername == 'body:raw':
            return force_uString(self.get_decoded_textparts(suspect))

        if headername == 'body' or headername == 'body:stripped':
            return force_uString(list(map(self.strip_text, self.get_decoded_textparts(suspect))))

        if headername.startswith('mime:'):
            allvalues = []
            realheadername = headername[5:]
            for part in messagerep.walk():
                hdrslist = self._get_headers(realheadername, part)
                allvalues.extend(hdrslist)
            return force_uString(allvalues)

        # standard header
        # the header:<headername> alias is used in apply_template to distinguish from builtin variables
        if headername.startswith('header:'):
            headername = headername[7:]

        return force_uString(self._get_headers(headername, messagerep))

    def _get_headers(self, headername:str, payload:MIMEMessage) -> tp.List[str]:
        valuelist = []
        if '*' in headername:
            regex = re.escape(headername)
            regex = regex.replace(r'\*', '.*')
            patt = re.compile(regex, re.IGNORECASE)

            for h in list(payload.keys()):
                if re.match(patt, h) is not None:
                    valuelist.extend(payload.get_all(h, []))
        else:
            valuelist = payload.get_all(headername, [])

        return valuelist

    def _numcmp(self, rule:SuspectFilterRule, strval:str) -> bool:
        """
        compare two numbers using given operator function.
        :param rule: SuspectFilterRule object with op and num defined
        :param strval: string numeric comparison value
        :return: boolean: True if comparison matches, False if strval is not numeric or comparison is no match
        """
        if isinstance(rule.num, float):
            try:
                numval = float(strval)
            except (TypeError, ValueError):
                return False
        elif isinstance(rule.num, int):
            try:
                numval = int(strval)
            except (TypeError, ValueError):
                return False
        else:
            numval = None
        if numval is None:
            return False

        return rule.op(numval, rule.num)


    def _get_matches(self, suspect:Suspect, verbose:bool=False, firsthit=True) -> tp.List[SuspectFilterResult]:
        
        rules = self.get_list()
        results = []

        for rule in rules:
            #(fieldname, pattern, arg) = tup
            vals = self.get_field(suspect, rule.fieldname)
            if vals is None or len(vals) == 0:
                if verbose:
                    self.logger.debug(f'{suspect.id} No field {rule.fieldname} found, checking against {self.filename}')
                continue

            for val in vals:
                if val is None:
                    continue
                try:
                    strval = str(val)

                    if rule.pattern is not None and rule.pattern.search(strval):
                        self.logger.debug(f"{suspect.id} MATCH field={rule.fieldname} arg={rule.args} regex={rule.pattern.pattern} against value={val}")
                        suspect.debug(f"message matches rule in {self.filename}: field={rule.fieldname} arg={rule.args} regex={rule.pattern.pattern} content={val}")
                        results.append(SuspectFilterResult(rule.fieldname, strval, rule.args, rule.pattern.pattern))
                        if firsthit:
                            break
                    elif rule.op is not None and self._numcmp(rule, strval):
                        self.logger.debug(f"{suspect.id} MATCH field={rule.fieldname} arg={rule.args} numcmp={rule.cmp} against value={val}")
                        suspect.debug(f"message matches rule in {self.filename}: field={rule.fieldname} arg={rule.args} numcmp={rule.cmp} content={val}")
                        results.append(SuspectFilterResult(rule.fieldname, strval, rule.args, rule.cmp))
                        if firsthit:
                            break
                    elif rule.pattern is None and rule.op is None:
                        self.logger.debug(f"{suspect.id} SKIPPED MATCH field={rule.fieldname} arg={rule.args} regex=n/a against value={val}")
                    elif verbose:
                        self.logger.debug(f"{suspect.id} NO MATCH field={rule.fieldname} arg={rule.args} regex={rule.cmp or rule.pattern.pattern} against value={val}")
                except UnicodeEncodeError:
                    pass
        
        return results
        
        
    def matches(self, suspect: Suspect, extended: bool = False, verbose: bool = False) -> tp.Tuple[bool, tp.Union[SuspectFilterResult, str, None]]:
        """
        returns (True,arg) if any regex matches, (False,None) otherwise

        if extended=True, returns all available info about the match in a list of SuspectFilterResult:
        True, (fieldname, matchedvalue, arg, regex)
        """
        results = self._get_matches(suspect, verbose, firsthit=True)
        
        if results and extended:
            return True, results[0]
        elif results and not extended:
            return True, results[0].arg
        else:
            self.logger.debug(f'{suspect.id} No match found in file {self.filename}')
            suspect.debug(f'message does not match any rule in {self.filename}')
            return False, None


    def get_args(self, suspect: Suspect, extended: bool = False, verbose: bool = False) -> tp.Union[tp.List[SuspectFilterResult], tp.List[str]]:
        """
        returns all args of matched regexes in a list
        if extended=True:  returns a list of SuspectFilterResult with all available information:
        (fieldname, matchedvalue, arg, regex)
        """
        results = self._get_matches(suspect, verbose, firsthit=False)
        if extended:
            return results
        else:
            return [r.arg for r in results]
        

    def lint(self):
        """check file and print warnings to console. returns True if everything is ok, False otherwise"""
        if not os.path.isfile(self.filename):
            print(f"ERROR: SuspectFilter file not found: {self.filename}")
            return False
        with open(self.filename, 'r') as fp:
            lines = fp.readlines()
        lineno = 0
        for line in lines:
            lineno += 1
            line = line.strip()
            if line == "":
                continue
            if line.startswith('#'):
                continue
            try:
                tup = self._load_perlstyle_line(line)
                if tup is not None:
                    continue
                self._load_simplestyle_line(line)
            except Exception as e:
                print(f"ERROR: in SuspectFilter file '{self.filename}', lineno {lineno} , line '{line}' : {e.__class__.__name__}: {str(e)}")
                return False
        return True


class HTMLStripper(HTMLParser):

    def __init__(self, strip_tags=None):
        super().__init__()
        self.strip_tags = strip_tags or ['script', 'style']
        self.reset()
        self.collect = True
        self.stripped_data = []

    def handle_data(self, data):
        if data and self.collect:
            self.stripped_data.append(data)

    def handle_starttag(self, tag, attrs):
        HTMLParser.handle_starttag(self, tag, attrs)
        if tag.lower() in self.strip_tags:
            self.collect = False

    def handle_endtag(self, tag):
        HTMLParser.handle_endtag(self, tag)
        if tag.lower() in self.strip_tags:
            self.collect = True

    def get_stripped_data(self):
        return ''.join(self.stripped_data)


class Cache(object):
    """
    Simple local cache object.
    cached data will expire after a defined interval
    """

    def __init__(self, cachetime=30, cleanupinterval=300):
        self.cache = {}
        self.cachetime = cachetime  # default caching time
        self.cleanupinterval = cleanupinterval
        self.lock = threading.Lock()
        self.logger = logging.getLogger(f"{__package__ or 'fuglu'}.settingscache")

        t = threading.Thread(target=self.clear_cache_thread)
        t.daemon = True
        t.start()

    def put_cache(self, key, obj, ttl=None):
        try:
            gotlock = self.lock.acquire(True)
            if gotlock:
                now = time.time()
                if ttl is not None:
                    exp = now + ttl
                else:
                    exp = now + self.cachetime
                self.cache[key] = (obj, now, exp)
        except Exception as e:
            self.logger.exception(e)
        finally:
            self.lock.release()

    def get_cache(self, key):
        ret = None
        try:
            gotlock = self.lock.acquire(True)
            if not gotlock:
                return None

            if key in self.cache:
                obj, instime, exptime = self.cache[key]
                now = time.time()
                if now-exptime > 0:
                    del self.cache[key]
                else:
                    ret = obj

        except Exception as e:
            self.logger.exception(e)
        finally:
            self.lock.release()
        return ret

    def clear_cache_thread(self):
        while True:
            time.sleep(self.cleanupinterval)
            now = time.time()
            cleancount = 0
            try:
                gotlock = self.lock.acquire(True)
                if not gotlock:
                    continue

                for key in set(self.cache.keys()):
                    obj, instime, exptime = self.cache[key]
                    if now-exptime > 0:
                        del self.cache[key]
                        cleancount += 1
            except Exception as e:
                self.logger.exception(e)
            finally:
                self.lock.release()
            self.logger.debug(f"Cleaned {cleancount} expired entries.")


class CacheSingleton(object):
    """
    Process singleton to store a default Cache instance
    Note it is important there is a separate Cache instance for each process
    since otherwise the Threading.Lock will screw up and block the execution.
    """

    instance = None
    procPID = None

    def __init__(self, *args, **kwargs):
        pid = os.getpid()
        logger = logging.getLogger("%s.%s" % (__package__, self.__class__.__name__))
        if pid == CacheSingleton.procPID and CacheSingleton.instance is not None:
            logger.debug("Return existing Cache Singleton for process with pid: %u" % pid)
        else:
            if CacheSingleton.instance is None:
                logger.info("Create CacheSingleton for process with pid: %u" % pid)
            elif CacheSingleton.procPID != pid:
                logger.warning("Replace CacheSingleton(created by process %u) for process with pid: %u" % (CacheSingleton.procPID, pid))

            CacheSingleton.instance = Cache(*args, **kwargs)
            CacheSingleton.procPID = pid

    def __getattr__(self, name):
        return getattr(CacheSingleton.instance, name)


def get_default_cache():
    """
    Function to get processor unique Cache Singleton
    """
    return CacheSingleton()


def hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
    """
    Create hash using iterator.
    Args:
        bytesiter (iterator): iterator for blocks of bytes, for example created by "file_as_blockiter"
        hasher (): a hasher, for example hashlib.md5
        ashexstr (bool): Creates hex hash if true

    Returns:

    """
    for block in bytesiter:
        hasher.update(block)
    return hasher.hexdigest() if ashexstr else hasher.digest()


def file_as_blockiter(afile, blocksize=65536):
    """
    Helper for hasher functions, to be able to iterate over a file
    in blocks of given size

    Args:
        afile (BytesIO): file buffer
        blocksize (int): block size in bytes

    Returns:
        iterator

    """
    with afile:
        block = afile.read(blocksize)
        while len(block) > 0:
            yield block
            block = afile.read(blocksize)


def create_filehash(fnamelst, hashtype, ashexstr=False):
    """
    Create list of hashes for all files in list
    Args:
        fnamelst (list): list containing filenames
        hashtype (string): type of hash (e.g. md5, sha1)
        ashexstr (bool): create hex string if true

    Raises:
        KeyError if hashtype is not implemented

    Returns:
        list[(str,hash)]: List of tuples with filename and hashes
    """
    available_hashers = {"md5": hashlib.md5,
                         "sha1": hashlib.sha1}

    return [(fname, hash_bytestr_iter(file_as_blockiter(open(fname, 'rb')),
                                      available_hashers[hashtype](), ashexstr=ashexstr))
            for fname in fnamelst]


def sess2suspect(sess, **kwargs) -> Suspect:
    from_address = sess.sender
    if from_address is None:
        from_address = kwargs.get('from_address')
    if from_address is not None:
        from_address = force_uString(from_address)

    recipients = sess.recipients
    if not sess.recipients:
        recipients = kwargs.get('recipients', [])
    recipients = [force_uString(r) for r in recipients]

    tempfilename = sess.tempfilename
    if tempfilename is None:
        tempfilename = kwargs.get('tempfilename', '/dev/null')
    
    # noinspection PyProtectedMember
    if sess._buffer is not None:
        # noinspection PyProtectedMember
        inbuffer = bytes(sess._buffer.getbuffer()),
    else:
        inbuffer = kwargs.get('inbuffer')
        
    # noinspection PyProtectedMember
    suspect = Suspect(from_address, recipients, tempfilename, att_cachelimit=sess._att_mgr_cachesize,
                      att_defaultlimit=sess._att_defaultlimit, att_maxlimit=sess._att_maxlimit,
                      queue_id=sess.queueid, id=id, inbuffer=inbuffer, milter_macros=sess.milter_macros)

    suspect.timestamp = sess.timestamp
    suspect.tags = sess.tags  # pass by reference - any tag change in suspect should be reflected in session

    for hdrname, hdrval in sess.addheaders.items():
        immediate = False if inbuffer else True
        suspect.add_header(key=hdrname, value=hdrval, immediate=immediate)

    if sess.heloname is not None and sess.addr is not None and sess.fcrdns is not None:
        suspect.clientinfo = force_uString(sess.heloname), force_uString(sess.addr), force_uString(sess.fcrdns)

    if hasattr(sess, 'mhandler'):
        suspect.tags['incomingport'] = sess.mhandler.port

    return suspect
