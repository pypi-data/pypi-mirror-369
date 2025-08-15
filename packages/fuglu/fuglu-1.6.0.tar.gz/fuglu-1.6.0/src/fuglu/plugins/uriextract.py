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

"""
A collection of plugins to
- extract URIs/email addresses from mail body and text attachments
- lookup URIs/email addresses on RBLs
These plugins require beautifulsoup and domainmagic
"""

from fuglu.shared import ScannerPlugin, DUNNO, DEFER, string_to_actioncode, apply_template, FileList, AppenderPlugin, \
    HAVE_BEAUTIFULSOUP, HAVE_LXML, Suspect, get_default_cache
from fuglu.stringencode import force_uString
from fuglu.extensions.sql import SQL_EXTENSION_ENABLED, get_session, RESTAPIError, RESTAPIConfig
from fuglu.extensions.filearchives import FITZ_AVAILABLE, PYPDF_AVAILABLE, Archivehandle, fitz, pypdf
from fuglu.funkyconsole import FunkyConsole
from .sa import UserPref, GLOBALSCOPE
import os
import html
import re
import random
import typing as tp
import io
import time
from urllib import parse as urlparse

try:
    from domainmagic.extractor import URIExtractor, fqdn_from_uri, redirect_from_url, ip_convert_base10
    from domainmagic.rbl import RBLLookup
    from domainmagic.tld import TLDMagic
    from domainmagic.mailaddr import domain_from_mail
    from domainmagic.validators import is_url_tldcheck, is_ip, is_hostname, is_fqdn, is_ipv4, is_email
    DOMAINMAGIC_AVAILABLE = True
except ImportError:
    DOMAINMAGIC_AVAILABLE = False
    def is_email(value):
        return value and '@' in value

if HAVE_BEAUTIFULSOUP:
    import bs4 as BeautifulSoup
else:
    BeautifulSoup = None


HAVE_OPENCV = HAVE_NUMPY = HAVE_QUIRC = HAVE_WECHATQR = False
try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False
try:
    import numpy
    HAVE_NUMPY = True
except ImportError:
    pass
try:
    import cv2
    HAVE_OPENCV = True
    
    try:
        cv2.wechat_qrcode.WeChatQRCode()
        HAVE_WECHATQR = HAVE_NUMPY
    except Exception:
        HAVE_WECHATQR = False
    
    def _have_quirc() -> bool:
        if not HAVE_NUMPY:
            return False
        mystring = 'fuglu'
        encoder = cv2.QRCodeEncoder_create()
        cimg = encoder.encode(mystring)
        decoder = cv2.QRCodeDetector()
        result = decoder.detectAndDecode(cimg)
        del cimg
        # needs quirc dependency, no programmatic way to detect it
        return result[1] is not None and result[0] == mystring
    HAVE_QUIRC = _have_quirc()
except ImportError:
    pass
try:
    from pyzbar import pyzbar
    HAVE_PYZBAR = True
except ImportError:
    HAVE_PYZBAR = False
HAVE_QRCODE = HAVE_WECHATQR or HAVE_QUIRC or (((HAVE_OPENCV and HAVE_NUMPY) or HAVE_PIL) and HAVE_PYZBAR)

try:
    import vobject
    from contextlib import redirect_stdout
except ImportError:
    vobject = None
    redirect_stdout = None
# remove invisible characters
invisible = re.compile(r"[\0-\x1F\x7F-\x9F\xAD\u0378\u0379\u037F-\u0383\u038B\u038D\u03A2\u0528-\u0530\u0557\u0558\u0560\u0588\u058B-\u058E\u0590\u05C8-\u05CF\u05EB-\u05EF\u05F5-\u0605\u061C\u061D\u06DD\u070E\u070F\u074B\u074C\u07B2-\u07BF\u07FB-\u07FF\u082E\u082F\u083F\u085C\u085D\u085F-\u089F\u08A1\u08AD-\u08E3\u08FF\u0978\u0980\u0984\u098D\u098E\u0991\u0992\u09A9\u09B1\u09B3-\u09B5\u09BA\u09BB\u09C5\u09C6\u09C9\u09CA\u09CF-\u09D6\u09D8-\u09DB\u09DE\u09E4\u09E5\u09FC-\u0A00\u0A04\u0A0B-\u0A0E\u0A11\u0A12\u0A29\u0A31\u0A34\u0A37\u0A3A\u0A3B\u0A3D\u0A43-\u0A46\u0A49\u0A4A\u0A4E-\u0A50\u0A52-\u0A58\u0A5D\u0A5F-\u0A65\u0A76-\u0A80\u0A84\u0A8E\u0A92\u0AA9\u0AB1\u0AB4\u0ABA\u0ABB\u0AC6\u0ACA\u0ACE\u0ACF\u0AD1-\u0ADF\u0AE4\u0AE5\u0AF2-\u0B00\u0B04\u0B0D\u0B0E\u0B11\u0B12\u0B29\u0B31\u0B34\u0B3A\u0B3B\u0B45\u0B46\u0B49\u0B4A\u0B4E-\u0B55\u0B58-\u0B5B\u0B5E\u0B64\u0B65\u0B78-\u0B81\u0B84\u0B8B-\u0B8D\u0B91\u0B96-\u0B98\u0B9B\u0B9D\u0BA0-\u0BA2\u0BA5-\u0BA7\u0BAB-\u0BAD\u0BBA-\u0BBD\u0BC3-\u0BC5\u0BC9\u0BCE\u0BCF\u0BD1-\u0BD6\u0BD8-\u0BE5\u0BFB-\u0C00\u0C04\u0C0D\u0C11\u0C29\u0C34\u0C3A-\u0C3C\u0C45\u0C49\u0C4E-\u0C54\u0C57\u0C5A-\u0C5F\u0C64\u0C65\u0C70-\u0C77\u0C80\u0C81\u0C84\u0C8D\u0C91\u0CA9\u0CB4\u0CBA\u0CBB\u0CC5\u0CC9\u0CCE-\u0CD4\u0CD7-\u0CDD\u0CDF\u0CE4\u0CE5\u0CF0\u0CF3-\u0D01\u0D04\u0D0D\u0D11\u0D3B\u0D3C\u0D45\u0D49\u0D4F-\u0D56\u0D58-\u0D5F\u0D64\u0D65\u0D76-\u0D78\u0D80\u0D81\u0D84\u0D97-\u0D99\u0DB2\u0DBC\u0DBE\u0DBF\u0DC7-\u0DC9\u0DCB-\u0DCE\u0DD5\u0DD7\u0DE0-\u0DF1\u0DF5-\u0E00\u0E3B-\u0E3E\u0E5C-\u0E80\u0E83\u0E85\u0E86\u0E89\u0E8B\u0E8C\u0E8E-\u0E93\u0E98\u0EA0\u0EA4\u0EA6\u0EA8\u0EA9\u0EAC\u0EBA\u0EBE\u0EBF\u0EC5\u0EC7\u0ECE\u0ECF\u0EDA\u0EDB\u0EE0-\u0EFF\u0F48\u0F6D-\u0F70\u0F98\u0FBD\u0FCD\u0FDB-\u0FFF\u10C6\u10C8-\u10CC\u10CE\u10CF\u1249\u124E\u124F\u1257\u1259\u125E\u125F\u1289\u128E\u128F\u12B1\u12B6\u12B7\u12BF\u12C1\u12C6\u12C7\u12D7\u1311\u1316\u1317\u135B\u135C\u137D-\u137F\u139A-\u139F\u13F5-\u13FF\u169D-\u169F\u16F1-\u16FF\u170D\u1715-\u171F\u1737-\u173F\u1754-\u175F\u176D\u1771\u1774-\u177F\u17DE\u17DF\u17EA-\u17EF\u17FA-\u17FF\u180F\u181A-\u181F\u1878-\u187F\u18AB-\u18AF\u18F6-\u18FF\u191D-\u191F\u192C-\u192F\u193C-\u193F\u1941-\u1943\u196E\u196F\u1975-\u197F\u19AC-\u19AF\u19CA-\u19CF\u19DB-\u19DD\u1A1C\u1A1D\u1A5F\u1A7D\u1A7E\u1A8A-\u1A8F\u1A9A-\u1A9F\u1AAE-\u1AFF\u1B4C-\u1B4F\u1B7D-\u1B7F\u1BF4-\u1BFB\u1C38-\u1C3A\u1C4A-\u1C4C\u1C80-\u1CBF\u1CC8-\u1CCF\u1CF7-\u1CFF\u1DE7-\u1DFB\u1F16\u1F17\u1F1E\u1F1F\u1F46\u1F47\u1F4E\u1F4F\u1F58\u1F5A\u1F5C\u1F5E\u1F7E\u1F7F\u1FB5\u1FC5\u1FD4\u1FD5\u1FDC\u1FF0\u1FF1\u1FF5\u1FFF\u200B-\u200F\u202A-\u202E\u2060-\u206F\u2072\u2073\u208F\u209D-\u209F\u20BB-\u20CF\u20F1-\u20FF\u218A-\u218F\u23F4-\u23FF\u2427-\u243F\u244B-\u245F\u2700\u2B4D-\u2B4F\u2B5A-\u2BFF\u2C2F\u2C5F\u2CF4-\u2CF8\u2D26\u2D28-\u2D2C\u2D2E\u2D2F\u2D68-\u2D6E\u2D71-\u2D7E\u2D97-\u2D9F\u2DA7\u2DAF\u2DB7\u2DBF\u2DC7\u2DCF\u2DD7\u2DDF\u2E3C-\u2E7F\u2E9A\u2EF4-\u2EFF\u2FD6-\u2FEF\u2FFC-\u2FFF\u3040\u3097\u3098\u3100-\u3104\u312E-\u3130\u318F\u31BB-\u31BF\u31E4-\u31EF\u321F\u32FF\u4DB6-\u4DBF\u9FCD-\u9FFF\uA48D-\uA48F\uA4C7-\uA4CF\uA62C-\uA63F\uA698-\uA69E\uA6F8-\uA6FF\uA78F\uA794-\uA79F\uA7AB-\uA7F7\uA82C-\uA82F\uA83A-\uA83F\uA878-\uA87F\uA8C5-\uA8CD\uA8DA-\uA8DF\uA8FC-\uA8FF\uA954-\uA95E\uA97D-\uA97F\uA9CE\uA9DA-\uA9DD\uA9E0-\uA9FF\uAA37-\uAA3F\uAA4E\uAA4F\uAA5A\uAA5B\uAA7C-\uAA7F\uAAC3-\uAADA\uAAF7-\uAB00\uAB07\uAB08\uAB0F\uAB10\uAB17-\uAB1F\uAB27\uAB2F-\uABBF\uABEE\uABEF\uABFA-\uABFF\uD7A4-\uD7AF\uD7C7-\uD7CA\uD7FC-\uF8FF\uFA6E\uFA6F\uFADA-\uFAFF\uFB07-\uFB12\uFB18-\uFB1C\uFB37\uFB3D\uFB3F\uFB42\uFB45\uFBC2-\uFBD2\uFD40-\uFD4F\uFD90\uFD91\uFDC8-\uFDEF\uFDFE\uFDFF\uFE1A-\uFE1F\uFE27-\uFE2F\uFE53\uFE67\uFE6C-\uFE6F\uFE75\uFEFD-\uFF00\uFFBF-\uFFC1\uFFC8\uFFC9\uFFD0\uFFD1\uFFD8\uFFD9\uFFDD-\uFFDF\uFFE7\uFFEF-\uFFFB\uFFFE\uFFFF]")
wsdotwsre = re.compile(r'www\s{1,3}\.\s{1,3}(?P<dom>[a-z0-9-]{3,64})\s{1,3}\.\s{1,3}(?P<tld>[a-z]{1,10})', re.I)
doublehttpre = re.compile(r'^https?:/{1,6}(?P<prot>https?://)', re.I)
wsre = re.compile(r'\s')
slashre = re.compile('/')
multishlashre = re.compile(':/{3,6}')

EXCLUDE_FQDN = {'www.w3.org', 'schemas.microsoft.com'}
EXCLUDE_DOMAIN = {'avast.com', }


class URIExtract(ScannerPlugin):
    """Extract URIs from message bodies and store them as list in tag body.uris"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.extractor = None

        self.requiredvars = {
            'domainskiplist': {
                'default': '${confdir}/extract-skip-domains.txt',
                'description': 'Domain skip list',
            },
            'skip_unrouted_ips': {
                'default': 'True',
                'description': 'skip IPs from unrouted ranges e.g. 10.0.0.0/8'
            },
            'timeout': {
                'default': '0',
                'description': 'Max. time after which extraction will be stopped (approximate only, <0.0:infinite). set to 0 for unlimited.',
            },
            'maxsize': {
                'default': '10485000',
                'description': 'Maximum size of processed mail parts/attachments.',
            },
            'maxsize_analyse': {
                'default': '2000000',
                'description': 'Maximum size of string to analyze in bytes.',
            },
            'loguris': {
                'default': 'False',
                'description': 'print extracted uris in fuglu log',
            },
            'usehacks': {
                'default': '0',
                'description': 'Use extra hacks (int level) trying to parse uris (0: no hacks)',
            },
            'uricheckheaders': {
                'default': '',
                'description': 'List with headers to check for uris',
            },
            'header_as_env_recipient': {
                'default': 'X-Original-Recipient',
                'description': 'override envelope recipient with value from one of these headers (if set - first occurrence wins)'
            },
        }

    def _prepare(self, to_domain=None):
        skiplistfile = self.config.get(self.section, 'domainskiplist')
        if self.extractor is None:
            self.extractor = URIExtractor()
            if skiplistfile != '':
                self.extractor.load_skiplist(skiplistfile)
            if to_domain:
                if isinstance(self.extractor.skiplist, set):
                    self.extractor.skiplist.add(to_domain)
                elif isinstance(self.extractor.skiplist, list):
                    # old version of domain magic
                    self.extractor.skiplist.append(to_domain)

    def _check_skiplist(self, uris, extractfuncname='extracturis', use_hacks=0, skip_unrouted_ips=True):
        if not self.extractor.skiplist:
            return uris

        extractfunc = getattr(self.extractor, extractfuncname)
        newuris = []
        for uri in uris:
            exturis = extractfunc(uri, use_hacks, skip_unrouted_ips)
            newuris.extend(exturis)
            # some uris will be returned in truncated form. in such case we want both variants.
            for exturi in exturis:
                if exturi in uri:
                    newuris.append(uri)
                    break
        return newuris

    def _normalise_components(self, uri, lazyhostname: bool = False):
        # - remove whitespace characters (unless encoded)
        # - decode urlencoding
        # - convert idn to punycode
        # - fix invalid protocol prefixes (double prefix, too many slashes)
        # - drop invalid ipv6-lookalike URIs
        # - drop URIs with invalid netloc
        try:
            # remove whitespaces in protocol and domain name
            parts = slashre.split(uri)
            for i in range(0, min(len(parts), 3)):
                parts[i] = wsre.sub('', parts[i])
            uri = '/'.join(parts)

            uri = multishlashre.sub('://', uri)
            uri = doublehttpre.sub(r'\g<prot>', uri)
            addproto = False
            if not '://' in uri:
                addproto = True
                uri = 'http://' + uri
            parsed_uri = urlparse.urlparse(uri)
            #netloc = re.sub(r'\s', '', parsed_uri.netloc)
            netloc = urlparse.unquote(parsed_uri.netloc).encode('idna').decode()
            netloc = netloc.rstrip('%').strip('.').strip()
            # we want a syntactically valid hostname or ip address
            if not is_hostname(uri, lazyhostname=lazyhostname) and not is_hostname(netloc, lazyhostname=lazyhostname) and not is_ip(netloc.strip('[]')):
                return None

            netloc = ip_convert_base10(netloc)
            new_uri = parsed_uri._replace(netloc=netloc)
            path = new_uri.path.strip()
            new_uri = new_uri._replace(path=path)
            uri = new_uri.geturl()
            if addproto:
                uri = uri[7:]
            return uri
        except ValueError:
            # usually: Invalid IPv6 URL
            return None

    def _removeprefixes(self, val, prefixes):  # str.removeprefix was only added in py3.9
        if not hasattr(val, 'removeprefix'):
            for prefix in prefixes:
                if val.startswith(prefix):
                    val = val[len(prefix):]
        else:
            for prefix in prefixes:
                val = val.removeprefix(prefix)
        return val

    def _quickfilter(self, uris, lazyhostname: bool = False):
        # - ignore mail addresses (mailto:)
        # - ignore internal references, phone numbers, javascript and html tags (#...)
        # - ignore incomplete template replacements typically starting with square brackets
        uris = [self._normalise_components(self._removeprefixes(u.strip().lstrip(
            '*').strip('"').rstrip('-'), ['blob:', ': ', '3D"', '=3D"', '=']), lazyhostname=lazyhostname) for u in uris]
        uris = [u for u in uris if u and
                not u.lower().startswith((
                    "mailto:", "cid:", "tel:", "fax:", "javascript:", '#', "file:", "[",
                    "x-apple-data-detectors:", "applewebdata:", "viber:", ))
                ]
        uris = list(set(uris))
        return uris

    def _get_rcpt_domain(self, suspect):
        env_headers = self.config.getlist(self.section, 'header_as_env_recipient')
        if env_headers:
            msgrep = suspect.get_message_rep()
            for header in env_headers:
                value = msgrep.get(header)
                if value and '@' in value:
                    return value.rsplit('@')[-1]
        return suspect.to_domain

    def _set_timeout(self, suspect):
        default_timeout = self.config.getfloat(self.section, 'timeout', fallback=0.0)
        # set filtersettings tag uriextract_timeout or emailextract_timeout
        timeout = suspect.get_tag('filtersettings', {}).get(f'{self.__class__.__name__.lower()}_timeout', default_timeout)
        self.logger.debug(f'{suspect.id} setting timeout to {timeout} config default is {default_timeout}')
        if timeout and timeout > 0:
            # use section name as timeout tag
            suspect.stimeout_set_timer(self.section, timeout)

    def _get_usehacks(self):
        """
        Domain magic hacks - see bitmask in domainmagic/extractor.py

        EX_HACKS_PROCURL = 0x01  # Search & extract URLs in URL parameters
        EX_HACKS_IDNA = 0x02  # convert characters using "Internationalizing Domain Names in Applications"
        EX_HACKS_LAZYHOSTNAME = 0x04  # Use lazy hostname regex in is_hostname allowing "_"
        """
        try:
            usehacks = self.config.getint(self.section, 'usehacks')
        except Exception:
            usehacks = self.config.getboolean(self.section, 'usehacks')
            usehacks = 1 if usehacks else 0
        return usehacks

    def _run(self, suspect: Suspect):
        if not DOMAINMAGIC_AVAILABLE:
            self.logger.info(f'{suspect.id} Not scanning - Domainmagic not available')
            return DUNNO

        loguris = self.config.getboolean(self.section, 'loguris')
        maxsize = self.config.getint(self.section, 'maxsize')
        maxsize_analyse = self.config.getint(self.section, 'maxsize_analyse')
        usehacks = self._get_usehacks()
        skip_unrouted_ips = self.config.getboolean(self.section, 'skip_unrouted_ips')
        self._set_timeout(suspect)
        rcpt_domain = self._get_rcpt_domain(suspect)
        self._prepare(rcpt_domain)

        uris = []
        hrefs = []
        textparts = self.get_decoded_textparts(suspect, ignore_words_without='.', maxsize=maxsize,
                                               maxsize_analyse=maxsize_analyse, hrefs=hrefs,  use_hacks=usehacks)
        for content in textparts:
            # check for timeout
            if not suspect.stimeout_continue(self.section):
                self.logger.warning(f"{suspect.id} Timeout in content loop: {suspect.stimeout_string(self.section)}")
                # save whatever is available atm
                suspect.set_tag('body.uris', uris)
                return DUNNO

            try:
                for uri in content.split(' '):
                    parturis = self.extractor.extracturis(uri, use_hacks=usehacks, skip_unrouted_ips=skip_unrouted_ips)
                    uris.extend(parturis)

                    if not suspect.stimeout_continue(self.section):
                        self.logger.warning(f"{suspect.id} Timeout in uri content loop: {suspect.stimeout_string(self.section)}")
                        # save whatever is available atm
                        suspect.set_tag('body.uris', uris)
                        return DUNNO

            except Exception as e:
                self.logger.error(f'{suspect.id}  failed to extract URIs from msg part: {e.__class__.__name__}: {str(e)}')

        hrefs = self._check_skiplist(hrefs, use_hacks=usehacks, skip_unrouted_ips=skip_unrouted_ips)
        uris.extend(hrefs)
        
        subject = suspect.decode_msg_header(suspect.get_header('subject', ''), logid=suspect.id)
        if subject:
            parturis = self.extractor.extracturis(subject, use_hacks=usehacks, skip_unrouted_ips=skip_unrouted_ips)
            uris.extend(parturis)
            if loguris:
                self.logger.debug(f'{suspect.id} Found URIs in subject part: {parturis}')

        rediruris = self._get_redirected_uris(suspect, uris)
        if rediruris:
            uris.extend(rediruris)
        uris = self._quickfilter(list(set(uris)), lazyhostname=usehacks>2)  # remove duplicates and obvious bogons

        # get uris extracted from headers (stored in headers.uris tag)
        headeruris = self._get_header_uris(suspect=suspect)
        if headeruris and loguris:
            self.logger.info(f'{suspect.id} Extracted {len(headeruris)} uris from headers')
            self.logger.debug(f'{suspect.id} Extracted uris "{headeruris}" from headers')

        if loguris:
            self.logger.info(f'{suspect.id} Extracted URIs: {" ".join(uris)}')
        suspect.set_tag('body.uris', uris)
        return DUNNO

    def examine(self, suspect):
        return self._run(suspect)

    def get_decoded_textparts(self, suspect, ignore_words_without=(), maxsize=None, maxsize_analyse=None, hrefs=None, use_hacks=None):
        textparts = []
        size_string_analyse = 0
        att_mgr = suspect.att_mgr
        for attObj in att_mgr.get_objectlist():
            # check for timeout
            if not suspect.stimeout_continue(self.section):
                self.logger.warning(f"{suspect.id} Timeout in loop extracting text parts: {suspect.stimeout_string(self.section)}")
                # save whatever is available atm
                return textparts

            decoded_payload = None
            if attObj.content_fname_check(contenttype_start="text/") \
                    or attObj.content_fname_check(name_end=(".txt", ".html", ".htm")) \
                    or (attObj.defects and attObj.content_fname_check(ctype_start="text/")):
                if maxsize and attObj.filesize and attObj.filesize > maxsize:
                    # ignore parts larger than given limit
                    self.logger.info(f'{suspect.id} ignore part {attObj.filename} with size {attObj.filesize}')
                    continue

                decoded_payload = attObj.decoded_buffer_text
                if not decoded_payload:
                    self.logger.debug(f'{suspect.id} no payload in attachment {attObj.filename}')
                    continue
                    
                if attObj.content_fname_check(contenttype_contains="html") \
                        or attObj.content_fname_check(name_contains=".htm") \
                        or (attObj.defects and attObj.content_fname_check(ctype_contains="html")):
                    # remove invisible characters (including \r\n) but also check original source
                    decoded_payload_orig = decoded_payload
                    decoded_payload = invisible.sub("", decoded_payload_orig)

                    decoded_payload_replacedchars = ""
                    if use_hacks:
                        # same as above, but handle newlines differently to catch a link starting at a
                        # new line which would otherwise be concatenated and then not recognised by domainmagic
                        decoded_payload_replacedchars = invisible.sub("", decoded_payload_orig.replace('\r', ' ').replace('\n', ' '))

                    try:
                        decoded_payload = html.unescape(decoded_payload)
                        decoded_payload_replacedchars = html.unescape(decoded_payload_replacedchars)
                    except Exception:
                        self.logger.debug(f'{suspect.id} failed to unescape html entities')

                    if HAVE_BEAUTIFULSOUP:
                        saferedir = []
                        atags = []
                        imgtags = []
                        atagshtml = None
                        if isinstance(hrefs, list):
                            try:
                                if HAVE_LXML:
                                    features = 'lxml'
                                elif HAVE_LXML and decoded_payload.startswith('<?x'):
                                    features = 'lxml-xml'
                                else:
                                    features = 'html.parser'
                                bshtml = BeautifulSoup.BeautifulSoup(io.StringIO(decoded_payload), features)
                            except Exception as e:
                                self.logger.warning(f"{suspect.id} BeautifulSoup parsing error: {e.__class__.__name__}: {str(e)}")
                                bshtml = None
                            
                            if bshtml:
                                try:
                                    atagshtml = bshtml.find_all('a')
                                except Exception as e:
                                    self.logger.warning(f"{suspect.id} Extracting a-tags - BeautifulSoup error: {str(e)}")
                                    atagshtml = None
    
                                if atagshtml:
                                    atags = list(set([atag.get("href") for atag in atagshtml if atag.get("href")]))
                                    # some gmail-fu
                                    saferedir = list(set([atag.get("data-saferedirecturl") for atag in atagshtml if atag.get("data-saferedirecturl")]))
                                    if DOMAINMAGIC_AVAILABLE:
                                        for uri in saferedir[:]:
                                            newuri = redirect_from_url(uri)
                                            if newuri != uri and newuri not in saferedir:
                                                saferedir.append(newuri)
                                # add to hrefs list
                                try:
                                    imgtagshtml = bshtml.find_all('img')
                                except Exception as e:
                                    self.logger.warning(f"{suspect.id} Extracting img-tags - BeautifulSoup error: {str(e)}")
                                    imgtagshtml = None
    
                                if imgtagshtml:
                                    imgtags = list(set([imgtag.get("src") for imgtag in imgtagshtml if imgtag.get("src")]))
                                hrefs.extend(atags)
                                hrefs.extend(saferedir)
                                hrefs.extend(imgtags)
                            suspect.set_tag('uri.safelinks', saferedir)
                            suspect.set_tag('uri.imgsrc', imgtags)
                        
                            if bshtml:
                                # check for a html <base> entity which makes links relative...
    
                                # basically only the first basetag counts, but here we
                                # extract all in case multiple tags have been inserted to
                                # confuse the algorithm
                                try:
                                    basetags = bshtml.find_all('base')
                                except Exception as e:
                                    self.logger.warning(f"{suspect.id} Extracting base-tags - BeautifulSoup error: {str(e)}")
                                    basetags = None
        
                                if basetags and len(basetags) > 1:
                                    self.logger.info(f"{suspect.id} found {len(basetags)} <base> tags...")
                                if basetags:
                                    basetags = [basetag.get("href") for basetag in basetags if basetag.get("href")]
                                else:
                                    basetags = []

                                if basetags:
                                    # if there is a base tag with href, extend href's found in a-tags
                                    # -> just append result to payload
                                    self.logger.info(f"{suspect.id} base tag{'s' if len(basetags) > 1 else ''} found in html!")
        
                                    # check if atags is none and calculste if true
                                    # (hrefs for atags might alredy be calculated before)
                                    if atagshtml is None:
                                        try:
                                            atagshtml = bshtml.find_all('a')
                                        except Exception as e:
                                            self.logger.warning(f"{suspect.id} Extracting base-a-tags - BeautifulSoup error: {str(e)}")
                                            atagshtml = None
                                        if atagshtml:
                                            atags = list(set([atag.get("href") for atag in atagshtml if atag.get("href")]))
                                        else:
                                            atags = []
                                    fulllinks = []
        
                                    # combine basetag with atag
                                    for basetag in basetags:
                                        for atag in atags:
                                            fulllinks.append(basetag + atag)
                                    fulllinks.extend(saferedir)
                                    fulllinks = list(set(fulllinks))
        
                                    # append links found to payload for further analysis
                                    if fulllinks:
                                        self.logger.info(f"{suspect.id} <base>-tag: provided {len(fulllinks)} uris for analysis")
                                        decoded_payload += " ".join(fulllinks)

                    if decoded_payload_replacedchars:
                        decoded_payload = decoded_payload + " " + decoded_payload_replacedchars

            if attObj.content_fname_check(contenttype="multipart/alternative"):
                if maxsize and len(attObj.decoded_buffer_text) and len(attObj.decoded_buffer_text) > maxsize:
                    # ignore parts larger than given limit
                    self.logger.info(f"{suspect.id} ignore part with contenttype 'multipart/alternative' and size {len(attObj.decoded_buffer_text)}")
                    continue

                decoded_payload = attObj.decoded_buffer_text

            # Calendar items are special, line continuation starts
            # with a whitespace -> join correctly to detect links correctly
            if attObj.content_fname_check(contenttype="text/calendar"):
                joinedlines = None
                if vobject and redirect_stdout:
                    try:
                        parsed = vobject.readOne(decoded_payload)
                        f = io.StringIO()
                        with redirect_stdout(f):
                            parsed.prettyPrint()
                        joinedlines = f.getvalue().splitlines()
                        self.logger.info(f"{suspect.id} decoded calendar item using vobject to {len(joinedlines)} lines")
                    except Exception as e:
                        self.logger.warning(f"{suspect.id} problem decoding calendar item using vobject: {str(e)}")

                if joinedlines is None:
                    buffer = decoded_payload.replace('\r\n', '\n').split('\n')

                    joinedlines = []
                    for line in buffer:
                        if line.startswith(' '):
                            if joinedlines:
                                joinedlines[-1] = joinedlines[-1].rstrip() + line.lstrip()
                            else:
                                joinedlines.append(line)
                        else:
                            joinedlines.append(line)
                    self.logger.info(f"{suspect.id} decoded calendar item to {len(joinedlines)} lines")

                decoded_payload = " ".join(joinedlines)

            if decoded_payload:
                if use_hacks:
                    # convert 'www . example . com' to recognizeable url
                    decoded_payload = wsdotwsre.sub(r'www.\g<dom>.\g<tld>', decoded_payload)
                # Some spam mails create very long lines that will dramatically slow down the regex later on.
                for ignore_element in ignore_words_without:
                    decoded_payload = " ".join([part for part in decoded_payload.split(' ') if ignore_element in part])
                if maxsize_analyse and size_string_analyse + len(decoded_payload) > maxsize_analyse:
                    # ignore parts larger than given limit
                    self.logger.info(
                        f'{suspect.id}  ignore part {attObj.filename} due to processed size {len(decoded_payload)} and current size of analyse string {size_string_analyse}')
                else:
                    textparts.append(decoded_payload)
                    size_string_analyse += len(decoded_payload)

        return textparts

    def _get_redirected_uris(self, suspect, uris):
        rediruris = []
        if DOMAINMAGIC_AVAILABLE:
            for uri in uris:
                rediruri = redirect_from_url(uri)
                if rediruri != uri:
                    rediruris.append(rediruri)
            suspect.set_tag('body.uris.redirected', rediruris)
        return rediruris

    def _get_header_uris(self, suspect: Suspect) -> tp.List[str]:
        headerlist = self.config.get(self.section, 'uricheckheaders')
        if not headerlist or not headerlist.strip():
            return []
        headerlist = Suspect.getlist_space_comma_separated(headerlist)
        if not headerlist:
            return []

        ignore_words_without = ["."]
        msgrep = suspect.get_message_rep()

        stringlist2analyse = []
        # loop over given list of header names
        for hname in headerlist:
            # extract headers with given name (multiple possible)
            hobjs = msgrep.get_all(hname)
            if hobjs:
                for h in hobjs:
                    hstring = suspect.decode_msg_header(h, logid=suspect.id)

                    decoded_payload = ""
                    for ignore_element in ignore_words_without:
                        decoded_payload = " ".join([part for part in hstring.split(' ') if ignore_element in part])

                    if decoded_payload.strip():
                        stringlist2analyse.append(decoded_payload)

        string2analyse = " ".join(stringlist2analyse)
        if not stringlist2analyse:
            return []

        usehacks = self._get_usehacks()
        skip_unrouted_ips = self.config.getboolean(self.section, 'skip_unrouted_ips')
        headeruris = self.extractor.extracturis(string2analyse, use_hacks=usehacks, skip_unrouted_ips=skip_unrouted_ips)
        suspect.set_tag('headers.uris', headeruris)
        return headeruris

    def lint(self):
        allok = True
        if not DOMAINMAGIC_AVAILABLE:
            print("ERROR: domainmagic lib or one of its dependencies (dnspython/pygeoip) is not installed!")
            allok = False

        if allok:
            allok = self.check_config()

        return allok


class EmailExtract(URIExtract):
    """Extract email addresses from message bodies and defined headers and store them as list in tag body.emails or header.emails """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

        # update the requiredvars dictionary inherited from URIExtract by additional values for EmailExtract
        self.requiredvars.update({
            'headers': {
                'default': 'Return-Path,Reply-To,From,X-RocketYMMF,X-Original-Sender,Sender,X-Originating-Email,Envelope-From,Disposition-Notification-To',
                'description': 'comma separated list of headers to check for adresses to extract'
            },

            'skipheaders': {
                'default': 'X-Original-To,Delivered-To,X-Delivered-To,Apparently-To,X-Apparently-To',
                'description': 'comma separated list of headers with email adresses that should be skipped in body search'
            },

            'with_envelope_sender': {
                'default': 'True',
                'description': 'include envelope sender address as header address'
            }
        })
        
    def _domains_from_emails(self, suspect:Suspect, emailaddresses:tp.Set[str]) -> tp.Set[str]:
        resultaddresses = set()
        for mail in emailaddresses:
            if mail and "@" in mail:
                try:
                    dom = mail.rsplit("@", 1)[-1]
                    if dom:
                        resultaddresses.add(dom)
                except Exception as e:
                    self.logger.error(f"{suspect.id} Couldn't split {mail} in localpart & domain: {e.__class__.__name__}: {str(e)}")
        return resultaddresses
    

    def _run(self, suspect):
        if not DOMAINMAGIC_AVAILABLE:
            self.logger.info(f'{suspect.id} Not scanning - Domainmagic not available')
            return DUNNO

        maxsize = self.config.getint(self.section, 'maxsize')
        maxsize_analyse = self.config.getint(self.section, 'maxsize_analyse')
        usehacks = self._get_usehacks()
        self._set_timeout(suspect)
        rcpt_domain = self._get_rcpt_domain(suspect)
        self._prepare(rcpt_domain)

        body_emails = set()
        hrefs = []
        for content in self.get_decoded_textparts(suspect, ignore_words_without="@", maxsize=maxsize, maxsize_analyse=maxsize_analyse, hrefs=hrefs):
            # check for timeout
            if not suspect.stimeout_continue(self.section):
                self.logger.warning(f"{suspect.id} Timeout in content loop: {suspect.stimeout_string(self.section)}")
                # save whatever is available atm
                body_domains = list(self._domains_from_emails(suspect, body_emails))
                suspect.set_tag('body.emails', list(body_emails))
                suspect.set_tag('body.emails.domains', body_domains)
                suspect.set_tag('header.emails', [])
                suspect.set_tag('header.emails.domains', [])
                suspect.set_tag('emails', list(body_emails))
                suspect.set_tag('emails.domains', body_domains)
                return DUNNO

            try:
                for email in content.split(' '):
                    part_emails = set(self.extractor.extractemails(email, usehacks))
                    body_emails.update(part_emails)

                    if not suspect.stimeout_continue(self.section):
                        self.logger.warning(f"{suspect.id} Timeout in email content loop: {suspect.stimeout_string(self.section)}")
                        # save whatever is available atm
                        body_domains = list(self._domains_from_emails(suspect, body_emails))
                        suspect.set_tag('body.emails', list(body_emails))
                        suspect.set_tag('body.emails.domains', body_domains)
                        suspect.set_tag('header.emails', [])
                        suspect.set_tag('header.emails.domains', [])
                        suspect.set_tag('emails', list(body_emails))
                        suspect.set_tag('emails.domains', body_domains)
                        return DUNNO

            except Exception as e:
                self.logger.error(f'{suspect.id} failed to extract Emails from msg part: {e.__class__.__name__}: {str(e)}')

        # directly use mail addresses from html hrefs in atags
        hrefs_all = [h[len("mailto:"):] for h in hrefs if h.lower().startswith("mailto:")]
        hrefs = []
        for email in hrefs_all:
            part_emails = set(self.extractor.extractemails(email, usehacks))
            body_emails.update(part_emails)

            if not suspect.stimeout_continue(self.section):
                self.logger.warning(f"{suspect.id} Timeout in email href loop: {suspect.stimeout_string(self.section)}")
                break
        
        
        if suspect.stimeout_continue(self.section):
            hrefs = set(self._check_skiplist(hrefs, extractfuncname='extractemails', use_hacks=usehacks))
            body_emails.update(hrefs)
    
        msgrep = suspect.get_message_rep()
        
        hdrs = ''
        for hdr in self.config.getlist(self.section, 'headers'):
            hdrs += " " + " ".join(force_uString(msgrep.get_all(hdr, "")))
        hdr_emails = self.extractor.extractemails(hdrs)
        if self.config.getboolean(self.section, 'with_envelope_sender') and suspect.from_address:
            hdr_emails.append(suspect.from_address)
    
        ignoreemailtext = ""
        for hdr in self.config.getlist(self.section, 'skipheaders'):
            ignoreemailtext += " " + " ".join(force_uString(msgrep.get_all(hdr, "")))
        ignoreemails = [x.lower() for x in self.extractor.extractemails(ignoreemailtext)]
        ignoreemails.extend(suspect.recipients)

        body_emails_final = set()
        for e in body_emails:
            if e.lower() not in ignoreemails:
                body_emails_final.add(e)

        hdr_emails_final = set()
        for e in hdr_emails:
            if e.lower() not in ignoreemails:
                hdr_emails_final.add(e)

        all_emails = set()
        all_emails.update(body_emails_final)
        all_emails.update(hdr_emails_final)

        # collect domains
        body_emaildomains_final = self._domains_from_emails(suspect, body_emails_final)
        hdr_emaildomains_final = self._domains_from_emails(suspect, hdr_emails_final)
        
        all_emaildomains = set()
        all_emaildomains.update(body_emaildomains_final)
        all_emaildomains.update(hdr_emaildomains_final)

        # set tags
        suspect.set_tag('body.emails', list(body_emails_final))
        suspect.set_tag('body.emails.domains', list(body_emaildomains_final))

        suspect.set_tag('header.emails', list(hdr_emails_final))
        suspect.set_tag('header.emails.domains', list(hdr_emaildomains_final))

        suspect.set_tag('emails', list(all_emails))
        suspect.set_tag('emails.domains', list(all_emaildomains))

        if self.config.getboolean(self.section, 'loguris'):
            self.logger.info(f'{suspect.id} Extracted emails: {", ".join(all_emails)}')
            self.logger.info(f'{suspect.id} Extracted emaildomains: {", ".join(all_emaildomains)}')

        return DUNNO


class QRResult(object):
    def __init__(self, data):
        self.data = data
    
    def __str__(self):
        return self.data


class QRExtract(ScannerPlugin):
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'check_tags': {
                'default': '',
                'description': 'also get image data from tags',
            },
            'maxsize': {
                'default': str(512*1024), # 512kb
                'description': 'maximum size of image file to check (in bytes)'
            },
            'prefer_pil': {
                'default': 'True',
                'description': 'prefer pil+pyzbar over opencv if both are available'
            },
            'preferred_decoder': {
                'default': 'pyzbar',
                'description': 'set one of wechat, quirc, or pyzbar. only has an effect if opencv is used.'
            },
        }
        self.quirc_decoder = cv2.QRCodeDetector() if HAVE_QUIRC else None
        self.wechat_decoder = cv2.wechat_qrcode.WeChatQRCode() if HAVE_WECHATQR else None
    
    
    def _quirc_decode(self, cimg) -> tp.List[QRResult]:
        result = self.quirc_decoder.decode(cimg)
        if result[1] is not None:
            return [QRResult(result[0])]
        return []
    
    def _wechat_decode(self, cimg) -> tp.List[QRResult]:
        result = self.wechat_decoder.detectAndDecode(cimg)
        if result[1] is not None:
            return [QRResult(r) for r in result[0]]
        return []
    
    
    def _extract_qrcode(self, suspect:Suspect, imagedata:bytes, imagename:str) -> tp.List[str]:
        content = []
        try:
            if HAVE_NUMPY and HAVE_OPENCV and (not HAVE_PIL or not self.config.getboolean(self.section, 'prefer_pil')):
                nimg = numpy.frombuffer(imagedata, dtype=numpy.uint8)
                cimg = cv2.imdecode(nimg, cv2.IMREAD_COLOR)
                preferred_decoder = self.config.get(self.section, 'preferred_decoder')
                if preferred_decoder=='wechat' and HAVE_WECHATQR or (not HAVE_QUIRC and not HAVE_PYZBAR):
                    result = self._wechat_decode(cimg)
                elif preferred_decoder=='quirc' and HAVE_QUIRC or not HAVE_PYZBAR:
                    result = self._quirc_decode(cimg)
                else:
                    result = pyzbar.decode(cimg)
                del cimg
            elif HAVE_PIL:
                with Image.open(io.BytesIO(imagedata)) as cimg:
                    result = pyzbar.decode(cimg)
            else:
                self.logger.warning(f'{suspect.id} no useable qr code extration method found')
                result = [] # we should never get here
            for item in result:
                try:
                    value = getattr(item, 'data')
                    content.append(force_uString(value))
                except AttributeError:
                    pass
        except Exception as e:
            self.logger.warning(f'{suspect.id} failed to decode image {imagename} due to {e.__class__.__name__}: {str(e)}')
        if content:
            self.logger.debug(f'{suspect.id} image {imagename} is qr code with content {"".join(content)}')
            suspect.set_tag('qrcode.attached', True)
            suspect.write_sa_temp_header('X-QRCode', str(len(content)))
        return content
    
    
    _re_qrbill = re.compile(r'^(SPC|BCD)\s')
    def _codecheck(self, data:tp.Iterable[str], uris:tp.Set[str], emails:tp.Set[str], text:tp.Set[str], qrtypes:tp.Set[str]) -> tp.Tuple[tp.Set[str], tp.Set[str], tp.Set[str], tp.Set[str]]:
        for item in data:
            if self._re_qrbill.match(item):
                # not all qr bills are detected: https://github.com/mchehab/zbar/issues/216
                qrtypes.add('bill')
                text.add(item)
            elif item.startswith('WIFI:'):
                qrtypes.add('wifi')
            elif item.startswith('BEGIN:VCARD'):
                qrtypes.add('vcard')
                text.add(item)
            elif item.lower().startswith('mailto:'):
                item = item[7:]
                if is_email(item):
                    emails.add(item)
            elif item.lower().startswith('matmsg:'):
                fields = item[7:].split(';')
                for field in fields:
                    try:
                        k,v = field.split(':',1)
                        if k.lower()=='to' and is_email(v):
                            emails.add(v)
                    except ValueError:
                        if is_email(item):
                            emails.add(item)
            elif is_email(item):
                emails.add(item)
            elif item.lower().startswith('http'):
                uris.add(item)
            elif is_fqdn(item):
                uris.add(f'http://{item}/')
            else:
                text.add(item)
        if uris:
            qrtypes.add('uri')
        if emails:
            qrtypes.add('email')
        return uris, emails, text, qrtypes
    
    
    def examine(self, suspect: Suspect) -> tp.Optional[tp.Union[int, tp.Tuple[int, str]]]:
        if not HAVE_QRCODE:
            return DUNNO
        
        maxsize = self.config.getint(self.section, 'maxsize')
        uris = set()
        emails = set()
        text = set()
        qrtypes = set()
        for attobj in suspect.att_mgr.get_objectlist(level=0):
            if attobj.content_fname_check(contenttype_start="image/"):
                if attobj.filesize < maxsize:
                    data = self._extract_qrcode(suspect, attobj.buffer, attobj.filename)
                    uris, emails, text, qrtypes = self._codecheck(data, uris, emails, text, qrtypes)
        for tagname in self.config.getlist(self.section, 'check_tags'):
            images = suspect.get_tag(tagname, [])
            for image in images:
                if len(image) < maxsize:
                    data = self._extract_qrcode(suspect, image, 'buffer')
                    uris, emails, text, qrtypes = self._codecheck(data, uris, emails, text, qrtypes)
        
        if uris:
            suspect.set_tag('qrcode.uris', list(uris))
        if emails:
            suspect.set_tag('qrcode.emails', list(emails))
        if text:
            suspect.set_tag('qrcode.text', list(text))
        if qrtypes:
            suspect.set_tag('qrcode.types', list(qrtypes))
            suspect.write_sa_temp_header('X-QRCode-Types', ';'.join(qrtypes))
        
        return DUNNO
    
    def lint(self):
        if not self.check_config():
            return False
        if not HAVE_PIL and (not HAVE_OPENCV and not HAVE_NUMPY):
            print('ERROR: missing dependency PIL')
            return False
        if not HAVE_PIL and not HAVE_OPENCV:
            print('ERROR: missing dependency opencv (cv2)')
            return False
        if not HAVE_PIL and not HAVE_NUMPY:
            print('ERROR: missing dependency numpy')
            return False
        if not HAVE_PYZBAR and not HAVE_QUIRC and not HAVE_WECHATQR:
            print('ERROR: missing dependency pyzbar or opencv quirc/wechatqr')
            return False
        if not HAVE_QRCODE:
            print('ERROR: missing dependency (unknown)')
            return False
        if not DOMAINMAGIC_AVAILABLE:
            print('WARNING: missing dependency domainmagic')
        return True


class PDFExtract(URIExtract):
    """
    Extract URIs and Email addresses from attached PDF files. It scans text parts and annotations.
    """
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
    
    
    def _get_pdfdata_fitz(self, suspect: Suspect) -> tp.Tuple[tp.List[str], tp.List[str]]:
        pdflinks = []
        pdfemails = []
        for attobj in suspect.att_mgr.get_objectlist(level=0):
            if attobj.contenttype == 'application/pdf':
                doc = fitz.open(None, attobj.buffer, 'pdf')
                if doc.is_encrypted or doc.needs_pass:
                    self.logger.debug(f'{suspect.id} {attobj.filename} is encrypted')
                    continue
                for page in doc:
                    linkdicts = page.get_links()
                    links = [l['uri'] for l in linkdicts if 'uri' in l]
                    if links:
                        pdflinks.extend(links)
                        
                    content = page.get_text()
                    links = self.extractor.extracturis(content)
                    pdflinks.extend(links)
                    emails = self.extractor.extractemails(content)
                    pdfemails.extend(emails)
                doc.close()
        return pdflinks, pdfemails
    
    
    def _get_pdfdata_pypdf(self, suspect: Suspect) -> tp.Tuple[tp.List[str], tp.List[str]]:
        pdflinks = []
        pdfemails = []
        for attobj in suspect.att_mgr.get_objectlist(level=0):
            if attobj.content_fname_check(contenttype='application/pdf'):
                reader = pypdf.PdfReader(io.BytesIO(attobj.buffer))
                if reader.is_encrypted:
                    self.logger.debug(f'{suspect.id} {attobj.filename} is encrypted')
                    continue
                for page in reader.pages:
                    if "/Annots" in page:
                        for annot in page["/Annots"]:
                            obj = annot.get_object()
                            pdflinks.append(obj['/A']['/URI'])
                    content = page.extract_text()
                    links = self.extractor.extracturis(content)
                    pdflinks.extend(links)
                    emails = self.extractor.extractemails(content)
                    pdfemails.extend(emails)
                if hasattr(reader, 'close'): # api doc sez has close, reality sez no
                    reader.close()
        return pdflinks, pdfemails
    
    
    def examine(self, suspect: Suspect):
        if not FITZ_AVAILABLE and not PYPDF_AVAILABLE:
            return DUNNO
        self._prepare()
        
        try:
            if PYPDF_AVAILABLE:
                pdflinks, pdfemails = self._get_pdfdata_pypdf(suspect)
            elif FITZ_AVAILABLE:
                pdflinks, pdfemails = self._get_pdfdata_fitz(suspect)
            else:
                pdflinks = pdfemails = []
        except ValueError as e:
            self.logger.warning(f'{suspect.id} failed to extract PDF due to {str(e)}')
            pdfemails = []
            pdflinks = []
        
        uris = set()
        emails = set(pdfemails)
        for uri in pdflinks:
            if uri.startswith('mailto:'):
                uri = uri[7:]
                if is_email(uri):
                    emails.add(uri)
            elif is_email(uri):
                emails.add(uri)
            elif uri.startswith('http'):
                uris.add(uri)
            elif is_hostname(uri):
                uris.add(f'http://{uri}/')
        
        if uris:
            uris = self._quickfilter(list(uris))
            uris.extend(suspect.get_tag('pdf.hyperlinks', []))
            suspect.set_tag('pdf.hyperlinks', list(set(uris)))
        if emails:
            emails.update(set(suspect.get_tag('pdf.emails', [])))
            suspect.set_tag('pdf.emails', list(emails))
        
        return DUNNO

    def lint(self):
        fc = FunkyConsole()
        ok = self.check_config()
        if not FITZ_AVAILABLE and not PYPDF_AVAILABLE:
            print(fc.strcolor('ERROR:', 'red') + ' neither pypdf nor fitz is installed')
            ok = False
        elif PYPDF_AVAILABLE:
            print(fc.strcolor(f"pypdf found", "green") + f", version: {pypdf.__version__}")
        elif FITZ_AVAILABLE:
            print(fc.strcolor(f"fitz found", "green") + f", version: {fitz.VersionFitz}")
        
        PDFDATA = b"%PDF-1.6\n%\xc3\xa4\xc3\xbc\xc3\xb6\xc3\x9f\n2 0 obj\n<</Length 3 0 R/Filter/FlateDecode>>\nstream\nx\x9c3\xd03T(\xe7*T0P0\xd030\xb2P0\xb54\xd5327U\xb001\xd4\xb303T(J\xe5\n\xd7R\xc8\xe3\nT\x00\x00\xb7\x12\x08\xae\nendstream\nendobj\n\n3 0 obj\n50\nendobj\n\n5 0 obj\n<<\n>>\nendobj\n\n6 0 obj\n<</Font 5 0 R\n/ProcSet[/PDF/Text]\n>>\nendobj\n\n1 0 obj\n<</Type/Page/Parent 4 0 R/Resources 6 0 R/MediaBox[0 0 595.303937007874 841.889763779528]/Contents 2 0 R>>\nendobj\n\n4 0 obj\n<</Type/Pages\n/Resources 6 0 R\n/MediaBox[ 0 0 595.303937007874 841.889763779528 ]\n/Kids[ 1 0 R ]\n/Count 1>>\nendobj\n\n7 0 obj\n<</Type/Catalog/Pages 4 0 R\n/OpenAction[1 0 R /XYZ null null 0]\n/Lang(en-GB)\n>>\nendobj\n\n8 0 obj\n<</Creator<FEFF005700720069007400650072>\n/Producer<FEFF004C0069006200720065004F0066006600690063006500200037002E0034>\n/CreationDate(D:20231212093958+01'00')>>\nendobj\n\nxref\n0 9\n0000000000 65535 f \n0000000234 00000 n \n0000000019 00000 n \n0000000140 00000 n \n0000000357 00000 n \n0000000159 00000 n \n0000000181 00000 n \n0000000481 00000 n \n0000000577 00000 n \ntrailer\n<</Size 9/Root 7 0 R\n/Info 8 0 R\n/ID [ <3F5378F3EEEAB9ABDCDBF8F6271B2488>\n<3F5378F3EEEAB9ABDCDBF8F6271B2488> ]\n/DocChecksum /57D3C8E2B4440460C382B7F079971FEE\n>>\nstartxref\n751\n%%EOF\n"
        
        if ok:
            ok = 'pdf' in Archivehandle.archive_avail
            if ok:
                from io import BytesIO
                try:
                    ah = Archivehandle('pdf', BytesIO(PDFDATA), 'lint.pdf')
                    ok = ah.__class__.__name__ == 'Archive_pdf'
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                    ok = False
        if ok:
            from fuglu.mailattach import Archivehandle as archhan
            ok = 'pdf' in archhan.archive_avail
        return ok


class BinaryExtract(URIExtract):
    """
    Extract URIs and Email addresses from strings in attached binary files
    """
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
    
    
    _rgx_strings = re.compile(rb"[\x20-\x7E]{6,}")
    
    def _get_uris_from_binary(self, suspect: Suspect) -> tp.Tuple[tp.List[str], tp.List[str]]:
        binlinks = []
        binemails = []
        maxsize = self.config.getint(self.section, 'maxsize')
        for attobj in suspect.att_mgr.get_objectlist(level=0):
            if attobj.is_archive:
                self.logger.debug(f'{suspect.id} skipping archive attachment {attobj.filename}')
                continue
            if attobj.maintype_mime == 'text':
                self.logger.debug(f'{suspect.id} skipping text attachment {attobj.filename}')
                continue
            if attobj.content_fname_check(contenttype='application/pdf') or attobj.filename.endswith('.pdf'):
                self.logger.debug(f'{suspect.id} skipping pdf attachment {attobj.filename}')
                continue
            if attobj.ismultipart_mime:
                self.logger.debug(f'{suspect.id} skipping multipart attachment {attobj.filename}')
                continue
            if attobj.filesize > maxsize:
                self.logger.debug(f'{suspect.id} skipping oversize ({attobj.filesize}>{maxsize}) attachment {attobj.filename}')
                continue
            bytevalues = self._rgx_strings.findall(attobj.buffer)
            stringvalues = [b.decode("utf-8", errors="ignore") for b in bytevalues]
            stringlines = '\n'.join(stringvalues)
            links = self.extractor.extracturis(stringlines)
            binlinks.extend(links)
            emails = self.extractor.extractemails(stringlines)
            binemails.extend(emails)
        return binlinks, binemails
        
    
    def examine(self, suspect: Suspect):
        self._prepare()
        uris, emails = self._get_uris_from_binary(suspect)
        
        if uris:
            self.logger.debug(f'{suspect.id} extracted {len(uris)} URLs from binary attachments')
            uris = self._quickfilter(list(uris))
            suspect.set_tag('bin.hyperlinks', list(set(uris)))
        if emails:
            self.logger.debug(f'{suspect.id} extracted {len(uris)} URLs from binary attachments')
            suspect.set_tag('bin.emails', list(emails))
        
        return DUNNO
    
    def lint(self):
        ok = self.check_config()
        return ok



class DomainAction(ScannerPlugin):
    """Perform Action based on Domains in message body"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

        self.requiredvars = {
            'blacklistconfig': {
                'default': '',
                'description': 'Domainmagic RBL lookup config file. DEPRECATED, use blocklistconfig!',
            },
            'blocklistconfig': {
                'default': '${confdir}/rbl.conf',
                'description': 'Domainmagic RBL lookup config file',
            },
            'welcomelists': {
                'default': '',
                'description': 'which RBL identifiers are welcome list entries? hint: add those on top of your rbl.conf',
            },
            'checksubdomains': {
                'default': 'yes',
                'description': 'check subdomains as well (from top to bottom, eg. example.com, bla.example.com, blubb.bla.example.com',
            },
            'action': {
                'default': 'DUNNO',
                'description': 'action on hit (dunno, reject, delete, etc)',
            },
            'message': {
                'default': '5.7.1 block listed URL ${domain} by ${blacklist}',
                'description': 'message template for rejects/ok messages',
            },
            'maxlookups': {
                'default': '10',
                'description': 'maximum number of domains to check per message',
            },
            'randomise': {
                'default': 'False',
                'description': 'randomise domain list before performing lookups',
            },
            'timeout': {
                'default': '10',
                'description': 'number of seconds to spen on lookups. this value may be exceeded as lookups are only aborted on next lookup beyond timeout seconds. set to 0 for unlimited',
            },
            'check_all': {
                'default': 'False',
                'description': 'if set to True do not abort on first hit, instead continue until maxlookups reached',
            },
            'extra_tld_file': {
                'default': '',
                'description': 'path to file with extra TLDs (2TLD or inofficial TLDs)'
            },
            'testentry': {
                'default': '',
                'description': 'test record that should be included in at least one checked rbl (only used in lint)'
            },
            'exceptions_file': {
                'default': '',
                'description': 'path to file containing domains that should not be checked (one per line)'
            },
            'exclude_rgx': {
                'default': '',
                'description': 'regular expression to match on URIs that should not be checked'
            },
            'suspect_tags': {
                'default': 'body.uris',
                'description': 'evaluate URIs listed in given tags (list tags white space separated)'
            },
            'userpref_types': {
                'default': 'uridnsbl_skip_domain',
                'description': 'comma separated list of spamassassin userpref types containing skip domain entries'
            },
            'userpref_dbconnection': {
                'default': '',
                'description': "sqlalchemy db connect string, e.g. mysql:///localhost/spamassassin",
            },
            'userpref_tag': {
                'default': '',
                'description': 'get list of domains that should not be checked from filtersettings subtag of given name',
            },
            'userpref_usecache': {
                'default': "True",
                'description': 'Use Mem Cache. This is recommended. However, if enabled it will take up to userpref_cache_ttl seconds until listing changes are effective.',
            },
            'userpref_cache_ttl': {
                'default': "300",
                'description': 'how long to keep userpref data in memory cache',
            },
            'restapi_endpoint': {
                'default': "",
                'description': """REST API endpoint path to userpref overrides""",
            },
            'restapi_timeout': {
                'default': "0",
                'description': """REST API timeout. set to 0 to use default timeout from databaseconfig section""",
            },
            'skip_rbldomain': {
                'default': '',
                'description': """skip given RBL domain for given recipient. format: recipient:rbldomain, rcptdomain:rbldomain""",
            },
        }

        self.cache = get_default_cache()
        self.rbllookup = None
        self.tldmagic = None
        self.extratlds = None
        self.lasttlds = None
        self.exceptions = None

    def _init_tldmagic(self):
        init_tldmagic = False
        extratlds = []

        if self.extratlds is None:
            extratldfile = self.config.get(self.section, 'extra_tld_file')
            if extratldfile and os.path.exists(extratldfile):
                self.extratlds = FileList(extratldfile, lowercase=True)
                init_tldmagic = True

        if self.extratlds is not None:
            extratlds = self.extratlds.get_list()
            if self.lasttlds != extratlds:  # extra tld file changed
                self.lasttlds = extratlds
                init_tldmagic = True

        if self.tldmagic is None or init_tldmagic:
            self.tldmagic = TLDMagic()
            for tld in extratlds:  # add extra tlds to tldmagic
                self.tldmagic.add_tld(tld)

    def _get_sa_userpref(self, fugluid):
        key = '%s-sa-userpref' % self.__class__.__name__
        usecache = self.config.getboolean(self.section, 'userpref_usecache')
        skipuri = {}
        if usecache:
            skipuri = self.cache.get_cache(key) or {}
        if not skipuri:
            skipuri = self._get_sql_userpref(fugluid)
            rest_skipuri = self._get_rest_userpref(fugluid)
            for scope in rest_skipuri:
                try:
                    skipuri[scope].extend(rest_skipuri[scope])
                    skipuri[scope] = list(set(skipuri[scope]))
                except KeyError:
                    skipuri[scope] = rest_skipuri[scope]
            if skipuri:
                cachettl = self.config.getint(self.section, 'userpref_cache_ttl')
                self.cache.put_cache(key, skipuri, ttl=cachettl)
        return skipuri

    def _get_sql_userpref(self, fugluid):
        skipuri = {}
        dbconn = self.config.get(self.section, 'userpref_dbconnection')
        if dbconn and SQL_EXTENSION_ENABLED:
            userpref_types = self.config.getlist(self.section, 'userpref_types')
            if not dbconn or not userpref_types:
                self.logger.debug(f'{fugluid} userpref_dbconnection or userpref_types not set')
                return skipuri
            dbsession = get_session(dbconn)
            query = dbsession.query(UserPref)
            query = query.filter(UserPref.preference.in_(userpref_types))
            result = query.all()
            for r in result:
                if r.preference.lower() == "emailbl_acl_freemail" and not r.value.startswith('!'):
                    continue
                value = r.value.lstrip('!').lower()
                try:
                    skipuri[r.username.lower()].append(value)
                except KeyError:
                    skipuri[r.username.lower()] = [value]
            for username in skipuri.keys():
                skipuri[username] = list(set(skipuri[username]))
        return skipuri

    def _get_rest_userpref(self, fugluid):
        skipuri = {}
        restapi_endpoint = self.config.get(self.section, 'restapi_endpoint')
        if restapi_endpoint:
            restapi_timeout = self.config.getfloat(self.section, 'restapi_timeout', fallback=0)
            restapi = RESTAPIConfig(self.config, fugluid)
            content = restapi.get(restapi_endpoint, restapi_timeout)
            userpref_types = self.config.getlist(self.section, 'userpref_types')
            for scope in content:
                preferences = content[scope]
                scope = scope.lower()
                if scope.startswith('%'):  # restapi stores domain wide userprefs with scope %domain
                    scope = scope[1:]
                for pref in preferences:
                    pref = pref.lower()
                    if pref in userpref_types:
                        try:
                            skipuri[scope].extend(preferences[pref])
                        except KeyError:
                            skipuri[scope] = preferences[pref]
                    elif pref == 'emailbl_acl_freemail':
                        for item in preferences[pref].keys():
                            if item.startswith('!'):
                                item = item.lstrip('!').lower()
                                try:
                                    skipuri[scope].append(item)
                                except KeyError:
                                    skipuri[scope] = [item]
        return skipuri

    def _gen_userskiplist(self, suspect):
        skiplist = []

        if self.exceptions is None:
            exceptionsfile = self.config.get(self.section, 'exceptions_file')
            if exceptionsfile and os.path.exists(exceptionsfile):
                self.exceptions = FileList(exceptionsfile, lowercase=True)
        if self.exceptions is not None:
            skiplist.extend(self.exceptions.get_list())

        tagname = self.config.get(self.section, 'userpref_tag')
        if tagname:
            skiplist.extend([x.lower() for x in suspect.get_tag('filtersettings', {}).get(tagname, [])])

        recipient = suspect.to_address.lower()
        userprefs = self._get_sa_userpref(suspect.id)
        skiplist.extend(userprefs.get(GLOBALSCOPE, []))
        skiplist.extend(userprefs.get(recipient.rsplit('@', 1)[-1], []))
        skiplist.extend(userprefs.get(recipient, []))

        return list(set(skiplist))

    def _check_skiplist(self, skiplist, domain):
        domain = domain.lower()
        for item in skiplist:
            if domain == item or domain.endswith(f'.{item}'):
                return True
        return False

    def _init_rbllookup(self):
        if self.rbllookup is None:
            blocklistconfig = self.config.get(self.section, 'blocklistconfig')
            if not blocklistconfig:
                blocklistconfig = self.config.get(self.section, 'blacklistconfig')
                if blocklistconfig:
                    self.logger.warning('DEPRECATED: please use blocklistconfig instead of blacklistconfig')
            
            if not blocklistconfig:
                self.logger.error('blocklistconfig not set in config')
            elif not os.path.exists(blocklistconfig):
                self.logger.error(f'blocklistconfig file {blocklistconfig} does not exist')
            
            if blocklistconfig and os.path.exists(blocklistconfig):
                self.rbllookup = RBLLookup()
                self.rbllookup.from_config(blocklistconfig)

    def _get_uris(self, suspect):
        uris = []
        tags = self.config.get(self.section, 'suspect_tags').split()
        for tag in tags:
            uris.extend(suspect.get_tag(tag, []))
        return uris
    
    def _skip_rbldomains(self, suspect):
        skip_rbldomains = set()
        skiplist_raw = self.config.getlist(self.section, 'skip_rbldomain', lower=True)
        if skiplist_raw:
            skiplist = {k:v for k,v in [x.strip().split(':') for x in skiplist_raw]}
            for rcpt in skiplist:
                if rcpt == suspect.to_domain or rcpt == suspect.to_address:
                    skip_rbldomains.add(skiplist[rcpt])
            if skip_rbldomains:
                self.logger.debug(f'{suspect.id} skipping lookups in rbldomains {",".join(skip_rbldomains)}')
        return skip_rbldomains
        

    def examine(self, suspect):
        if not DOMAINMAGIC_AVAILABLE:
            self.logger.info(f'{suspect.id} Not scanning - Domainmagic not available')
            return DUNNO

        self._init_rbllookup()
        if self.rbllookup is None:
            self.logger.error(f'{suspect.id} Not scanning - blocklistconfig could not be loaded')
            return DUNNO

        try:
            timeout = self.config.getfloat(self.section, 'timeout')
        except ValueError:
            timeout = 0
        starttime = time.time()

        urls = self._get_uris(suspect)
        if not urls:
            self.logger.debug(f'{suspect.id} no urls to check')
            return DUNNO
        try:
            skiplist = self._gen_userskiplist(suspect)
        except RESTAPIError as e:
            self.logger.warning(f'{suspect.id} DEFER due to RESTAPIError: {str(e)}')
            return DEFER, 'Internal Server Error'

        domains = set()
        self._init_tldmagic()
        exclude_rgx = self.config.get(self.section, 'exclude_rgx')
        for url in urls:
            try:
                if url and is_url_tldcheck(url, exclude_fqdn=EXCLUDE_FQDN, exclude_domain=EXCLUDE_DOMAIN, exclude_rgx=exclude_rgx):
                    domains.add(fqdn_from_uri(url))
            except Exception as e:
                self.logger.error(f"{suspect.id} (examine:fqdn_from_uri): {e} for uri: {url}")
        domains = list(domains)

        if self.config.getboolean(self.section, 'randomise'):
            random.shuffle(domains)

        action = DUNNO
        message = None
        hits = {}
        counter = 0
        self.logger.debug(f'{suspect.id} checking {len(domains)} domains: {", ".join(domains)}')
        welcomelists = self.config.getlist(self.section, 'welcomelists')
        checked = set()
        for domain in domains:
            if self._check_skiplist(skiplist, domain):
                self.logger.debug(f'{suspect.id} skipping lookup of {domain} (skiplisted)')
                continue
            
            counter += 1
            if counter > self.config.getint(self.section, 'maxlookups'):
                self.logger.info(f'{suspect.id} maximum number of domains reached')
                break
            
            tldcount = self.tldmagic.get_tld_count(domain)
            parts = domain.split('.')
            
            if self.config.getboolean(self.section, 'checksubdomains'):
                subrange = range(tldcount+1, len(parts)+1)
            else:
                subrange = [tldcount+1]
            
            skip_rbldomains = self._skip_rbldomains(suspect)
            for subindex in subrange:
                subdomain = '.'.join(parts[-subindex:])
                if subdomain in checked:
                    continue
                
                try:
                    listings = self.rbllookup.listings(subdomain, skip_rbldomains=skip_rbldomains)
                    if listings:
                        self.logger.debug(f'{suspect.id} URL host {subdomain} in {domain} listed by {", ".join(list(listings.keys()))}')
                    else:
                        self.logger.debug(f'{suspect.id} URL host {subdomain} in {domain} not listed')
                    for identifier, humanreadable in iter(listings.items()):
                        if identifier in welcomelists:
                            self.logger.debug(f'{suspect.id} skipping lookup of {subdomain} in {domain} (welcomelisted by {identifier})')
                            break
                        hits[domain] = identifier
                        suspect.set_tag('uri.rbl.listed', True)
                        suspect.set_tag('uri.rbl.address', domain)
                        suspect.set_tag('uri.rbl.list', identifier)
                        suspect.set_tag('uri.rbl.info', humanreadable)
                        self.logger.info(f'{suspect.id} URL host {domain} flagged as {identifier} because {humanreadable}')
                        action = string_to_actioncode(self.config.get(self.section, 'action'), self.config)
                        message = apply_template(self.config.get(self.section, 'message'), suspect, dict(domain=domain, blacklist=identifier))
                        if not self.config.getboolean(self.section, 'check_all'):
                            return action, message
                    checked.add(subdomain)
                except Exception as e:
                    self.logger.error(f'{suspect.id} error looking up {subdomain} due to {e.__class__.__name__}: {str(e)}')
            
            endtime = time.time()
            if timeout and endtime-starttime > timeout:
                self.logger.info(f'{suspect.id} lookup timeout exceeded')
                break
        
        suspect.set_tag('uri.rbl.allresults', hits)
        return action, message

    def lint(self):
        allok = True
        if not DOMAINMAGIC_AVAILABLE:
            print("ERROR: domainmagic lib or one of its dependencies (dnspython/pygeoip) is not installed!")
            allok = False

        if allok:
            allok = self.check_config()

        if allok and not SQL_EXTENSION_ENABLED and self.config.get(self.section, 'userpref_dbconnection'):
            print('WARNING: sql extension not active but spamassassin userpref query enabled')
            allok = False

        if allok:
            blconf = self.config.get(self.section, 'blocklistconfig')
            if not blconf:
                blconf = self.config.get(self.section, 'blacklistconfig')
                if blconf:
                    print('DEPRECATED: please use blocklistconfig instead of blacklistconfig')
            if not blconf:
                allok = False
                print('ERROR: blocklistconfig not defined')
            elif not os.path.exists(blconf):
                allok = False
                print(f'ERROR: blocklistconfig {blconf} not found')
            else:
                self._init_rbllookup()
                if self.rbllookup is None:
                    allok = False
                    print('ERROR: rbllokup could still not be initialised')

        if allok and self.config.has_option(self.section, 'extra_tld_file'):
            extratldfile = self.config.get(self.section, 'extra_tld_file')
            if extratldfile and not os.path.exists(extratldfile):
                allok = False
                print(f'WARNING: extra_tld_file {extratldfile} not found')

        if allok and self.config.has_option(self.section, 'domainlist_file'):
            domainlist_file = self.config.get(self.section, 'domainlist_file')
            if domainlist_file and not os.path.exists(domainlist_file):
                allok = False
                print(f'WARNING: domainlist_file {domainlist_file} not found')

        if allok:
            exceptionsfile = self.config.get(self.section, 'exceptions_file')
            if exceptionsfile and not os.path.exists(exceptionsfile):
                allok = False
                print(f'WARNING: exceptions_file {exceptionsfile} not found')

        testentry = self.config.get(self.section, 'testentry')
        if allok and testentry:
            self._init_rbllookup()
            listings = self.rbllookup.listings(testentry)
            if not listings:
                allok = False
                print(f'WARNING: test entry {testentry} not found in any configured RBL zones')
            else:
                print(listings)

        tags = self.config.get(self.section, 'suspect_tags').split()
        print('INFO: checking URIs listed in tags: %s' % ' '.join(tags))
        
        welcomelists = self.config.getlist(self.section, 'welcomelists')
        print('INFO: considering the following RBLs as welcomelists: %s' % ' '.join(welcomelists))

        return allok


class EmailAction(DomainAction):
    """Perform Action based on email addresses in message body or headers"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.domainlist = None
        self.requiredvars.update({
            'blacklistconfig': {'default': ''},
            'blocklistconfig': {'default': '${confdir}/rblemail.conf'},
            'message': {'default': '5.7.1 block listed email address ${address} by ${blacklist}'},
            'exceptions_file': {'description': 'path to file containing email addresses that should not be checked (one per line)'},
            'userpref_types': {'default': 'emailbl_acl_freemail, uridnsbl_skip_domain'},
            'userpref_tag': {'description': 'get list of email addresses that should not be checked from filtersettings subtag of given name'},
            'domainlist_file': {
                'default': '',
                'description': 'path to file containing a list of domains. if specified, only query email addresses in these domains.'
            }
        })
        del self.requiredvars['extra_tld_file']
        del self.requiredvars['checksubdomains']

    def _in_domainlist(self, email_address):
        domainlist_file = self.config.get(self.section, 'domainlist_file').strip()
        if domainlist_file == '':
            return True

        if self.domainlist is None:
            self.domainlist = FileList(domainlist_file, lowercase=True)

        in_domainlist = False
        domain = domain_from_mail(email_address)
        if domain in self.domainlist.get_list():
            in_domainlist = True

        return in_domainlist

    def _check_skiplist(self, skiplist, emailaddr):
        emailaddr = emailaddr.lower()
        maildomain = emailaddr.rsplit('@', 1)[-1]
        for item in skiplist:
            comp_mail = '@' in item
            if comp_mail and item == emailaddr:
                return True
            elif not comp_mail and maildomain == item or maildomain.endswith(f'.{item}'):
                return True
        return False

    def examine(self, suspect):
        if not DOMAINMAGIC_AVAILABLE:
            self.logger.info(f'{suspect.id} Not scanning - Domainmagic not available')
            return DUNNO

        self._init_rbllookup()
        if self.rbllookup is None:
            self.logger.error(f'{suspect.id} Not scanning - blocklistconfig could not be loaded')
            return DUNNO

        try:
            skiplist = self._gen_userskiplist(suspect)
        except RESTAPIError as e:
            self.logger.warning(f'{suspect.id} DEFER due to RESTAPIError: {str(e)}')
            return DEFER, 'Internal Server Error'

        try:
            timeout = self.config.getfloat(self.section, 'timeout')
        except ValueError:
            timeout = 0
        starttime = time.time()

        action = DUNNO
        message = None
        hits = {}
        checked = {}
        addrs = []
        for addrtype in ['header.emails', 'body.emails']:
            addrs.extend(suspect.get_tag(addrtype, []))
            addrs = list(set(addrs))

        if self.config.getboolean(self.section, 'randomise'):
            random.shuffle(addrs)

        self.logger.debug(f'{suspect.id} checking {len(addrs)} addrs: {", ".join(addrs)}')
        for addr in addrs:
            if self._check_skiplist(skiplist, addr):
                self.logger.debug(f'{suspect.id} skipping lookup of {addr} (skiplisted)')
                continue

            if not self._in_domainlist(addr):
                self.logger.debug(f'{suspect.id} skipping lookup of {addr} (not in domain list)')
                continue

            if len(checked) > self.config.getint(self.section, 'maxlookups'):
                self.logger.info("%s maximum number of %s addresses reached" % (suspect.id, addrtype))
                break

            try:
                listings = checked[addr]
            except KeyError:
                try:
                    listings = self.rbllookup.listings(addr)
                    checked[addr] = listings
                except Exception as e:
                    self.logger.error(f'{suspect.id} error looking up {addr} due to {e.__class__.__name__}: {str(e)}')
                    listings = {}

            for identifier, humanreadable in iter(listings.items()):
                hits[addr] = identifier
                suspect.set_tag('email.rbl.listed', True)
                suspect.set_tag('email.rbl.type', addrtype)
                suspect.set_tag('email.rbl.address', addr)
                suspect.set_tag('email.rbl.list', identifier)
                suspect.set_tag('email.rbl.info', humanreadable)
                self.logger.info("%s : %s address %s flagged as %s because %s" % (suspect.id, addrtype, addr, identifier, humanreadable))
                action = string_to_actioncode(self.config.get(self.section, 'action'), self.config)
                message = apply_template(self.config.get(self.section, 'message'), suspect, dict(domain=addr, address=addr, blacklist=identifier))
                if not self.config.getboolean(self.section, 'check_all'):
                    return action, message

            endtime = time.time()
            if timeout and endtime-starttime > timeout:
                self.logger.info(f'{suspect.id} lookup timeout exceeded')
                break

        suspect.set_tag('uri.rbl.allresults', hits)
        return action, message


# --------- #
# Appenders #
# --------- #
class URIExtractAppender(URIExtract, AppenderPlugin):
    """Separate class to have a simple separate configuration section"""

    def process(self, suspect, decision):
        """If running as appender"""
        _ = self._run(suspect)


class EmailExtractAppender(EmailExtract, AppenderPlugin):
    """Separate class to have a simple separate configuration section"""

    def process(self, suspect, decision):
        """If running as appender"""
        _ = self._run(suspect)
