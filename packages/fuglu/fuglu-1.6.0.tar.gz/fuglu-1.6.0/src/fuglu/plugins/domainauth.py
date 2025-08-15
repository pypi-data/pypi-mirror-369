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
"""
Antiphish / Forging Plugins (DKIM / SPF / SRS etc)

requires: dkimpy (not pydkim!!)
requires: pyspf
requires: pydns (or alternatively dnspython if only dkim is used)
requires: pysrs
requires: pynacl (rare dependeny of dkimpy, needed for elliptic curve signatures)
requires: dmarc (>= 1.1.0)
requires: authres (for arc signing)
"""
import ipaddress
import logging
import os
import sys
import re
import time
import traceback
import typing as tp
import fnmatch
import socket
import email
import email.policy
import operator
from hashlib import md5
from email.header import Header
from unittest.mock import MagicMock
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from fuglu.shared import ScannerPlugin, apply_template, FileList, string_to_actioncode, get_default_cache, \
    extract_domain, Suspect, Cache, actioncode_to_string, deprecated, get_outgoing_helo, SuspectFilter, \
    FuConfigParser, DUNNO, ACCEPT
from fuglu.mshared import BMPMailFromMixin, BMPRCPTMixin, BMPEOBMixin, BasicMilterPlugin, EOM, retcode2milter
from fuglu.extensions.sql import get_session, SQL_EXTENSION_ENABLED, get_domain_setting, text
import fuglu.extensions.dnsquery as dnsquery
import fuglu.extensions.aiodnsquery as aiodnsquery
from fuglu.stringencode import force_bString, force_uString
from fuglu.logtools import PrependLoggerMsg
from fuglu.lib.patchedemail import PatchedMessage

DKIMPY_AVAILABLE = False
ARCSIGN_AVAILABLE = False
PYSPF_AVAILABLE = False
DMARC_AVAILABLE = False
SRS_AVAILABLE = False
PYNACL_AVAILABLE = False

try:
    import dkim
    from dkim import DKIM, ARC
    if dnsquery.DNSQUERY_EXTENSION_ENABLED:
        DKIMPY_AVAILABLE = True
        try:
            import authres
            ARCSIGN_AVAILABLE = True
        except ImportError:
            authres = MagicMock()
    try:
        import nacl
        PYNACL_AVAILABLE = True
    except ImportError:
        pass
except ImportError:
    dkim = MagicMock()
    DKIM = None
    ARC = MagicMock()

try:
    import spf
    HAVE_SPF = True
    if dnsquery.DNSQUERY_EXTENSION_ENABLED:
        PYSPF_AVAILABLE = True
except ImportError:
    class spf(object):
        query = MagicMock()
    HAVE_SPF = False

try:
    from domainmagic.tld import TLDMagic
    from domainmagic.mailaddr import domain_from_mail
    from domainmagic.validators import is_ipv6, is_email
    DOMAINMAGIC_AVAILABLE = True
except ImportError:
    DOMAINMAGIC_AVAILABLE = False
    TLDMagic = None

    def domain_from_mail(address, **kwargs):
        if address and "@" in address:
            return address.rsplit("@", 1)[-1]
        return address

    def is_ipv6(ipaddr):
        return ipaddr and ':' in ipaddr
    
    def is_email(value):
        return value and '@' in value

try:
    import dmarc
    DMARC_AVAILABLE = True
    if dnsquery.DNSQUERY_EXTENSION_ENABLED and DOMAINMAGIC_AVAILABLE:
        DMARC_AVAILABLE = True
except ImportError:
    dmarc = MagicMock()

try:
    import SRS
    SRS_AVAILABLE = True
except ImportError:
    SRS = None

SAHEADER_SPF = 'X-SPFCheck'
SAHEADER_ARC = 'X-ARCVerify'
SAHEADER_DKIM = 'X-DKIMVerify'
DKIM_PASS_AUTHOR = 'passauthor'  # dkim record is valid and in authors/from hdr domain
DKIM_PASS_SENDER = 'passsender'  # dkim record is valid and in envelope sender domain
DKIM_PASS = 'pass'
DKIM_FAIL = 'fail'
DKIM_NONE = 'none'
DKIM_POLICY = 'policy'
DKIM_NEUTRAL = 'neutral'
DKIM_TEMPFAIL = 'tempfail'
DKIM_PERMFAIL = 'permfail'
DKIM_SKIP = 'skip'
SAHEADER_DMARC_RESULT = 'X-DMARC-Result'
SAHEADER_DMARC_DISPO = 'X-DMARC-Dispo'
DMARC_REJECT = 'reject'
DMARC_QUARANTINE = 'quarantine'
DMARC_UNAVAILABLE = 'unavailable'
DMARC_SKIP = 'skip'
DMARC_NONE = 'none'
DMARC_PASS = 'pass'
DMARC_FAIL = 'fail'
DMARC_RECORDFAIL = 'recordfail'
DMARC_TEMPFAIL = 'tempfail'
SPF_SKIP = 'skip'

IP_PROTO_ALL = 'all'
IP_PROTO_IP4 = 'ipv4'
IP_PROTO_IP6 = 'ipv6'
IP_PROTOS = [IP_PROTO_ALL, IP_PROTO_IP4, IP_PROTO_IP6]

class IPProtoCheckMixin:
    """
    IP Protocol Check Mixin
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requiredvars.update({
            'check_protocols': {
                'default': IP_PROTO_IP6,
                'description': f'IP protocols to check for reject/defer. must be one of {", ".join(IP_PROTOS)}'
            },
        })
    
    
    def _check_protocol(self, ip: str) -> bool:
        clientip = ipaddress.ip_address(ip)
        check_protocols = self.config.get(self.section, 'check_protocols')
        if check_protocols == 'all':
            return True
        if (clientip.version == 6 and check_protocols == 'ipv6') or (
                clientip.version == 4 and check_protocols == 'ipv4'):
            return True
        return False


_re_at = re.compile(r"(?<=[@＠])[\w.-]+")


def extract_from_domains(suspect:Suspect, header:str='From', get_display_part:bool=False) -> tp.Optional[tp.List[str]]:
    """
    Returns a list of all domains found in From header
    :param suspect: Suspect
    :param header: name of header to extract, defaults to From
    :param get_display_part: set to True to search and extract domains found in display part, not the actual addresses
    :return: list of domain names or None in case of errors
    """

    # checking display part there's no need checking for the validity of the associated
    # mail address
    from_addresses = suspect.parse_from_type_header(header=header, validate_mail=(not get_display_part))
    if len(from_addresses) < 1:
        return None
    
    from_doms = set()
    for item in from_addresses:
        if get_display_part:
            domain_match = _re_at.search(item[0])
            if domain_match is None:
                continue
            from_doms.add(domain_match.group())
        elif len(item)>1 and item[1] and '@' in item[1]:
            try:
                from_doms.add(extract_domain(item[1]))
            except Exception:
                logging.getLogger("fuglu.plugin.domainauth.extract_from_domains").debug(f'{suspect.id} {traceback.format_exc()}')
    return list(from_doms)


def extract_from_domain(suspect:Suspect, header:str='From', get_display_part:bool=False) -> tp.Optional[str]:
    """
    Returns the most significant domain found in From header.
    Usually this means the last domain that can be found.
    :param suspect: Suspect object
    :param header: name of header to extract, defaults to From
    :param get_display_part: set to True to search and extract domains found in display part, not the actual addresses
    :return: string with domain name or None if nothing found
    """
    from_doms = extract_from_domains(suspect, header, get_display_part)
    if from_doms and from_doms[-1]:
        from_dom = from_doms[-1].lower()
    else:
        from_dom = None
    return from_dom


async def check_iprev(suspect: Suspect, config) -> tp.Optional[str]:
    # see https://www.rfc-editor.org/rfc/rfc8601#section-2.7.3
    clientinfo = suspect.get_client_info(config)
    if clientinfo:
        helo, ip, ptr = clientinfo
        if ptr and ptr != 'unknown':
            return 'pass'
        try:
            if aiodnsquery.AIODNSQUERY_EXTENSION_ENABLED:
                confirmed = await aiodnsquery.fcrdnslookup(ip, reraise=True)
            else:
                confirmed = dnsquery.fcrdnslookup(ip, reraise=True)
            if confirmed:
                return 'pass'
            else:
                return 'fail'
        except (aiodnsquery.FuSERVFAIL, aiodnsquery.FuTIMEOUT):
            return 'temperror'
        except Exception:
            return 'permerror'
    return None


def check_skip_on_tag(suspect: Suspect, taglist:tp.Iterable[str]) -> tp.Optional[str]:
    for tag in taglist:
        if '==' in tag:
            tagname, tagvalue = tag.split('==',1)
            op = operator.eq
        elif '!=' in tag:
            tagname, tagvalue = tag.split('!=',1)
            op = operator.ne
        else:
            tagname = tag
            tagvalue = True
            op = operator.eq
        if op(suspect.get_tag(tagname, False), tagvalue):
            return tagname
    return None


def parse_received_xxx(hdrvalue: str) -> tp.Tuple[tp.Optional[str], tp.Dict[str, str], tp.Optional[str]]:
    status = None
    expl = None
    fieldmap = {}
    if hdrvalue:
        fields = hdrvalue.replace('\r','').replace('\n', '').split(';')
        if fields and fields[0]:
            values = fields[0].split(None,2)
            if len(values) == 3:
                status, _, expl = values
                expl = expl.rsplit(')',1)[0]
                firstfield = fields[0].rsplit(None,1)[-1]
                fields[0] = firstfield
                fieldmap = {v[0].lower().strip():v[1].strip() for v in [f.split('=',1) for f in fields if '=' in f]}
    return status, fieldmap, expl


async def query_dmarc(domain:str, timeout:int=5) -> tp.Optional[tp.List[str]]:
    records = []
    hostname = f'_dmarc.{domain}'
    try:
        result = await aiodnsquery.lookup(hostname, aiodnsquery.QTYPE_TXT, reraise=True, timeout=timeout)
        if result is None:
            return records
    except (aiodnsquery.FuTIMEOUT, aiodnsquery.FuSERVFAIL): # temporary lookup errors
        return None
    except Exception: # permanent lookup errors, treat as "no record"
        return records

    for item in result:
        item = force_uString(item).strip('"')
        if item.lower().startswith('v=dmarc1'):
            record = ' '.join(i.strip('"') for i in item.split())  # fix records like "v=DMARC1;" "p=none;"
            records.append(record)

    return records


class ARCVerifyPlugin(ScannerPlugin):
    """
This plugin checks the ARC signature of the message and sets tags.
Tags set:
 * ARCVerify.skipreason set if the verification has been skipped
 * ARCVerify.cv chain validation result
 * ARCVerify.message ARC validation message

Please install dkimpy and not pydkim as mandatory dependency to use this plugin.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'max_lookup_time': {
                'default': '5',
                'description': 'maximum time per DNS lookup',
            },
            'result_header': {
                'default': '',
                'description': 'write result to header of name specified here. leave empty to not write any header.'
            },
            'create_received_arc': {
                'default': 'False',
                'description': 'create Received-ARC header'
            },
        }

    def __str__(self):
        return "ARC Verify"

    dkim_dns_func = None
    
    def _create_received_arc(self, cv: str, message:str, arcdomain: str, selector: str) -> str:
        """
        create received-arc header based on current arc check result
        """
        myname = get_outgoing_helo(self.config)
        fields = [f'receiver={myname}']
        if selector:
            fields.append(f'selector={selector}')
        if arcdomain:
            fields.append(f'arcdomain={arcdomain}')
        headervalue = f'{cv} ({myname}: {message}) {"; ".join(fields)}'
        return headervalue

    def examine(self, suspect):
        suspect.set_tag("ARCVerify.cv", DKIM_SKIP)
        if not DKIMPY_AVAILABLE:
            suspect.debug("dkimpy not available, can not check ARC")
            suspect.set_tag('ARCVerify.skipreason', 'dkimpy library not available')
            return DUNNO
        
        suspect.set_tag("ARCVerify.cv", DKIM_NONE)
        msgrep = suspect.get_message_rep()
        for hdrname in ARC.ARC_HEADERS:
            hdrname = force_uString(hdrname)
            if hdrname not in msgrep:
                suspect.set_tag('ARCVerify.skipreason', 'not ARC signed')
                suspect.write_sa_temp_header(SAHEADER_ARC, DKIM_NONE)
                result_header = self.config.get(self.section, 'result_header')
                if result_header:
                    suspect.add_header(result_header, DKIM_NONE)
                suspect.debug(f"{suspect.id} ARC signature header {hdrname} not found")
                return DUNNO

        timeout = self.config.getfloat(self.section, 'max_lookup_time')
        source = suspect.get_source(newline=b'\r\n')
        cv = DKIM_NONE
        message = 'Not signed'
        arc_domain = None
        arc_selector = None
        try:
            # use the local logger of the plugin but prepend the fuglu id
            d = ARC(source, logger=PrependLoggerMsg(self.logger, prepend=suspect.id, maxlevel=logging.INFO), timeout=timeout)
            try:
                if self.dkim_dns_func is not None:
                    data = d.verify(dnsfunc=self.dkim_dns_func)
                else:
                    data = d.verify()
                if len(data) != 3:
                    self.logger.warning(f"{suspect.id} ARC validation with unexpected data: {data}")
                else:
                    self.logger.debug(f"{suspect.id} ARC result {data}")
                    cv, result, message = data
                    cv = force_uString(cv)
                    if result and result[0] and 'as-domain' in result[0]:
                        arc_domain = force_uString(result[0].get('as-domain'))
                    if result and result[0] and 'as-selector' in result[0]:
                        arc_selector = force_uString(result[0].get('as-selector'))
            except Exception as de:
                self.logger.warning(f"{suspect.id} ARC validation failed: {de.__class__.__name__}: {str(de)}")
        except dkim.MessageFormatError as e:
            cv = DKIM_FAIL
            message = 'Message format error'
            self.logger.warning(f"{suspect.id} ARC validation failed: Message format error")
            self.logger.debug(f"{suspect.id} {str(e)}")
            suspect.set_tag('ARCVerify.skipreason', 'plugin error')
        except NameError as e:
            cv = DKIM_SKIP
            message = 'Plugin error'
            self.logger.warning(f"{suspect.id} ARC validation failed due to missing dependency: {str(e)}")
            suspect.set_tag('ARCVerify.skipreason', 'plugin error')
        except Exception as e:
            cv = DKIM_SKIP
            message = 'Plugin error'
            self.logger.warning(f"{suspect.id} ARC validation failed: {e.__class__.__name__}: {str(e)}")
            suspect.set_tag('ARCVerify.skipreason', 'plugin error')
        
        
        suspect.set_tag("ARCVerify.cv", cv)
        suspect.set_tag("ARCVerify.message", message)
        suspect.set_tag("ARCVerify.domain", arc_domain)
        suspect.set_tag("ARCVerify.selector", arc_selector)
        suspect.write_sa_temp_header(SAHEADER_ARC, cv)
        result_header = self.config.get(self.section, 'result_header')
        if result_header:
            suspect.add_header(result_header, cv)
        if self.config.getboolean(self.section, 'create_received_arc'):
            rcvdarchdr = self._create_received_arc(cv, message, arc_domain, arc_selector)
            suspect.add_header('Received-ARC', rcvdarchdr, immediate=True)
        return DUNNO

    def lint(self):
        all_ok = self.check_config()

        if not DKIMPY_AVAILABLE:
            print("Missing dependency: dkimpy https://launchpad.net/dkimpy")
            all_ok = False

        if not dnsquery.DNSQUERY_EXTENSION_ENABLED:
            print("Missing dependency: no supported DNS libary found: pydns or dnspython")
            all_ok = False

        return all_ok


class ARCRcvdPlugin(ScannerPlugin):
    """
If ARCVerify plugin is not run in this instance of Fuglu, use this plugin to extract a
"Received-ARC" header (a custom header in the style of Received-SPF but for ARC authentication)
created by a Fuglu/Spam filter running on a previous system.
Set create_received_arc in ARCVerify plugin config to write such a header. It'll write a header such as:
Received-ARC: pass (firsthost.fuglu.org: some status message) key1=value1;key2=value2
To enable reading set received_arc_header_receiver in ARCRcvdPlugin config to the hostname/domain of the
server writing the header, e.g. in this case firsthost.fuglu.org or .fuglu.org.
The hostname is always read recursively, e.g. .fuglu.org would also match otherhost.fuglu.org
The result is then written to local subject tags such as ARCVerify.cv, ARCVerify.message, ARCVerify.domain, ARCVerify.selector
    """
    
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'received_arc_header_receiver': {
                'default': '',
                'description': 'if arc verify plugin is not run locally, use received-arc header with receiver field value in given domain name. leave empty to not parse received-arc header'
            },
        }
    
    
    def examine(self, suspect):
        rcvdarcreceiver = self.config.get(self.section, 'received_arc_header_receiver')
        if not rcvdarcreceiver:
            self.logger.debug(f'{suspect.id} received_arc_header_receiver not defined')
            return DUNNO
        
        msgrep = suspect.get_message_rep()
        rcvdarc_all = msgrep.get_all('Received-ARC', [])
        for rcvdarc in rcvdarc_all:
            try:
                rcvdarc = suspect.decode_msg_header(rcvdarc, logid=suspect.id)
                rcvdarcstatus, fields, expl = parse_received_xxx(rcvdarc)
                receiver = fields.get('receiver')
                if rcvdarcstatus and receiver and receiver.lower().endswith(rcvdarcreceiver.lower()):
                    arcval = rcvdarcstatus.lower()
                    
                    suspect.set_tag("ARCVerify.cv", arcval)
                    suspect.set_tag("ARCVerify.message", expl)
                    if 'arcdomain' in fields:
                        suspect.set_tag("ARCVerify.domain", fields.get('arcdomain'))
                    if 'selector' in fields:
                        suspect.set_tag("ARCVerify.selector", fields.get('arcselector'))
                    suspect.write_sa_temp_header(SAHEADER_ARC, arcval)
                    self.logger.debug(f'{suspect.id} evaluated received-arc header {rcvdarc}')
                    break
                elif rcvdarc:
                    self.logger.debug(f'{suspect.id} failed to get status from received-arc header. status={rcvdarcstatus} receiver={receiver} received-arc={rcvdarc}')
                elif not rcvdarc:
                    self.logger.debug(f'{suspect.id} not a valid received-arc header {rcvdarc}')
            except Exception as e:
                self.logger.error(
                    f'{suspect.id} failed to parse received-arc header "{rcvdarc}" due to {e.__class__.__name__}: {str(e)}')
        return DUNNO

class ARCStripPlugin(ScannerPlugin):
    """
    This plugin removes previous ARC headers if ARC validation failed.
    """
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'strip_only_fail': {
                'default': 'True',
                'description': 'only strip broken ARC seals',
            },
            'arcstrip_filter': {
                'default': '${confdir}/arcstrip_filter.regex',
                'description': 'filterfile containing suspectfilter rules to strip broken arc signatures',
            },
        }
        self.arcstrip_filter = None

    def _init_arcstrip_filter(self):
        """checks if there is a bacn filter file and initializes it. """
        if self.arcstrip_filter is None:
            filename = self.config.get(self.section, 'arcstrip_filter')
            if filename and os.path.exists(filename):
                self.arcstrip_filter = SuspectFilter(filename)
    
    
    def __str__(self):
        return "ARC Strip"
    
    
    def examine(self, suspect):
        if suspect.get_tag("ARCVerify.cv") != DKIM_FAIL and self.config.getboolean(self.section, 'strip_only_fail'):
            self.logger.debug(f'{suspect.id} not stripping arc headers, ARCVerify.cv={suspect.get_tag("ARCVerify.cv")}')
            return DUNNO
        
        self._init_arcstrip_filter()
        if self.arcstrip_filter is None:
            self.logger.debug(f'{suspect.id} not stripping arc headers, filter not initialised')
            return DUNNO
        
        match, arg = self.arcstrip_filter.matches(suspect)
        if match:
            authres_hdr = suspect.get_header('Authentication-Results')
            if authres_hdr:
                suspect.set_tag('authres', authres_hdr) # keep for use in ARCSignPlugin._reuse_authres_header
                self.logger.debug(f'{suspect.id} stored previous authres header {authres_hdr}')
            
            delhdrs = {'ARC-Seal', 'ARC-Message-Signature', 'ARC-Authentication-Results', 'Authentication-Results'}
            stripped = suspect.remove_headers_from_source(delhdrs)
            if stripped:
                self.logger.info(f'{suspect.id} removed previous arc headers')
            else:
                self.logger.debug(f'{suspect.id} no arc headers found')
            suspect.set_tag('ARCStrip', stripped)
        else:
            self.logger.debug(f'{suspect.id} not stripping arc headers, no filter match')
        return DUNNO
    
    
    def lint(self):
        ok = self.check_config()
        if ok:
            filename = self.config.get(self.section, 'arcstrip_filter')
            if not filename:
                ok = False
                print('WARNING: no arcstrip_filter file specified. this plugin will do nothing.')
            if filename and not os.path.exists(filename):
                ok = False
                print(f'ERROR: arcstrip_filter file {filename} not found. this plugin will do nothing.')
        return ok


class ARCSignPlugin(ScannerPlugin):
    """
This plugin creates the ARC signature headers of the message.
Special attention is given if message is from outlook.com, which adds broken authentication results headers.
This plugin will add 4 new headers:
 * Authentication-Results
 * ARC-Authentication-Results
 * ARC-Message-Signature
 * ARC-Seal

Please install dkimpy and not pydkim as mandatory dependency to use this plugin.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'privatekeyfile': {
                'default': "${confdir}/dkim/${header_from_domain}.key",
                'description': "Location of the private key file. supports standard template variables plus additional ${header_from_domain} which extracts the domain name from the From: -Header and ${auth_host} which defaults to fuglu's helo. Leave empty to not actually sign, only create the Authentication-Results header.",
            },

            'selector': {
                'default': 'default',
                'description': 'selector to use when signing, supports templates and additional variables (see privatekeyfile)',
            },

            'signheaders': {
                'default': 'From,Reply-To,Subject,Date,To,CC,Resent-Date,Resent-From,Resent-To,Resent-CC,In-Reply-To,References,List-Id,List-Help,List-Unsubscribe,List-Subscribe,List-Post,List-Owner,List-Archive',
                'description': 'comma separated list of headers to sign. empty string=sign all headers',
            },

            'signdomain': {
                'default': 'header:From',
                'description': 'which domain to use in signature? use header:headername or static:example.com or tmpl:${template_var} (tmpl supports additional vars header_from_domain and auth_host)',
            },
            
            'get_authres_tag': {
                'default': '',
                'description': 'name of suspect tag providing authentication-results header'
            },

            'trust_authres_rgx': {
                'default': '',
                'description': 'do not create own but use authentication-results header of previous host if ptr matches given regex'
            },

            'reuse_authres_tag': {
                'default': '',
                'description': 'name of suspect tag that must be set to True to enable authenetication-results header reuse (as per trust_authres_rgx). if empty no tag is checked and trust_authres_rgx is always checked.'
            },

            'debug_domains': {
                'default': '',
                'description': 'list of recipient domains for which to print additional debug output (potentially noisy)'
            },
            
            'debugdumpdir': {
                'default': '',
                'description': 'define a directory where to dump sources on errors'
            },
        }

    def __str__(self):
        return "ARC Sign"

    def _get_source(self, suspect: Suspect, authres_hdr: str, debug_headers: tp.List[str]) -> bytes:
        """
        get source and patch/remove invalid authres headers (e.g. from microsoft)
        :param suspect: Suspect
        :return: message source as bytes
        """
        clientinfo = suspect.get_client_info(self.config)
        helo = clientinfo[0].lower() if clientinfo and clientinfo[0] else None
        ptr = clientinfo[2].lower() if clientinfo and clientinfo[2] else None
        tempsuspect = Suspect(suspect.from_address, suspect.to_address, '/dev/null', id=suspect.id)
        tempsuspect.set_source(suspect.get_source())
        msgrep = tempsuspect.get_message_rep()
        authres_hdrs = msgrep.get_all('Authentication-Results', [])
        ok_hdrs = []
        if authres_hdrs:
            for hdr in authres_hdrs:
                hdr = hdr.strip(';')
                try:
                    try:
                        authres.AuthenticationResultsHeader.parse(f'Authentication-Results: {hdr}')
                        ok_hdrs.append(hdr)
                    except authres.core.SyntaxError:
                        if helo and ptr and ptr.endswith(('.outlook.com', '.mx.microsoft')):
                            helohdr = f'{helo}; {hdr}'
                            authres.AuthenticationResultsHeader.parse(f'Authentication-Results: {helohdr}')
                            ok_hdrs.append(helohdr)
                            self.logger.debug(f'{suspect.id} patching invalid authres header {hdr}')
                        else:
                            self.logger.debug(f'{suspect.id} not patching invalid authres header from {helo}')
                            raise
                except authres.core.SyntaxError:
                    self.logger.warning(f'{suspect.id} dropping invalid authres header {hdr}')
            tempsuspect.remove_headers_from_source({'Authentication-Results'})
        if authres_hdr:
            ok_hdrs.append(authres_hdr)
        for hdr in ok_hdrs:
            hdr = hdr.replace('\r', '').replace('\n', '')
            tempsuspect.add_header('Authentication-Results', hdr, immediate=True)
        self.logger.debug(f'{suspect.id} using {len(ok_hdrs)} authres headers')
        for header in debug_headers:
            header = force_uString(header)
            value = msgrep.get(header)
            if value:
                myhash = md5(force_bString(value)).hexdigest() # nosemgrep CWE-327
                self.logger.debug(f'{suspect.id} source header {myhash} {header}: {value}')
        return tempsuspect.get_source()

    def _authres_insert_arcpass(self, suspect:Suspect, authres_hdr:str) -> str:
        fields = authres_hdr.split(';')
        has_arc = False
        for field in fields:
            if field.strip().lower().startswith('arc='):
                has_arc = True
                break
        if not has_arc:  # previous arc sig found but not mentioned in authres header
            if suspect.get_tag('ARCStrip') is True:
                # ARC was stripped, we spoof pass status. maybe need to set to None
                arcstatus = DKIM_PASS
            else:
                arcstatus = suspect.get_tag('ARCVerify.cv')
                if arcstatus == DKIM_SKIP: # no arc check performed
                    arcstatus = None
            if arcstatus: # only set if we have a reasonable status
                fields.append(f'arc={arcstatus}')
        return ';'.join(fields)

    def _reuse_authres_header(self, suspect: Suspect, authhost: str) -> tp.Optional[str]:
        hdr = None
        ptrrgx = self.config.get(self.section, 'trust_authres_rgx')
        tag = self.config.get(self.section, 'reuse_authres_tag')
        reuse_tag = suspect.get_tag(tag, False) if tag else True
        if ptrrgx and reuse_tag == True:
            self.logger.debug(f'{suspect.id} ptrrgx is set and tag {tag} is {suspect.get_tag(tag)}')
            clientinfo = suspect.get_client_info(self.config)
            ptr = clientinfo[2].lower() if clientinfo and clientinfo[2] else None
            if ptr and re.search(ptrrgx, ptr):
                msgrep = suspect.get_message_rep()
                hdr = msgrep.get('Authentication-Results')
                if hdr is None:
                    hdr = suspect.get_tag('authres')
                if hdr is not None:
                    hdr = hdr.strip(';')
                    try:
                        authres.AuthenticationResultsHeader.parse(f'Authentication-Results: {hdr}')
                    except authres.core.SyntaxError:
                        hdr = f'{authhost}; {hdr}'
                    else:
                        fields = hdr.split(';')
                        fields[0] = authhost
                        hdr = ';'.join(fields)
                    if msgrep.get('ARC-Seal'):  # previous arc sig found. we trust it passed. used for m365
                        hdr = self._authres_insert_arcpass(suspect, hdr)
                    self.logger.debug(f'{suspect.id} using previous authres header {hdr}')
                else:
                    self.logger.debug(f'{suspect.id} no previous authres header found')
            else:
                self.logger.debug(f'{suspect.id} ptr {ptr} does not match regex {ptrrgx}')
        else:
            self.logger.debug(f'{suspect.id} ptrrgx is empty or tag {tag} is not True')
        return hdr

    async def _create_authres_header(self, suspect: Suspect, authhost: str, hdrfrom: str) -> str:
        """
        create authentication result header value as per rfc8601
        :param suspect: Suspect object
        :param authhost: name of authentication host (first field of authres header)
        :return: bytes string of authentication header, at least host.example.com;none
        """
        values = [authhost, ]
        spfstate = suspect.get_tag('SPF.status')
        if spfstate and spfstate != SPF_SKIP:
            values.append(f'spf={spfstate} smtp.mailfrom={suspect.from_domain}')
        dkimstate = suspect.get_tag("DKIMVerify.result")
        if dkimstate:
            dkimtag = f'dkim={dkimstate}'
            dkimdomain = suspect.get_tag("DKIMVerify.dkimdomain")
            if dkimdomain:
                dkimtag = f'{dkimtag} header.d={dkimdomain}'
            dkimdomaini = suspect.get_tag("DKIMVerify.dkimdomaini")
            if dkimdomaini:
                dkimtag = f'{dkimtag} header.i={dkimdomaini}'
            selector = suspect.get_tag("DKIMVerify.selector")
            if selector:
                dkimtag = f'{dkimtag} header.s={selector}'
            values.append(dkimtag)
        dmarcstate = suspect.get_tag('dmarc.result')
        if dmarcstate and dmarcstate not in [DMARC_SKIP, DMARC_NONE]:
            dmarctag = f'dmarc={dmarcstate}'
            if hdrfrom:
                dmarctag = f'{dmarctag} header.from={hdrfrom}'
            values.append(dmarctag)
        #arcstate = suspect.get_tag('ARCVerify.cv')
        #if arcstate:
        #    values.append(f'arc={arcstate}')  # not part of rfc
        iprev = await check_iprev(suspect, self.config)
        if iprev:
            values.append(f'iprev={iprev}')
        if len(values) == 1:
            values.append('none')
        hdr = ';'.join(values)
        self.logger.debug(f'{suspect.id} using generated authres header {hdr}')
        return hdr

    def _get_sign_domain(self, suspect: Suspect, headerfromdomain: str) -> str:
        domain = None
        sigkey = self.config.get(self.section, 'signdomain')
        if ':' in sigkey:
            key, value = sigkey.split(':', 1)
            if key == 'header' and value.lower() == 'from':
                domain = headerfromdomain
            elif key == 'header':
                domain = extract_from_domain(suspect, header=value)
            elif key == 'static':
                domain = value
            elif key == 'tmpl':
                domain = apply_template(value, suspect, dict(header_from_domain=headerfromdomain, auth_host=get_outgoing_helo(self.config)))
        return domain

    async def examine(self, suspect):
        if not ARCSIGN_AVAILABLE:
            suspect.debug("dkimpy or authres not available, can not sign ARC")
            self.logger.debug(f"{suspect.id} ARC signing skipped - missing dkimpy or authres library")
            return DUNNO
        
        if not suspect.get_header('received'):
            self.logger.warning(f'{suspect.id} no received header found, cannot add ARC signature')
            return DUNNO
        
        headerfromdomain = extract_from_domain(suspect)
        authhost = get_outgoing_helo(self.config)
        domain = self._get_sign_domain(suspect, headerfromdomain)
        selector = apply_template(self.config.get(self.section, 'selector'), suspect, dict(header_from_domain=headerfromdomain, auth_host=authhost))

        if domain is None:
            self.logger.warning(f"{suspect.id} Failed to extract From-header domain for ARC signing")
            return DUNNO

        privkeyfile = apply_template(self.config.get(self.section, 'privatekeyfile'), suspect, dict(header_from_domain=headerfromdomain, auth_host=authhost))
        privkeycontent = None
        if not privkeyfile:
            self.logger.debug(f'{suspect.id} ARC privkey not defined, will only create authres header')
        elif not os.path.isfile(privkeyfile):
            self.logger.warning(f"{suspect.id} ARC signing failed for domain {headerfromdomain} private key not found: {privkeyfile}")
            return DUNNO
        else:
            with open(privkeyfile, 'br') as f:
                privkeycontent = f.read()

        headerconfig = self.config.get(self.section, 'signheaders')
        if headerconfig is None or headerconfig.strip() == '':
            inc_headers = None
        else:
            inc_headers = [force_bString(h.strip().lower()) for h in headerconfig.split(',')]

        authres_hdr = None
        get_authres_tag = self.config.get(self.section, 'get_authres_tag')
        if get_authres_tag:
            # get authres header from tag. no checks applied.
            authres_hdr = suspect.get_tag(get_authres_tag)
            if authres_hdr:
                self.logger.debug(f'{suspect.id} using authres header from tag {get_authres_tag}: {authres_hdr}')
        if authres_hdr is None:
            authres_hdr = self._reuse_authres_header(suspect, authhost)
        if authres_hdr is None:  # if empty string we use hdr from previous host but none was set
            authres_hdr = await self._create_authres_header(suspect, authhost, headerfromdomain)
        
        debug_headers = []
        debug_domains = self.config.getlist(self.section, 'debug_domains')
        if debug_domains and suspect.to_domain in debug_domains:
            debug_headers = inc_headers[:]
            debug_headers.append('authentication-results')
        
        if privkeycontent is not None:
            try:
                source = self._get_source(suspect, authres_hdr, debug_headers)
                d = ARC(source, logger=PrependLoggerMsg(self.logger, prepend=suspect.id, maxlevel=logging.INFO))
                arc_set = d.sign(force_bString(selector), force_bString(domain), privkeycontent, force_bString(authhost), include_headers=inc_headers)
                if not arc_set:
                    self.logger.warning(f'{suspect.id} empty ARC signature set')
                    debugdumpdir = self.config.get(self.section, 'debugdumpdir')
                    if debugdumpdir:
                        filename = os.path.join(debugdumpdir, f'{suspect.id}.eml')
                        with open(filename, 'wb') as f:
                            f.write(suspect.get_source())
                        self.logger.warning(f'{suspect.id} ARC sealing failed, dumped original source to {filename}')
                        
                        filename = os.path.join(debugdumpdir, f'{suspect.id}.arcsource.eml')
                        with open(filename, 'wb') as f:
                            f.write(source)
                        self.logger.warning(f'{suspect.id} ARC sealing failed, dumped ARC source to {filename}')
                    
                else:
                    arc_set.reverse()
                    for item in arc_set:
                        hdr, val = item.split(b':', 1)
                        # dkim.ARC provides properly folded headers. we trust they're valid.
                        suspect.add_header(force_uString(hdr.strip()), force_uString(val), immediate=True, raw=True)
            except Exception as de:
                if suspect.get_tag("ARCVerify.cv") == DKIM_NONE and suspect.get_header('ARC-Seal') == '0':
                    self.logger.debug(f"{suspect.id} ARC signing of ARC-Seal:0 message failed: {de.__class__.__name__}: {str(de)}")
                else:
                    self.logger.warning(f"{suspect.id} ARC signing failed: {de.__class__.__name__}: {str(de)}")
                    self.logger.debug(f"{suspect.id} ARC signing failed: {de.__class__.__name__}: {str(de)}", exc_info=de)
        
        # This header should be on top
        authres_hdr = authres_hdr.replace('\r', '').replace('\n', '')
        suspect.add_header('Authentication-Results', authres_hdr, immediate=True)
        return DUNNO

    def lint(self):
        all_ok = self.check_config()

        if not DKIMPY_AVAILABLE:
            print("Missing dependency: dkimpy https://launchpad.net/dkimpy")
            all_ok = False
        elif not ARCSIGN_AVAILABLE:
            print("Missing dependency: authres")
        if not dnsquery.DNSQUERY_EXTENSION_ENABLED:
            print("Missing dependency: no supported DNS libary found. pydns or dnspython")
            all_ok = False

        # if privkey is a filename (no placeholders) check if it exists
        privkeytemplate = self.config.get(self.section, 'privatekeyfile')
        if not privkeytemplate:
            print('no private key file specified. will not create ARC seal, only authres')
        elif '{' not in privkeytemplate and not os.path.exists(privkeytemplate):
            print(f"Private key file {privkeytemplate} not found")
            all_ok = False
        elif os.path.exists(privkeytemplate):
            try:
                with open(privkeytemplate, 'br') as f:
                    privkeycontent = f.read()
            except Exception as e:
                print(f'failed to read private key due to {e.__class__.__name__}: {str(e)}')
                all_ok = False

        sigkey = self.config.get(self.section, 'signdomain')
        if not ':' in sigkey:
            print(f'Invalid signdomain config value: {sigkey}')
            all_ok = False
        else:
            key, value = sigkey.split(':', 1)
            if key not in ['header', 'static', 'tmpl']:
                print(f'Invalid signdomain value: {sigkey} - {key} should be one of header, static')
                all_ok = False
            elif key == 'static' and not '.' in value:
                print(f'Invalid signdomain value: {sigkey} - {value} should be a valid domain name')
                all_ok = False

        return all_ok


class DKIMVerifyResult:
    valid = False
    dkimdomain = ''
    selector = ''
    dkimval = DKIM_NEUTRAL
    dkimmsg = 'unknown'
    saval = None
    record_domaini = ''
    is_authordomain = False
    is_senderdomain = False
    keysize = 0


class DKIMVerifyPlugin(IPProtoCheckMixin, ScannerPlugin):
    """
This plugin checks the DKIM signature of the message and sets tags.
DKIMVerify.sigvalid : True if there was a valid DKIM signature, False if there was an invalid DKIM signature
the tag is not set if there was no dkim header at all

DKIMVerify.skipreason: set if the verification has been skipped

The plugin does not take any action based on the DKIM test result since a failed DKIM validation by itself
should not cause a message to be treated any differently. Other plugins might use the DKIM result
in combination with other factors to take action (for example a "DMARC" plugin could use this information)

It is currently recommended to leave both header and body canonicalization as 'relaxed'.
Using 'simple' can cause the signature to fail.

Please install dkimpy and not pydkim as mandatory dependency to use this plugin.
    """

    # set as class variable for simple unit test monkey patching
    DKIM = DKIM
    dkim_dns_func = None

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.skiplist = FileList(filename=None, strip=True, skip_empty=True, skip_comments=True, lowercase=True)
        self.requiredvars = {
            'skiplist': {
                'default': '',
                'description': 'File containing a list of domains (one per line) which are not checked'
            },
            'max_lookup_time': {
                'default': '5',
                'description': 'maximum time per DNS lookup',
            },
            'strip_subject_rgx': {
                'default': '',
                'description': 'apply this regular expression to strip values/tags from subject',
            },
            'result_header': {
                'default': '',
                'description': 'write result to header of name specified here. leave empty to not write any header.'
            },
            'skip_on_tag': {
                'default': '',
                'description': 'skip DKIM evaluation if tag is present and has specified value (examples: x,y==z,a!=b -> x must be True, y must be "z" and a must not be "b")'
            },
            'create_received_dkim': {
                'default': 'False',
                'description': 'create Received-DKIM header'
            },
            'debugdumpdir': {
                'default': '',
                'description': 'define a directory where to dump sources on errors'
            },
            'on_tempfail': {
                'default': 'DUNNO',
                'description': 'action on DNS lookup temp fail. leave to DUNNO if running in after-queue mode'
            },
            'on_nokey': {
                'default': 'DUNNO',
                'description': 'action on DKIM evaluation error because no key is published in DNS. leave to DUNNO if running in after-queue mode'
            },
            'on_fail': {
                'default': 'DUNNO',
                'description': 'action on DKIM evaluation error (other than missing key). leave to DUNNO if running in after-queue mode'
            },
        }
        self.rgx_cache = {}
    
    def __str__(self):
        return "DKIM Verify"
    
    def _get_source(self, suspect:Suspect) -> bytes:
        """
        get message source from suspect and "patch" subject by applying strip_subject_rgx
        :param suspect: the suspect object
        :return: bytes representation of original message source (possibly with modified subject)
        """
        source = suspect.get_source(newline=b'\r\n')
        strip_subject_rgx = self.config.get(self.section, 'strip_subject_rgx')
        if strip_subject_rgx:
            msgrep = email.message_from_bytes(source, _class=PatchedMessage, policy=email.policy.SMTP)
            oldsubject = msgrep.get('subject')
            if oldsubject:
                oldsubject = suspect.decode_msg_header(oldsubject, logid=suspect.id)
            if oldsubject:
                rgx = self.rgx_cache.get(strip_subject_rgx)
                if rgx is None:
                    rgx = re.compile(strip_subject_rgx, re.I)
                    self.rgx_cache = {strip_subject_rgx:rgx}
                newsubject = rgx.sub('', oldsubject).strip()
                if oldsubject.strip() != newsubject:
                    self.logger.debug(f'{suspect.id} updating subject to {newsubject}')
                    tmpsuspect = Suspect(from_address=suspect.from_address, recipients=suspect.recipients, tempfile=None, inbuffer=source)
                    tmpsuspect.set_header('subject', newsubject)
                    source = tmpsuspect.get_source()
                else:
                    self.logger.debug(f'{suspect.id} not updating subject')
            else:
                self.logger.debug(f'{suspect.id} not subject found')
        return source
    
    def _create_received_dkim(self, result:DKIMVerifyResult) -> str:
        """
        create received-dkim header based on current dkim check result
        """
        dkimval = result.saval or result.dkimval
        myname = get_outgoing_helo(self.config)
        fields = [f'receiver={myname}']
        if result.selector:
            fields.append(f'selector={result.selector}')
        if result.dkimdomain:
            fields.append(f'dkimdomain={result.dkimdomain}')
        if result.record_domaini:
            fields.append(f'dkimdomaini={result.record_domaini}')
        headervalue = f'{dkimval} ({myname}: {result.dkimmsg}) {"; ".join(fields)}'
        return headervalue
    
    
    def _get_dkim_hdr_tags(self, suspect:Suspect, header:tp.Union[str, bytes, email.header.Header]) -> tp.Dict[bytes, bytes]:
        hdrval = suspect.decode_msg_header(header, logid=suspect.id)
        # wants bytes, returns dict of bytes
        tags = dkim.util.parse_tag_value(force_bString(hdrval))
        return tags
    
    
    def _eval_dkim(self, suspect:Suspect, dkimhdrs:tp.List[str], hdr_from_domain:str) -> DKIMVerifyResult:
        result = DKIMVerifyResult()
        
        source = self._get_source(suspect)
        env_from_domain = suspect.from_domain.lower()
        timeout = self.config.getfloat(self.section, 'max_lookup_time')
        try:
            # use the local logger of the plugin but prepend the fuglu id
            dkimcheck = self.DKIM(source,
                                  logger=PrependLoggerMsg(self.logger, prepend=suspect.id, maxlevel=logging.INFO),
                                  timeout=timeout)
            # one dkim header has to be valid
            # trust priority: d=hdr_from, d=env_from, d=3rdparty
            dkimexc = False
            for i in range(0, len(dkimhdrs)):
                tags = self._get_dkim_hdr_tags(suspect, dkimhdrs[i])
                record_domain = tags.get(b'd', b'').decode().lower()
                result.record_domaini = tags.get(b'i', b'').decode().lower()
                record_selector = tags.get(b's', b'').decode().lower()
                try:
                    if self.dkim_dns_func is not None:
                        record_valid = dkimcheck.verify(idx=i, dnsfunc=self.dkim_dns_func)  # in unit tests as dkim module cannot be patched with mock
                    else:
                        record_valid = dkimcheck.verify(idx=i)
                    result.keysize = dkimcheck.keysize
                    if record_valid:
                        result.valid = True
                        if record_domain == hdr_from_domain or record_domain.endswith(f'.{hdr_from_domain}') \
                                or hdr_from_domain.endswith(f'.{record_domain}'):
                            result.is_authordomain = True
                            result.dkimval = DKIM_PASS
                            result.dkimmsg = result.saval = DKIM_PASS_AUTHOR
                            result.dkimdomain = record_domain
                            result.selector = record_selector
                            break  # highest level of trust, finish evaluation
                        elif not result.is_authordomain and suspect.from_domain and \
                                (record_domain == env_from_domain or record_domain.endswith(f'.{env_from_domain}')):
                            result.is_senderdomain = True
                            result.dkimval = DKIM_PASS
                            result.dkimmsg = result.saval = DKIM_PASS_SENDER
                            result.dkimdomain = record_domain
                            result.selector = record_selector
                        elif not result.is_authordomain and not result.is_senderdomain:
                            result.dkimmsg = result.dkimval = DKIM_PASS
                            result.dkimdomain = record_domain
                            result.selector = record_selector
                    elif not result.valid and result.dkimval != DKIM_PASS:  # don't set to fail if we already have a pass
                        result.dkimval = DKIM_FAIL
                        result.dkimdomain = record_domain
                        result.selector = record_selector
                        if result.keysize == 0:
                            result.dkimmsg = f'no key {result.selector}._domainkeys.{result.dkimdomain}'
                        elif result.keysize < dkimcheck.minkey:
                            result.dkimmsg = f'keysize {result.keysize}b {result.selector}._domainkeys.{result.dkimdomain}'
                        else:
                            result.dkimmsg = 'validation failed'
                    self.logger.debug(f"{suspect.id}: DKIM idx={i} valid={result.valid} domain={record_domain} selector={record_selector} authordomain={result.is_authordomain} senderdomain={result.is_senderdomain} keysize={result.keysize}")
                except dkim.DKIMException as de:
                    if result.dkimval != DKIM_PASS:  # this exception is only a problem if we do not already have a pass
                        self.logger.warning(f'{suspect.id} DKIM validation failed idx={i} domain={record_domain} selector={record_selector}: {str(de)}')
                        dkimexc = True
                        if not result.dkimdomain and record_domain:
                            result.dkimdomain = record_domain
                        result.dkimmsg = 'validaton failed'
                    else:
                        self.logger.debug(f'{suspect.id} DKIM validation failed after {DKIM_PASS} idx={i} domain={record_domain} selector={record_selector}: {str(de)}')
            
            if dkimexc:
                if result.dkimval != DKIM_PASS:
                    result.dkimval = DKIM_PERMFAIL
                debugdumpdir = self.config.get(self.section, 'debugdumpdir')
                if debugdumpdir:
                    filename = os.path.join(debugdumpdir, f'{suspect.id}.eml')
                    with open(filename, 'wb') as f:
                        f.write(suspect.get_source())
                    self.logger.warning(f'{suspect.id} DKIM validation failed, dumped original source to {filename}')
                    
                    filename = os.path.join(debugdumpdir, f'{suspect.id}.dkimsource.eml')
                    with open(filename, 'wb') as f:
                        f.write(source)
                    self.logger.warning(f'{suspect.id} DKIM validation failed, dumped DKIM source to {filename}')
        except dkim.MessageFormatError as e:
            result.dkimval = DKIM_NEUTRAL
            result.dkimmsg = 'message format error'
            self.logger.warning(f'{suspect.id} DKIM validation failed: Message format error: {str(e)}')
            suspect.set_tag('DKIMVerify.skipreason', 'message error')
        except (TimeoutError, dnsquery.DNS_TIMEOUT) as e:
            result.dkimval = DKIM_TEMPFAIL
            result.dkimmsg = 'timeout error'
            self.logger.warning(f'{suspect.id} DKIM validation failed due to: {str(e)}')
            suspect.set_tag('DKIMVerify.skipreason', 'dns error')
        except NameError as e:
            result.dkimmsg = 'internal error'
            self.logger.warning(f'{suspect.id} DKIM validation failed due to missing dependency: {str(e)}')
            suspect.set_tag('DKIMVerify.skipreason', 'plugin error')
        except Exception as e:
            result.dkimmsg = 'validation error'
            self.logger.warning(f'{suspect.id} DKIM validation failed: {e.__class__.__name__}: {str(e)}')
            self.logger.debug(f'{suspect.id} {traceback.format_exc()}')
            suspect.set_tag('DKIMVerify.skipreason', 'plugin error')
            
        return result
        
    
    def examine(self, suspect:Suspect):
        if suspect.get_tag("DKIMVerify.result") is not None:
            suspect.debug(f"{suspect.id} DKIM already validated, skip further processing")
            return DUNNO
        
        suspect.set_tag("DKIMVerify.result", DKIM_SKIP)
        if not DKIMPY_AVAILABLE:
            suspect.debug(f"{suspect.id} dkimpy not available, can not check DKIM")
            suspect.set_tag('DKIMVerify.skipreason', 'dkimpy library not available')
            return DUNNO

        hdr_from_domain = extract_from_domain(suspect)
        if not hdr_from_domain:
            self.logger.debug(f'{suspect.id} DKIM Verification skipped, no header from address')
            suspect.set_tag("DKIMVerify.skipreason", 'no header from address')
            return DUNNO

        self.skiplist.filename = self.config.get(self.section, 'skiplist')
        skiplist = self.skiplist.get_list()
        if hdr_from_domain in skiplist:
            self.logger.debug(f'{suspect.id} DKIM Verification skipped, sender domain skiplisted')
            suspect.set_tag("DKIMVerify.skipreason", 'sender domain skiplisted')
            return DUNNO

        taglist = self.config.getlist(self.section, 'skip_on_tag')
        skip_tag = check_skip_on_tag(suspect, taglist)
        if skip_tag is not None:
            value = suspect.get_tag(skip_tag)
            suspect.set_tag("DKIMVerify.skipreason", f'skip on tag {skip_tag}={value}')
            self.logger.debug(f'{suspect.id} DKIM Verification skipped, tag {skip_tag}={value}')
            return DUNNO

        dkimhdrs = suspect.get_message_rep().get_all('dkim-signature')
        if not dkimhdrs:
            self.logger.debug(f'{suspect.id} DKIM Verification skipped, no dkim-signature header found')
            suspect.set_tag('DKIMVerify.skipreason', 'not dkim signed')
            suspect.set_tag("DKIMVerify.result", DKIM_NONE)
            suspect.write_sa_temp_header(SAHEADER_DKIM, DKIM_NONE)
            result_header = self.config.get(self.section, 'result_header')
            if result_header:
                suspect.add_header(result_header, DKIM_NONE)
            suspect.debug("No dkim signature header found")
            return DUNNO
        
        result = self._eval_dkim(suspect, dkimhdrs, hdr_from_domain)

        # also needed e.g. in dmarc
        suspect.set_tag("DKIMVerify.sigvalid", result.valid)
        suspect.set_tag("DKIMVerify.result", result.dkimval)
        suspect.set_tag("DKIMVerify.dkimdomain", result.dkimdomain)
        suspect.set_tag("DKIMVerify.dkimdomaini", result.record_domaini)
        suspect.set_tag("DKIMVerify.selector", result.selector)
        suspect.set_tag("DKIMVerify.sigvalidauthor", result.is_authordomain)
        suspect.set_tag("DKIMVerify.sigvalidsender", result.is_senderdomain)
        suspect.set_tag("DKIMVerify.dkimmsg", result.dkimmsg)
        suspect.set_tag("DKIMVerify.keysize", result.keysize)
        suspect.write_sa_temp_header(SAHEADER_DKIM, result.saval or result.dkimval)
        result_header = self.config.get(self.section, 'result_header')
        if result_header:
            suspect.add_header(result_header, result.saval or result.dkimval)
        if self.config.getboolean(self.section, 'create_received_dkim'):
            rcvddkimhdr = self._create_received_dkim(result)
            suspect.add_header('Received-DKIM', rcvddkimhdr, immediate=True)
        self.logger.debug(f'{suspect.id} DKIM validation complete: valid={result.valid} domain={result.dkimdomain} selector={result.selector} keysize={result.keysize} result={result.saval}')
        
        action = DUNNO
        message = None
        if not result.valid:
            client_info = suspect.get_client_info(self.config)
            if client_info:
                helo, clientip, revdns = client_info
                do_reject = self._check_protocol(clientip)
                if do_reject:
                    if result.dkimval==DKIM_TEMPFAIL:
                        action = string_to_actioncode(self.config.get(self.section, 'on_tempfail'))
                        msg = 'temporarily failed to evaluate DKIM signature'
                    elif result.keysize == 0:
                        action = string_to_actioncode(self.config.get(self.section, 'on_nokey'))
                        msg = f'failed to evaluate DKIM signature: {result.dkimmsg}'
                    else:
                        action = string_to_actioncode(self.config.get(self.section, 'on_fail'))
                        msg = f'failed to evaluate DKIM signature: {result.dkimmsg}'
                    if action != DUNNO:
                        message = msg
        return action, message

    def lint(self):
        all_ok = self.check_config()

        if not DKIMPY_AVAILABLE:
            print("ERROR: Missing dependency: dkimpy https://launchpad.net/dkimpy")
            all_ok = False
        
        if not PYNACL_AVAILABLE:
            print("WARNING: Missing dependency: pynacl (not all DKIM signatures will be verified correctly)")

        if not dnsquery.DNSQUERY_EXTENSION_ENABLED:
            print("ERROR: Missing dependency: no supported DNS libary found: pydns or dnspython")
            all_ok = False
        
        strip_subject_rgx = self.config.get(self.section, 'strip_subject_rgx')
        if strip_subject_rgx:
            try:
                re.compile(strip_subject_rgx, re.I)
            except Exception as e:
                print(f'ERROR: failed to compile regex {strip_subject_rgx} due to {e.__class__.__name__}: {str(e)}')
                all_ok = False

        return all_ok


# test:
# plugdummy.py -p ...  domainauth.DKIMSignPlugin -s <sender> -o canonicalizeheaders:relaxed -o canonicalizebody:simple -o signbodylength:False
# cat /tmp/fuglu_dummy_message_out.eml | swaks -f <sender>  -s <server>
# -au <username> -ap <password> -4 -p 587 -tls -d -  -t
# <someuser>@gmail.com


class DKIMRcvdPlugin(ScannerPlugin):
    """
If DKIMVerify plugin is not run in this instance of Fuglu, use this plugin to extract a
"Received-DKIM" header (a custom header in the style of Received-SPF but for DKIM verification)
created by a Fuglu/Spam filter running on a previous system.
Set create_received_dkim in DKIMVerify plugin config to write such a header. It'll write a header such as:
Received-DKIM: pass (firsthost.fuglu.org: some status message) key1=value1;key2=value2
To enable reading set received_dkim_header_receiver in DKIMRcvdPlugin config to the hostname/domain of the
server writing the header, e.g. in this case firsthost.fuglu.org or .fuglu.org.
The hostname is always read recursively, e.g. .fuglu.org would also match otherhost.fuglu.org
    """
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'received_dkim_header_receiver': {
                'default': '',
                'description': 'if dkim verify plugin is not run locally, use received-dkim header with receiver field value in given domain name. leave empty to not parse received-dkim header'
            },
        }
    
    
    def examine(self, suspect):
        rcvddkimreceiver = self.config.get(self.section, 'received_dkim_header_receiver')
        if not rcvddkimreceiver:
            self.logger.debug(f'{suspect.id} received_dkim_header_receiver not defined')
            return DUNNO
        
        msgrep = suspect.get_message_rep()
        rcvddkim_all = msgrep.get_all('Received-DKIM', [])
        for rcvddkim in rcvddkim_all:
            try:
                rcvddkim = suspect.decode_msg_header(rcvddkim, logid=suspect.id)
                rcvddkimstatus, fields, expl = parse_received_xxx(rcvddkim)
                receiver = fields.get('receiver')
                if rcvddkimstatus and receiver and receiver.lower().endswith(rcvddkimreceiver.lower()):
                    rcvddkimstatus = rcvddkimstatus.lower()
                    if rcvddkimstatus in [DKIM_PASS_SENDER, DKIM_PASS_AUTHOR]:
                        self.logger.debug(f'{suspect.id} rewriting DKIM status from {rcvddkimstatus} to {DKIM_PASS}')
                        dkimval = DKIM_PASS
                    else:
                        dkimval = rcvddkimstatus
                    
                    suspect.set_tag("DKIMVerify.sigvalid", rcvddkimstatus in [DKIM_PASS, DKIM_PASS_AUTHOR, DKIM_PASS_SENDER])
                    suspect.set_tag("DKIMVerify.result", dkimval)
                    suspect.set_tag("DKIMVerify.dkimdomain", fields.get('dkimdomain'))
                    suspect.set_tag("DKIMVerify.dkimdomaini", fields.get('dkimdomaini'))
                    suspect.set_tag("DKIMVerify.selector", fields.get('selector'))
                    suspect.set_tag("DKIMVerify.dkimmsg", expl)
                    suspect.write_sa_temp_header(SAHEADER_DKIM, rcvddkimstatus)
                    break
                elif rcvddkim:
                    self.logger.debug(f'{suspect.id} failed to get status from received-dkim header. status={rcvddkimstatus} receiver={receiver} received-dkim={rcvddkim}')
                elif not rcvddkim:
                    self.logger.debug(f'{suspect.id} not a valid received-dkim header {rcvddkim}')
            except Exception as e:
                self.logger.error(f'{suspect.id} failed to parse received-dkim header "{rcvddkim}" due to {e.__class__.__name__}: {str(e)}')
        return DUNNO


class DKIMSignPlugin(ScannerPlugin):
    """
Add DKIM Signature to outgoing mails

Setting up your keys:

::

    mkdir -p /etc/fuglu/dkim
    domain=example.com
    openssl genrsa -out /etc/fuglu/dkim/${domain}.key 1024
    openssl rsa -in /etc/fuglu/dkim/${domain}.key -out /etc/fuglu/dkim/${domain}.pub -pubout -outform PEM
    # print out the DNS record:
    echo -n "default._domainkey TXT  \\"v=DKIM1; k=rsa; p=" ; cat /etc/fuglu/dkim/${domain}.pub | grep -v 'PUBLIC KEY' | tr -d '\\n' ; echo ";\\""


If fuglu handles both incoming and outgoing mails you should make sure that this plugin is skipped for incoming mails.

Please install dkimpy and not pydkim as mandatory dependency to use this plugin.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'privatekeyfile': {
                'description': "Location of the private key file. supports standard template variables plus additional ${header_from_domain} which extracts the domain name from the From: -Header",
                'default': "${confdir}/dkim/${header_from_domain}.key",
            },

            'canonicalizeheaders': {
                'description': "Type of header canonicalization (simple or relaxed)",
                'default': "relaxed",
            },

            'canonicalizebody': {
                'description': "Type of body canonicalization (simple or relaxed)",
                'default': "relaxed",
            },

            'selector': {
                'description': 'selector to use when signing, supports templates. besides all suspect items variable header_from_domain is supported',
                'default': 'default',
            },

            'signheaders': {
                'description': 'comma separated list of headers to sign. empty string=sign all headers',
                'default': 'From,Reply-To,Subject,Date,To,CC,Resent-Date,Resent-From,Resent-To,Resent-CC,In-Reply-To,References,List-Id,List-Help,List-Unsubscribe,List-Subscribe,List-Post,List-Owner,List-Archive',
            },

            'signbodylength': {
                'description': 'include l= tag in dkim header',
                'default': 'False',
            },
        }

    def __str__(self):
        return "DKIM Sign"

    def examine(self, suspect):
        if not DKIMPY_AVAILABLE:
            suspect.debug("dkimpy not available, can not sign DKIM")
            self.logger.error(f'{suspect.id} DKIM signing skipped - missing dkimpy library')
            return DUNNO

        message = suspect.get_source(newline=b'\r\n')
        header_from_domain = extract_from_domain(suspect)
        if header_from_domain is None:
            self.logger.debug(f"{suspect.id} Failed to extract From-header domain for DKIM signing")
            return DUNNO

        addvalues = dict(header_from_domain=header_from_domain)
        selector = apply_template(self.config.get(self.section, 'selector'), suspect, addvalues)
        privkeyfile = apply_template(self.config.get(self.section, 'privatekeyfile'), suspect, addvalues)
        if not os.path.isfile(privkeyfile):
            self.logger.debug(f"{suspect.id}: DKIM signing failed for domain {header_from_domain}, private key not found: {privkeyfile}")
            return DUNNO

        with open(privkeyfile, 'br') as f:
            privkeycontent = f.read()

        canH = dkim.Simple
        if self.config.get(self.section, 'canonicalizeheaders').lower() == 'relaxed':
            canH = dkim.Relaxed
        canB = dkim.Simple
        if self.config.get(self.section, 'canonicalizebody').lower() == 'relaxed':
            canB = dkim.Relaxed
        canon = (canH, canB)
        headerconfig = self.config.get(self.section, 'signheaders')
        if headerconfig is None or headerconfig.strip() == '':
            inc_headers = None
        else:
            inc_headers = headerconfig.strip().split(',')

        blength = self.config.getboolean(self.section, 'signbodylength')

        dkimhdr = dkim.sign(message, force_bString(selector), force_bString(header_from_domain), privkeycontent,
                            canonicalize=canon, include_headers=inc_headers, length=blength,
                            logger=suspect.get_tag('debugfile'))
        if dkimhdr.startswith(b'DKIM-Signature: '):
            dkimhdr = dkimhdr[16:]
        # dkim.sign provides a properly folded header. we trust it's valid.
        suspect.add_header('DKIM-Signature', force_uString(dkimhdr), immediate=True, raw=True)
        return DUNNO

    def lint(self):
        all_ok = self.check_config()

        if not DKIMPY_AVAILABLE:
            print("Missing dependency: dkimpy https://launchpad.net/dkimpy")
            all_ok = False
        if not dnsquery.DNSQUERY_EXTENSION_ENABLED:
            print("Missing dependency: no supported DNS libary found. pydns or dnspython")
            all_ok = False

        # if privkey is a filename (no placeholders) check if it exists
        privkeytemplate = self.config.get(self.section, 'privatekeyfile')
        if '{' not in privkeytemplate and not os.path.exists(privkeytemplate):
            print("Private key file %s not found" % privkeytemplate)
            all_ok = False

        return all_ok


class DKIMStripPlugin(ScannerPlugin):
    """
    This plugin removes previous DKIM headers if subject was changed
    """
    
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'senderdomains': {
                'default': '',
                'description': 'only strip specific header sender domains. list comma separated.',
            },
            'recipientdomains': {
                'default': '',
                'description': 'only strip specific envelope recipient domains. list comma separated.',
            },
            'verbose': {
                'default': 'False',
                'description': 'be extra verbose'
            }
        }
    
    
    def __str__(self):
        return "DKIM Strip"
    
    
    def examine(self, suspect):
        verbose = self.config.getboolean(self.section, 'verbose')
        origsubj = suspect.get_tag('origsubj')
        if origsubj is None:
            if verbose:
                self.logger.debug(f'{suspect.id} subject unaltered (no origsubj tag)')
            return DUNNO
        
        hdr_from_domain = None
        hdr_from_address = suspect.parse_from_type_header(header='From', validate_mail=True)
        if hdr_from_address and hdr_from_address[0] and hdr_from_address[0][1]:
            hdr_from_domain = domain_from_mail(hdr_from_address[0][1])
        if not hdr_from_domain:
            self.logger.debug(f'{suspect.id} No From header address found')
            return DUNNO
        
        recipientdomains = self.config.getlist(self.section, 'recipientdomains')
        if suspect.to_domain not in recipientdomains:
            if verbose:
                self.logger.debug(f'{suspect.id} {suspect.to_domain} not in {recipientdomains}')
            return DUNNO
        
        senderdomains = self.config.getlist(self.section, 'senderdomains')
        if hdr_from_domain.lower() not in senderdomains:
            if verbose:
                self.logger.debug(f'{suspect.id} {hdr_from_domain} not in {senderdomains}')
            return DUNNO
            
        subject = suspect.get_header('subject')
        if origsubj != subject:
            rm = suspect.remove_headers_from_source({'DKIM-Signature'})
            if rm:
                self.logger.info(f'{suspect.id} removed dkim headers')
            elif verbose:
                self.logger.debug(f'{suspect.id} no dkim headers')
        elif verbose:
            self.logger.debug(f'{suspect.id} subject unaltered: origsubj={origsubj} subject={subject}')
        return DUNNO
    
    
    def lint(self):
        ok = self.check_config()
        if ok:
            recipientdomains = self.config.getlist(self.section, 'recipientdomains')
            if not recipientdomains:
                print('WARNING: no recipient domains specified. this plugin will do nothing.')
            senderdomains = self.config.getlist(self.section, 'senderdomains')
            if not senderdomains:
                print('WARNING: no sender domains specified. this plugin will do nothing.')
        return ok


class NetworkList(FileList):
    def _parse_lines(self, lines):
        lines = super()._parse_lines(lines)
        return [ipaddress.ip_network(x, False) for x in lines]

    def is_listed(self, addr):
        try:
            ipaddr = ipaddress.ip_address(addr)
            for net in self.get_list():
                if ipaddr in net:
                    return True
        except ValueError:
            pass
        return False


class SPFPlugin(ScannerPlugin, BasicMilterPlugin, BMPMailFromMixin, BMPRCPTMixin, BMPEOBMixin):
    """
    =====================
    = Milter RCPT stage =
    =====================
    This plugin performs SPF validation using the pyspf module https://pypi.python.org/pypi/pyspf/
    by default, it just logs the result (test mode)

    to enable actual rejection of messages, add a config option on_<resulttype> with a valid postfix action. eg:

    on_fail = REJECT

    on_{result} = ...
    valid {result} types are: 'pass', 'permerror', 'fail', 'temperror', 'softfail', 'none', and 'neutral'
    you probably want to define REJECT for fail and softfail


    operation mode examples
    -----------------------
    I want to reject all hard fails and accept all soft fails (case 1):
      - do not set domain_selective_spf_file
      - set selective_softfail to False
      - set on_fail to REJECT and on_softfail to DUNNO

    I want to reject all hard fails and all soft fails (case 2):
      - do not set domain selective_spf_file
      - set selective_softfail to False
      - set on_fail to REJECT and on_softfail to REJECT

    I only want to reject select hard and soft fails (case 3):
      - set a domain_selective_spf_file and list the domains to be tested
      - set selective_softfail to False
      - set on_fail to REJECT and on_softfail to REJECT

    I want to reject all hard fails and only selected soft fails (case 4):
      - set a domain_selective_spf_file and list the domains to be tested for soft fail
      - set selective_softfail to True
      - set on_fail to REJECT and on_softfail to REJECT

    I want to reject select hard fails and accept all soft fails (case 5):
      - set a domain selective_spf_file and list the domains to be tested for hard fail
      - set selective_softfail to False
      - set on_fail to REJECT and on_softfail to DUNNO

    ==========================
    = NON-Milter stage (EOM) =
    ==========================
    This plugin checks the SPF status and sets tag 'SPF.status' to one of the official states 'none', 'pass', 'fail',
    'softfail, 'neutral', 'permerror', 'temperror', or 'skipped' if the SPF check could not be peformed.
    Tag 'SPF.explanation' contains a human-readable explanation of the result.
    Additional information to be used by SA plugin is added

    The plugin does not take any action based on the SPF test result since. Other plugins might use the SPF result
    in combination with other factors to take action (for example a "DMARC" plugin could use this information)

    However, if mark_milter_check=True then the message is marked as spam if the milter stage
    check would reject this (fail or softfail). This feature is to avoid rejecting at milter stage
    but mark later in post-queue mode as spam.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.check_cache = Cache()

        self.requiredvars = {
            'ip_whitelist_file': {
                'default': '',
                'description': 'file containing a list of IP adresses or CIDR ranges to be exempted from SPF checks. 127.0.0.0/8 is always exempted',
            },
            'domain_whitelist_file': {
                'default': '',
                'description': 'if this is non-empty, all except sender domains in this file will be checked for SPF. define exceptions by prefixing with ! (e.g. example.com !foo.example.com). define TLD wildcards using * (e.g. example.*)',
            },
            'domain_selective_spf_file': {
                'default': '',
                'description': 'if this is non-empty, only sender domains in this file will be checked for SPF. define exceptions by prefixing with ! (e.g. example.com !foo.example.com). define TLD wildcards using * (e.g. example.*)',
            },
            'ip_selective_spf_file': {
                'default': '',
                'description': 'if this is non-empty, only sender IPs in this file will be checked for SPF. If IP also whitelisted, this is ignored: no check. This has precedence over domain_selective_spf_file',
            },
            'selective_softfail': {
                'default': 'False',
                'description': 'evaluate all senders for hard fails (unless listed in domain_whitelist_file) and only evaluate softfail for domains listed in domain_selective_spf_file',
            },
            'check_subdomain': {
                'default': 'False',
                'description': 'apply checks to subdomain of whitelisted/selective domains',
            },
            'dbconnection': {
                'default': '',
                'description': 'SQLAlchemy Connection string, e.g. mysql://root@localhost/spfcheck?charset=utf8. Leave empty to disable SQL lookups',
            },
            'domain_sql_query': {
                'default': "SELECT check_spf from domain where domain_name=:domain",
                'description': 'get from sql database :domain will be replaced with the actual domain name. must return field check_spf',
            },
            'on_fail': {
                'default': 'DUNNO',
                'description': 'Action for SPF fail. (DUNNO, DEFER, REJECT)',
            },
            'on_fail_dunnotag': {
                'default': '',
                'description': 'If Suspect/Session tag is set, return DUNNO on fail',
            },
            'on_softfail': {
                'default': 'DUNNO',
                'description': 'Action for SPF softfail. (DUNNO, DEFER, REJECT)',
            },
            'on_softfail_dunnotag': {
                'default': '',
                'description': 'If Suspect/Session tag is set, return DUNNO on softfail',
            },
            'messagetemplate': {
                'default': 'SPF ${result} for domain ${from_domain} from ${client_address} : ${explanation}',
                'description': 'reject message template for policy violators'
            },
            'max_lookups': {
                'default': '10',
                'description': 'maximum number of lookups (RFC defaults to 10)',
            },
            'max_lookup_time': {
                'default': '20',
                'description': 'maximum time per DNS lookup (RFC defaults to 20 seconds)',
            },
            'strict_level': {
                'default': '1',
                'description': 'strictness of SPF lookup: 0: relaxed, 1: strict, 2: harsh',
            },
            'hoster_mx_exception': {
                'default': '.google.com .protection.outlook.com .mx.microsoft',
                'description': 'always consider pass if mail is sent from server with PTR ending in name specified, MX points to this server, and SPF record contains MX directive',
            },
            'hoster_include_exception': {
                'default': '', # '.protection.outlook.com' is a hot candidate
                'description': 'always consider pass if mail is sent from servers with PTR ending in name specified and SPF record contains include directive ending with name specified',
            },
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            },
            'temperror_retries': {
                'default': '3',
                'description': 'maximum number of retries on temp error',
            },
            'temperror_sleep': {
                'default': '3',
                'description': 'waiting interval between retries on temp error',
            },
            'mark_milter_check': {
                'default': 'False',
                'description': '(eom) check milter setup criterias, mark as spam on hit',
            },
            'skip_on_tag': {
                'default': 'welcomelisted.confirmed',
                'description': 'skip SPF check if any of the tags listed is set to specified value (examples: x,y==z,a!=b -> x must be True, y must be "z" and a must not be "b")',
            },
            'result_header': {
                'default': '',
                'description': 'write result to header of name specified here. leave empty to not write any header. deprecated, enable create_received_spf instead'
            },
            'create_received_spf': {
                'default': 'True',
                'description': 'create Received-SPF header'
            },
            'use_header_as_env_sender': {
                'default': '',
                'description': 'override envelope sender with value from one of these headers (if set - first occurrence wins) only works in after queue mode or milter header, eoh, eob stage'
            },
            'respect_dmarc': {
                'default': 'False',
                'description': 'if envelope sender domain has dmarc record, do not reject even on spf fail. only applies if run end of body.'
            }
        }

        self.ip_skiplist_loader = None
        self.selective_ip_loader = None

        self.selective_domain_loader = None
        self.domain_skiplist_loader = None

    def __check_domain(self, domain, listentry, check_subdomain):
        listed = False
        if listentry == domain:
            listed = True
        elif check_subdomain and domain.endswith(f'.{listentry}'):
            listed = True
        elif listentry.endswith('.*') and fnmatch.fnmatch(domain, listentry):
            listed = True
        elif check_subdomain and listentry.endswith('.*') and fnmatch.fnmatch(domain, f'*.{listentry}'):
            listed = True
        return listed

    def _domain_in_list(self, domain, domain_list, check_subdomain):
        listed = False

        # check if listed
        for item in domain_list:
            # skip exceptions
            if item.startswith('!'):
                continue
            listed = self.__check_domain(domain, item, check_subdomain)
            if listed:
                break

        # if previous loop said listed, check for exceptions
        if listed:
            for item in domain_list:
                if item.startswith('!'):
                    item = item[1:]
                    listed = not self.__check_domain(domain, item, check_subdomain)
                    if not listed:
                        break

        return listed

    def _check_domain_skiplist(self, domain: str):
        domain_skiplist_file = self.config.get(self.section, 'domain_whitelist_file').strip()
        if self.domain_skiplist_loader is None:
            if domain_skiplist_file and os.path.exists(domain_skiplist_file):
                self.domain_skiplist_loader = FileList(domain_skiplist_file, lowercase=True)
        if self.domain_skiplist_loader is not None:
            check_subdomain = self.config.getboolean(self.section, 'check_subdomain')
            return self._domain_in_list(domain, self.domain_skiplist_loader.get_list(), check_subdomain)
        return False

    def _check_domain_selective(self, from_domain: str, sessid: str = "<sessionid>", logmsgs: bool = True) -> bool:
        do_check = self.check_cache.get_cache(from_domain)
        if do_check is not None:
            if logmsgs:
                self.logger.debug(f"{sessid} domain {from_domain} in cache -> set do_check to {do_check}")
            return do_check

        do_check = None
        check_subdomain = self.config.getboolean(self.section, 'check_subdomain')

        domain_skiplist_file = self.config.get(self.section, 'domain_whitelist_file').strip()
        if domain_skiplist_file:
            skiplisted = self._check_domain_skiplist(from_domain)
            if skiplisted:
                do_check = False
            self.logger.debug(f"{sessid} domain {from_domain} skiplisted {skiplisted} -> set do_check to {do_check}")

        if do_check is None:
            selective_sender_domain_file = self.config.get(self.section, 'domain_selective_spf_file').strip()
            if self.selective_domain_loader is None:
                if selective_sender_domain_file and os.path.exists(selective_sender_domain_file):
                    self.selective_domain_loader = FileList(selective_sender_domain_file, lowercase=True)
            if self.selective_domain_loader is not None:
                if self._domain_in_list(from_domain, self.selective_domain_loader.get_list(), check_subdomain):
                    if logmsgs:
                        self.logger.debug(f"{sessid} domain {from_domain} in domain_selective_spf_file -> set do_check to True")
                    do_check = True
            # elif not selective_sender_domain_file:
            #    do_check = True

        if do_check is not False:
            dbconnection = self.config.get(self.section, 'dbconnection').strip()
            sqlquery = self.config.get(self.section, 'domain_sql_query')

            # use DBConfig instead of get_domain_setting
            if dbconnection and SQL_EXTENSION_ENABLED:
                cache = get_default_cache()
                if get_domain_setting(from_domain, dbconnection, sqlquery, cache, self.section, False, self.logger):
                    if logmsgs:
                        self.logger.debug(f"{sessid} domain {from_domain} has spf-dbsetting -> set do_check to True")
                    do_check = True

            elif dbconnection and not SQL_EXTENSION_ENABLED:
                self.logger.error(f'{sessid} dbconnection specified but sqlalchemy not available - skipping db lookup')

        if do_check is None:
            do_check = False

        self.check_cache.put_cache(from_domain, do_check)
        return do_check

    def _check_ip_skipisted(self, suspect, addr):
        if not addr:
            return False
        try:
            ipaddr = ipaddress.ip_address(addr)
        except ValueError:
            self.logger.warning(f'{suspect.id} not an ip address: {addr}')
            return False

        if not ipaddr.is_global:
            return True

        # check ip whitelist
        ip_skiplist_file = self.config.get(self.section, 'ip_whitelist_file', fallback='').strip()
        if self.ip_skiplist_loader is None:
            if ip_skiplist_file and os.path.exists(ip_skiplist_file):
                self.ip_skiplist_loader = NetworkList(ip_skiplist_file, lowercase=True)

        if self.ip_skiplist_loader is not None:
            return self.ip_skiplist_loader.is_listed(addr)
        return False

    def _check_ip_selective(self, addr):
        ip_selective_file = self.config.get(self.section, 'ip_selective_spf_file', fallback='').strip()
        if self.selective_ip_loader is None:
            if ip_selective_file and os.path.exists(ip_selective_file):
                self.selective_ip_loader = NetworkList(ip_selective_file, lowercase=True)

        if self.selective_ip_loader is not None:
            return self.selective_ip_loader.is_listed(addr)
        return False
    

    _re_mx = re.compile(r'\s\+?mx(?:/[0-9]{1,3})?\s')

    def _hoster_mx_exception(self, sessid: str, spfrecord:str, query: spf.query, hosters: tp.List[str], client_name: str) -> bool:
        """
        workaround / relaxed check for senders who are unable to use proper includes in their spf record
        """
        client_name = client_name.lower().rstrip('.')
        mxrec = None
        if not spfrecord:
            spfrecord = query.dns_spf(query.d)
        if not spfrecord:
            return False
        if not self._re_mx.search(spfrecord):
            return False
        for hoster in hosters:
            if client_name and client_name.endswith(hoster):
                try:
                    if mxrec is None:
                        mxrec = [mx[1].to_text(True) for mx in query.dns(query.d, 'MX')]

                    for mx in mxrec:
                        if mx.endswith(hoster):
                            self.logger.debug(f'{sessid} {query.d} got mx {mx} in hoster {hoster}')
                            return True
                except Exception as e:
                    self.logger.info(f'{sessid} failed to lookup mx record for domain {query.d}: {e.__class__.__name__}: {str(e)}')
        return False
    
    
    _re_include = re.compile(r'\s\+?include:(?P<inc>[a-z0-9.-]{3,256})?\s')
    def _hoster_include_exception(self, sessid: str, spfrecord:str, query: spf.query, hosters: tp.List[str], client_name: str) -> bool:
        """
        workaround / relaxed check for hosters too incompetent to list all their outgoing ips in their include
        """
        client_name = client_name.lower().rstrip('.')
        if not spfrecord:
            spfrecord = query.dns_spf(query.d)
        if not spfrecord:
            return False
        includes = self._re_include.findall(spfrecord)
        if not includes:
            return False
        else:
            for hoster in hosters:
                for include in includes:
                    if include.endswith(hoster) and client_name.endswith(hoster):
                        self.logger.debug(f'{sessid} {query.d} got include {include} in hoster {hoster}')
                        return True
        return False
            

    def _spf_lookup(self, sessid:str, query:spf.query, retries:int=3) -> tp.Tuple[str,str,str]:
        """
        save lookup of spf record. queries dns types txt and spf
        """
        spfrecord = None
        try:
            spfrecord = query.dns_spf(query.d)
            if not spfrecord and self.config.getint(self.section, 'strict_level') < 2:
                spfrecords = [t for t in query.dns_txt(query.d, 'SPF', ignore_void=True) if spf.RE_SPF.match(t)]
                if len(spfrecords)>1:
                    raise spf.PermError('Two or more type SPF spf records found.')
                if spfrecords:
                    spfrecord = spf.to_ascii(spfrecords[0])
            self.logger.debug(f'{sessid} domain={query.d} record={spfrecord}')
            result, _, explanation = query.check(spfrecord)
        except (spf.AmbiguityWarning, spf.PermError, spf.TempError) as e:
            exceptionmap = {
                'AmbiguityWarning': 'ambiguous',
                'PermError': 'permerror',
                'TempError': 'temperror',
            }
            result = exceptionmap.get(e.__class__.__name__, e.__class__.__name__)
            explanation = str(e)
            self.logger.debug(f'{sessid} domain={query.d} record is {result}: {explanation}')
        if result == 'temperror' and retries > 0:
            time.sleep(self.config.getint(self.section, 'temperror_sleep'))
            retries -= 1
            result, explanation, spfrecord = self._spf_lookup(sessid, query, retries=retries)
        elif result == 'temperror' and retries == 0:
            self.logger.debug(f'{sessid} result is temperror after multiple retries')
        return result, explanation, spfrecord

    def run_all_spf_tests(self,
                          sender: tp.Optional[str],
                          helo_name: tp.Optional[str],
                          client_address: tp.Optional[str],
                          client_name: tp.Optional[str],
                          sessid: str = "<sessionid>",
                          catch_exceptions: bool = True,
                          ) -> tp.Tuple[str, str]:
        """run spf check and apply hoster exceptions"""

        result = 'none'
        explanation = ''
        spfrecord = None
        strict_level = self.config.getint(self.section, 'strict_level')
        query = spf.query(client_address, sender, helo_name, strict=strict_level)
        try:
            retries = self.config.getint(self.section, 'temperror_retries')
            maxlookups = self.config.getint(self.section, 'max_lookups')
            spf.MAX_LOOKUP = maxlookups
            maxlookuptime = self.config.getint(self.section, 'max_lookup_time')
            spf.MAX_PER_LOOKUP_TIME = maxlookuptime
            spf.query.timeout = maxlookuptime
            if is_ipv6(client_address):
                # ugly hack, but only very few hosts have aaaa records and result in too many permerrors
                spf.MAX_VOID_LOOKUPS = maxlookups
            if client_address and sender:
                result, explanation, spfrecord = self._spf_lookup(sessid, query, retries=retries)
                self.logger.debug(f"{sessid} lookup result={result} record={spfrecord}")
            elif sender:
                self.logger.debug(f'{sessid} skipped SPF check for {sender} because client_address is empty')
            else:
                self.logger.debug(f'{sessid} skipped SPF check because sender is empty')
        except Exception as e:
            if "SERVFAIL" in str(e):  # this may be obsolete now
                # info level is enough
                self.logger.info(f'{sessid} failed to check SPF for {sender} due to: {e.__class__.__name__}: {str(e)}')
            else:
                self.logger.error(f'{sessid} failed to check SPF for {sender} due to: {e.__class__.__name__}: {str(e)}')
                self.logger.debug(f'{sessid} {traceback.format_exc()}')
            if not catch_exceptions:
                raise Exception(str(e)).with_traceback(e.__traceback__)

        hoster_mx_exception = self.config.getlist(self.section, 'hoster_mx_exception', separators=' ', lower=True)
        if spfrecord and hoster_mx_exception and result in ['fail', 'softfail'] and helo_name and helo_name.endswith(tuple(hoster_mx_exception)):
            self.logger.debug(f'{sessid} testing hoster mx exception')
            if self._hoster_mx_exception(sessid=sessid, spfrecord=spfrecord, query=query, hosters=hoster_mx_exception, client_name=client_name):
                self.logger.debug(f'{sessid} overriding {result} for {sender} due to hoster mx exception')
                result = 'pass'
                explanation = 'hoster mx permit'
        hoster_include_exception = self.config.getlist(self.section, 'hoster_include_exception', separators=' ', lower=True)
        if spfrecord and hoster_include_exception and result in ['fail', 'softfail'] and helo_name and helo_name.endswith(tuple(hoster_include_exception)):
            if self._hoster_include_exception(sessid=sessid, spfrecord=spfrecord, query=query, hosters=hoster_include_exception, client_name=client_name):
                self.logger.debug(f'{sessid} overriding {result} for {sender} due to hoster mx exception')
                result = 'pass'
                explanation = 'hoster include permit'
        return result, explanation
    
    
    def _create_received_spf(self, suspect:Suspect, result:str, explanation:str, client_ip:str, helo_name:str) -> str:
        """
        create received-spf header based on current spf check result
        """
        myname = get_outgoing_helo(self.config)
        fields = [f'receiver={myname}']
        sender_domain = '<>'
        if suspect.from_address:
            fields.append(f'envelope-from={suspect.from_address}')
            sender_domain = domain_from_mail(suspect.from_address)
        if client_ip:
            fields.append(f'client-ip={client_ip}')
        if helo_name:
            fields.append(f'helo={helo_name}')
            
        result_map = {
            'pass': 'Pass',
            'fail': 'Fail',
            'softfail': 'SoftFail',
            'neutral': 'Neutral',
            'none': 'None',
            'temperror': 'TempError',
            'permerror': 'PermError',
            'ambiguous': 'PermError',
            'unknown': 'PermError',
            'trusted': 'Pass',
            'local': 'Pass',
        }
        
        if not explanation and result == 'none':
            explanation = f'{sender_domain} does not designate permitted sender hosts'
        elif not explanation:
            explanation = 'unknown'
        elif explanation and ('\n' in explanation or '\r' in explanation):
            explanation = explanation.replace('\n', '<NEWLINE>').replace('\r', '<LINEBREAK>')

        if result not in result_map:
            self.logger.error(f"{suspect.id} -> spf result '{result}' not in result_map")
        headervalue = f'{result_map.get(result)} ({myname}: {explanation}) {"; ".join(fields)}'
        return headervalue
    
    def _get_from_address(self, suspect:Suspect) -> str:
        env_hdr = self.config.getlist(self.section, 'use_header_as_env_sender', resolve_env=True)
        for hdrname in env_hdr:
            value = suspect.get_header(hdrname)
            if value and is_email(value):
                self.logger.debug(f'{suspect.id} using address {value} from header {hdrname} as envelope sender override')
                return value
        return suspect.from_address
    
    def _get_clientinfo(self, suspect:Suspect) -> tp.Tuple[tp.Optional[str],tp.Optional[str],tp.Optional[str]]:
        clientinfo = suspect.get_client_info(self.config)
        if clientinfo is None:
            suspect.debug(f"{suspect.id} client info not available for SPF check")
            helo = ip = revdns = None
        else:
            helo, ip, revdns = clientinfo
        return ip, helo, revdns

    async def _run(self, suspect: Suspect):
        action = DUNNO
        message = None
        suspect.set_tag('SPF.status', SPF_SKIP)
        suspect.set_tag("SPF.explanation", 'no SPF check performed')

        if not HAVE_SPF:
            suspect.set_tag("SPF.explanation", 'missing dependency')
            self.logger.debug(f'{suspect.id} SPF Check skipped, missing dependency')
            return DUNNO, message
        
        taglist = self.config.getlist(self.section, 'skip_on_tag')
        skip_tag = check_skip_on_tag(suspect, taglist)
        if skip_tag is not None:
            value = suspect.get_tag(skip_tag)
            suspect.set_tag("SPF.explanation", f'skip on tag {skip_tag}={value}')
            self.logger.debug(f'{suspect.id} SPF Check skipped, tag {skip_tag}={value}')
            return DUNNO, message
        
        from_address = self._get_from_address(suspect)
        if not from_address:
            suspect.set_tag("SPF.explanation", 'skipped bounce')
            self.logger.debug(f'{suspect.id} SPF Check skipped, bounce')
            return DUNNO, message

        clientip, helo_name, clienthostname = self._get_clientinfo(suspect)
        if clientip is None:
            suspect.set_tag("SPF.explanation", 'could not extract client information')
            self.logger.debug(f"{suspect.id} SPF Check skipped, could not extract client information")
            return DUNNO, message

        clientip = force_uString(clientip)
        if self._check_ip_skipisted(suspect, clientip):
            suspect.set_tag("SPF.explanation", 'IP skiplisted')
            self.logger.debug(f'{suspect.id} SPF Check skipped, IP skiplist for IP={clientip}')
            return DUNNO, message
        
        sender = force_uString(from_address)
        senderdomain = domain_from_mail(sender).lower()

        ip_selective = self._check_ip_selective(clientip)
        domain_skiplisted = self._check_domain_skiplist(senderdomain)
        if domain_skiplisted and not ip_selective:
            suspect.set_tag("SPF.explanation", 'Domain skiplisted')
            self.logger.debug(f'{suspect.id} SPF Check skipped, Domain skiplist for sender {senderdomain}')
            return DUNNO, message
        elif domain_skiplisted and ip_selective:
            self.logger.info(f'{suspect.id} sender={senderdomain} is skiplisted, but ip={clientip} is selective')

        domain_selective = self._check_domain_selective(senderdomain)
        selective_softfail = self.config.getboolean(self.section, 'selective_softfail')
        check_selective = self.config.get(self.section, 'domain_selective_spf_file').strip() != ''
        do_check = False
        do_eval = False

        if not check_selective and not selective_softfail:  # case 1&2 check all domains
            self.logger.debug(f'{suspect.id} sender={senderdomain} check=all softfail=all selected=yes')
            do_check = True
        elif check_selective and not selective_softfail:  # case 3&5 check only select domains
            if ip_selective:
                self.logger.debug(f'{suspect.id} sender={senderdomain} check=select softfail=all selected=ip')
                do_check = True
            elif domain_selective:
                self.logger.debug(f'{suspect.id} sender={senderdomain} check=select softfail=all selected=dom')
                do_check = True
            else:
                self.logger.info(f'{suspect.id} sender={senderdomain} check=select softfail=all selected=no')
        elif check_selective and selective_softfail:  # case 4 check every domain, evaluate select softfails later
            self.logger.debug(f'{suspect.id} sender={senderdomain} check=select softfail=select selected=yes')
            do_check = True
            do_eval = True
        elif not check_selective and selective_softfail:  # this wouldn't make sense
            self.logger.warning(f'{suspect.id} sender={senderdomain} check=all softfail=select selected=no')
        else:
            self.logger.info(f'{suspect.id} sender={senderdomain} check=n/a softfail=n/a selected=no')

        result = 'none'
        explanation = 'SPF not checked'
        if do_check:
            helo_name = force_uString(helo_name or '')
            clienthostname = force_uString(clienthostname)
            result, explanation = self.run_all_spf_tests(sender=sender, helo_name=helo_name, client_address=clientip,
                                                         client_name=clienthostname, sessid=suspect.id, catch_exceptions=False)
        
        if self.config.getboolean(self.section, 'create_received_spf'):
            self.logger.debug(f"{suspect.id} -> write received spf for result: '{result}'")
            rcvdspfhdr = self._create_received_spf(suspect, result, explanation, clientip, helo_name)
            suspect.add_header('Received-SPF', rcvdspfhdr, immediate=True)

        if do_eval:
            if result == 'softfail' and not domain_selective:
                result = 'none'
                self.logger.debug(f'{suspect.id} resetting SPF softfail for non-selective domain {senderdomain}')

        suspect.set_tag("SPF.status", result)
        suspect.set_tag("spf.result", result)  # obsolete?
        suspect.set_tag("SPF.explanation", explanation)
        
        result_header = self.config.get(self.section, 'result_header') # deprecated
        if result_header:
            suspect.add_header(result_header, result)
        suspect.write_sa_temp_header(SAHEADER_SPF, result) # deprecated
        suspect.debug(f"SPF status: {result} ({explanation})")
        self.logger.info(f'{suspect.id} SPF status: client={clientip}, sender={sender}, h={helo_name} result={result} {explanation}')

        if self.config.has_option(self.section, f'on_{result}'):
            action = string_to_actioncode(self.config.get(self.section, f'on_{result}'))
            action = self._check_dunnotag(suspect, result, action)
        elif result != 'none':
            self.logger.debug(f'{suspect.id} no config option on_{result}')
        
        if action not in [DUNNO, ACCEPT]:
            if self.config.has_option(self.section, f'tmpl_{result}'):
                template = self.config.get(self.section, f'tmpl_{result}')
            else:
                template = self.config.get(self.section,'messagetemplate' )
            params = dict(result=result, explanation=explanation, client_address=clientip)
            message = apply_template(template, suspect, params)
        else:
            message = None
        
        if action not in [DUNNO, ACCEPT]:
            respect_dmarc = self.config.getboolean(self.section, 'respect_dmarc')
            if respect_dmarc and suspect.source: # we need msg source to extract header from domain
                header_from_domain = extract_from_domain(suspect)
                if header_from_domain:
                    timeout = self.config.getint(self.section, 'max_lookup_time')
                    dmarc_records = await query_dmarc(header_from_domain, timeout)
                    suspect.set_tag('SPF.dmarcrecords', {header_from_domain: dmarc_records})
                    if dmarc_records and len(dmarc_records) == 1:
                        self.logger.info(f'{suspect.id} found dmarc record for {header_from_domain}, overriding action={actioncode_to_string(action)} message={message}')
                        action = DUNNO
                        message = None

        return action, message

    def _check_dunnotag(self, suspect, result, action):
        on_softfail_dunnotag = self.config.get(self.section, 'on_softfail_dunnotag')
        if on_softfail_dunnotag and action != DUNNO and result == 'softfail':
            on_softfail_dunnotag_value = suspect.get_tag(on_softfail_dunnotag, None)
            if on_softfail_dunnotag_value:
                self.logger.info(f"{suspect.id} Change from softfail action to DUNNO/CONTINUE due to WL:{on_softfail_dunnotag_value}")
                action = DUNNO

        on_fail_dunnotag = self.config.get(self.section, 'on_fail_dunnotag')
        if on_fail_dunnotag and action != DUNNO and result == 'fail':
            on_fail_dunnotag_value = suspect.get_tag(on_fail_dunnotag, None)
            if on_fail_dunnotag_value:
                self.logger.info(f"{suspect.id} Change from fail action to DUNNO/CONTINUE due to WL:{on_fail_dunnotag_value}")
                action = DUNNO
        return action

    async def _run_milter(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], sender: tp.Union[str, bytes], recipient: tp.Union[str, bytes], state: str = None):
        suspect = Suspect(force_uString(sender), force_uString(recipient), '/dev/null', id=sess.id,
                          queue_id=sess.queueid, milter_macros=sess.milter_macros)
        suspect.clientinfo = force_uString(sess.heloname), force_uString(sess.addr), force_uString(sess.ptr)
        suspect.timestamp = sess.timestamp
        suspect.tags = sess.tags
        
        if state == asm.EOB:
            buffer = sess.buffer.getbuffer()
            suspect.set_source(buffer.tobytes())
        
        action, message = await self._run(suspect)

        if state == asm.EOB and action != DUNNO:
            action = self._eob_block_on_reject(suspect, action, message)
        
        for header, value in suspect.added_headers.items():
            self.logger.debug(f'{sess.id} adding header {header}: {value}')
            sess.add_header(header, value, immediate=True)
        for header, value in suspect.addheaders.items():
            self.logger.debug(f'{sess.id} adding header {header}: {value}')
            sess.add_header(header, value)
        if not suspect.added_headers and not suspect.addheaders:
            self.logger.debug(f'{sess.id} no spf headers to add')
        
        outaction = retcode2milter.get(action, None)
        if outaction is None:
            outaction = sm.TEMPFAIL
            message = "temporary SPF evaluation error"
            self.logger.error(f"{sess.id} Couldn't convert return from normal out:{action}({actioncode_to_string(action)}) to milter return!")
        sess.tags['SPF.mresponse'] = (outaction, message)
        return outaction, message

    def _eob_block_on_reject(self, suspect, action, message):
        if self.config.getboolean(self.section, 'mark_milter_check') and action != DUNNO:
            self.logger.warning(f"{suspect.id} Block because SPF would reject with: {message}")
            blockinfo = {'SPFCheck': message}
            self._blockreport(suspect, blockinfo, enginename='SPFPlugin')
            action = DUNNO
        return action

    async def examine(self, suspect: Suspect) -> tp.Union[int, tp.Tuple[int, tp.Optional[str]]]:
        action, message = await self._run(suspect)
        action = self._eob_block_on_reject(suspect, action, message)
        return action, message

    async def examine_mailfrom(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], sender: str) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return await self._run_milter(sess, sender, b'root@localhost', asm.MAILFROM)

    async def examine_rcpt(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        resp = sess.tags.get('SPF.mresponse')
        if resp and len(resp) == 2:  # reuse result from previous recipient. test result is purely sender based.
            return resp
        return  await self._run_milter(sess, sess.sender, recipient, asm.RCPT)

    async def examine_eob(self, sess: tp.Union[asm.MilterSession, sm.MilterSession]) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return  await self._run_milter(sess, sess.sender, sess.to_address, asm.EOB)

    def lint(self, state=EOM) -> bool:
        from fuglu.funkyconsole import FunkyConsole
        if state and state not in self.state and state != EOM:
            # not active in current state
            return True

        lint_ok = True
        fc = FunkyConsole()

        if not dnsquery.DNSQUERY_EXTENSION_ENABLED:
            print(fc.strcolor("ERROR: ", "red"), "no dns module installed")
            lint_ok = False

        if not HAVE_SPF:
            print(fc.strcolor("ERROR: ", "red"), "pyspf or dnspython module not installed - this plugin will do nothing")
            lint_ok = False

        if not self.check_config():
            print(fc.strcolor("ERROR: ", "red"), "Error checking config")
            lint_ok = False

        if self.config.has_option(self.section, 'skiplist'):
            print(fc.strcolor("WARNING: ", "yellow"), 'skiplist configured - this is obsolete, use ip_whitelist_file instead')

        import configparser
        for result in ["fail", "softfail", "none", "neutral", "pass", "permerror", "temperror"]:
            try:
                configaction = self.config.get(self.section, f'on_{result}')
                if configaction:
                    action = string_to_actioncode(configaction)
                    action = retcode2milter.get(action, None)
                    if not action:
                        lint_ok = False
                        print(fc.strcolor("ERROR: ", "red"), f"'on_{result}'-Action value {configaction}' not in allowed choices: 'DUNNO', 'DEFER', 'REJECT'")
            except configparser.NoOptionError:
                pass
            except Exception as e:
                lint_ok = False
                print(fc.strcolor("ERROR: ", "red"), f'failed to evaluate check result due to {e.__class__.__name__}: {str(e)}')

        domain_skiplist_file = self.config.get(self.section, 'domain_whitelist_file').strip()
        if domain_skiplist_file and not os.path.exists(domain_skiplist_file):
            print(fc.strcolor("WARNING: ", "yellow"), f"domain_whitelist_file {domain_skiplist_file} does not exist")
            lint_ok = False

        selective_sender_domain_file = self.config.get(self.section, 'domain_selective_spf_file').strip()
        if selective_sender_domain_file and not os.path.exists(selective_sender_domain_file):
            print(fc.strcolor("WARNING: ", "yellow"), f"domain_selective_spf_file {selective_sender_domain_file} does not exist")
            lint_ok = False

        if domain_skiplist_file and selective_sender_domain_file:
            print(fc.strcolor("WARNING: ", "yellow"),
                  'domain_whitelist_file and domain_selective_spf_file specified - whitelist '
                  'has precedence, will check all domains and ignore domain_selective_spf_file')

        ip_skiplist_file = self.config.get(self.section, 'ip_whitelist_file').strip()
        if ip_skiplist_file and not os.path.exists(ip_skiplist_file):
            print(fc.strcolor("WARNING: ", "yellow"), f"ip_whitelist_file {ip_skiplist_file} does not exist - IP whitelist is disabled")
            lint_ok = False

        sqlquery = self.config.get(self.section, 'domain_sql_query')
        dbconnection = self.config.get(self.section, 'dbconnection').strip()
        if not SQL_EXTENSION_ENABLED and dbconnection:
            print(fc.strcolor("WARNING: ", "yellow"), "SQLAlchemy not available, cannot use SQL backend")
            lint_ok = False
        elif not dbconnection:
            print(fc.strcolor("INFO: ", "blue"), "No DB connection defined. Disabling SQL backend")
        else:
            if not sqlquery.lower().startswith('select '):
                lint_ok = False
                print(fc.strcolor("ERROR: ", "red"), f"SQL statement must be a SELECT query, got {sqlquery.split()[0]} instead")
            if lint_ok:
                try:
                    conn = get_session(dbconnection)
                    conn.execute(text(sqlquery), {'domain': 'example.com'})
                except Exception as e:
                    lint_ok = False
                    print(fc.strcolor("ERROR: ", "red"), f'{e.__class__.__name__}: {str(e)}')
        
        strict_level = self.config.get(self.section, 'strict_level')
        try:
            strict_level = int(strict_level)
            strict_ok = (0 <= strict_level <= 2)
        except (TypeError, ValueError):
            strict_ok = False
        if not strict_ok:
            lint_ok = False
            print(fc.strcolor("ERROR: ", "red"), f"strict must be 0, 1 or 2, got {strict_level} instead")
        return lint_ok


class DMARCPlugin(IPProtoCheckMixin, ScannerPlugin):
    """
This plugin evaluates DMARC policy of the sender domain. If DMARC policy is violated and designates
reject or quarantine, message can be rejected or marked as spam.
This plugin depends on tags written by SPFPlugin and DKIMVerifyPlugin, so they must run beforehand.

Tags set:
  * dmarc.result result of DMARC evaluation

Requires python dmarc library
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        if DOMAINMAGIC_AVAILABLE:
            self.tldmagic = TLDMagic()
        else:
            self.tldmagic = None

        self.requiredvars = {
            'on_quarantine': {
                'default': 'DUNNO',
                'description': 'Action if DMARC disposition evaluates to "quarantine". Set to DUNNO if running in after-queue mode. Set to TAG to mark message as spam.',
            },
            'on_reject': {
                'default': 'DUNNO',
                'description': 'Action if DMARC disposition evaluates to "reject". Set to DUNNO if running in after-queue mode.',
            },
            'messagetemplate': {
                'default': 'DMARC disposition of ${header_from_domain} recommends rejection',
                'description': 'reject message template for policy violators'
            },
            'on_tempfail': {
                'default': 'DUNNO',
                'description': 'Action if DMARC record resulted in temporary DNS lookup. Set to DUNNO if running in after-queue mode, else DUNNO or DEFER.',
            },
            'on_permfail': {
                'default': 'DUNNO',
                'description': 'Action if DMARC record is syntactically wrong or multiple records found. Set to DUNNO if running in after-queue mode.',
            },
            'max_lookup_time': {
                'default': '20',
                'description': 'maximum time per DNS lookup',
            },
            'result_header': {
                'default': '',
                'description': 'write result to header of name specified here. leave empty to not write any header.'
            },
            'dispo_header': {
                'default': '',
                'description': 'write dispo to header of name specified here. leave empty to not write any header.'
            },
            'received_spf_header_receiver': {
                'default': '',
                'description': 'if spf plugin is not run locally, use received-spf header with receiver field value in given domain name. leave empty to not parse received-spf header'
            },
            'use_header_as_env_sender': {
                'default': '',
                'description': 'override envelope sender with value from one of these headers (if set - first occurrence wins)'
            },
        }

    def _get_dkim_result(self, suspect: Suspect) -> tp.Tuple[tp.Optional[dmarc.DKIMResult], tp.Optional[str], tp.Optional[str]]:
        value = suspect.get_tag("DKIMVerify.result")

        # unsigned should return None
        dkim_value_map = {
            DKIM_PASS: dmarc.DKIM_PASS,
            DKIM_PASS_AUTHOR: dmarc.DKIM_PASS,
            DKIM_PASS_SENDER: dmarc.DKIM_PASS,
            DKIM_FAIL: dmarc.DKIM_FAIL,
            DKIM_PERMFAIL: dmarc.DKIM_PERMFAIL,
            DKIM_TEMPFAIL: dmarc.DKIM_TEMPFAIL,
            DKIM_NEUTRAL: dmarc.DKIM_NEUTRAL,
            DKIM_POLICY: dmarc.DKIM_NEUTRAL,
        }
        if value is None or value not in dkim_value_map:
            dkim_result = dkim_domain = dkim_selector = None
        else:
            dkim_result = dmarc.DKIMResult(dkim_value_map.get(value))
            dkim_domain = suspect.get_tag("DKIMVerify.dkimdomain")
            dkim_selector = suspect.get_tag("DKIMVerify.selector")

        self.logger.debug(f'{suspect.id} dkim result={dkim_result} status={value} domain={dkim_domain} selector={dkim_selector}')
        return dkim_result, dkim_domain, dkim_selector
    
    def _get_spf_result(self, suspect:Suspect) -> dmarc.SPFResult:
        status = suspect.get_tag('SPF.status', None)
        if status is None:
            rcvdspfreceiver = self.config.get(self.section, 'received_spf_header_receiver')
            if rcvdspfreceiver:
                msgrep = suspect.get_message_rep()
                rcvdspf_all = msgrep.get_all('Received-SPF', [])
                for rcvdspf in rcvdspf_all:
                    try:
                        rcvdspf = suspect.decode_msg_header(rcvdspf, logid=suspect.id)
                        rcvdspfstatus, fields, expl = parse_received_xxx(rcvdspf)
                        receiver = fields.get('receiver')
                        if rcvdspfstatus and receiver and receiver.lower().endswith(rcvdspfreceiver.lower()):
                            status = rcvdspfstatus.lower()
                            suspect.set_tag('SPF.status', status)
                            break
                        elif rcvdspf:
                            self.logger.debug(f'{suspect.id} failed to get status from received-spf header. status={rcvdspfstatus} receiver={receiver} received-spf={rcvdspf}')
                        elif not rcvdspf:
                            self.logger.debug(f'{suspect.id} not a valid received-spf header: {rcvdspf}')
                    except Exception as e:
                        self.logger.error(f'{suspect.id} failed to parse received-spf header "{rcvdspf}" due to {e.__class__.__name__}: {str(e)}')

        # skipped, unknown, none should return None
        spf_value_map = {
            'pass': dmarc.SPF_PASS,
            'softfail': dmarc.SPF_FAIL,
            'fail': dmarc.SPF_FAIL,
            'neutral': dmarc.SPF_NEUTRAL,
            'temperror': dmarc.SPF_TEMPFAIL,
            'permerror': dmarc.SPF_PERMFAIL,
            'skip': dmarc.SPF_PASS, # if we skipped spf check previously we should consider it passed
        }
        if status is None or status not in spf_value_map:
            spf_result = None
        else:
            spf_result = dmarc.SPFResult(spf_value_map.get(status))
        self.logger.debug(f'{suspect.id} spf result={spf_result} status={status}')
        return spf_result

    def _mk_aspf(self, suspect:Suspect, spf_result:tp.Optional[dmarc.SPFResult]) -> tp.Optional[dmarc.SPF]:
        from_domain = suspect.from_domain
        env_headers = self.config.getlist(self.section, 'use_header_as_env_sender', resolve_env=True)
        if env_headers:
            for header in env_headers:
                value = suspect.get_header(header)
                if value and '@' in value:
                    from_domain = domain_from_mail(value)
                    self.logger.debug(f'{suspect.id} SPF override env domain={from_domain} from header {header}')
    
        if spf_result is None:
            aspf = None
        elif not from_domain: # bounce
            aspf = None
        else:
            aspf = dmarc.SPF(domain=from_domain, result=spf_result)
        return aspf

    def _mk_adkim(self, dkim_domain:str, dkim_result:tp.Optional[dmarc.DKIMResult], dkim_selector:str) -> tp.Optional[dmarc.DKIM]:
        if dkim_result is None:
            adkim = None
        else:
            adkim = dmarc.DKIM(domain=dkim_domain, result=dkim_result, selector=dkim_selector)
        return adkim

    def _do_dmarc_check(self, dmarc_record:str, header_from_domain:str, aspf:tp.Optional[dmarc.SPF], adkim:tp.Optional[dmarc.DKIM], suspectid:str, org_domain:str) -> tp.Tuple[dmarc.DMARCResult, dmarc.DMARCDisposition]:
        result = None
        dispo = None
        try:
            d = dmarc.DMARC()
            p = d.parse_record(record=dmarc_record, domain=header_from_domain, org_domain=org_domain)
            r = d.get_result(p, spf=aspf, dkim=adkim)
            result = r.result
            dispo = r.disposition
        except dmarc.RecordValueError as e:
            self.logger.info(f'{suspectid} invalid DMARC record for {header_from_domain}: "{dmarc_record}" value error: {str(e)}')
        except dmarc.RecordSyntaxError as e:
            self.logger.info(f'{suspectid} invalid DMARC record for {header_from_domain}: "{dmarc_record}" syntax error: {str(e)}')
        except ValueError:
            if aspf is not None:
                dbgaspf = f'{aspf.domain};{aspf.result}'
            else:
                dbgaspf = 'none'
            if adkim is not None:
                dbgadkim = f'{adkim.domain};{adkim.result};{adkim.selector}'
            else:
                dbgadkim = None
            self.logger.error(f'{suspectid} DMARC ValueError: header_from_domain={header_from_domain} aspf={dbgaspf} adkim={dbgadkim} dmarc_record={dmarc_record}')
        return result, dispo
    
    def _write_result(self, suspect:Suspect, value:str) -> None:
        suspect.set_tag('dmarc.result', value)
        suspect.write_sa_temp_header(SAHEADER_DMARC_RESULT, value)
        result_header = self.config.get(self.section, 'result_header')
        if result_header:
            suspect.add_header(result_header, value)
    
    def _write_dispo(self, suspect:Suspect, value:str) -> None:
        suspect.set_tag('dmarc.dispo', value)
        suspect.write_sa_temp_header(SAHEADER_DMARC_DISPO, value)
        result_header = self.config.get(self.section, 'dispo_header')
        if result_header:
            suspect.add_header(result_header, value)

    async def examine(self, suspect):
        if not DMARC_AVAILABLE:
            suspect.set_tag('dmarc.result', DMARC_UNAVAILABLE)
            self.logger.debug(f'{suspect.id} DMARC check skipped. dmarc library unavailable')
            return DUNNO

        header_from_domain = extract_from_domain(suspect)
        if not header_from_domain:
            self._write_result(suspect, DMARC_SKIP)
            self.logger.debug(f'{suspect.id} no valid domain found in From header')
            return DUNNO

        dispo = DMARC_UNAVAILABLE
        org_domain = None
        timeout = self.config.getfloat(self.section, 'max_lookup_time')
        if 'SPF.dmarcrecords' in suspect.tags and header_from_domain in suspect.tags['SPF.dmarcrecords']:
            # spf plugin may have looked up dmarc records before
            dmarc_records = suspect.tags['SPF.dmarcrecords'][header_from_domain]
        else:
            dmarc_records = await query_dmarc(header_from_domain, timeout)
        if dmarc_records is None:
            self.logger.debug(f'{suspect.id} failed to lookup dmarc record for header from domain {header_from_domain}')
            self._write_result(suspect, DMARC_TEMPFAIL)
            dispo = DMARC_TEMPFAIL
        else:
            dmarc_records_len = len(dmarc_records)
            if dmarc_records_len == 0 or dmarc_records_len > 1:
                # No valid records found, try Organizational Domain
                if self.tldmagic is not None:
                    domain = self.tldmagic.get_domain(header_from_domain)
                    if domain and domain != header_from_domain:
                        org_domain = domain
                        dmarc_records = await query_dmarc(org_domain, timeout)
                        if dmarc_records is None:
                            self.logger.debug(f'{suspect.id} failed to lookup dmarc record for org domain {org_domain}')
                            self._write_result(suspect, DMARC_TEMPFAIL)
                            dispo = DMARC_TEMPFAIL
                            dmarc_records_len = -1 # set to negative value to skip the following if/elif/elif block
                        else:
                            dmarc_records_len = len(dmarc_records)
            
            if dmarc_records_len == 0:
                self._write_result(suspect, DMARC_NONE)
                self.logger.debug(f'{suspect.id} no DMARC record found for domain {header_from_domain}')
                return DUNNO
            elif dmarc_records_len > 1:
                self._write_result(suspect, DMARC_RECORDFAIL)
                self.logger.debug(f'{suspect.id} DMARC check failed. too many records count={dmarc_records_len}')
                dispo = DMARC_RECORDFAIL
            elif dmarc_records_len == 1:
                spf_result = self._get_spf_result(suspect)
                dkim_result, dkim_domain, dkim_selector = self._get_dkim_result(suspect)
        
                aspf = self._mk_aspf(suspect, spf_result)
                adkim = self._mk_adkim(dkim_domain, dkim_result, dkim_selector)
                result, dispo = self._do_dmarc_check(dmarc_records[0], header_from_domain, aspf, adkim, suspect.id, org_domain)
                self.logger.debug(f'{suspect.id} dmarc eval for {header_from_domain} with result={result} and dispo={dispo} input spf={spf_result} dkim_result={dkim_result} dkim_domain={dkim_domain} dkim_selector={dkim_selector}')

                if result is None:
                    self._write_result(suspect, DMARC_RECORDFAIL)
                    dispo = DMARC_RECORDFAIL
                elif result == dmarc.POLICY_PASS:
                    self._write_result(suspect, DMARC_PASS)
                elif result == dmarc.POLICY_FAIL:
                    self._write_result(suspect, DMARC_FAIL)
        
        do_reject = False
        client_info = suspect.get_client_info(self.config)
        if client_info:
            helo, clientip, revdns = client_info
            do_reject = self._check_protocol(clientip)
        
        action = DUNNO
        msg = None
        if dispo == dmarc.POLICY_DIS_NONE:
            # explicitly set dispo none
            self._write_dispo(suspect, DMARC_NONE)
            
        elif dispo == dmarc.POLICY_DIS_REJECT:
            self._write_dispo(suspect, DMARC_REJECT)
            if do_reject:
                action = string_to_actioncode(self.config.get(self.section, 'on_reject'))
                msg = apply_template(self.config.get(self.section, 'messagetemplate'), suspect,
                                            dict(header_from_domain=header_from_domain))
            
        elif dispo == dmarc.POLICY_DIS_QUARANTINE:
            self._write_dispo(suspect, DMARC_QUARANTINE)
            act = self.config.get(self.section, 'on_quarantine')
            if act.upper() == 'TAG':
                self._spamreport(suspect, True, False, 'DMARC check evaluates to QUARANTINE', 0, enginename=None)
            elif do_reject:
                action = string_to_actioncode(act)
            msg = apply_template(self.config.get(self.section, 'messagetemplate'), suspect,
                                         dict(header_from_domain=header_from_domain))
        
        elif dispo == DMARC_TEMPFAIL:
            self._write_dispo(suspect, DMARC_NONE) # even if no dmarc result, set dispo=none for consistency
            if do_reject:
                action = string_to_actioncode(self.config.get(self.section, 'on_tempfail'))
                msg = f'failed to lookup dmarc record _dmarc.{header_from_domain}'
        
        elif dispo == DMARC_RECORDFAIL:
            self._write_dispo(suspect, DMARC_NONE) # even if no dmarc result, set dispo=none for consistency
            if do_reject:
                action = string_to_actioncode(self.config.get(self.section, 'on_permfail'))
                msg = f'invalid dmarc record on _dmarc.{header_from_domain}'
        
        message = msg if action != DUNNO else None
        return action, message

    def __str__(self):
        return "DMARC"

    def lint(self):
        all_ok = self.check_config()

        if not DMARC_AVAILABLE:
            print("ERROR: Missing dependency: dmarc")
            all_ok = False
        elif dmarc.__version__ < '1.1.0':
            print(f"ERROR: Outdated dependency: dmarc version must be at least 1.1.0 found {dmarc.__version__}")
            all_ok = False

        if not aiodnsquery.AIODNSQUERY_EXTENSION_ENABLED:
            print("ERROR: Missing dependency: no supported DNS libary found: pydns or dnspython")
            all_ok = False

        return all_ok


class DomainAuthPlugin(ScannerPlugin):
    """
    **EXPERIMENTAL**
    This plugin checks the header from domain against a list of domains which must be authenticated by DKIM and/or SPF.
    This is somewhat similar to DMARC but instead of asking the sender domain for a DMARC policy record this plugin allows you to force authentication on the recipient side.

    This plugin depends on tags written by SPFPlugin and DKIMVerifyPlugin, so they must run beforehand.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars = {
            'domainsfile': {
                'description': "File containing a list of domains (one per line) which must be DKIM and/or SPF authenticated",
                'default': "${confdir}/auth_required_domains.txt",
            },
            'failaction': {
                'default': 'DUNNO',
                'description': "action if the message doesn't pass authentication (DUNNO, REJECT)",
            },
            'rejectmessage': {
                'default': 'sender domain ${header_from_domain} must pass DKIM and/or SPF authentication',
                'description': "reject message template if running in pre-queue mode",
            },
        }
        self.logger = self._logger()
        self.filelist = FileList(filename=None, strip=True, skip_empty=True, skip_comments=True, lowercase=True)
        self.enginename = 'domainauth'

    def examine(self, suspect):
        self.filelist.filename = self.config.get(self.section, 'domainsfile')
        checkdomains = self.filelist.get_list()

        envelope_sender_domain = suspect.from_domain.lower()
        header_from_domain = extract_from_domain(suspect)
        if header_from_domain is None:
            return DUNNO

        if header_from_domain not in checkdomains:
            return DUNNO

        # TODO: do we need a tag from dkim to check if the verified dkim domain
        # actually matches the header from domain?
        dkimresult = suspect.get_tag('DKIMVerify.sigvalid', False)
        if dkimresult is True:
            return DUNNO

        # DKIM failed, check SPF if envelope senderdomain belongs to header
        # from domain
        spfresult = suspect.get_tag('SPF.status', 'unknown')
        if (envelope_sender_domain == header_from_domain or envelope_sender_domain.endswith(
                f'.{header_from_domain}')) and spfresult == 'pass':
            return DUNNO

        act = self.config.get(self.section, 'failaction')
        if act.upper() == 'TAG':
            self._spamreport(suspect, True, False, 'DomainAuth check evaluates to QUARANTINE', 0, enginename=None)
            action = DUNNO
        else:
            action = string_to_actioncode(act)
        values = dict(header_from_domain=header_from_domain)
        message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, values)
        return action, message

    def __str__(self):
        return "DomainAuth"

    def lint(self):
        allok = self.check_config() and self.lint_file()
        return allok

    def lint_file(self):
        filename = self.config.get(self.section, 'domainsfile')
        if not os.path.exists(filename):
            print("domains file %s not found" % filename)
            return False
        return True


class SpearPhishPlugin(ScannerPlugin):
    """Mark spear phishing mails as virus

    The spearphish plugin checks if the sender domain in the "From"-Header matches the envelope recipient Domain ("Mail
    from my own domain") but the message uses a different envelope sender domain. This blocks many spearphish attempts.

    Note that this plugin can cause blocks of legitimate mail , for example if the recipient domain is using a third party service
    to send newsletters in their name. Such services often set the customers domain in the 'From' header but use their own domains in the envelope for
    bounce processing. Use the 'Plugin Skipper' or any other form of whitelisting in such cases.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.filelist = FileList(strip=True, skip_empty=True, skip_comments=True, lowercase=True,
                                 additional_filters=None, minimum_time_between_reloads=30)

        self.requiredvars = {
            'domainsfile': {
                'default': '${confdir}/spearphish-domains',
                'description': 'Filename where we load spearphish domains from. One domain per line. If this setting is empty, the check will be applied to all domains.',
            },
            'virusenginename': {
                'default': 'Fuglu SpearPhishing Protection',
                'description': 'Name of this plugins av engine',
            },
            'virusname': {
                'default': 'TRAIT.SPEARPHISH',
                'description': 'Name to use as virus signature',
            },
            'virusaction': {
                'default': 'DEFAULTVIRUSACTION',
                'description': "action if spear phishing attempt is detected (DUNNO, REJECT, DELETE)",
            },
            'rejectmessage': {
                'default': 'threat detected: ${virusname}',
                'description': "reject message template if running in pre-queue mode and virusaction=REJECT",
            },
            'dbconnection': {
                'default': "mysql://root@localhost/spfcheck?charset=utf8",
                'description': 'SQLAlchemy Connection string. Leave empty to disable SQL lookups',
            },
            'domain_sql_query': {
                'default': "SELECT check_spearphish from domain where domain_name=:domain",
                'description': 'get from sql database :domain will be replaced with the actual domain name. must return boolean field check_spearphish',
            },
            'check_display_part': {
                'default': 'False',
                'description': "set to True to also check display part of From header (else email part only)",
            },
            'checkbounces': {
                'default': 'True',
                'description': 'disable this if you want to exclude mail with empty envelope sender (bounces, NDRs, OOO) from being marked as spearphish'
            },
        }

    # this looks like a duplicate of get_domain_setting from extensions.sql
    @deprecated
    def get_domain_setting(self, domain, dbconnection, sqlquery, cache, cachename, default_value=None, logger=None):
        if logger is None:
            logger = logging.getLogger('fuglu.plugin.domainauth.SpearPhishPlugin.sql')

        cachekey = f'{cachename}-{domain}'
        cached = cache.get_cache(cachekey)
        if cached is not None:
            logger.debug("got cached setting for %s" % domain)
            return cached

        settings = default_value

        try:
            session = get_session(dbconnection)

            # get domain settings
            dom = session.execute(text(sqlquery), {'domain': domain}).fetchall()

            if not dom and not dom[0] and len(dom[0]) == 0:
                logger.warning(
                    "Can not load domain setting - domain %s not found. Using default settings." % domain)
            else:
                settings = dom[0][0]

            session.close()

        except Exception as e:
            logger.error("Exception while loading setting for %s : %s %s" % (domain, e.__class__.__name__, str(e)))

        cache.put_cache(cachekey, settings)
        logger.debug("refreshed setting for %s" % domain)
        return settings

    def should_we_check_this_domain(self, suspect):
        domainsfile = self.config.get(self.section, 'domainsfile')
        if domainsfile.strip() == '':  # empty config -> check all domains
            return True

        if not os.path.exists(domainsfile):
            return False

        self.filelist.filename = domainsfile
        envelope_recipient_domain = suspect.to_domain.lower()
        checkdomains = self.filelist.get_list()
        if envelope_recipient_domain in checkdomains:
            return True

        dbconnection = self.config.get(self.section, 'dbconnection').strip()
        sqlquery = self.config.get(self.section, 'domain_sql_query')
        do_check = False
        # use DBConfig instead of get_domain_setting
        if dbconnection:
            cache = get_default_cache()
            cachename = self.section
            do_check = self.get_domain_setting(suspect.to_domain, dbconnection, sqlquery, cache, cachename, False,
                                               self.logger)
        return do_check

    def examine(self, suspect):
        if not self.should_we_check_this_domain(suspect):
            return DUNNO
        envelope_recipient_domain = suspect.to_domain.lower()
        envelope_sender_domain = suspect.from_domain.lower()
        if envelope_sender_domain == envelope_recipient_domain or envelope_sender_domain.endswith(
                f'.{envelope_recipient_domain}'):
            return DUNNO  # we only check the message if the env_sender_domain differs. If it's the same it will be caught by other means (like SPF)

        if not self.config.getboolean(self.section, 'checkbounces') and not suspect.from_address:
            return DUNNO

        header_from_domains = extract_from_domains(suspect)
        if header_from_domains is None:
            header_from_domains = []
        self.logger.debug(f'{suspect.id} checking domain {",".join(header_from_domains)} (source: From header address part)')

        if self.config.getboolean(self.section, 'check_display_part'):
            display_from_domain = extract_from_domain(suspect, get_display_part=True)
            if display_from_domain is not None and display_from_domain not in header_from_domains:
                header_from_domains.append(display_from_domain)
                self.logger.debug(f'{suspect.id} checking domain {display_from_domain} (source: From header display part)')

        actioncode = DUNNO
        message = None

        for header_from_domain in header_from_domains:
            if header_from_domain == envelope_recipient_domain:
                virusname = self.config.get(self.section, 'virusname')
                virusaction = self.config.get(self.section, 'virusaction')
                actioncode = string_to_actioncode(virusaction, self.config)

                logmsg = f'{suspect.id} spear phish pattern detected, env_rcpt_domain={envelope_sender_domain} env_sender_domain={envelope_sender_domain} header_from_domain={header_from_domain}'
                self.logger.info(logmsg)
                self.flag_as_phish(suspect, virusname)

                message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, {'virusname': virusname})
                break

        return actioncode, message

    def flag_as_phish(self, suspect, virusname):
        engine = self.config.get(self.section, 'virusenginename')
        suspect.tags[f'{engine}.virus'] = {'message content': virusname}
        suspect.tags['virus'][engine] = True

    def __str__(self):
        return "Spearphish Check"

    def lint(self):
        allok = self.check_config() and self._lint_file() and self._lint_sql()
        return allok

    def _lint_file(self):
        filename = self.config.get(self.section, 'domainsfile')
        if not os.path.exists(filename):
            print("Spearphish domains file %s not found" % filename)
            return False
        return True

    def _lint_sql(self):
        lint_ok = True
        sqlquery = self.config.get(self.section, 'domain_sql_query')
        dbconnection = self.config.get(self.section, 'dbconnection').strip()
        if not SQL_EXTENSION_ENABLED and dbconnection:
            print('SQLAlchemy not available, cannot use SQL backend')
            lint_ok = False
        elif not dbconnection:
            print('No DB connection defined. Disabling SQL backend')
        else:
            if not sqlquery.lower().startswith('select '):
                lint_ok = False
                print('SQL statement must be a SELECT query')
            if lint_ok:
                try:
                    conn = get_session(dbconnection)
                    conn.execute(text(sqlquery), {'domain': 'example.com'})
                except Exception as e:
                    lint_ok = False
                    print(str(e))
        return lint_ok


class SenderRewriteScheme(ScannerPlugin):
    """
    SRS (Sender Rewriting Scheme) Plugin
    This plugin encrypts envelope sender and decrypts bounce recpient addresses with SRS
    As opposed to postsrsd it decides by RECIPIENT address whether sender address should be rewritten.
    This plugin only works in after queue mode

    Required dependencies:
     * pysrs
    Recommended dependencies:
     * sqlalchemy
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

        self.requiredvars = {
            'dbconnection': {
                'default': "mysql://root@localhost/spfcheck?charset=utf8",
                'description': 'SQLAlchemy Connection string. Leave empty to rewrite all senders',
            },

            'domain_sql_query': {
                'default': "SELECT use_srs from domain where domain_name=:domain",
                'description': 'get from sql database :domain will be replaced with the actual domain name. must return field use_srs',
            },

            'forward_domain': {
                'default': 'example.com',
                'description': 'the new envelope sender domain',
            },

            'secret': {
                'default': '',
                'description': 'cryptographic secret. set the same random value on all your machines',
            },

            'maxage': {
                'default': '8',
                'description': 'maximum lifetime of bounces',
            },

            'hashlength': {
                'default': '8',
                'description': 'size of auth code',
            },

            'separator': {
                'default': '=',
                'description': 'SRS token separator',
            },

            'rewrite_header_to': {
                'default': 'True',
                'description': 'set True to rewrite address in To: header in bounce messages (reverse/decrypt mode)',
            },
            
            'spf_only': {
                'default': 'False',
                'description': 'only rewrite if sender domain is spf protected (requires SPFPlugin to run first)',
            }
        }

    def get_sql_setting(self, domain, dbconnection, sqlquery, cache, cachename, default_value=None, logger=None):
        if logger is None:
            logger = logging.getLogger('fuglu.plugin.domainauth.SenderRewriteScheme.sql')

        cachekey = '%s-%s' % (cachename, domain)
        cached = cache.get_cache(cachekey)
        if cached is not None:
            logger.debug("got cached settings for %s" % domain)
            return cached

        settings = default_value

        try:
            session = get_session(dbconnection)

            # get domain settings
            dom = session.execute(text(sqlquery), {'domain': domain}).fetchall()

            if not dom or not dom[0] or len(dom[0]) == 0:
                logger.debug("Can not load domain settings - domain %s not found. Using default settings." % domain)
            else:
                settings = dom[0][0]

            session.close()

        except Exception as e:
            self.logger.error("Exception while loading settings for %s : %s: %s" % (domain, e.__class__.__name__, str(e)))

            cache.put_cache(cachekey, settings)
        logger.debug("refreshed settings for %s" % domain)
        return settings

    def should_we_rewrite_this_domain(self, suspect):
        forward_domain = self.config.get(self.section, 'forward_domain')
        if suspect.to_domain.lower() == forward_domain:
            return True  # accept for decryption

        dbconnection = self.config.get(self.section, 'dbconnection')
        sqlquery = self.config.get(self.section, 'domain_sql_query')

        if dbconnection.strip() == '':
            return True  # empty config -> rewrite all domains

        cache = get_default_cache()
        cachename = self.section
        setting = self.get_sql_setting(suspect.to_domain, dbconnection, sqlquery, cache, cachename, False, self.logger)
        return setting

    def _init_srs(self):
        secret = self.config.get(self.section, 'secret')
        maxage = self.config.getint(self.section, 'maxage')
        hashlength = self.config.getint(self.section, 'hashlength')
        separator = self.config.get(self.section, 'separator')
        srs = SRS.new(secret=secret, maxage=maxage, hashlength=hashlength, separator=separator, alwaysrewrite=True)
        return srs

    def _update_to_hdr(self, suspect, to_address):
        old_hdr = suspect.get_header('To')
        if old_hdr and '<' in old_hdr:
            start = old_hdr.find('<')
            if start < 1:  # malformed header does not contain <> brackets
                start = old_hdr.find(':')  # start >= 0
            name = old_hdr[:start]
            new_hdr = f'{name} <{to_address}>'
        else:
            new_hdr = f'<{to_address}>'
        suspect.set_header('To', new_hdr)

    def examine(self, suspect):
        if not SRS_AVAILABLE:
            return DUNNO
        
        if self.config.getboolean(self.section, 'spf_only') and suspect.get_tag("SPF.status") == 'none':
            self.logger.info(f'{suspect.id} ignoring mail from {suspect.from_domain} without spf')
            return DUNNO

        if not self.should_we_rewrite_this_domain(suspect):
            self.logger.info(f'{suspect.id} ignoring mail to {suspect.to_address}')
            return DUNNO

        if not suspect.from_address:
            self.logger.info(f'{suspect.id} ignoring bounce message')
            return DUNNO

        srs = self._init_srs()
        forward_domain = self.config.get(self.section, 'forward_domain').lower()
        if suspect.from_domain.lower() == forward_domain and suspect.from_address.lower().startswith('srs'):
            self.logger.info(f'{suspect.id} skipping already signed address {suspect.from_address}')
        elif suspect.to_domain.lower() == forward_domain and suspect.to_address.lower().startswith('srs'):
            orig_rcpt = suspect.to_address
            try:
                recipient = srs.reverse(orig_rcpt)
                suspect.to_address = recipient
                new_rcpts = [recipient if x == orig_rcpt else x for x in suspect.recipients]
                suspect.recipients = new_rcpts
                if self.config.getboolean(self.section, 'rewrite_header_to'):
                    self._update_to_hdr(suspect, recipient)
                self.logger.info(f'{suspect.id} decrypted bounce address {orig_rcpt} to {recipient}')
            except Exception as e:
                self.logger.error(f'{suspect.id} Failed to decrypt {orig_rcpt} reason: {e.__class__.__name__}: {str(e)}')
        else:
            orig_sender = suspect.from_address
            try:
                try:
                    sender = srs.forward(orig_sender, forward_domain)
                except AttributeError:
                    # python 3.9 -> deprecated encodestring has been replaced by encodcebytes
                    import base64
                    base64.encodestring = base64.encodebytes
                    sender = srs.forward(orig_sender, forward_domain)
                suspect.from_address = sender
                self.logger.info(f'{suspect.id} signed {orig_sender} to {sender}')
            except Exception as e:
                self.logger.error(f'{suspect.id} Failed to sign {orig_sender} reason: {e.__class__.__name__}: {str(e)}')

        del srs
        return DUNNO

    def __str__(self):
        return "Sender Rewrite Scheme"

    def lint(self):
        allok = self.check_config()
        if not SRS_AVAILABLE:
            allok = False
            print('SRS library not found')

        if not self.config.get(self.section, 'secret'):
            allok = False
            print('no secret set in config')

        if allok:
            srs = self._init_srs()
            forward_domain = self.config.get(self.section, 'forward_domain')
            try:
                srs.forward('foobar@example.com', forward_domain)
            except AttributeError:
                # python 3.9 -> deprecated encodestring has been replaced by encodcebytes
                import base64
                base64.encodestring = base64.encodebytes
                srs.forward('foobar@example.com', forward_domain)

        sqlquery = self.config.get(self.section, 'domain_sql_query')
        if not sqlquery.lower().startswith('select '):
            allok = False
            print('SQL statement must be a SELECT query')
        if not SQL_EXTENSION_ENABLED:
            allok = False
            print('SQLAlchemy not available, cannot use SQL backend')
        if allok:
            dbconnection = self.config.get(self.section, 'dbconnection')
            if dbconnection.strip() == '':
                print('No DB connection defined. Disabling SQL backend, all addresses will be rewritten.')
            else:
                try:
                    conn = get_session(dbconnection)
                    conn.execute(text(sqlquery), {'domain': 'example.com'})
                except Exception as e:
                    allok = False
                    print(f'ERROR: {e.__class__.__name__}: {str(e)}')

        return allok


_ipexclude = re.compile(r'^(127|0|10|192\.168|172\.(1[6-9]|[2-3][0-9]|4[0-1])|169\.254|100\.(6[4-9]|[7-9][0-9]|1[0-1][0-9]|12[0-7]))\.')


def get_host_ipaddr(inhostname: tp.Optional[str] = None) -> tp.Optional[str]:
    """
    guess local IP address (or from given host)
    :return: string with an IP address
    """
    dummyhost = "255.255.255.254"
    defaultip = '0.0.0.0'

    try:
        hostname = inhostname if inhostname else socket.getfqdn()  # ore use get_outgoing_helo ?
        ipguess = [ip for ip in socket.gethostbyname_ex(hostname)[2] if not _ipexclude.match(ip)]
    except (socket.gaierror, UnicodeError):
        # name does not resolve or hostname is empty
        ipguess = []

    if not ipguess and not inhostname:
        ipguess = [[(s.connect((dummyhost, 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]

    myip = (ipguess + [defaultip])[0]
    return myip


class SPFOut(SPFPlugin):
    """
Check SPF on outgoing system. Ensures that your host is included in sender domain's SPF record.
Only mail that would not sender domain's SPF policy will be allowed to pass.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars.update({
            'ip': {
                'default': '',
                'description': 'IP used for spf check (env: "$VARNAME", empty: from given hostname or extract from machine)',
            },
            'hostname': {
                'default': '',
                'description': 'hostname/helo used for spf check (env: "$VARNAME", empty: extract from machine)',
            },
            'hoster_mx_exception': {'default': ''},
            'on_fail': {'default': 'REJECT'},
            'on_softfail': {'default': 'REJECT'},
            'messagetemplate': {'default': 'SPF record for domain ${from_domain} does not include smarthost.'},
            'create_received_spf': {'default': 'False'},
        })

        self._myip = None
        self._myhostname = None
        self._myhelo = None

    def _init_ipnames(self, logprefix):
        self._myip = None

        inip = self.config.get(self.section, "ip", resolve_env=True)
        inhost = self.config.get(self.section, "hostname", resolve_env=True)
        if not inhost:
            inhost = get_outgoing_helo(self.config)

        if inhost:
            try:
                self._myhelo = inhost
                self._myhostname = inhost
                if inip:
                    self._myip = inip
                else:
                    # get ip from host
                    self._myip = get_host_ipaddr(inhostname=inhost)
                    self.logger.debug(f'{logprefix} detected local IP address {self._myip} from hostname {inhost}')
            except Exception as e:
                self.logger.debug(f'{logprefix} failed to detect host information due to {e.__class__.__name__}: {str(e)}')

        if self._myip is None:
            self._myip = get_host_ipaddr()
            self._myhostname = socket.getfqdn()  # ore use get_outgoing_helo ?
            self.logger.debug(f'{logprefix} detected local IP address {self._myip}')

    def _get_clientinfo(self, suspect):
        if self._myip is None:
            self._init_ipnames(suspect.id)
            if not self._myip:
                raise ValueError(f"Couldn't extract IP address!")

        return self._myip, self._myhelo, self._myhelo

    def lint(self, state=EOM) -> bool:
        ok = super().lint(state=state)
        self._init_ipnames('')
        print(f'INFO: HELO: {self._myhelo} / IP: {self._myip}')
        return ok


class NoHaveAuth(ScannerPlugin):
    """
    Qualify mail based on presence or absence of any auth mechanisms (spf, dkim, arc, dmarc, fcrdns)
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'checks': {
                'default': 'spf,dkim,dmarc,arc,fcrdns',
                'description': 'authentication checks to consider',
            },
            'dummy_checks': {
                'default': 'dkim,dmarc,arc',
                'description': 'dummy replacements for header/content depending checks',
            },
            'failaction': {
                'default': 'DUNNO',
                'description': "action if the message doesn't pass any authentication (DUNNO, DEFER, REJECT)",
            },
            'rejectmessage': {
                'default': 'sender domain ${header_from_domain} does not pass any authentication check',
                'description': "reject message template if running in pre-queue/milter mode",
            },
        }

    def examine(self, suspect: Suspect):
        checks = self.config.getlist(self.section, 'checks', lower=True)
        if not checks:
            self.logger.debug(f'{suspect.id} no checks defined')

        spf_ok = suspect.get_tag("SPF.status") == 'pass'
        spf_checked = suspect.get_tag("SPF.status") not in [None, SPF_SKIP]

        dkim_ok = suspect.get_tag("DKIMVerify.result") == DKIM_PASS
        dkim_checked = suspect.get_tag('DKIMVerify.skipreason') is None

        dmarc_ok = suspect.get_tag('dmarc.result') == DMARC_PASS
        dmarc_checked = suspect.get_tag('dmarc.result') not in [None, DMARC_UNAVAILABLE]

        arc_ok = suspect.get_tag("ARCVerify.cv") == DKIM_PASS
        arc_checked = suspect.get_tag('ARCVerify.skipreason') is None

        fcrdns_ok = check_iprev(suspect, self.config) == 'pass'

        dummy_checks = self.config.getlist(self.section, 'dummy_checks', lower=True)
        if 'dkim' in dummy_checks and not dkim_checked:
            dkim_ok = suspect.get_header('dkim-signature') is not None
            dkim_checked = True
        if 'arc' in dummy_checks and not arc_checked:
            arc_ok = suspect.get_header('arc-seal') is not None
            arc_checked = True
        if 'dmarc' in dummy_checks and not dmarc_checked:
            have_dmarc = dnsquery.lookup(f'_dmarc.{suspect.from_domain}', 'TXT')
            if not have_dmarc:
                headerfromdomain = extract_from_domain(suspect)
                if headerfromdomain:
                    have_dmarc = dnsquery.lookup(f'_dmarc.{headerfromdomain}', 'TXT')
            dmarc_ok = spf_ok and dkim_ok and have_dmarc
            dmarc_checked = True

        all_fail = True
        if 'spf' in checks and spf_checked and spf_ok:
            all_fail = False
        if 'dkim' in checks and dkim_checked and dkim_ok:
            all_fail = False
        if 'dmarc' in checks and dmarc_checked and dmarc_ok:
            all_fail = False
        if 'arc' in checks and arc_checked and arc_ok:
            all_fail = False
        if 'fcrdns' in checks and fcrdns_ok:
            all_fail = False

        suspect.set_tag('NoHaveAuth', all_fail)
        if all_fail:
            self.logger.debug(f'{suspect.id} all checks failed')
            suspect.write_sa_temp_header('X-NoHaveAuth', 'true')
            actioncode = self._problemcode('failaction')
            message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, {})
            return actioncode, message
        return DUNNO


class PTRPlugin(IPProtoCheckMixin, BMPRCPTMixin, BasicMilterPlugin):
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

        self.requiredvars = {
            'logonly': {
                'default': 'False',
                'description': 'only log errors, do not reject/defer',
            },
            'debug': {
                'default': 'False',
                'description': 'excessively log behaviour',
            },
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            },
        }
    
    async def examine_rcpt(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        debug = self.config.getboolean(self.section, 'debug')
        resp = sess.tags.get('PTR.mresponse')
        if resp and len(resp) == 2:  # reuse result from previous recipient. test result is purely client host based.
            if debug:
                self.logger.debug(f'{sess.id} previous result {resp}')
            return resp
        if sess.fcrdns and force_uString(sess.fcrdns) != 'unknown':
            if debug:
                self.logger.debug(f'{sess.id} found fcrdns {sess.fcrdns}')
            # fcrdns compliant
            return sm.CONTINUE
        if not sess.addr:
            if debug:
                self.logger.warning(f'{sess.id} session has no ip')
            # no ip?
            return sm.CONTINUE
        if not self._check_protocol(force_uString(sess.addr)):
            # no need to check for this IP's protocol
            return sm.CONTINUE
        logonly = self.config.getboolean(self.section, 'logonly')
        try:
            if aiodnsquery.AIODNSQUERY_EXTENSION_ENABLED:
                result = await aiodnsquery.fcrdnslookup(force_uString(sess.addr), reraise=True, strict=True)
            else:
                result = dnsquery.fcrdnslookup(force_uString(sess.addr), reraise=True, strict=True)
        except Exception as e:
            result = None
            self.logger.debug(f'{sess.id} failed to lookup FcRDNS of IP {force_uString(sess.addr)} due to {e.__class__.__name__}: {str(e)}')
            if not logonly:
                return sm.TEMPFAIL, f'DNS error while checking FcRDNS of IP {force_uString(sess.addr)}'
        if not result:
            self.logger.debug(f'{sess.id} IP {force_uString(sess.addr)} has no FcRDNS')
            if not logonly:
                return sm.REJECT, f'IP {force_uString(sess.addr)} has no FcRDNS'
        if debug:
            self.logger.warning(f'{sess.id} not rejecting message from {sess.addr} {sess.fcrdns} with result {result}')
        return sm.CONTINUE

    def lint(self, state=None) -> bool:
        ok = self.check_config()
        if not aiodnsquery.AIODNSQUERY_EXTENSION_ENABLED and not dnsquery.DNSQUERY_EXTENSION_ENABLED:
            ok = False
            print('ERROR: no dns library installed. requires either aiodns, dnspython or pydns')
        return ok


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    c = FuConfigParser()
    c.add_section('DKIMVerifyPlugin')
    c.set('DKIMVerifyPlugin', 'create_received_dkim', 'True')
    s = Suspect('sender@unittests.fuglu.org', 'rcpt@unittest.fuglu.org', sys.argv[1])
    d = DKIMVerifyPlugin(c)
    d.examine(s)
    print(s.tags)
    print(s.get_header('Received-DKIM'))