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

import contextlib
import json
import typing as tp
import os
from fuglu.caching import smart_cached_memberfunc
from fuglu.shared import FileList, redact_uri

DISTRO_NONE = 0
DISTRO_ELASTIC = 1
DISTRO_OPEN = 2


HAVE_ELASTICSEARCH = DISTRO_NONE
try:
    import elasticsearch
    elasticclientlib = elasticsearch
    ElasticClient = elasticsearch.Elasticsearch
    AsyncElasticClient = elasticsearch.AsyncElasticsearch
    class ElasticException(Exception): # until elasticsearch 7.x, no longer available in elasticsearch 9.x
        pass
    HAVE_ELASTICSEARCH = DISTRO_ELASTIC
    STATUS = f'available, using elasticsearch {elasticsearch.__versionstr__}'
except ImportError:
    try:
        import opensearchpy
        elasticclientlib = opensearchpy
        ElasticClient = opensearchpy.OpenSearch
        AsyncElasticClient = opensearchpy.AsyncOpenSearch
        ElasticException = opensearchpy.exceptions.OpenSearchException
        HAVE_ELASTICSEARCH = DISTRO_OPEN
        STATUS = f'available, using opensearch {opensearchpy.__versionstr__}'
    except ImportError:
        elasticclientlib = None
        ElasticClient = None
        AsyncElasticClient = None
        STATUS = f'elasticsearch not installed'

        class ElasticException(Exception):
            pass

if HAVE_ELASTICSEARCH > DISTRO_NONE:
    # silence excessive error logging by urllib3
    elasticclientlib.logger.setLevel(50)

ENABLED = HAVE_ELASTICSEARCH != DISTRO_NONE

def lint_elastic():
    if HAVE_ELASTICSEARCH == DISTRO_NONE:
        print('ERROR: elasticsearch or opensearch library not available')
        return False
    elif HAVE_ELASTICSEARCH == DISTRO_ELASTIC:
        print(f'INFO: Elastic Distro is ElasticSearch, library version {elasticclientlib.__versionstr__}')
    elif HAVE_ELASTICSEARCH == DISTRO_OPEN:
        print(f'INFO: Elastic Distro is OpenSearch, library version {elasticclientlib.__versionstr__}')
    return True


class MappingFile(FileList):
    def _parse_lines(self, lines):
        content = '\n'.join(lines)
        try:
            jsoncontent = json.loads(content)
        except Exception as e:
            self.logger.error(f'failed to load json data: {e.__class__.__name__}: {str(e)}')
            jsoncontent = None
        return jsoncontent
    

class ElasticMixin:
    """
    ElasticSearch Mixin class for Plugins
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requiredvars.update({
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
            'elastic_replicas': {
                'default': '',
                'description': 'override number of replicas. leave empty for default.',
            },
            'elastic_mapping_file': {
                'default': '',
                'description': 'read elastic mapping from json file. leave empty to use default mapping.',
            },
        })
        self.mapping_file = None
    
    
    @contextlib.contextmanager
    async def get_elastic_connection(self) -> AsyncElasticClient:
        elastic_uris = self.config.getlist(self.section, 'elastic_uris', resolve_env=True)
        if elastic_uris:
            verify_certs = self.config.getboolean(self.section, 'elastic_verify_certs')
            timeout = self.config.getfloat(self.section, 'elastic_timeout', fallback=30)
            es = AsyncElasticClient(hosts=elastic_uris, verify_certs=verify_certs, ssl_show_warn=False, timeout=timeout)
        
            try:
                yield es
            finally:
                await es.close()
    

    def _get_mapping(self, mapping_file:str, mapping:str) -> tp.Dict[str,tp.Any]:
        if not self.mapping_file and mapping_file and os.path.exists(mapping_file):
            self.mapping_file = MappingFile(filename=mapping_file)
        if self.mapping_file:
            loaded_mapping = self.mapping_file.get_list()
            if not loaded_mapping:
                self.logger.error(f'mapping file {mapping_file} could not be loaded')
            else:
                mapping = loaded_mapping
        return mapping
    
    
    @smart_cached_memberfunc(inputs=[])
    async def _set_index_mapping(self, indexname: str, mapping: str) -> None:
        self.logger.info(f'checking mapping of index {indexname}')
        async with self.get_elastic_connection() as es:
            exists = await es.indices.exists(index=indexname)
            if exists:
                need_put = False
                current_mapping = await es.indices.get_mapping(index=indexname)
                properties = current_mapping.get(indexname, {}).get('mappings', {}).get('properties', {})
                
                mapping_file = self.config.get(self.section, 'elastic_mapping_file', fallback='')
                new_mapping = self._get_mapping(mapping_file, mapping)
                
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
                        r = await es.indices.put_mapping(body=new_mapping, index=indexname)
                    except ElasticException as e:
                        r = {'exc': e.__class__.__name__, 'msg': str(e)}
                    if r.get('acknowledged'):
                        self.logger.info(f'put new mapping to elastic index {indexname}')
                    else:
                        self.logger.info(f'error putting new mapping to elastic index {indexname} : {str(r)}\n'
                                         f'Input data body ways:\n'
                                         f'{json.dumps(new_mapping, indent=4)}')
                else:
                    self.logger.debug(f'no need to update mapping of elastic index {indexname}')
            else:
                log_mapping = {'mappings': mapping}
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
    
    async def _lint(self):
        ok = lint_elastic()
        if ok:
            async with self.get_elastic_connection() as es:
                if es is None:
                    print('WARNING: elastic_uris not defined, this plugin will do nothing')
                    ok = False
                elif not es.ping():
                    elastic_uris = self.config.getlist(self.section, 'elastic_uris', resolve_env=True)
                    print(f'ERROR: failed to connect to elasticsearch {", ".join([redact_uri(u) for u in elastic_uris])}, connection info: {str(es)}')
                    ok = False
        return ok
        