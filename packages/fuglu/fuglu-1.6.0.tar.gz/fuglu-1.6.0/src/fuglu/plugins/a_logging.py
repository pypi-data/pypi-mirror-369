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
from fuglu.shared import AppenderPlugin, apply_template, get_outgoing_helo, FileList, actioncode_to_string, \
    FuConfigParser, Suspect, redact_uri
from fuglu.stringencode import force_uString, force_bString
from fuglu.mailattach import NoExtractInfo
from fuglu.caching import smart_cached_memberfunc
from fuglu.plugins.uriextract import EXCLUDE_DOMAIN, EXCLUDE_FQDN
from fuglu.extensions.elastic import ElasticClient, AsyncElasticClient, ElasticException, lint_elastic
import fuglu.extensions.aiodnsquery
from email.header import Header
import datetime
import time
import re
import os
import json
import logging
import urllib
import urllib.parse
import hashlib
import copy
import asyncio
import typing as tp
try:
    from domainmagic import extractor, tld
    from domainmagic.mailaddr import strip_batv, decode_srs, domain_from_mail, split_mail
    from domainmagic.validators import is_email, is_url_tldcheck
    HAVE_DOMAINMAGIC = True
except ImportError:
    HAVE_DOMAINMAGIC = False


LOG_MAPPING = {
    "properties": {
        "headers": {"type": "nested", "properties": {"content": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 4096}}}}},
        "spamreport": {"type": "nested"},
        "virusreport": {"type": "nested"},
        "blockedreport": {"type": "nested"},
        "uris": {"type": "nested", "properties": {"uri": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 512}}}}},
        "attachments": {"type": "nested"},
        "client_ip": {"type": "ip"}, "origin_ip": {"type": "ip"},
        "size": {"type": "integer"},
    }
}


class MappingFile(FileList):
    def _parse_lines(self, lines):
        content = '\n'.join(lines)
        try:
            jsoncontent = json.loads(content)
        except Exception as e:
            self.logger.error(f'failed to load json data: {e.__class__.__name__}: {str(e)}')
            jsoncontent = None
        return jsoncontent

def dict2str(result:tp.Dict) -> str:
    return ', '.join([f'{x}={y}' for x,y in result.items()])


class URILogger(object):
    def __init__(self, config, section):
        self.logger = logging.getLogger(f'fuglu.plugin.logging.{self.__class__.__name__}')
        self.config = config
        self.section = section
        self.tldmagic = None
        self.extratlds = None
        self.extratlds_lastlist = None
        self._init_tldmagic()

    def _init_tldmagic(self) -> None:
        init_tldmagic = False
        extratlds = []

        if self.extratlds is None:
            extratldfile = self.config.get(self.section, 'extra_tld_file')
            if extratldfile and os.path.exists(extratldfile):
                self.extratlds = FileList(extratldfile, lowercase=True)
                init_tldmagic = True

        if self.extratlds is not None:
            extratlds = self.extratlds.get_list()
            if self.extratlds_lastlist != extratlds:  # extra tld file changed
                self.extratlds_lastlist = extratlds
                init_tldmagic = True

        if self.tldmagic is None or init_tldmagic:
            self.tldmagic = tld.TLDMagic()
            for t in extratlds:  # add extra tlds to tldmagic
                self.tldmagic.add_tld(t)

    def _remove_uris_in_rcpt_domain(self, uris:tp.Dict[str,str], to_domain:str, suspectid:str='') -> tp.Dict[str, str]:
        if uris is None:
            return {}
        new_uris = {}
        for uri in uris.keys():
            try:
                if not uri.startswith('http'):
                    parseuri = f'http://{uri}'
                else:
                    parseuri = uri
                u = urllib.parse.urlparse(parseuri)
            except Exception as e:
                # log error and skip on logging this uri on error
                self.logger.error(f"{suspectid} unparseable URL {uri} {e.__class__.__name__}: {str(e)}")
                continue

            if u.hostname and (u.hostname == to_domain or u.hostname.endswith(f'.{to_domain}')):
                self.logger.debug(f'{suspectid} skipping URL in recipient domain: {uri}')
                continue
            elif not u.hostname:
                self.logger.debug(f'{suspectid} not a parseable URL: {uri}')
            new_uris[uri] = uris.get(uri, 'unknown')
        return new_uris

    def _remove_uri_fragments(self, uris:tp.Dict[str,str], suspectid:str) -> tp.Dict[str, str]:
        new_uris = {}
        urikeys = list(uris.keys())
        for uri in urikeys:
            fragment = False
            for u in urikeys:
                if uri != u and uri in u:
                    self.logger.debug(f'{suspectid} discarding uri fragment {uri} in {u}')
                    fragment = True
                    break
            if not fragment:
                new_uris[uri] = uris.get(uri, 'unknown')
        return new_uris

    def _get_domain_from_fqdn(self, fqdn:str, suspect:Suspect=None) -> tp.Optional[str]:
        try:
            self._init_tldmagic()
            domain = self.tldmagic.get_domain(fqdn).lower()
        except Exception as e:
            # log error
            self.logger.error(f"{suspect.id if suspect else '<>'} msg: {str(e)} fqdn: {fqdn}")
            return None
        return domain

    def _get_domain_from_uri(self, uri:str, suspect:Suspect=None) -> tp.Tuple[tp.Optional[str], tp.Optional[str]]:
        try:
            fqdn = extractor.domain_from_uri(uri)
            if fqdn in EXCLUDE_FQDN:
                return None, None
        except Exception as e:
            # log error
            self.logger.error(f"{suspect.id if suspect else '<>'} msg: {str(e)} uri: {uri}")
            return None, None
        domain = self._get_domain_from_fqdn(fqdn, suspect)
        if domain and domain in EXCLUDE_DOMAIN:
            return None, None
        return fqdn, domain

    def get_all_uris(self, suspect:Suspect, maxitems:int) -> tp.List[tp.Dict[str,str]]:
        urilist = []
        tags = self.config.getlist(self.section, 'log_uri_tags')
        uris = {}
        for tag in tags:
            taguris = suspect.get_tag(tag, [])
            for uri in taguris:
                if uri not in uris and is_url_tldcheck(uri, exclude_fqdn=EXCLUDE_FQDN, exclude_domain=EXCLUDE_DOMAIN):
                    uris[uri] = tag

        uris = self._remove_uris_in_rcpt_domain(uris, suspect.to_domain, suspect.id or '<>')
        uris = self._remove_uri_fragments(uris, suspect.id or '<>')
        for rawuri in list(uris.keys())[:maxitems]:
            uri = extractor.redirect_from_url(rawuri)
            fqdn, domain = self._get_domain_from_uri(uri, suspect=suspect)
            if domain is None:
                self.logger.warning(f'{suspect.id} failed to extract domain from uri {uri}')
                continue
            logitem = {
                'type': 'uri',
                'fqdn': fqdn,
                'domain': domain,
                'uri': uri,
                'src': uris.get(rawuri, 'unknown')
            }
            urilist.append(logitem)
        return urilist

    def get_all_emails(self, suspect:Suspect, maxitems:int) -> tp.List[tp.Dict[str,str]]:
        urilist = []
        tags = self.config.getlist(self.section, 'log_email_tags')
        emails = {}
        for tag in tags:
            tagaddrs = suspect.get_tag(tag, [])
            for addr in tagaddrs:
                if is_email(addr):
                    emails[addr] = tag

        for addr in list(emails.keys())[:maxitems]:
            if addr.startswith('//'):
                continue
            fqdn = domain_from_mail(addr)
            domain = self._get_domain_from_fqdn(fqdn, suspect)
            if domain is None:
                self.logger.warning(f'{suspect.id} failed to extract domain from email address {addr}')
                continue
            logitem = {
                'type': 'email',
                'fqdn': fqdn,
                'domain': domain,
                'uri': addr,
                'src': emails.get(addr, 'unknown')
            }
            urilist.append(logitem)
        return urilist


SKIP_ARCHIVE_RE = [
    re.compile(r'^LOG/[0-9]{1,20}\.DLF$') # found in .idab
]
class AttLogger(object):
    def __init__(self, config, section):
        self.logger = logging.getLogger(f'fuglu.plugin.logging.{self.__class__.__name__}')
        self.config = config
        self.section = section

    def _skip_attachment_type(self, att_type:str) -> bool:
        SKIPS = ['text/xml', 'text/json']
        for item in SKIPS:
            # att_type might be None
            if att_type and (att_type == item or att_type.startswith(item)):
                return True
        return False
    
    def _skip_filename(self, filename:str) -> bool:
        for item in SKIP_ARCHIVE_RE:
            if item.match(filename):
                return True
        return False

    def get_all_attachments(self, suspect:Suspect, maxitems:int=50) -> tp.List[tp.Dict[str,tp.Union[str,int,bool]]]:
        hashes = self.config.getlist(self.section, 'log_attachment_hashes')
        archivecontentmaxsize = self.config.getint(self.section, 'archivecontentmaxsize')
        attachments = []
        
        noextractinfo = NoExtractInfo()
        attachmentlist = suspect.att_mgr.get_objectlist(level=1, maxsize_extract=archivecontentmaxsize, include_parents=True, noextractinfo=noextractinfo)
        attachmentcount = len(attachmentlist)
        #self.logger.debug(f'{suspect.id} got attachment list of {attachmentcount} items')

        noextractlist = noextractinfo.get_filtered(minus_filters=["level"])
        for item in noextractlist:
            self.logger.warning(f'{suspect.id} extraction failed of file {item[0]} with message {item[1]}')
        #self.logger.debug(f'{suspect.id} found {attachmentcount} attachments, failed to extract {len(noextractlist)}')

        count = 0
        for attObj in attachmentlist:
            if not suspect.stimeout_continue(self.section):
                self.logger.error(f'{suspect.id} exceeded elastic data aggregation timeout after {count} attachments. next attachment would be {attObj.filename}')
                break
            if count >= maxitems:
                break
                
            filename = attObj.location()
            if attachmentcount >= maxitems and attObj.in_archive and (self._skip_attachment_type(attObj.contenttype) or self._skip_filename(filename)):
                continue

            logitem = {
                'name': filename,
                'size': attObj.filesize or 0,
                'mime': attObj.contenttype,
                'is_inline': attObj.is_inline,
                'is_attachment': attObj.is_attachment,
                'is_archive': attObj.is_archive,
                'in_archive': attObj.in_archive,
                'is_archive_pw': attObj.is_protected_archive,
            }
            for hashtype in hashes:
                logitem[hashtype] = attObj.get_checksum(hashtype)
            attachments.append(logitem)
            count += 1
        self.logger.debug(f'{suspect.id} got {len(attachments)} attachments')
        return attachments


class ElasticBackend(object):
    def __init__(self, config, section):
        self.config = config
        self.section = section
        self.logger = logging.getLogger(f'fuglu.plugin.logging.{self.__class__.__name__}')
        self.mapping_file = None

    def get_elastic_connection(self, use_async:bool=False) -> tp.Union[ElasticClient, AsyncElasticClient]:
        es = None
        elastic_uris = self.config.getlist(self.section, 'elastic_uris', resolve_env=True)
        if elastic_uris:
            verify_certs = self.config.getboolean(self.section, 'elastic_verify_certs')
            timeout = self.config.getfloat(self.section, 'elastic_timeout', fallback=30)
            if use_async:
                es = AsyncElasticClient(hosts=elastic_uris, verify_certs=verify_certs, ssl_show_warn=False, timeout=timeout)
            else:
                es = ElasticClient(hosts=elastic_uris, verify_certs=verify_certs, ssl_show_warn=False, timeout=timeout)
        return es

    def get_elastic_index(self, suspect: Suspect) -> str:
        indextmpl = self.config.get(self.section, 'elastic_index')
        tagindexlist = [item.rsplit(':', 1) for item in self.config.getlist(self.section, 'elastic_index_by_tags')]
        for tag, itmpl in tagindexlist:
            if suspect.get_tag(tag):
                indextmpl = itmpl
        indexname = apply_template(indextmpl, suspect)
        return indexname

    def _get_mapping(self, mapping_file:str) -> tp.Dict[str,tp.Any]:
        new_mapping = LOG_MAPPING

        if not self.mapping_file and mapping_file and os.path.exists(mapping_file):
            self.mapping_file = MappingFile(filename=mapping_file)
        if self.mapping_file:
            loaded_mapping = self.mapping_file.get_list()
            if not loaded_mapping:
                self.logger.error(f'mapping file {mapping_file} could not be loaded')
            else:
                new_mapping = loaded_mapping

        return new_mapping

    @smart_cached_memberfunc(inputs=[])
    async def _set_index_mapping(self, indexname: str) -> None:
        self.logger.info(f'checking mapping of index {indexname}')
        es = self.get_elastic_connection(use_async=True)
        exists = await es.indices.exists(index=indexname)
        if exists:
            need_put = False
            current_mapping = await es.indices.get_mapping(index=indexname)
            properties = current_mapping.get(indexname, {}).get('mappings', {}).get('properties', {})

            mapping_file = self.config.get(self.section, 'elastic_mapping_file', fallback='')
            new_mapping = self._get_mapping(mapping_file)

            try:
                for key in new_mapping['properties']:
                    proptype = properties.get(key, {}).get('type')
                    if not new_mapping['properties'][key]['type'] == properties.get(key, {}).get('type'):
                        need_put = True
                        self.logger.debug(f"mapping update required due to property of key '{key}'\n:"
                                          f"new: {json.dumps(new_mapping['properties'][key]['type'], indent=4)}\n\n"
                                          f"current: {json.dumps(proptype, indent=4)}")
                        break
            except KeyError as e:
                need_put = False
                if mapping_file:
                    self.logger.error(f'failed to load mapping file {mapping_file}: {e.__class__.__name__}: {str(e)}')
                else:
                    self.logger.error(f'invalid mapping: {e.__class__.__name__}: {str(e)}')

            if need_put:
                try:
                    r = await es.indices.put_mapping(body=LOG_MAPPING, index=indexname)
                except ElasticException as e:
                    r = {'exc': e.__class__.__name__, 'msg': str(e)}
                if r.get('acknowledged'):
                    self.logger.info(f'put new mapping to elastic index {indexname}')
                else:
                    self.logger.info(f'error putting new mapping to elastic index {indexname} : {str(r)}\n'
                                     f'Input data body ways:\n'
                                     f'{json.dumps(LOG_MAPPING, indent=4)}')
            else:
                self.logger.debug(f'no need to update mapping of elastic index {indexname}')
        else:
            log_mapping = {'mappings': LOG_MAPPING}
            try:
                replicas = self.config.get(self.section, 'elastic_replicas', resolve_env=True)
                try:
                    replicas = int(replicas)
                except (TypeError, ValueError):
                    self.logger.debug('not setting replicas')
                    replicas = None
                if replicas is not None:
                    log_mapping['settings'] = {'index': {'number_of_replicas': replicas}}
                r = await es.indices.create(index=indexname, body=log_mapping)
            except ElasticException as e:
                r = {'exc': e.__class__.__name__, 'msg': str(e)}
            if r.get('acknowledged'):
                self.logger.info(f'created new elastic index {indexname}')
            else:
                self.logger.info(f'error creating new elastic index {indexname} : {str(r)}')
            try:
                self.logger.debug(f"body to create elastic index was:\n{json.dumps(log_mapping, indent=4)}")
            except Exception as e:
                # don't let logging break code
                self.logger.exception(e)
                pass
        await es.close()

    async def log_to_elastic(self, suspect: Suspect, logdata: tp.Dict[str, tp.Any], rcpt_id: int, retry: int = 3) -> tp.Dict[str, str]:
        result = {'rcpt_id': rcpt_id}
        try:
            logdata['timestamp'] = datetime.datetime.fromtimestamp(suspect.timestamp, datetime.timezone.utc).isoformat()
            es = self.get_elastic_connection(use_async=True)
            indexname = self.get_elastic_index(suspect)
            await self._set_index_mapping(indexname)
            documentid = f'{suspect.id}_{rcpt_id}'
            timeout = self.config.getfloat(self.section, 'elastic_timeout', fallback=30)
            try:
                r = await es.index(index=indexname, id=documentid, body=logdata, request_timeout=timeout)
            finally:
                await es.close()
            for key in ['_id', 'result']:
                try:
                    result[key] = r[key]
                except KeyError:
                    self.logger.warning(f'{suspect.id} key {key} not found in result {r}')
            self.logger.debug(f'{suspect.id} indexed in elastic {indexname}: {dict2str(r)}')
        except Exception as e:
            if retry > 0:
                self.logger.debug(f'{suspect.id} failed to index in elastic, retry={retry} reason={e.__class__.__name__}: {str(e)}')
                await asyncio.sleep(0.2*(4-retry))
                result = await self.log_to_elastic(suspect, logdata, rcpt_id, retry=retry-1)
            else:
                raise
        return result


class ElasticLogger(AppenderPlugin):
    """
    write fuglu log data directly to elasticsearch
    all data related to a suspect is written to one elasticsearch document, what data exactly will be logged can be configured to a certain degree
    if write to elasticsearch fails, optionally fallback logging to local json files can be enabled. these json files can later be reimported.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'elastic_uris': {
                'default': '',
                'description': 'comma separated list of ElasticSearch host definition (hostname, hostname:port, https://user:pass@hostname:port/)',
            },
            'elastic_verify_certs': {
                'default': 'True',
                'description': 'verify server\'s SSL certificates',
            },
            'elastic_timeout': {
                'default': '30',
                'description': 'set elastic connection timeout to this value',
            },
            'elastic_retry': {
                'default': '3',
                'description': 'how many retries on elastic logging errors (e.g. timeouts)',
            },
            'elastic_index': {
                'default': 'fuglulog-${date}',
                'description': 'Name of ElasticSearch index in which document will be stored. Template vars (e.g. ${to_domain} or ${date}) can be used.',
            },
            'elastic_mapping_file': {
                'default': '',
                'description': 'read elastic mapping from json file. leave empty to use default mapping.',
            },
            'elastic_replicas': {
                'default': '',
                'description': 'override number of replicas. leave empty for default.',
            },
            'elastic_index_by_tags': {
                'default': '',
                'description': 'Comma separated list of tuples of SuspectTag:IndexName of ElasticSearch index in which document will be stored. Template vars (e.g. ${to_domain} or ${date}) can be used for index name. SuspectTag value must evaluate to True. First hit wins.',
            },
            'log_headers': {
                'default': 'from:addr,from:namedecode,to:pseudo:md5,reply-to:addr,subject,subject:decode,subject:hash:md5,message-id:low',
                'description:': """
                    Name of message headers to log and extract.
                    Address headers (e.g. To, From, Reply-To) support tags such as :addr (address only), :pseudo:algo (address only, with hashed localpart), :name (name label only), :namedecode (name label only, decoded).
                    All header support tag hash:algo - algo must be one of hashlibs supported hash algorithms
                    All headers support tag decode - try decode encoded headers
                    All header support tag low - lowercase value
                    All header names will be prefixed hdr_ in elastic document, - and : will be converted to _
                    Currently only one tag per header is possible
                    Name will be renamed according to log_field_map.
                """
            },
            'log_values': {
                'default': 'id,from_address:low,from_domain:low,from_localpart:low,queue_id,size,timestamp',
                'description:': """
                    Name of suspect attribute values to log and extract.
                    Email address like values support :pseudo:algo (hash localpart)
                    All values support tag low - lowercase value
                    Name will be renamed according to log_field_map.
                """
            },
            'log_milter_macros': {
                'default': 'auth_authen',
                'description:': """
                    Name of suspect attribute values to log and extract.
                    Email address like values support :pseudo:algo (hash localpart)
                    All values support tag low - lowercase value
                    Name will be renamed according to log_field_map.
                """
            },
            'log_field_map': {
                'default': 'id:fugluid, injectqueueid:queueid, attachment_bounce_queueid:bounceqid,from_address_low:from_address,from_domain_low:from_domain,from_localpart_low:from_localpart',
                'description': """
                    Rename field names prior to logging.
                    map is a comma separated list of key:value pairs.
                    key is the name of the field to be renamed (as written to elastic document),
                    value is the resulting name.
                """
            },
            'log_tags': {
                'default': 'to_address,to_domain,to_localpart,to_address:pseudo:md5,to_localpart:pseudo:md5,injectqueueid,fuzor.digest,log.scanhost,log.decision,log.client_helo,log.client_ip,log.client_hostname,log.client_hostnames,log.processtime,archived,Attachment.bounce.queueid,spf.result,dkim.result,arc.result,dmarc.result,log.real_from_address,recipient_id,insidemail',
                'description:': 'Name of message tags to log and extract. Some tags will be renamed.'
            },
            'log_raw_headers': {
                'default': 'all',
                'description': 'log raw headers. set to "all" for all headers or comma separated list of header names to be logged'
            },
            'log_uris': {
                'default': '50',
                'description': 'log URI information (specify max number of URIs and email addresses to log, 0 to disable URI logging)'
            },
            'log_email_tags': {
                'default': 'body.emails',
                'description': 'log URIs listed in given tags'
            },
            'log_uri_tags': {
                'default': 'body.uris,uris.safelinks,headers.uris',
                'description': 'log URIs listed in given tags'
            },
            'log_attachments': {
                'default': '50',
                'description': 'log attachment information (specify max number of attachments to log, 0 to disable attachment logging)'
            },
            'log_attachment_hashes': {
                'default': 'md5,sha1',
                'description': f'log attachment checksums, specify any hash supported by hashlib: {",".join(hashlib.algorithms_available)}'
            },
            'log_header_as_env_sender': {
                'default': 'X-Original-Sender, X-Mail-Args, Return-Path',
                'description': 'override envelope sender with value from one of these headers (if set - first occurrence wins)'
            },
            'log_header_as_env_recipient': {
                'default': 'X-Original-Recipient',
                'description': 'override envelope recipient with value from one of these headers (if set - first occurrence wins)'
            },
            'extra_tld_file': {
                'default': '',
                'description': 'path to file with extra TLDs (2TLD or inofficial TLDs)'
            },
            'fallback_logdir': {
                'default': '/usr/local/fuglu/maillog/',
                'description': 'path to directory where logs are stored in case of elasticsearch connection/indexing failure'
            },
            'error_write_eml_dir': {
                'default': '',
                'description': 'in case of error write .eml of suspect to given parent directory. leave empty to never write'
            },
            'timeout': {
                'default': '30',
                'description': 'maximum time to spend on data aggregation',
            },
            'archivecontentmaxsize': {
                'default': '5000000',
                'description': 'only extract and examine files up to this amount of (uncompressed) bytes',
            },
        }
        self.urilogger = None
        self.attlogger = None
        self.elasticbackend = None
        self.fieldmap = None

    def _init_components(self) -> None:
        if self.urilogger is None:
            self.urilogger = URILogger(self.config, self.section)
        if self.attlogger is None:
            self.attlogger = AttLogger(self.config, self.section)
        if self.elasticbackend is None:
            self.elasticbackend = ElasticBackend(self.config, self.section)

    def _normalise_fieldname(self, field_name: str) -> str:
        if self.fieldmap is None:
            self.fieldmap = {k: v for k, v in [x.strip().rsplit(':', 1) for x in self.config.getlist(self.section, 'log_field_map')]}

        field_name = field_name.lower()

        if field_name.startswith('log.'):
            field_name = field_name[4:]

        badchars = '-.:'
        for c in badchars:
            field_name = field_name.replace(c, '_')

        field_name = self.fieldmap.get(field_name, field_name)
        return field_name

    def _get_hasher_from_tag(self, header_tag: str) -> tp.Tuple[tp.Union[None, tp.Callable], str]:
        algo = header_tag.rsplit(':', 1)[-1]
        if algo in hashlib.algorithms_available:
            hasher = getattr(hashlib, algo)
        else:
            hasher = None
        return hasher, algo

    def _pseudonymise(self, suspect: Suspect, address: str, header_tag: str) -> str:
        if address:
            hasher, algo = self._get_hasher_from_tag(header_tag)
            if '@' in address:
                lhs, dom = split_mail(address)
            else:
                lhs = address
                dom = None
            if lhs is not None:
                try:
                    lhs = hasher(force_bString(lhs)).hexdigest()
                    if dom is not None:
                        return f'{lhs}@{dom}'
                    else:
                        return lhs
                except TypeError:
                    self.logger.error(f'{suspect.id} failed to pseudonymise {address} with lhs {lhs}')
        return address

    def _normalise_header(self, suspect: Suspect, header_name: str, header_tag: str, header_value: str) -> str:
        header_name = header_name.lower()
        header_value = header_value.strip()
        if header_tag is not None:
            header_tag = header_tag.lower()
            if header_tag.startswith('hash'):
                hasher, algo = self._get_hasher_from_tag(header_tag)
                if hasher is not None:
                    try:
                        header_value = hasher(force_bString(header_value)).hexdigest()
                    except TypeError as e:
                        self.logger.error(f"{suspect.id} hasher({str(hasher)}) problem ({str(e)}) for header tag:{header_tag} and value:{header_value} -> bytes:{force_bString(header_value)}")
                        header_value = None
                else:
                    self.logger.info(f'{suspect.id} unsupported hash algorithm {algo} in header {header_name}')
            elif header_tag == 'low':
                header_value = header_value.lower()
            elif header_tag == 'decode':
                header_value = suspect.decode_msg_header(header_value, logid=suspect.id)
            elif header_name in ['from', 'to', 'reply-to', 'sender']:
                try:
                    parsed_header = suspect.parse_from_type_header(header=header_name, validate_mail=True)
                    if parsed_header:
                        display, address = parsed_header[0]
                        if header_tag == 'addr':
                            header_value = address
                        elif header_tag == 'name':
                            header_value = display
                        elif header_tag == 'namedecode':
                            header_value = suspect.decode_msg_header(display, logid=suspect.id)
                        elif header_tag.startswith('pseudo:'):
                            header_value = self._pseudonymise(suspect, address, header_tag)
                        else:
                            self.logger.warning(f'{suspect.id} invalid header tag {header_tag} in header {header_name}')
                except Exception as e:
                    self.logger.warning(f'{suspect.id} error extracting {header_name} address: {e.__class__.__name__}: {str(e)}')
                    header_value = None
        if header_name == 'message_id':  # make sure all message ids get logged with leading and trailing <> for normalised search
            if not header_value.startswith('<'):
                header_value = f'<{header_value}'
            if not header_value.endswith('>'):
                header_value = f'{header_value}>'

        return header_value

    def _get_suspect_header_data(self, suspect: Suspect) -> tp.Dict[str, str]:
        logdata = {}
        msg_header_data = self.config.getlist(self.section, 'log_headers')
        msgrep = suspect.get_message_rep()
        for header_name_tag in msg_header_data:
            if ':' in header_name_tag:
                header_name, header_tag = header_name_tag.split(':', 1)
            else:
                header_tag = None
                header_name = header_name_tag
            header_value = msgrep.get(header_name)
            if isinstance(header_value, Header):
                try:
                    header_value = str(header_value)
                except Exception:
                    header_value = header_value.encode()
            if header_value:
                header_value = self._normalise_header(suspect, header_name, header_tag, header_value)
                if header_value:
                    header_name = self._normalise_fieldname(f'hdr_{header_name_tag}')
                    logdata[header_name] = header_value
        return logdata

    def _get_env_override(self, suspect: Suspect, configoption) -> tp.Union[None, str]:
        env_headers = self.config.getlist(self.section, configoption)
        if env_headers:
            for header in env_headers:
                value = suspect.get_header(header)
                if value and '@' in value:
                    return value
        return None

    def _get_suspect_attr(self, suspect: Suspect, attr: str):
        value = None
        override = True
        if attr in ['from_address', 'from_domain', 'from_localpart']:
            value = self._get_env_override(suspect, 'log_header_as_env_sender')
            if value and attr == 'from_domain':
                value = domain_from_mail(value)
            elif value and attr == 'from_localpart':
                value = split_mail(value)[0]
            if value:
                value = value.lower()
        elif attr in ['to_address', 'to_domain', 'to_localpart']:
            value = self._get_env_override(suspect, 'log_header_as_env_recipient')
            if value and attr == 'to_domain':
                value = domain_from_mail(value)
            elif value and attr == 'to_localpart':
                value = split_mail(value)[0]
            if value:
                value = value.lower()
        else:
            override = False

        if not override or value is None:
            try:
                value = force_uString(getattr(suspect, attr))
            except AttributeError:
                self.logger.debug(f'{suspect.id} no suspect attribute {attr}')
        return value

    def _get_suspect_fields(self, suspect: Suspect) -> tp.Dict[str, str]:
        logdata = {}
        suspect_fields = self.config.getlist(self.section, 'log_values')
        tagged_fields = {}
        for field in suspect_fields:
            if ':' in field:
                real_field, field_tag = field.split(':', 1)
                tagged_fields[real_field] = field_tag
            else:
                real_field = field
                field_tag = None
            value = self._get_suspect_attr(suspect, real_field)
            if field_tag and field_tag.startswith('pseudo:') and value:
                value = self._pseudonymise(suspect, value, field_tag)
            if field_tag and (field_tag == 'low' or field_tag.startswith('low:')) and value:
                value = value.lower()
            key = self._normalise_fieldname(field)
            logdata[key] = value
        return logdata
    
    def _get_milter_macros(self, suspect: Suspect) -> tp.Dict[str, str]:
        logdata = {}
        milter_macros = self.config.getlist(self.section, 'log_milter_macros')
        for mm in milter_macros:
            value = suspect.milter_macros.get(mm)
            key = self._normalise_fieldname(mm)
            logdata[key] = value
        return logdata

    def _get_suspect_funcs(self, suspect: Suspect) -> tp.Dict[str, bool]:
        logdata = {}
        status = suspect.get_status()
        for func_name in status:
            key = self._normalise_fieldname(func_name)
            logdata[key] = status[func_name]
        return logdata

    def _get_suspect_tags(self, suspect: Suspect) -> tp.Dict[str, tp.Union[str, bool, int, float]]:
        logdata = {}
        suspect_tags = self.config.getlist(self.section, 'log_tags')
        for tag in suspect_tags:
            value = suspect.get_tag(tag)
            if value is not None:
                key = self._normalise_fieldname(tag)
                if isinstance(value, (list, dict)):
                    try:
                        json.dumps(value)
                    except Exception as e:
                        self.logger.warning(f'{suspect.id} failed to convert tag {tag} to json data due to {e.__class__.__name__} {str(e)} with value {value}')
                elif not isinstance(value, (bool, int, float)):
                    value = force_uString(value)
                logdata[key] = value
        return logdata

    def _get_raw_headers(self, suspect: Suspect, header_names: tp.List[str]) -> tp.List[tp.Dict[str, str]]:
        allhdr = header_names[0] == 'all'
        headerdata = []
        hdrline = 0
        add_headers = list(suspect.addheaders.items())
        msgrep = suspect.get_message_rep()
        msg_headers = msgrep.items()
        headers = add_headers + msg_headers
        hdrlines = len(headers)
        for hdr_name, hdr_content in headers:
            hdr_name_low = hdr_name.lower()
            if not (allhdr or hdr_name_low in header_names):
                continue
            hdrline += 1
            hdrdata = {}
            hdrdata['headerlines'] = hdrlines  # how many lines will be written in log
            hdrdata['line'] = hdrline  # current line number
            hdrdata['header'] = hdr_name
            hdrdata['iheader'] = hdr_name_low
            hdrdata['content'] = force_uString(hdr_content).strip()
            headerdata.append(hdrdata)
        return headerdata

    def _get_virus_reports(self, suspect: Suspect) -> tp.List[tp.Dict[str, str]]:
        logdata = []
        engines = suspect.get_tag('virus', {})
        for engine in engines.keys():
            if engines[engine]:
                virusreport = suspect.get_tag(f'{engine}.virus')
                for item in virusreport:
                    logitem = {}
                    logitem['engine'] = engine
                    logitem['file'] = item
                    logitem['virus'] = virusreport[item]
                    logdata.append(logitem)
            else:
                self.logger.debug(f'{suspect.id} no virus report to log for engine {engine}')
        return logdata

    def _get_blocked_reports(self, suspect: Suspect) -> tp.List[tp.Dict[str, str]]:
        logdata = []
        engines = suspect.get_tag('blocked', {})
        for engine in engines.keys():
            if engines[engine]:
                blockreport = suspect.get_tag(f'{engine}.blocked')
                for item in blockreport:
                    logitem = {}
                    logitem['engine'] = engine
                    logitem['file'] = item
                    logitem['blockinfo'] = blockreport[item]
                    logdata.append(logitem)
            else:
                self.logger.debug(f'{suspect.id} no blocked report to log for engine {engine}')
        return logdata

    def _get_spam_reports(self, suspect: Suspect) -> tp.List[tp.Dict[str, str]]:
        logdata = []
        engines = suspect.get_tag('spam', {})
        for engine in engines.keys():
            logitem = {}
            logitem['spam'] = suspect.get_tag('spam', {}).get(engine, False)
            logitem['highspam'] = suspect.get_tag('highspam', {}).get(engine, False)
            logitem['report'] = force_uString(suspect.get_tag(f'{engine}.report'))
            for key in ['score', 'skipreason', 'stripped']:
                value = suspect.get_tag(f'{engine}.{key}')
                if value or isinstance(value, (bool, int, float)):
                    # log for integer/float also if value is 0 (which evaluates to False otherwise...) or boolean False
                    logitem[key] = value
            logdata.append(logitem)
        return logdata

    def _get_log_userdata(self, suspect: Suspect, logdata: tp.Dict) -> tp.Dict[str, tp.Union[str, bool, int, float]]:
        logdata.update(self._get_suspect_tags(suspect))
        return logdata
    
    def _get_log_coredata(self, suspect: Suspect) -> tp.Dict[str, tp.Union[str, bool, int, float]]:
        logdata = {}
        logdata.update(self._get_suspect_fields(suspect))
        logdata.update(self._get_milter_macros(suspect))
        logdata.update(self._get_suspect_funcs(suspect))
        logdata.update(self._get_suspect_header_data(suspect))

        header_names = self.config.getlist(self.section, 'log_raw_headers')
        headers = self._get_raw_headers(suspect, header_names)
        if headers:
            logdata['headers'] = headers

        spamreport = self._get_spam_reports(suspect)
        if spamreport:
            logdata['spamreport'] = spamreport

        virusreport = self._get_virus_reports(suspect)
        if virusreport:
            logdata['virusreport'] = virusreport

        blockreport = self._get_blocked_reports(suspect)
        if blockreport:
            logdata['blockedreport'] = blockreport

        maxatt = self.config.getint(self.section, 'log_attachments')
        if maxatt > 0:
            try:
                att = self.attlogger.get_all_attachments(suspect, maxatt)
                if att:
                    logdata['attachments'] = att
            except Exception as e:
                self.logger.error(f'{suspect.id} failed to extract attachments: {e.__class__.__name__}: {str(e)}')
                self.logger.debug(f'{suspect.id} failed to extract attachments', exc_info=e)
                suspect.set_tag('loggererror', True)

        maxuri = self.config.getint(self.section, 'log_uris')
        if maxuri > 0:
            uris = self.urilogger.get_all_uris(suspect, maxuri)
            emails = self.urilogger.get_all_emails(suspect, maxuri)
            uris.extend(emails)
            if uris:
                logdata['uris'] = uris

        return logdata

    def _log_to_file(self, suspect: Suspect, logdata: tp.Dict, rcpt_id: int) -> None:
        dirpath = self.config.get(self.section, 'fallback_logdir')
        if dirpath:
            if not os.path.exists(dirpath):
                self.logger.error(f'{suspect.id} inexisting log dump dir {dirpath} - logging to /tmp instead')
                dirpath = '/tmp'

            indexname = self.elasticbackend.get_elastic_index(suspect)
            filename = f'{suspect.id}_{rcpt_id}.json'
            indexpath = os.path.join(dirpath, indexname)
            filepath = os.path.join(indexpath, filename)
            try:
                jsondata = json.dumps(logdata)
                if not os.path.exists(indexpath):
                    os.mkdir(indexpath)
                with open(filepath, 'w') as f:
                    f.write(jsondata)
                self.logger.info(f'{suspect.id} dumped {len(jsondata)} bytes of json data to {filepath}')
            except Exception as e:
                self.logger.error(f'{suspect.id} failed to dump json data to {filepath} due to {e.__class__.__name__} {str(e)}')
    
    def _write_eml(self, suspect: Suspect) -> None:
        dirpath = self.config.get(self.section, 'error_write_eml_dir')
        if dirpath:
            if not os.path.exists(dirpath):
                self.logger.error(f'{suspect.id} inexisting eml write dir {dirpath} - writing to /tmp instead')
                dirpath = '/tmp'
            
            filepath = os.path.join(dirpath, f'{suspect.id}.eml')
            try:
                msgbytes = suspect.get_message_rep().as_bytes()
                with open(filepath, 'wb') as f:
                    f.write(msgbytes)
                self.logger.debug(f'{suspect.id} wrote {len(msgbytes)} bytes of mail content to {filepath}')
            except Exception as e:
                self.logger.error(f'{suspect.id} failed to write mail content to {filepath} due to {e.__class__.__name__} {str(e)}')
    
    
    def _normalise_address(self, address: str) -> str:
        address = strip_batv(address)
        address = decode_srs(address)
        address = address.lower()
        return address
    
    def _get_sender_address(self, suspect:Suspect) -> str:
        sender_address = suspect.get_tag('log.real_from_address')
        if not sender_address:
            for headername in ['sender', 'from']:
                from_addresses = suspect.parse_from_type_header(header=headername)
                if from_addresses and from_addresses[0] and from_addresses[0][1] and '@' in from_addresses[0][1]:
                    sender_address = from_addresses[0][1]
                    if sender_address:
                        self.logger.debug(f'{suspect.id} got sender_address={sender_address} from hdr={headername}')
                        break
        else:
            self.logger.debug(f'{suspect.id} got sender_address={sender_address} from env')
        return sender_address

    async def _add_tags(self, suspect: Suspect, decision: tp.Union[None, str] = None) -> None:
        suspect.set_tag('log.scanhost', get_outgoing_helo(self.config))
        suspect.set_tag('recipient_count', len(suspect.recipients))
        suspect.set_tag('log.processtime', time.time()-suspect.timestamp)

        if decision is not None:
            suspect.set_tag('log.decision', actioncode_to_string(decision))

        clientinfo = suspect.get_client_info(self.config)
        if clientinfo is not None:
            clienthelo, clientip, clienthostname = clientinfo
            suspect.set_tag('log.client_helo', clienthelo)
            suspect.set_tag('log.client_ip', clientip)
            suspect.set_tag('log.client_hostname', clienthostname)
            if clienthostname == 'unknown':
                ptrs = await fuglu.extensions.aiodnsquery.revlookup(clientip)
                if ptrs:
                    suspect.set_tag('log.client_hostnames', ptrs)
                    self.logger.debug(f'{suspect.id} found unverified ptrs for {clientip}: {", ".join(ptrs)}')

        from_address = suspect.from_address
        if not from_address:
            from_address = self._get_env_override(suspect, 'log_header_as_env_sender')
        if from_address:
            try:
                real_from_address = self._normalise_address(from_address)
                real_from_localpart, real_from_domain = split_mail(real_from_address)
                suspect.set_tag('log.real_from_address', real_from_address)
                suspect.set_tag('log.real_from_domain', real_from_domain)
                suspect.set_tag('log.real_from_localpart', real_from_localpart)
            except Exception as e:
                self.logger.warning(f'{suspect.id} could not normalise address {suspect.from_address} error was {e.__class__.__name__} {str(e)}')
        
        sender_address = self._get_sender_address(suspect)
        if sender_address:
            sender_address = self._normalise_address(sender_address)
            sender_localpart, sender_domain = split_mail(sender_address)
            suspect.set_tag('log.sender_address', sender_address)
            suspect.set_tag('log.sender_domain', sender_domain)
            suspect.set_tag('log.sender_localpart', sender_localpart)

    async def process(self, suspect: Suspect, decision: str) -> None:
        if not HAVE_DOMAINMAGIC:
            self.logger.warning(f'{suspect.id} not logging: domainmagic not available')
            return

        self._init_components()
        es = self.elasticbackend.get_elastic_connection()
        if es is None:
            self.logger.warning(f'{suspect.id} not logging: cannot get elastic connection')
            return
        try:
            await es.close()
        except Exception as e:
            self.logger.warning(f'{suspect.id} failed to close elastic connection {e.__class__.__name__}: {str(e)}')
        
        timeout = self.config.getint(self.section, 'timeout')
        suspect.stimeout_set_timer(self.section, timeout)
        await self._add_tags(suspect, decision)
        core_logdata = self._get_log_coredata(suspect)
        await self._async_process(suspect, core_logdata)
        
        
    async def _async_process(self, suspect, core_logdata):
        rcpt_id = 0
        rcpt_count = len(suspect.recipients)
        tasks = []
        all_logdata = {}
        retry = self.config.getint(self.section, 'elastic_retry')
        for recipient in suspect.recipients:
            #self.logger.debug(f'{suspect.id} preparing log data for recipient={recipient} with rcpt_id={rcpt_id}')
            recipient = recipient.lower()
            suspect.set_tag('to_address', recipient)
            suspect.set_tag('to_domain', domain_from_mail(recipient))
            suspect.set_tag('to_localpart', split_mail(recipient)[0])
            suspect.set_tag('recipient_id', rcpt_id)
            suspect.set_tag('insidemail', suspect.get_tag('log.sender_domain') == suspect.get_tag('to_domain'))
            logdata = self._get_log_userdata(suspect, copy.deepcopy(core_logdata))
            all_logdata[rcpt_id] = logdata
            if retry >= 0: # disable elastic and dump straight to json file if retry is negative
                future = self.elasticbackend.log_to_elastic(suspect, logdata, rcpt_id, retry=retry)
                tasks.append(future)
            else:
                self.logger.warning(f'{suspect.id} retry={retry} not writing to elastic')
            rcpt_id += 1
            if not suspect.stimeout_continue(self.section) and rcpt_id<rcpt_count:
                self.logger.error(f'{suspect.id} exceeded elastic data aggregation timeout after {rcpt_id} / {rcpt_count} recipients')
                self._log_to_file(suspect, logdata, rcpt_id)
                
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f'{suspect.id} failed to index in elastic due to {result.__class__.__name__} {str(result)}')
            else:
                rcpt_id = result['rcpt_id']
                self.logger.info(f'{suspect.id} processed {len(str(all_logdata[rcpt_id]))}b with result {dict2str(result)}')
                del all_logdata[rcpt_id]
        for rcpt_id in all_logdata:
            self._log_to_file(suspect, all_logdata[rcpt_id], rcpt_id)
        
        if suspect.get_tag('loggererror') is True:
            self._write_eml(suspect)

    def lint(self):
        if not HAVE_DOMAINMAGIC:
            print('ERROR: domainmagic library missing, this plugin will do nothing')
            return False

        if not lint_elastic():
            return False

        self._init_components()
        es = self.elasticbackend.get_elastic_connection()
        if es is None:
            print('WARNING: elastic_uris not defined, this plugin will do nothing')
            return False
        elif not es.ping():
            elastic_uris = self.config.getlist(self.section, 'elastic_uris', resolve_env=True)
            print(f'ERROR: failed to connect to elasticsearch {", ".join([redact_uri(u) for u in elastic_uris])}, connection info: {str(es)}')
            return False

        dirpath = self.config.get(self.section, 'fallback_logdir')
        if dirpath and not os.path.exists(dirpath):
            print(f'ERROR: fallback logdir {dirpath} does not exist')
            return False

        invalid_hashes = [h for h in self.config.getlist(self.section, 'log_attachment_hashes') if h not in hashlib.algorithms_available]
        if invalid_hashes:
            print(f'ERROR: invalid hash algorithms in log_attachment_hashes: {",".join(invalid_hashes)}')
            return False

        # superficial lint of mapping...
        mapping_file = self.config.get(self.section, 'elastic_mapping_file')
        new_mapping = self.elasticbackend._get_mapping(mapping_file)
        try:
            for key in new_mapping['properties']:
                if not new_mapping['properties'][key]['type']:
                    print(f'empty value in key {key}')
                    return False
        except KeyError as e:
            print(str(e))
            return False
        
        retry = self.config.getint(self.section, 'elastic_retry')
        if retry < 0:
            print(f'WARNING: retry={retry} not writing to elastic')
        
        replicas = self.config.get(self.section, 'elastic_replicas', resolve_env=True)
        try:
            replicas = int(replicas)
        except (TypeError, ValueError):
            replicas = None

        if replicas is not None:
            print(f'INFO: setting to {replicas} replicas when creating indices')
        else:
            print(f'INFO: not overriding number of replicas...')

        return True


class ElasticImport(object):
    def __init__(self, configfile):
        self.config = FuConfigParser()
        if os.path.exists(configfile):
            with open(configfile) as fp:
                self.config.read_file(fp)
        else:
            print(f'ERROR: no such config {configfile}')
        self.section = 'ElasticLogger'
        self.backend = ElasticBackend(self.config, 'ElasticLogger')

    def _log_to_elastic(self, indexname, suspectid, logdata):
        es = self.backend.get_elastic_connection()
        self.backend._set_index_mapping(indexname)
        success = True
        timeout = self.config.getfloat(self.section, 'elastic_timeout', fallback=30)
        r = es.index(index=indexname, id=suspectid, body=logdata, request_timeout=timeout)
        if not '_id' in r:
            print(f'{suspectid} key _id not found in result {r}')
            success = False
        print(f'{suspectid} indexed in elastic {indexname}: {dict2str(r)}')
        return success

    def load_files(self, cleanup=True):
        dirpath = self.config.get(self.section, 'fallback_logdir')
        if not dirpath:
            print('fallback_logdir not set, nothing to do')
        else:
            indexnames = [x[1] for x in os.walk(dirpath)][0]
            for indexname in indexnames:
                filenames = [x[2] for x in os.walk(os.path.join(dirpath, indexname))][0]
                for filename in filenames:
                    if filename.endswith('.json'):
                        suspectid = filename.rsplit('.')[0]
                        filepath = os.path.join(dirpath, indexname, filename)
                        with open(filepath) as fp:
                            filecontent = json.load(fp)
                        try:
                            if re.match(r'^[0-9]+\.[0-9]+$', filecontent['timestamp']):
                                ts = float(filecontent['timestamp'])
                                dt = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).isoformat()
                                filecontent['timestamp'] = dt
                                print(f'WARNING: found timestamp as {ts} converted to {dt}')
                            success = self._log_to_elastic(indexname, suspectid, filecontent)
                            if success and cleanup:
                                os.remove(filepath)
                        except Exception as e:
                            print(f'failed to import {filepath} due to {e.__class__.__name__}: {str(e)}')
            if cleanup:
                self._cleanup_dirs(dirpath)

    def _cleanup_dirs(self, dirpath):
        indexnames = [x[1] for x in os.walk(dirpath)][0]
        for indexname in indexnames:
            abspath = os.path.join(dirpath, indexname)
            filenames = [x[2] for x in os.walk(abspath)][0]
            if not filenames:
                os.rmdir(abspath)
                print(f'removed empty dir {abspath}')


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--mapping', help='print elastic index mapping and quit', action='store_true')
    parser.add_argument(
        '--import', help='import json files stored in fallback_logdir. expects path to config file as argument. Config file must have a section [ElasticLogger]', default='/etc/fuglu/conf.d/logging.conf')
    parser.add_argument('--keepfiles', help='do not remove files that were imported successfully', action='store_true')
    args = parser.parse_args()
    importconfig = getattr(args, 'import')
    if not os.path.isfile(importconfig):
        importconfig = None

    if not args.mapping and not importconfig:
        parser.print_help()
        sys.exit(1)
    elif args.mapping:
        print('Logger indices mapping:')
        print(json.dumps(LOG_MAPPING))
        sys.exit(0)
    elif importconfig:
        elimp = ElasticImport(importconfig)
        try:
            elimp.load_files(not args.keepfiles)
        except KeyboardInterrupt:
            print('aborted by user')
            sys.exit(0)
