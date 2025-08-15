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

from fuglu.shared import Suspect, ScannerPlugin, DUNNO
#from fuglu.extensions.dnsquery import lookup, fcrdnslookup, QTYPE_MX, QTYPE_A, QTYPE_NS, QTYPE_AAAA
import fuglu.extensions.aiodnsquery as aiodnsquery
from fuglu.stringencode import force_uString
from fuglu.mshared import BasicMilterPlugin, BMPRCPTMixin, BMPEOBMixin, BMPEOHMixin
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from operator import itemgetter
import ipaddress
import typing as tp
import re


LOOKUP_TYPES = [aiodnsquery.QTYPE_A, aiodnsquery.QTYPE_AAAA, aiodnsquery.QTYPE_MX, 'MXA', aiodnsquery.QTYPE_NS, 'NSA']


class DNSData(ScannerPlugin, BasicMilterPlugin, BMPRCPTMixin, BMPEOBMixin):
    """
Perform DNS lookups on sender or recipient domain and store them in suspect tag for later use

Plugin wrrites the following tags:
 * dnsdata.sender
 * dnsdata.recipient
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'recipient_lookups': {
                'default': '',
                'description': 'comma separated list of dns lookup types to perform on recipient domains. supports %s MXA=get A of all MX, NSA=get A of all NS' % ','.join(LOOKUP_TYPES),
            },

            'sender_lookups': {
                'default': '',
                'description': 'comma separated list of dns lookup types to perform on sender domain. supports same types as recipient_lookup',
            },
            
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }

    @staticmethod
    def _sort_mx(result: tp.List[str]) -> tp.List[str]:
        """
        sort MX ascending by prio, strip prio from lookup response
        """
        sortable_result = [(int(s[0]), s[1]) for s in [r.split() for r in sorted(result)]]
        sorted_result = sorted(sortable_result, key=itemgetter(0))
        return [s[1] for s in sorted_result]

    @staticmethod
    async def _do_lookup_a(result: tp.List[str]) -> tp.List[str]:
        aresult = []
        for rec in result:
            res = await aiodnsquery.lookup(rec, aiodnsquery.QTYPE_A) or []
            for ip in res:  # maintain previous result order (important for MXA)
                if not ip in aresult:
                    aresult.append(ip)
        return aresult

    async def _do_lookups(self, domain:str, qtypes:tp.List[str]) -> tp.Dict[str, tp.List[str]]:
        results = {}
        for qtype in qtypes:
            lookupqtype = qtype[:2] if qtype in ['MXA', 'NSA'] else qtype
            result = await aiodnsquery.lookup(domain, lookupqtype)
            if qtype in [aiodnsquery.QTYPE_MX, 'MXA'] and result:
                result = self._sort_mx(result)
            if qtype in ['MXA', 'NSA'] and result:
                result = await self._do_lookup_a(result)
            if result is not None:
                results[qtype] = [r.rstrip('.') for r in result]
        return results

    async def _run(self, suspect, recipients:tp.List[str]):
        if suspect.tags.get('dnsdata.sender') is None:
            sender_lookups = [l.upper() for l in self.config.getlist(self.section, 'sender_lookups')]
            sender_results = await self._do_lookups(suspect.from_domain, sender_lookups)
            suspect.tags['dnsdata.sender'] = sender_results
            self.logger.debug(f'{suspect.id} dnsdata for senderdomain {suspect.from_domain} values {sender_results}')

        recipient_lookups = [l.upper() for l in self.config.getlist(self.section, 'recipient_lookups')]
        for recipient in recipients:
            rcpt_domain = recipient.rsplit('@', 1)[-1]
            recipient_tagname = f'dnsdata.recipient.{rcpt_domain.lower()}'
            if suspect.tags.get(recipient_tagname) is None:
                rcpt_results = await self._do_lookups(rcpt_domain, recipient_lookups)
                suspect.tags[recipient_tagname] = rcpt_results
                self.logger.debug(f'{suspect.id} dnsdata for rcpt domain {rcpt_domain} {rcpt_results}')

    async def examine(self, suspect):
        await self._run(suspect, suspect.recipients)
        return DUNNO, None

    async def examine_rcpt(self, sess, recipient):
        await self._run(sess, [force_uString(recipient)])
        return sm.CONTINUE, None

    async def examine_eob(self, sess):
        await self._run(sess, [force_uString(r) for r in sess.recipients])
        return sm.CONTINUE, None

    def lint(self, state=None):
        ok = self.check_config()
        if not ok:
            print('ERROR: failed to check config')
            
        if not aiodnsquery.AIODNSQUERY_EXTENSION_ENABLED:
            print('ERROR: dependency aiodns not installed')
            ok = False

        sender_lookups = [l.upper() for l in self.config.getlist(self.section, 'sender_lookups')]
        for item in sender_lookups:
            if item not in LOOKUP_TYPES:
                ok = False
                print(f'WARNING: invalid sender lookup type {item}')

        recipient_lookups = [l.upper() for l in self.config.getlist(self.section, 'recipient_lookups')]
        for item in recipient_lookups:
            if item not in LOOKUP_TYPES:
                ok = False
                print(f'WARNING: invalid recipient lookup type {item}')

        return ok



class GetOrigin(ScannerPlugin, BasicMilterPlugin, BMPEOHMixin):
    """
    Determine origin host of message from dedicated headers and/or received header
    
    X-Client-IP:0.0.0.0
    X-SenderIP:0.0.0.0
    X-SenderIP:0.0.0.0 (0.0.0.0)
    X-Source-IP:0.0.0.0
    X-Originated-At:0.0.0.0!00000
    X-Source-Sender:(XXXXXXX) [0.0.0.0]:00000
    X-Originating-IP:[0.0.0.0]
    X-FXIT-IP:IPv4[0.0.0.0] Epoch[0000000000]
    X-PHP-Script:example.com/script.php for 8.8.8.8
    X-PHP-Filename:/path/to/script.php REMOTE_ADDR: 8.8.8.8
    X-Forward: 8.8.8.8
    X-Forward: 8.8.8.8, 10.2.3.4
    X-FEAS-Client-IP: 0.0.0.0
    X-EN-OrigIP: 0.0.0.0
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'headers': {
                'default': 'X-Client-IP,X-SenderIP,X-Source-IP,X-Originated-At,X-Source-Sender,X-Originating-IP,X-FXIT-IP,X-PHP-Script,X-PHP-Filename,X-Forward,X-FEAS-Client-IP,X-EN-OrigIP',
                'description': 'comma separated list of headers containing potential originator IP',
            },
            
            'state': {
                'default': asm.EOH,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            },
            
            'verbose': {
                'default': 'False',
                'description': 'enable more verbose logging'
            }
        }
        
    def _get_origin_hdr(self, msgrep, suspect:Suspect) -> tp.Optional[str]:
        origin = None
        headers = self.config.getlist(self.section, 'headers')
        for header in headers:
            value = force_uString(msgrep.get(header))
            if value:
                if '[' in value:
                    value = value.split('[',1)[-1]
                if ']' in value:
                    value = value.split(']',1)[0]
                if '!' in value:
                    value = value.split('!',1)[0]
                if ' for ' in value or ' REMOTE_ADDR: ' in value:
                    value = value.split()[-1]
                if ', ' in value:
                    value = value.split(',')[0]
                if value.endswith(')') and ' (' in value:
                    value = value.split()[0]
                try:
                    if ipaddress.ip_address(value).is_global:
                        self.logger.debug(f'{suspect.id} got origin ip {value} from header {header}')
                        origin = value
                        break
                    elif self.config.getboolean(self.section, 'verbose'):
                        self.logger.debug(f'{suspect.id} not a global ip {value} in received header {header}')
                except ValueError:
                    self.logger.debug(f'{suspect.id} not a valid ip {value} in header {header}')
        return origin
    
    _rgx_rcvd_exim = re.compile(r'^from (?P<revdns>\S{3,256})? ?\(?\[(?P<ip>(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|(?:[0-9a-f:]{3,40}))\](?::[0-9]{1,5})?\)?(?: .{0,256}helo=(?P<helo>\S{3,256})\))? by (?P<by>\S{3,256}) (?:with esmtpa )?.{0,256}\(Exim', re.MULTILINE)
    _rgx_rcvd_other = re.compile(r'from \[?(?P<revdns>\S{3,256})\]? ?\(?\[(?P<ip>(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|(?:[0-9a-f:]{3,40}))(?::[0-9]{1,5})?\)?\](?: helo=(?P<helo>\S{3,256}))?\) by (?P<by>\S{3,256}) .{0,256}E?SMTPS?')
    _rgx_rcvd_squirrel = re.compile(r'from (?P<ip>(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|(?:[0-9a-f:]{3,40})) \(SquirrelMail.{0,100}\) by (?P<by>\S{3,256})')

    def _parse_rcvd_header_extra(self, rcvd: str) -> tp.Optional[tp.Tuple[tp.Optional[str], tp.Optional[str], tp.Optional[str], tp.Optional[str]]]:
        """
        parse received lines written by exim. examples:
        from [8.8.8.8] (helo=PREDATOR) by mail.fuglu.org (Exim) with esmtpsa (TLS1.2:ECDHE_SECP256R1__RSA_SHA512__AES_256_GCM:256) (envelope-from <sender@unittest.fuglu.org>) id 1t6hvS-00BEX5-1R for recipient@unittest.fuglu.org; Fri, 01 Nov 2024 04:02:15 +0100
        from revdns.fuglu.org ([8.8.8.8]:55584) by mail.fuglu.org with esmtpa (Exim 4.93) (envelope-from <sender@unittest.fuglu.org>) id 1t6lz4-002HTH-OJ for recipient@unittest.fuglu.org; Fri, 01 Nov 2024 08:22:15 +0100
        from [8.8.8.8] (port=50084 helo=helo.fuglu.org) by mail.fuglu.org with esmtpsa (TLS1.2) tls TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (Exim 4.96.2) (envelope-from <sender@unittest.fuglu.org>) id 1t6qsV-0009dq-2T for recipient@unittest.fuglu.org; Fri, 01 Nov 2024 08:35:48 -0400
        
        parse received lines written by some other MTAs, examples:
        from [8.8.8.8] ([8.8.8.8:50302] helo=somehosthelo) by mail.fuglu.org (envelope-from <sender@unittest.fuglu.org>) (ecelerity 4.4.1.20033 r(msys-ecelerity:tags/4.4.1.0^0)) with ESMTPS (cipher=DHE-RSA-AES256-GCM-SHA384) id 6B/CA-20522-B29C6776; Thu, 02 Jan 2025 12:13:16 -0500
        from 8.8.8.8 (SquirrelMail authenticated user h0595bbt) by mail.fuglu.org with HTTP; Mon, 13 Jan 2025 01:00:56 +0100'
        
        returns None or a tuple of helo, revdns, ip, by
        each value can be None or a string
        """
        for rgx in [self._rgx_rcvd_exim, self._rgx_rcvd_other, self._rgx_rcvd_squirrel]:
            match = rgx.search(rcvd)
            if match is not None:
                break
        else: # none of the rgx hit
            return None
        rev_ip_h_by = match.groupdict()
        revdns = rev_ip_h_by.get('revdns')
        ip = rev_ip_h_by.get('ip')
        helo = rev_ip_h_by.get('helo')
        by = rev_ip_h_by.get('by')
        if revdns and revdns.rstrip(']') == ip: # _rgx_rcvd_other may extract revdns as e.g. 8.8.8.8]
            revdns = None
        return helo, revdns, ip, by
    
    def _get_origin_rcvd(self, msgrep, suspect:Suspect) -> tp.Tuple[tp.Optional[str], tp.Optional[str], tp.Optional[str]]:
        origin = None
        originhelo = None
        originptr = None
        rcvdhdrs = msgrep.get_all('received')
        if rcvdhdrs:
            lastrcvd = suspect.decode_msg_header(rcvdhdrs[-1], logid=suspect.id)
            values = suspect._parse_rcvd_header(lastrcvd)
            if not values:
                values = self._parse_rcvd_header_extra(lastrcvd)
            if values:
                self.logger.debug(f'{suspect.id} parsed default rcvd header helo={values[0]} ptr={values[1]} ip={values[2]}')
            else:
                values = self._parse_rcvd_header_extra(lastrcvd)
                if values:
                    self.logger.debug(f'{suspect.id} parsed extra rcvd header helo={values[0]} ptr={values[1]} ip={values[2]}')
                else:
                    self.logger.warning(f'{suspect.id} failed to parse rcvd header {lastrcvd}')
            if values:
                helo, revdns, ipresult, by = values
                try:
                    if ipaddress.ip_address(ipresult).is_global:
                        origin = ipresult
                        originhelo = helo
                        if revdns and revdns!='unknown':
                            originptr = revdns.rstrip('.')
                    elif self.config.getboolean(self.section, 'verbose'):
                        self.logger.debug(f'{suspect.id} not a global ip {ipresult} in received header {lastrcvd}')
                except ValueError:
                    self.logger.debug(f'{suspect.id} not a valid ip {ipresult} in received header {lastrcvd}')
        return origin, originhelo, originptr
        
    
    async def _run(self, suspect:Suspect):
        msgrep = suspect.get_message_rep()
        # if origin header is set, use its value as origin ip
        origin = self._get_origin_hdr(msgrep, suspect)
        
        clientinfo = suspect.get_client_info(self.config)
        originrcvd, originhelo, originptr = self._get_origin_rcvd(msgrep, suspect)
        
        self.logger.debug(f'{suspect.id} client={clientinfo[1] if clientinfo else None} originhdr={origin} originrcvd={originrcvd} originhelo={originhelo}')
        if origin is not None and clientinfo and origin!=originrcvd!=clientinfo[1]:
            # origin header and received info are not consistent, we can't use helo/ptr info from received
            originhelo = None
            originptr = None
        if origin is None and clientinfo and originrcvd!=clientinfo[1]:
            # if last received ip is global and not equals delivery host (clientinfo) it may be the origin
            origin = originrcvd
        elif origin is None and clientinfo and originrcvd==clientinfo[1]:
            # last received header is delivery client, it's probably not the origin
            originhelo = None
            originptr = None
        if originptr is None and origin is not None:
            # if we do not have an originptr yet, we look it up from origin ip
            fcrdns = await aiodnsquery.fcrdnslookup(origin)
            if fcrdns:
                originptr = fcrdns[0] # only use the first one
    
        if origin is not None:
            suspect.set_tag('origin.ip', origin)
            suspect.write_sa_temp_header('X-Fuglu-Origin-IP', origin)
        if originhelo is not None:
            suspect.set_tag('origin.helo', originhelo)
            suspect.write_sa_temp_header('X-Fuglu-Origin-HELO', originhelo)
        if originptr is not None:
            suspect.set_tag('origin.ptr', originptr)
            suspect.write_sa_temp_header('X-Fuglu-Origin-PTR', originptr)

    async def examine(self, suspect):
        await self._run(suspect)
        return DUNNO, None
    
    async def examine_eoh(self, sess: tp.Union[asm.MilterSession, sm.MilterSession]) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        pseudobody = b''
        for hdr, val in sess.original_headers:
            pseudobody += hdr + b': ' + val + b'\r\n'
        pseudobody += b'\r\n\r\n'

        suspect = Suspect(force_uString(sess.sender), force_uString(sess.recipients[0]), None, id=sess.id,
                          queue_id=sess.queueid, milter_macros=sess.milter_macros, inbuffer=pseudobody)
        suspect.timestamp = sess.timestamp
        suspect.tags = sess.tags  # pass by reference - any tag change in suspect should be reflected in session
        await self._run(suspect)
        return sm.CONTINUE
    
    def lint(self, state=None):
        all_ok = self.check_config()
        
        if not aiodnsquery.AIODNSQUERY_EXTENSION_ENABLED:
            print('WARNING: dependency aiodns not installed - some data may be incomplete')
        
        return all_ok
        