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

import typing as tp
import logging
import ipaddress


class _DummyExc(Exception):
    pass


STATUS = "not loaded"
_NXDOMAIN = _DummyExc
DNS_TIMEOUT = TimeoutError
_PYDNSEXC = _DummyExc
_NONAMESERVER = _DummyExc
_NOANSWER = _DummyExc
try:
    from dns import resolver, exception, flags, __version__ as dnsversion
    HAVE_DNSPYTHON = True
    STATUS = f"available, using dnspython {dnsversion}"
    _NXDOMAIN = resolver.NXDOMAIN
    DNS_TIMEOUT = exception.Timeout
    _NONAMESERVER = resolver.NoNameservers
    _NOANSWER = resolver.NoAnswer
    myresolver = resolver.Resolver()
except ImportError:
    resolver = exception = flags = dnsversion = None
    HAVE_DNSPYTHON = False

HAVE_PYDNS = False
if not HAVE_DNSPYTHON:
    try:
        import DNS
        HAVE_PYDNS = True
        DNS.DiscoverNameServers()
        STATUS = f"available, using pydns {DNS.__version__}"
        _PYDNSEXC = DNS.Base.ServerError
        logging.warning('support for pydns is deprecated in fuglu, please install dnspython')
    except ImportError:
        DNS = None
        STATUS = "DNS not installed"

ENABLED = DNSQUERY_EXTENSION_ENABLED = HAVE_DNSPYTHON or HAVE_PYDNS


QTYPE_A = 'A'
QTYPE_AAAA = 'AAAA'
QTYPE_MX = 'MX'
QTYPE_NS = 'NS'
QTYPE_TXT = 'TXT'
QTYPE_PTR = 'PTR'
QTYPE_CNAME = 'CNAME'
QTYPE_SPF = 'SPF'
QTYPE_SRV = 'SRV'
QTYPE_SOA = 'SOA'
QTYPE_CAA = 'CAA'
QTYPE_DS = 'DS'
QTYPE_CDS = 'CDS'
QTYPE_DNSKEY = 'DNSKEY'
QTYPE_SSHFP = 'SSHFP'
QTYPE_TLSA = 'TLSA'
QTYPE_NSEC = 'NSEC'
QTYPE_NSEC3 = 'NSEC3'
QTYPE_NSEC3PARAM = 'NSEC3PARAM'
QTYPE_RRSIG = 'RRSIG'


class FuNXDOMAIN(Exception):
    pass


class FuTIMEOUT(Exception):
    pass


class FuSERVFAIL(Exception):
    pass


class FuNoNameserver(Exception):
    pass


class FuNoAnswer(Exception):
    pass


class FuNoDNSSec(Exception):
    pass


def lookup(hostname: str, qtype: str = QTYPE_A, reraise: bool = False, dnssec: bool = None, timeout: float = None) -> tp.Optional[tp.List[str]]:
    """
    performs dns lookup
    :param hostname: string: the fqdn to look up
    :param qtype: string: the qtype (A, AAAA, MX, ...)
    :param reraise: boolean: if True reraise lookup exceptions. if False suppress and return None.
    :param dnssec: boolean: if None no special handling of dnssec. if True result must be dnssec secured, else raises NoFuDNSSec exception. if False return response even if dnssec validation would fail.
    :param timeout: float: maximum query time
    :return: List of DNS replies (string) on successful lookup, empty List if no DNS answer, None on error
    """
    # noinspection PyExceptClausesOrder
    try:
        if HAVE_DNSPYTHON:
            if dnssec is True:
                myresolver.flags = flags.RD | flags.AD
            elif dnssec is False:
                myresolver.flags = flags.RD | flags.CD

            arequest = myresolver.resolve(hostname, qtype, lifetime=timeout)

            if dnssec is True and not arequest.response.flags & flags.AD:
                raise FuNoDNSSec

            arecs = []
            for rec in arequest:
                arecs.append(rec.to_text())
            return arecs

        elif HAVE_PYDNS:
            logger = logging.getLogger('fuglu.extensions.DNSQuery')
            logger.warning('support for pydns is deprecated in fuglu, please install dnspython')
            return DNS.dnslookup(hostname, qtype)

    except _NXDOMAIN:
        if reraise:
            raise FuNXDOMAIN
    except DNS_TIMEOUT:
        if reraise:
            raise FuTIMEOUT
    except _NONAMESERVER:
        if reraise:
            raise FuNoNameserver
    except _NOANSWER:
        if reraise:
            raise FuNoAnswer
    except _PYDNSEXC as e:
        if reraise and 'NXDOMAIN' in e.message:
            raise FuNXDOMAIN
        if reraise and 'SERVFAIL' in e.message:
            raise FuSERVFAIL
    except Exception:
        if reraise:
            raise

    return None


def mxlookup(domain: str, reraise: bool=False, dnssec: bool=None, timeout: float = None) -> tp.Optional[tp.List[str]]:
    """
    perform MX lookup of given domain
    :param domain: see lookup
    :param reraise: see lookup
    :param dnssec: see lookup
    :param timeout: see lookup
    :return: List of MX servers on successful lookup, empty List if no DNS answer, None on error
    """
    try:
        if HAVE_DNSPYTHON:
            mxrecs = lookup(domain, qtype=QTYPE_MX, reraise=reraise, dnssec=dnssec, timeout=timeout)
            mxrecs.sort()  # automatically sorts by priority
            return [x.split(None, 1)[-1] for x in mxrecs]  # only return server name

        elif HAVE_PYDNS:
            logger = logging.getLogger('fuglu.extensions.DNSQuery')
            logger.warning('support for pydns is deprecated in fuglu, please install dnspython')
            mxrecs = []
            mxrequest = DNS.mxlookup(domain)
            for dataset in mxrequest:
                if type(dataset) == tuple:
                    mxrecs.append(dataset)

            mxrecs.sort()  # automatically sorts by priority
            return [x[1] for x in mxrecs]

    except Exception:
        pass

    return None


def revlookup(ip: str, reraise: bool = False, dnssec: bool = None, timeout: float = None) -> tp.Optional[tp.List[str]]:
    """
    reverse lookup of IP address
    :param ip: string of IPv4 or IPv6 address
    :param reraise: see lookup
    :param dnssec: see lookup
    :param timeout: see lookup
    :return: see lookup
    """
    ipaddr = ipaddress.ip_address(ip)
    revip = ipaddr.reverse_pointer
    return lookup(revip, qtype=QTYPE_PTR, reraise=reraise, dnssec=dnssec, timeout=timeout)


def fcrdnslookup(ip: str, reraise: bool = False, dnssec: bool = None, timeout: float = None, strict=False) -> tp.Optional[tp.List[str]]:
    fcrdns = set()
    ptrs = revlookup(ip, reraise, dnssec, timeout)
    if ptrs:
        testip = ipaddress.ip_address(ip)
        for ptr in ptrs:
            ips = lookup(ptr, QTYPE_A if testip.version==4 else QTYPE_AAAA, reraise=reraise, dnssec=dnssec, timeout=timeout)
            if ips and ip in ips:
                fcrdns.add(ptr)
    if strict and ptrs and set(ptrs) != fcrdns:
        return None
    return list(fcrdns) or None

