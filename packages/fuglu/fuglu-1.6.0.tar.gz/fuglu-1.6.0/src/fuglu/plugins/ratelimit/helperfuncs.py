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
import typing as tp
import ipaddress as ia
import ipaddress

import fuglu.extensions.dnsquery
from domainmagic import extractor, tld
from domainmagic.validators import is_url_tldcheck
from fuglu.extensions import dnsquery
from fuglu.stringencode import force_uString
from fuglu.shared import Suspect
from fuglu.plugins.uriextract import EXCLUDE_DOMAIN, EXCLUDE_FQDN
from fuglu.extensions.dnsquery import lookup, FuNXDOMAIN, FuTIMEOUT, FuSERVFAIL, FuNoNameserver, FuNoAnswer
from fuglu.connectors.asyncmilterconnector import MilterSession
from fuglu.logtools import get_context_logger

BE_VERBOSE = False  # for debugging


def ip2network(ipstring: str, prefixlen: int = 32) -> str:
    """
    Take an ip string and the prefixlen to calculate the network string
    which can be used as a key in the RateLimitPlugin
    """
    with get_context_logger('fuglu.ratelimit.helperfuncs.ip2network') as logger:
        try:
            network = ia.ip_network(f"{ipstring}/{prefixlen}", False).with_prefixlen
        except ValueError as e:
            logger.error(str(e))
            network = ''
        return network


# Singleton implementation for Domainmagic
class DomainMagic(object):
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.tldmagic = tld.TLDMagic()


def get_domain_from_uri(uri: str, suspect=None) -> tp.Optional[str]:
    """Extract domain from uri"""

    suspectid = suspect.id if suspect else '<>'
    with get_context_logger(f'fuglu.ratelimit.helperfuncs.get_domain_from_uri(id={suspectid})') as logger:
        exclude_fqdn = ['www.w3.org', 'schemas.microsoft.com']
        exclude_domain = ['avast.com']

        if not uri:
            return None

        uri = uri.strip()
        if uri.startswith("["):
            if uri.endswith("]"):
                uri = uri.lstrip("[").rstrip("]")
            else: # broken items, would result in "Invalid IPv6 URL uri"
                return None
        try:
            fqdn = extractor.domain_from_uri(uri)
            if fqdn in exclude_fqdn:
                return None
        except Exception as e:
            # log error
            logger.error(f"{suspectid} msg: {e.__class__.__name__}: {str(e)} uri: {uri}")
            return None

        try:
            domain = DomainMagic.instance().tldmagic.get_domain(fqdn)
        except Exception as e:
            # log error
            logger.error(f"{suspectid} msg: {e.__class__.__name__}: {str(e)} fqdn: {fqdn}")
            return None

        if domain in exclude_domain:
            return None
        return domain


def split_helo2host_domain(helo: str, suspect=None):
    """Split helo to host, domain"""
    suspectid = suspect.id if suspect else '<>'
    with get_context_logger(f'fuglu.ratelimit.helperfuncs.split_helo2host') as logger:
        domain = get_domain_from_uri(helo, suspect=suspect)
        if not domain:
            return helo, ""
        try:
            hostname = helo.rsplit("."+domain, 1)[0]
        except Exception as e:
            logger.error(f"{suspectid} msg: {str(e)} helo: {helo}, domain: {domain}")
            hostname = ""
        return hostname, domain


# Singleton implementation for GeoIP
class GeoIP(object):
    _instances = {}

    @classmethod
    def instance(cls, filename):
        try:
            return cls._instances[filename]
        except KeyError:
            newinstance = cls(filename)
            cls._instances[filename] = newinstance
            return newinstance

    def __init__(self, filename):
        try:
            from geoip2.database import Reader
        except ImportError:
            Reader = None

        self._filename = filename
        self._reader = Reader(filename) if Reader else None

    def print(self):
        print(f'filename is(id={id(self)}): {self._filename}')

    @property
    def reader(self):
        return self._reader


def asn(ipaddr: tp.Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address], geoipfilename: str)\
        -> tp.Union[None, tp.Tuple[int, str, tp.Union[ipaddress.IPv4Address, ipaddress.IPv6Address], tp.Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]]:
    """Extract ASN properties

    geoipfilename is geoip filename containing as ndata
    """
    from geoip2.errors import AddressNotFoundError
    with get_context_logger('fuglu.ratelimit.helperfuncs.asn') as logger:
        try:
            response = GeoIP.instance(geoipfilename).reader.asn(ipaddr)
        except AddressNotFoundError:
            return None
        except FileNotFoundError:
            logger.error(f"failed to load {geoipfilename}")
            return None

        try:
            response_network = response.network
        except AttributeError:
            # older geoip versions
            response_network = None

        return (
            response.autonomous_system_number,
            response.autonomous_system_organization,
            response.ip_address,
            response_network,
        )


def match_key_in_array(inputarray: tp.Optional[tp.List[str]], searchstring: str = "", suspect=None) -> tp.Optional[str]:
    """Search for string in array"""
    suspectid = suspect.id if suspect else '<>'
    with get_context_logger(f'fuglu.ratelimit.helperfuncs.match_key_in_array') as logger:
        if inputarray is None:
            return None

        foundaddr = None
        if inputarray and searchstring in inputarray:
            foundaddr = searchstring

        if BE_VERBOSE:
            logger.debug(f"{suspectid} found {foundaddr} in {inputarray}")

        # don't return an empty list, return None in this case
        return foundaddr if foundaddr else None


def valid_fqdn(urilist: tp.Optional[tp.List[str]], suspect=None) -> tp.Optional[tp.List[str]]:
    """Reduce uri list to fqdn's only"""
    suspectid = suspect.id if suspect else '<>'
    with get_context_logger(f'fuglu.ratelimit.helperfuncs.match_key_in_array') as logger:
        if urilist is None:
            return None
        domains = set()
        try:
            for url in urilist:
                try:
                    if url and is_url_tldcheck(url, exclude_fqdn=EXCLUDE_FQDN, exclude_domain=EXCLUDE_DOMAIN):
                        domains.add(extractor.fqdn_from_uri(url))
                except Exception as e:
                    logger.error(f"{suspectid} (examine:fqdn_from_uri): {e} for uri: {url}")
        except Exception:
            logger.exception(e)
        domains = list(domains)
        # don't return an empty list, return None in this case
        return domains if domains else None


def convert_truefalse(input: tp.Optional[str], suspect=None) -> str:
    """Split helo to host, domain"""
    return str(bool(input))


def create_sudomain_list(domain: str, reverse: bool = False, suspect=None) -> tp.Optional[tp.List[str]]:
    """
    Create subdomain list, from domain to smallest subdomain
    unless reversed.

    Example:
        - in: a.b.c.d.com
          out: [d.com, c.d.com, b.c.d.com, a.b.c.d.com]
        - in: a.b.c.d.com (reverse=True)
          out: [a.b.c.d.com, b.c.d.com, c.d.com, d.com]
    """

    suspectid = suspect.id if suspect else '<>'
    with get_context_logger(f'fuglu.ratelimit.helperfuncs.create_subdomain_list') as logger:

        try:
            tldcount = DomainMagic.instance().tldmagic.get_tld_count(domain)
        except Exception as e:
            # log error
            logger.error(f"{suspectid} msg: {str(e)} domain: {domain}")
            return None

        parts = domain.split('.')

        subrange = range(tldcount + 1, len(parts) + 1)
        checkstrings = []
        for subindex in subrange:
            subdomain = '.'.join(parts[-subindex:])
            checkstrings.append(subdomain)
        if checkstrings and reverse:
            checkstrings = checkstrings[::-1]
        return checkstrings


def packargs(*args, **kwargs):
    """
    Small helper function if result should be packed
    This is required if output of the previous function is an array
    and it should be passed as an array into the next function, because
    usually arrays are expanded and threated as separate arguments into
    the next function
    """
    if args:
        return (args,)
    else:
        return None


def get_nameservers(idomain: tp.Union[str, tp.List[str]], suspect=None) -> tp.Optional[tp.List[str]]:
    """For input domain/list of domains return first set of nameservers found"""

    suspectid = suspect.id if suspect else '<>'
    with get_context_logger(f'fuglu.ratelimit.helperfuncs.create_subdomain_list') as logger:

        if isinstance(idomain, str):
            dlist = [idomain]
        else:
            dlist = idomain

        # check if list is nonempty
        if dlist and isinstance(dlist, (list, tuple)):
            for dom in dlist:
                try:
                    answers: tp.List[str] = dnsquery.lookup(dom, dnsquery.QTYPE_NS)
                    answers = [a.rstrip('.') for a in answers if a and a.rstrip('.')] if answers else []
                    if len(answers):
                        return answers
                except Exception as e:
                    logger.error(f"{suspectid} got: {str(e)} querying ns for: {dom}")

        return None


def filter4left_tuple(tuplelist: tp.Union[tp.Tuple, tp.List],
                      filter: str,
                      lowercase: bool = True,
                      suspect=None) -> tp.Optional[tp.List[str]]:
    suspectid = suspect.id if suspect else '<>'
    if isinstance(tuplelist, tuple):
        tuplelist = tuplelist[0]
    newlist = []
    for tup in tuplelist:
        k, v = tup
        k = force_uString(k, convert_none=True)
        if lowercase:
            k = k.lower()
        # if filter ist '*' get all headers
        # (this is used for headercounts in restrictions)
        if (filter == "*" and k.strip()) or k == filter:
            newlist.append(v)
    if newlist:
        return newlist
    else:
        return None


def arraylength_largerthan(array: tp.List, maxlength=0, suspect=None) -> bool:
    suspectid = suspect.id if suspect else '<>'
    with get_context_logger(f'fuglu.ratelimit.helperfuncs.arraylength_largerthan') as logger:
        islarger = len(array) > maxlength
        if suspect:
            # set tags so values can be used in reject message
            try:
                # note: these tags will be prefixed by "tag_" if used in the reject message,
                # Example: "array length exceeded ${tag_arraylength} > ${tag_maxlength}"
                suspect.tags["arraylength"] = len(array)
                suspect.tags["maxlength"] = maxlength
            except Exception as e:
                logger.debug(f"Problem setting tags: {str(e)}")
        logger.debug(f"{suspectid} arraylength: {len(array)} {'>' if islarger else '<='} {maxlength}")
        return islarger


def decode_from_type_headers(tuplelist: tp.Union[tp.Tuple, tp.List], name="From", suspect=None) -> tp.Optional[tp.List[str]]:
    suspectid = suspect.id if suspect else '<>'
    if isinstance(tuplelist, tuple):
        tuplelist = tuplelist[0]

    buffer = b"\r\n".join([tup[0]+b": "+tup[1] for tup in tuplelist])
    if buffer:
        # build dummy suspect
        s = Suspect("from@fuglu.org", "to@fuglu.org", tempfile=None, inbuffer=buffer)
        addrs = s.parse_from_type_header(header=name, validate_mail=True)
        if addrs:
            return (addrs, )
        else:
            return None
    else:
        return None


def select_tuple_index(tuplelist: tp.Union[tp.Tuple, tp.List],
                       index: int,
                       suspect=None) -> tp.Optional[tp.List[str]]:
    suspectid = suspect.id if suspect else '<>'
    if isinstance(tuplelist, tuple):
        tuplelist = tuplelist[0]
    try:
        return ([tup[index] for tup in tuplelist], )
    except Exception:
        return None


def select_element_by_index(iterable: tp.Union[tp.Tuple, tp.List],
                            index: int,
                            suspect=None) -> tp.Optional[tp.List[str]]:
    suspectid = suspect.id if suspect else '<>'
    with get_context_logger(f'fuglu.helperfuncs.get_element_by_index') as logger:
        try:
            return iterable[index]
        except Exception as e:
            logger.error(f"Can't select element {index} of iterable {iterable}: {str(e)}")
        return None


def domain_from_email(emaillist: tp.List[str], suspect=None) -> tp.Optional[tp.List[str]]:
    if emaillist:
        out = list(set([m.rsplit("@", 1)[1] for m in emaillist if m and "@" in m]))
        if out:
            return out
    return None


def get_skip_ptr_unknown(ptr: str, suspect=None) -> tp.Optional[str]:
    with get_context_logger(f'fuglu.helperfuncs.get_skip_ptr') as logger:
        if ptr and isinstance(ptr, str) and ptr.lower() == "unknown":
            logger.debug(f"Return None because ptr is unknown")
            return None
        else:
            return ptr


def get_ptr(ipaddress: str, suspect=None, verify: bool = False) -> tp.Optional[str]:
    """get ptr, return 'unknown' if none is found to match MilterSession implementation"""
    with get_context_logger(f'fuglu.helperfuncs.get_ptr') as logger:

        # first, try to get ptr from milter suspect
        if suspect and isinstance(suspect, MilterSession):
            # shortcut -> if ptr is known: return directly
            if suspect.ptr and suspect.ptr != "unknown":
                logger.debug(f"ptr={suspect.ptr} defined in miltersession: don't recalculate")
                return suspect.ptr
            elif suspect.ptr:
                logger.debug(f"no valid ptr={suspect.ptr} defined in miltersession -> recalculate")

        logger.debug(f"no ptr defined in miltersession: recalculate")

        try:
            answers: tp.List[str] = fuglu.extensions.dnsquery.revlookup(ipaddress, reraise=True)
            answers = [a.rstrip('.') for a in answers if a and a.rstrip('.')] if answers else []
            if len(answers):
                if answers[0] and verify:
                    fwd = lookup(answers[0])
                    if not fwd or not ipaddress in answers:
                        return 'unknown'
                logger.debug(f"no ptr defined in miltersession: recalculated as {answers[0]}")
                return answers[0]
        except FuNXDOMAIN:
            logger.debug(f"return nxdomain as ptr for: {ipaddress}")
            return 'nxdomain'
        except (FuTIMEOUT, FuSERVFAIL, FuNoNameserver, FuNoAnswer) as e:
            logger.debug(f"got: {e.__class__.__name__}: {str(e)} querying PTR for: {ipaddress}")
        except Exception as e:
            logger.error(f"got: {e.__class__.__name__}: {str(e)} querying PTR for: {ipaddress}")
        logger.debug(f"no ptr defined in miltersession: return unknown")
        return "unknown"


def suspecttagsummary(inputdictstring: tp.Optional[tp.Dict[str, bool]], suspect=None):
    with get_context_logger(f'fuglu.helperfuncs.suspecttagsummary') as logger:
        try:
            for key in list(inputdictstring.keys()):
                val = inputdictstring[key]
                if val:
                    return True
        except Exception as e:
            logger.error(f"({type(e)}) {str(e)}")
            pass
        return None


def sender_recipient_match(recipient: str, suspect: tp.Optional[MilterSession] = None) -> tp.Optional[str]:
    """Return email if recipient matches sender of suspect, None otherwise"""
    with get_context_logger(f'fuglu.helperfuncs.sender_recipient_match') as logger:
        if not suspect:
            logger.debug("no suspect -> return")
            return None
        sender = force_uString(suspect.sender, convert_none=True)
        if not (sender and sender.strip()):
            logger.debug(f"no sender({suspect.sender}) -> return")
            return None
        if not (recipient and recipient.strip()):
            logger.debug(f"no recipient({recipient}) suspect.recipients=[{force_uString(suspect.recipients)}]-> return")
            return None
        sender_norm = sender.strip().lower()
        recipient_norm = recipient.strip().lower()
        if sender_norm == recipient_norm:
            logger.debug(f"sender({sender_norm}) == recipient({recipient})")
            return sender_norm
        else:
            logger.debug(f"sender({sender_norm}) != recipient({recipient}) -> return")
            return None


def sender_recipient_domainkey(recipient: str, keys: str, suspect: tp.Optional[MilterSession] = None) -> tp.Optional[str]:
    """Return key if key is found in sender and recipient domain, None otherwise"""
    with get_context_logger(f'fuglu.helperfuncs.sender_recipient_domainkey') as logger:
        if not suspect:
            logger.debug("no suspect -> return")
            return None

        sender = force_uString(suspect.sender, convert_none=True)
        if not (sender and sender.strip()):
            logger.debug(f"no sender({suspect.sender}) -> return")
            return None
        if not (recipient and recipient.strip()):
            logger.debug(f"no recipient({recipient}) suspect.recipients=[{force_uString(suspect.recipients)}]-> return")
            return None

        sender_norm = sender.strip().lower()
        recipient_norm = recipient.strip().lower()

        sender_domain = sender_norm.rsplit("@", maxsplit=1)[-1]
        recipient_domain = recipient_norm.rsplit("@", maxsplit=1)[-1]

        keys = keys.lstrip("'").lstrip('"').rstrip("'").rstrip('"')
        keys = [k.strip().lower() for k in keys.split(";") if (k and k.strip())]

        for key in keys:
            if key in sender_domain and key in recipient_domain:
                logger.debug(f"key {key} found in sender&recipient domain!")
                return key

        logger.debug(f"non keys found in sender & recipient domains...")
        return None
