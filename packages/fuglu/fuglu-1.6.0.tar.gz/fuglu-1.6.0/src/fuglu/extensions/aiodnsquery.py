import typing as tp
import ipaddress
try:
    import aiodns
    ENABLED = AIODNSQUERY_EXTENSION_ENABLED = True
    STATUS = f"available, using pydns {aiodns.__version__}"
except ImportError:
    ENABLED = AIODNSQUERY_EXTENSION_ENABLED = False
    STATUS = "not loaded"

class FuNXDOMAIN(Exception): pass
class FuTIMEOUT(Exception): pass
class FuSERVFAIL(Exception): pass
class FuNoNameserver(Exception): pass
class FuNoAnswer(Exception): pass
class FuNoDNSSec(Exception): pass  # DNSSEC support not implemented in aiodns

QTYPE_A = 'A'
QTYPE_AAAA = 'AAAA'
QTYPE_MX = 'MX'
QTYPE_NS = 'NS'
QTYPE_PTR = 'PTR'
QTYPE_TXT = 'TXT'

async def lookup(hostname: str, qtype: str = QTYPE_A, reraise: bool = False, dnssec: bool = None, timeout: float = None) -> tp.Optional[tp.List[str]]:
    """
    Asynchronous DNS lookup.
    """
    try:
        async with aiodns.DNSResolver() as resolver:
            if timeout:
                resolver.timeout = timeout
            
            qtype = qtype.upper() # must be uppercase
            result = await resolver.query(hostname, qtype)
        
        if qtype == QTYPE_MX:
            # implicit null mx (e.g. example.com) is returned as empty string
            return [f"{r.priority} {r.host or '.'}" for r in sorted(result, key=lambda x: x.priority)]
        elif qtype == QTYPE_PTR:
            return [r.name for r in result] if isinstance(result, list) else [result.name]
        else:
            return [r.host if hasattr(r, 'host') else r.text if hasattr(r, 'text') else str(r) for r in result]

    except aiodns.error.DNSError as e:
        if reraise:
            if e.args[0] == aiodns.error.ARES_ENOTFOUND:
                raise FuNXDOMAIN
            elif e.args[0] == aiodns.error.ARES_ETIMEOUT:
                raise FuTIMEOUT
            elif e.args[0] == aiodns.error.ARES_ESERVFAIL:
                raise FuSERVFAIL
            elif e.args[0] == aiodns.error.ARES_ENODATA:
                raise FuNoAnswer
            elif e.args[0] == aiodns.error.ARES_ENOTIMP:
                raise FuNoNameserver
            else:
                raise
        return None
    except Exception:
        if reraise:
            raise
        return None

async def mxlookup(domain: str, reraise: bool = False, dnssec: bool = None, timeout: float = None) -> tp.Optional[tp.List[str]]:
    """
    Asynchronous MX record lookup.
    """
    mxrecs = await lookup(domain, qtype=QTYPE_MX, reraise=reraise, dnssec=dnssec, timeout=timeout)
    if mxrecs:
        return [x.split(None, 1)[-1] for x in mxrecs]
    return None

async def revlookup(ip: str, reraise: bool = False, dnssec: bool = None, timeout: float = None) -> tp.Optional[tp.List[str]]:
    """
    Asynchronous reverse DNS lookup.
    """
    ipaddr = ipaddress.ip_address(ip)
    revip = ipaddr.reverse_pointer
    del ipaddr
    return await lookup(revip, qtype=QTYPE_PTR, reraise=reraise, dnssec=dnssec, timeout=timeout)

async def fcrdnslookup(ip: str, reraise: bool = False, dnssec: bool = None, timeout: float = None, strict: bool = False) -> tp.Optional[tp.List[str]]:
    """
    Asynchronous forward-confirmed reverse DNS (FCrDNS) lookup.
    """
    fcrdns = set()
    ptrs = await revlookup(ip, reraise, dnssec, timeout)
    if ptrs:
        qtype = QTYPE_A if '.' in ip else QTYPE_AAAA
        for ptr in ptrs:
            ips = await lookup(ptr, qtype, reraise=reraise, dnssec=dnssec, timeout=timeout)
            if ips and ip in ips:
                fcrdns.add(ptr)
    if strict and ptrs and set(ptrs) != fcrdns:
        return None
    return list(fcrdns) or None