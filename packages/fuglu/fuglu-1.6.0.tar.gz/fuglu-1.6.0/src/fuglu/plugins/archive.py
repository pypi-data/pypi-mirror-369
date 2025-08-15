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
from fuglu.shared import ScannerPlugin, DUNNO, SuspectFilter, apply_template, get_outgoing_helo, Suspect, redact_uri, utcnow
from fuglu.stringencode import force_uString, force_bString
from fuglu.extensions.elastic import ElasticClient, lint_elastic, ElasticException, AsyncElasticClient
from fuglu.caching import smart_cached_memberfunc
from fuglu.utils.version import get_main_version
import os
import shutil
import pwd
import grp
import logging
import time
import smtplib
import socket
import datetime
from collections import OrderedDict
from base64 import b64encode
from urllib.parse import urljoin
import urllib.request
import typing as tp
import asyncio
from contextlib import asynccontextmanager

try:
    from cassandra.cluster import Cluster
    from cassandra.policies import RoundRobinPolicy
    from cassandra import __version__ as cassandraversion
    HAVE_CASSANDRA = True
except ImportError:
    HAVE_CASSANDRA = False

try:
    import boto3
    from botocore.exceptions import ClientError as S3ClientError
    from botocore.client import Config as S3Config
    HAVE_S3 = True
except ImportError:
    HAVE_S3 = False
    
try:
    import aioboto3
    from botocore.exceptions import ClientError as S3ClientError
    HAVE_AIOS3 = True
except ImportError:
    HAVE_AIOS3 = False

try:
    import aiohttp
    HAVE_AIOHTTP = True
except ImportError:
    HAVE_AIOHTTP = False


LOG_MAPPING = {
    "properties": {
        "blob": {
            "type": "binary"
        }
    }
}

class ArchiveException(Exception):
    pass

class AbstractBackend(object):
    requiredvars = {}

    def __init__(self, config, section):
        self.config = config
        self.section = section
        self.logger = logging.getLogger(f'fuglu.plugin.archive.{self.__class__.__name__}')

    def __str__(self):
        return self.__class__.__name__

    def archive(self, suspect: Suspect, fugluid_override: str=None) -> tp.Dict[str,str]:
        """
        writes to actual archive. raise exception if archiving failed
        :param suspect: the suspect object
        :param fugluid_override: an alternative fuglu/suspect id to be logged instead of suspect.id
        :return: dict with result data
        """
        raise NotImplementedError()

    def lint(self):
        raise NotImplementedError()

    def _get_msg_source(self, suspect: Suspect, original:bool=True) -> bytes:
        if original:
            content = suspect.get_original_source()
        else:
            content = suspect.get_source()
        return content


class LocalDirBackend(AbstractBackend):
    """
    This is the default backend. It stores mail in a local directory.
    Status: Mature
    """
    requiredvars = {
        'local_archivedir': {
            'default': '/tmp',
            'description': 'storage for archived messages',
        },
        'local_subdirtemplate': {
            'default': '${to_domain}/${to_localpart}/${date}',
            'description': 'subdirectory within archivedir',
        },
        'local_filenametemplate': {
            'default': '${archiveid}.eml',
            'description': 'filename template for the archived messages',
        },
        'local_useoriginal': {
            'default': 'True',
            'description': "if true/1/yes: store original message\nif false/0/no: store message probably altered by previous plugins, eg with spamassassin headers",
        },
        'local_chown': {
            'default': '',
            'description': "change owner of saved messages (username or numeric id) - this only works if fuglu is running as root (which is NOT recommended)",
        },
        'local_chgrp': {
            'default': '',
            'description': "change group of saved messages (groupname or numeric id) - the user running fuglu must be a member of the target group for this to work",
        },
        'local_chmod': {
            'default': '',
            'description': "set file permissions of saved messages",
        },
    }

    def archive(self, suspect, fugluid_override=None):
        archivedir = self.config.get(self.section, 'local_archivedir')
        if archivedir == "":
            self.logger.error(f'{suspect.id} Archivedir is not specified')
            return

        subdirtemplate = self.config.get(self.section, 'local_subdirtemplate')

        # the archive root dir
        startdir = os.path.abspath(archivedir)

        # relative dir within archive root
        subdir = apply_template(subdirtemplate, suspect)
        if subdir.endswith('/'):
            subdir = subdir[:-1]
        if subdir.startswith('/'):
            subdir = subdir[1:]

        # filename without dir
        filenametemplate = self.config.get(self.section, 'local_filenametemplate')

        values = {
            'archiveid': fugluid_override or suspect.id,
        }
        filename = apply_template(filenametemplate, suspect, values)
        # make sure filename can't create new folders
        filename = filename.replace('/', '_')

        # absolute final filepath
        requested_path = os.path.join(startdir, subdir, filename)

        finaldir = os.path.dirname(requested_path)
        if not os.path.isdir(finaldir):
            os.makedirs(finaldir, 0o755)

        if self.config.getboolean(self.section, 'local_useoriginal'):
            shutil.copy(suspect.tempfile, requested_path)
        else:
            with open(requested_path, 'wb') as fp:
                # write bytes
                fp.write(suspect.get_source())

        chmod = self.config.get(self.section, 'local_chmod')
        chgrp = self.config.get(self.section, 'local_chgrp')
        chown = self.config.get(self.section, 'local_chown')
        if chmod or chgrp or chown:
            self._setperms(requested_path, chmod, chgrp, chown, suspect.id)

        self.logger.info(f'{suspect.id} Message from {suspect.from_address} to {suspect.to_address} archived as {requested_path}')
        return dict(filepath=requested_path)

    def lint(self):
        archivedir = self.config.get(self.section, 'local_archivedir')
        if archivedir == "":
            print('Archivedir is not specified')
            return False

        if not os.path.isdir(archivedir):
            print(f"Archivedir {archivedir} does not exist or is not a directory")
            return False

        return True

    def _setperms(self, filename, chmod, chgrp, chown, fugluid):
        """Set file permissions and ownership
        :param filename The target file
        :param chmod string representing the permissions (example '640')
        :param chgrp groupname or group id of the target group. the user running fuglu must be a member of this group for this to work
        :param chown username or user id of the target user. fuglu must run as root for this to work (which is not recommended for security reasons)
        """

        # chmod
        if chmod:
            perm = int(chmod, 8)
            try:
                os.chmod(filename, perm)
            except Exception:
                self.logger.error(f'{fugluid }could not set permission on file {filename}')

        # chgrp
        changetogroup = -1
        if chgrp:
            group = None
            try:
                group = grp.getgrnam(chgrp)
            except KeyError:
                pass

            if group is None:
                try:
                    group = grp.getgrgid(int(chgrp))
                except (KeyError, ValueError):
                    pass

            if group is not None:
                changetogroup = group.gr_gid
            else:
                self.logger.warning(f'{fugluid} Group {chgrp} not found')

        # chown
        changetouser = -1
        if chown:
            user = None
            try:
                user = pwd.getpwnam(chown)
            except KeyError:
                pass

            if user is None:
                try:
                    user = pwd.getpwuid(int(chown))
                except (KeyError, ValueError):
                    pass

            if user is not None:
                changetouser = user.pw_uid
            else:
                self.logger.warning(f'{fugluid} User {chown} not found')

        if changetogroup != -1 or changetouser != -1:
            try:
                os.chown(filename, changetouser, changetogroup)
            except Exception as e:
                self.logger.error(f'{fugluid} Could not change user/group of file {filename} : {e.__class__.__name__}: {str(e)}')


class ElasticBackend(AbstractBackend):
    """
    This backend stores mail in ElasticSearch.
    Status: Mature (using opensearch)
    """
    requiredvars = {
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
        'elastic_index': {
            'default': 'fugluquar-${date}',
            'description': 'Name of ElasticSearch index in which document will be stored. Template vars (e.g. ${to_domain} or ${date}) can be used.',
        },
        'elastic_replicas': {
            'default': '',
            'description': 'override number of replicas. leave empty for default.',
        },
        'elastic_extrafields': {
            'default': '',
            'description': 'comma separated list of additional fields to be added to document. Any fuglu Suspect variable is permitted (e.g. to_address)',
        },
        'elastic_useoriginal': {
            'default': 'True',
            'description': """should we store the original message as retreived from postfix or store the
                                current state in fuglu (which might have been altered by previous plugins)""",
        },
    }
    elastic_connection = {}
    
    def get_elastic_connection(self, use_async: bool = False) -> tp.Union[ElasticClient, AsyncElasticClient]:
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
    
    def _get_elastic_index(self, suspect):
        indextmpl = self.config.get(self.section, 'elastic_index')
        indexname = apply_template(indextmpl, suspect)
        return indexname

    @smart_cached_memberfunc(inputs=[])
    async def _set_index_mapping(self, indexname: str) -> None:
        self.logger.info(f'checking mapping of index {indexname}')
        es = self.get_elastic_connection(use_async=True)
        
        exists = await es.indices.exists(index=indexname)
        if exists:
            need_put = False
            current_mapping = await es.indices.get_mapping(index=indexname)
            properties = current_mapping.get(indexname, {}).get('mappings', {}).get('properties', {})

            new_mapping = LOG_MAPPING

            try:
                for key in new_mapping['properties']:
                    if not new_mapping['properties'][key]['type'] == properties.get(key, {}).get('type'):
                        need_put = True
                        self.logger.debug(f"mapping update required due to property of key '{key}'")
                        break
            except KeyError as e:
                need_put = False
                self.logger.error(f'invalid mapping: {e.__class__.__name__}: {str(e)}')

            if need_put:
                try:
                    r = await es.indices.put_mapping(body=LOG_MAPPING, index=indexname)
                except ElasticException as e:
                    r = {'exc': e.__class__.__name__, 'msg': str(e)}
                if r.get('acknowledged'):
                    self.logger.info(f'put new mapping to elastic index {indexname}')
                else:
                    self.logger.info(f'error putting new mapping to elastic index {indexname} : {str(r)}')
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
        await es.close()

    async def archive(self, suspect, fugluid_override=None, reload=False, retry=3):
        original = self.config.getboolean(self.section, 'elastic_useoriginal')
        content = self._get_msg_source(suspect, original)

        # store b64-encoded content if possible to account for malformed sources
        try:
            blob = b64encode(content).decode('ascii')
        except Exception as e:
            self.logger.warning(f"{suspect.id} Could not b64 encode blob due to: {str(e)}")
            blob = None
        doc = {
            'fugluid': fugluid_override or suspect.id,
            'fugluid_original': suspect.id,
            'content': None if blob else force_uString(content),
            'timestamp': datetime.datetime.fromtimestamp(suspect.timestamp, datetime.timezone.utc),
            'to_address': suspect.to_address.lower() if suspect.to_address else '',
            'to_domain': suspect.to_domain.lower() if suspect.to_domain else '',
            'blob': blob,
        }

        extrafields = self.config.getlist(self.section, 'elastic_extrafields')
        for field in extrafields:
            doc[field] = apply_template('${%s}' % field, suspect)
        
        result = await self.archive_elastic(suspect, doc, retry)
        return result
        
    async def archive_elastic(self, suspect: Suspect, doc: tp.Dict[str, tp.Any], retry:int = 3) -> tp.Dict[str,str]:
        result = {}
        timeout = self.config.getfloat(self.section, 'elastic_timeout', fallback=30)
        while retry > 0:
            retry -= 1
            try:
                es = self.get_elastic_connection(use_async=True)
                indexname = self._get_elastic_index(suspect)
                await self._set_index_mapping(indexname)
                try:
                    r = await es.index(index=indexname, id=suspect.id, body=doc, request_timeout=timeout)
                finally:
                    await es.close()
                for key in ['_id', 'result']:
                    try:
                        result[key] = r[key]
                    except KeyError:
                        self.logger.error(f'{suspect.id} key {key} not found in result {r}')

                self.logger.info(f'{suspect.id} indexed in elastic: {r}')
                retry = 0  # stop while loop
            except Exception as e:
                if retry > 0:
                    self.logger.debug(f'{suspect.id} failed to index in elastic, retry={retry} reason={e.__class__.__name__}: {str(e)}')
                    await asyncio.sleep(0.2*(4-retry))
                    result = await self.archive_elastic(suspect, doc, retry=retry-1)
                else:
                    raise
        return result

    def lint(self):
        if not lint_elastic():
            return False

        es = self.get_elastic_connection()
        if es is None:
            print('WARNING: elastic_uris not defined, this backend will do nothing')
            return False
        if not es.ping():
            elastic_uris = self.config.getlist(self.section, 'elastic_uris', resolve_env=True)
            print(f'ERROR: failed to connect to elasticsearch {", ".join([redact_uri(u) for u in elastic_uris])}, connection info: {str(es)}')
            return False
        
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


class CassandraBackend(AbstractBackend):
    """
    This backend stores mail in an Apache Cassandra database cluster.
    Status: abandoned (last used in 2018)
    """
    requiredvars = {
        'cassandra_hosts': {
            'default': '',
            'description': "quarantine cassandra hostnames, separated by comma",
        },
        'cassandra_keyspace': {
            'default': 'fugluquar',
            'description': "quarantine cassandra keyspace",
        },
        'cassandra_ttl': {
            'default': str(14*24*3600),
            'description': "ttl for quarantined files in seconds",
        },
        'cassandra_useoriginal': {
            'default': 'True',
            'description': """should we store the original message as retreived from postfix or store the
                                current state in fuglu (which might have been altered by previous plugins)""",
        },
    }

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.cassandra_session = None
        self.cass_prep_quarantine = None

    def get_cassandra_session(self):
        if self.cassandra_session is None:
            keyspace = self.config.get(self.section, 'cassandra_keyspace')
            # default idle_heartbeat_interval=30, we lower it to reduce write errors
            hosts = self.config.getlist(self.section, 'cassandra_hosts')
            lbp = RoundRobinPolicy()
            cassandra_cluster = Cluster(hosts, protocol_version=4, idle_heartbeat_interval=10, load_balancing_policy=lbp)
            self.cassandra_session = cassandra_cluster.connect(keyspace)

            self.cass_prep_quarantine = self.cassandra_session.prepare("INSERT INTO quarantine (fugluid, messagecontent) VALUES (?, ?)  USING TTL ?")
        return self.cassandra_session

    def _cassandra_store(self, suspect, fugluid_override, retry=3):
        """Store message source into cassandra"""
        ttl = self.config.getint(self.section, 'cassandra_ttl')
        original = self.config.getboolean(self.section, 'cassandra_useoriginal')
        content = self._get_msg_source(suspect, original)
        try:
            session = self.get_cassandra_session()
            fugluid = fugluid_override or suspect.id
            session.execute(self.cass_prep_quarantine, (fugluid, bytearray(content), ttl), timeout=20)
        except Exception as e:
            if retry > 0:
                self.logger.info(f'{suspect.id} failed to write to cassandra. try {retry}/3. error was: {e.__class__.__name__}: {str(e)}')
                time.sleep(0.1)
                self._cassandra_store(suspect, fugluid_override, retry-1)
            else:
                raise

    def archive(self, suspect, fugluid_override=None):
        result = {}
        self._cassandra_store(suspect, fugluid_override)
        self.logger.info(f'{suspect.id} stored in cassandra')
        result['success'] = True
        return result

    def lint(self):
        if not HAVE_CASSANDRA:
            print('ERROR: cassandra driver not available')
            return False

        print(f"INFO: Cassandra Driver Version: {cassandraversion}")

        try:
            self.get_cassandra_session().execute("SELECT * FROM quarantine WHERE fugluid='dummy'")
        except Exception as e:
            print(f"ERROR: cassandra connection failed: {e.__class__.__name__}: {str(e)}")
            return False

        return True


class S3Backend(AbstractBackend):
    """
    This backend stores mail in S3 (or compatible) storage
    Status: experimental
    """
    requiredvars = {
        's3_uri': {
            'default': '',
            'description': "s3 uri",
        },
        's3_bucket': {
            'default': 'fugluquar',
            'description': "quarantine s3 bucket name",
        },
        's3_access_id': {
            'default': '',
            'description': "s3 access id",
        },
        's3_access_key': {
            'default': '',
            'description': "s3 access secret key",
        },
        's3_ttl': {
            'default': str(14*24*3600),
            'description': "ttl for quarantined files in seconds",
        },
    }
    
    
    def _get_s3_connection(self):
        s3_uri = self.config.get(self.section, 's3_uri')
        s3_access_id = self.config.get(self.section, 's3_access_id')
        s3_access_key = self.config.get(self.section, 's3_access_key')
        
        config = S3Config(
           signature_version = 's3v4'
        )
        s3 = boto3.resource('s3',
                    endpoint_url=s3_uri,
                    aws_access_key_id=s3_access_id,
                    aws_secret_access_key=s3_access_key,
                    config=config)
        return s3
    
    def archive(self, suspect, fugluid_override=None):
        result = {'success': False}
        if not HAVE_S3:
            return result
        
        s3 = self._get_s3_connection()
        
        bucketname = self.config.get(self.section, 's3_bucket')
        ttl = self.config.getint(self.section, 's3_ttl')
        exp = utcnow() + datetime.timedelta(seconds=ttl)
        filename = f'{fugluid_override or suspect.id}.eml'
        try:
            s3.create_bucket(bucketname)
            s3obj = s3.Object(bucket_name=bucketname, key=filename)
            s3obj.put(
                Body=suspect.get_source(),
                ContentType='message/rfc822',
                Expires=exp,
            )
            result['success'] = True
        except S3ClientError as e:
            raise ArchiveException(f'{suspect.id} failed to write data to bucket {bucketname} as {filename} due to {str(e)}')
        return result

    def lint(self):
        if not HAVE_S3:
            print('ERROR: s3 library (boto3) not available')
            return False
        else:
            s3 = self._get_s3_connection()
            bucketname = self.config.get(self.section, 's3_bucket')
            try:
                s3.meta.client.head_bucket(Bucket=bucketname)
            except S3ClientError as e:
                s3_uri = self.config.get(self.section, 's3_uri')
                print(f'ERROR: failed to access {bucketname} on {s3_uri} due to {str(e)}')
                return False

        return True


class AIOS3Backend(AbstractBackend):
    """
    This backend stores mail in S3 (or compatible) storage
    Status: experimental
    """
    requiredvars = {
        'aios3_uri': {
            'default': '',
            'description': "s3 uri",
        },
        'aios3_region': {
            'default': '',
            'description': "s3 region",
        },
        'aios3_bucket': {
            'default': 'fugluquar',
            'description': "quarantine s3 bucket name",
        },
        'aios3_access_id': {
            'default': '',
            'description': "s3 access id",
        },
        'aios3_access_key': {
            'default': '',
            'description': "s3 access secret key",
        },
        'aios3_ttl': {
            'default': str(14*24*3600),
            'description': "ttl for quarantined files in seconds",
        },
        'aios3_timeout': {
            'default': '10',
            'description': "timeout of upload operation",
        },
    }
    
    async def archive(self, suspect, fugluid_override=None):
        result = {'success': False}
        if not HAVE_AIOS3:
            return result
        
        timeout = self.config.getint(self.section, 'aios3_timeout')
        try:
            result = await asyncio.wait_for(self._archive(suspect,fugluid_override), timeout=timeout)
        except asyncio.TimeoutError:
            s3_uri = self.config.get(self.section, 'aios3_uri')
            raise ArchiveException(f'{suspect.id} timeout writing to S3 storage {s3_uri}')
        return result
        
    
    @asynccontextmanager
    async def get_s3_client(self):
        s3_uri = self.config.get(self.section, 'aios3_uri')
        s3_region = self.config.get(self.section, 'aios3_region')
        s3_access_id = self.config.get(self.section, 'aios3_access_id')
        s3_access_key = self.config.get(self.section, 'aios3_access_key')
        
        session = aioboto3.Session()
        async with session.client(
            's3',
            endpoint_url=s3_uri,
            region_name=s3_region,
            aws_access_key_id=s3_access_id,
            aws_secret_access_key=s3_access_key
        ) as s3:
            try:
                yield s3
            finally:
                await s3.close()
            
    
    async def _archive(self, suspect, fugluid_override=None):
        result = {'success': False}
        
        bucketname = self.config.get(self.section, 'aios3_bucket')
        ttl = self.config.getint(self.section, 'aios3_ttl')
        filename = f'{fugluid_override or suspect.id}.eml'
        extraargs = {
            'ContentType': 'message/rfc822',
            'Expires': utcnow() + datetime.timedelta(seconds=ttl),
            'ACL': 'private',
        }
        
        async with self.get_s3_client() as s3:
            try:
                await s3.upload_fileobj(
                    Fileobj=suspect.get_source(),
                    Bucket=bucketname,
                    Key=filename,
                    ExtraArgs=extraargs)
                result['success'] = True
            except S3ClientError as e:
                raise ArchiveException(f'{suspect.id} failed to write data to bucket {bucketname} as {filename} due to {str(e)}')
        return result
    
        
    async def lint(self):
        if not HAVE_AIOS3:
            print('ERROR: s3 library (aioboto3) not available')
            return False
        else:
            bucketname = self.config.get(self.section, 'aios3_bucket')
            s3_uri = self.config.get(self.section, 'aios3_uri')
            try:
                async with self.get_s3_client() as s3:
                    await s3.head_bucket(Bucket=bucketname)
            except S3ClientError as e:
                print(f'ERROR: failed to access {bucketname} on {s3_uri} due to {str(e)}')
                return False
            except Exception as e:
                print(f'ERROR: failed to access {bucketname} on {s3_uri} due to {e.__class__.__name__}: {str(e)}')
                return False
        return True
    


class WebDavBackend(AbstractBackend):
    """
    This backend stores mail in webdav storage
    Status: experimental
    """
    requiredvars = {
        'webdav_uri': {
            'default': '',
            'description': "webdav base uri (e.g. https://webdav.example.com/path/to/quar)",
        },
        'webdav_username': {
            'default': '',
            'description': "webdav username",
        },
        'webdav_password': {
            'default': '',
            'description': "webdav password",
        },
        'webdav_timeout': {
            'default': '10',
            'description': "webdav http timeout",
        },
    }
    
    def _install_passman(self, webdav_uri):
        username = self.config.get(self.section, 'webdav_username')
        password = self.config.get(self.section, 'webdav_password')
        if username and password:
            passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, webdav_uri, username, password)
            authhandler = urllib.request.HTTPBasicAuthHandler(passman)
            opener = urllib.request.build_opener(authhandler)
            urllib.request.install_opener(opener)
    
    def archive(self, suspect, fugluid_override=None):
        result = {'success': False}
        timeout = self.config.getfloat(self.section, 'webdav_timeout')
        webdav_uri = self.config.get(self.section, 'webdav_uri')
        self._install_passman(webdav_uri)
        
        filename = f'{fugluid_override or suspect.id}.eml'
        uri = urljoin(webdav_uri, filename)
        source = suspect.get_source()
        
        try:
            req = urllib.request.Request(url=uri, data=source, method='PUT')
            if not req.type in ['https', 'http']:
                self.logger.error(f'{suspect.id} not an http(s) URI: {webdav_uri}')
                return result
            req.add_header('Content-Length', str(len(source)))
            req.add_header('User-Agent', f'Fuglu/{get_main_version().strip()}')
            with urllib.request.urlopen(req, timeout=timeout) as f: # nosemgrep CWE-939
                pass
            if 200 <= f.status <= 299: # put ok can be 201
                result['success'] = True
                result['archiveuri'] = uri
                self.logger.info(f'{suspect.id} successful upload to {uri}')
            else:
                self.logger.error(f'{suspect.id} failed to upload to {uri} due to {f.status} {f.reason}')
        except Exception as e:
            raise ArchiveException(f'{suspect.id} failed to upload to {uri} due to {e.__class__.__name__}: {str(e)}')
        return result

    def lint(self):
        webdav_uri = self.config.get(self.section, 'webdav_uri')
        self._install_passman(webdav_uri)
        try:
            req = urllib.request.Request(url=webdav_uri, method='HEAD')
            if not req.type in ['https', 'http']:
                print(f'ERROR: not an http(s) URI: {webdav_uri}')
                return False
            req.add_header('User-Agent', f'Fuglu/{get_main_version().strip()}')
            with urllib.request.urlopen(req) as f: # nosemgrep CWE-939
                pass
            if not 200 <= f.status <= 299:
                print(f'ERROR: failed to check {webdav_uri} due to {f.status} {f.reason}')
                return False
        except Exception as e:
            print(f'ERROR: failed to check {webdav_uri} due to {e.__class__.__name__}: {str(e)}')
            return False
        return True


class AIOWebDavBackend(AbstractBackend):
    """
    This backend stores mail in webdav storage
    Status: experimental
    """
    requiredvars = {
        'aiowebdav_uri': {
            'default': '',
            'description': "webdav base uri (e.g. https://webdav.example.com/path/to/quar)",
        },
        'aiowebdav_username': {
            'default': '',
            'description': "webdav username",
        },
        'aiowebdav_password': {
            'default': '',
            'description': "webdav password",
        },
        'aiowebdav_timeout': {
            'default': '10',
            'description': "webdav http timeout",
        },
    }
    
    async def do_upload(self, session, webdav_uri, content, suspectid='n/a'):
        error = None
        headers = {'User-Agent': f'Fuglu/{get_main_version().strip()}'}
        response = await session.put(webdav_uri, data=content, headers=headers)
        async with response as resp:
            if resp.status in (200, 201, 204):
                self.logger.debug(f'{suspectid}: Upload successful: {resp.status} {resp.reason}')
            else:
                text = await resp.text()
                error = f'{resp.status} {resp.reason} {text}'
        return error
    
    async def archive(self, suspect, fugluid_override=None):
        result = {'success': False}
        if not HAVE_AIOHTTP:
            return result
        
        timeout = self.config.getfloat(self.section, 'aiowebdav_timeout')
        webdav_uri = self.config.get(self.section, 'aiowebdav_uri')
        username = self.config.get(self.section, 'aiowebdav_username')
        password = self.config.get(self.section, 'aiowebdav_password')
        auth = aiohttp.BasicAuth(login=username, password=password) if username and password else None
        try:
            async with aiohttp.ClientSession(auth=auth) as session:
                error = await asyncio.wait_for(self.do_upload(session, webdav_uri, suspect.get_source()), timeout=timeout)
                if not error:
                    result['success'] = True
                    result['archiveuri'] = webdav_uri
        except Exception as e:
            error = f'{e.__class__.__name__}: {str(e)}'
        if error:
            raise ArchiveException(f'{suspect.id} failed to upload to {webdav_uri} due to {error}')
        return result
    
    async def lint(self):
        if not HAVE_AIOHTTP:
            print('ERROR: missing dependency aiohttp')
            return False
        webdav_uri = self.config.get(self.section, 'aiowebdav_uri')
        username = self.config.get(self.section, 'aiowebdav_username')
        password = self.config.get(self.section, 'aiowebdav_password')
        auth = aiohttp.BasicAuth(login=username, password=password) if username and password else None
        headers = {'User-Agent': f'Fuglu/{get_main_version().strip()}'}
        try:
            async with aiohttp.ClientSession(auth=auth) as session:
                response = await session.head(webdav_uri, headers=headers) # await before context manager for proper mocking
                async with response as resp:
                    if not 200 <= resp.status <= 299:
                        print(f'ERROR: failed to check {webdav_uri} due to {resp.status} {resp.reason}')
                        return False
        except Exception as e:
            print(f'ERROR: failed to check {webdav_uri} due to {e.__class__.__name__}: {str(e)}')
            return False
        return True
        

dovecot_username_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890.-_@'


def dovecot_username(username):
    legal_username = ''
    for char in username:
        if char in dovecot_username_chars:
            legal_username += char
    return legal_username


class MyLMTP(smtplib.LMTP):
    LMTP_PORT = 24

    # versions before 3.9 don't pass timeout to SMTP
    # https://github.com/python/cpython/blob/3.9/Lib/smtplib.py#L1079
    def __init__(self, host='', port=LMTP_PORT, local_hostname=None, source_address=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """Initialize a new instance."""
        #super().__init__(host, port, local_hostname=local_hostname, source_address=source_address)
        smtplib.SMTP.__init__(self, host, port, local_hostname=local_hostname, source_address=source_address, timeout=timeout)

    # https://github.com/python/cpython/blob/3.9/Lib/smtplib.py#L803

    def sendmail(self, from_addr, to_addrs, msg, mail_options=(), rcpt_options=()):
        self.ehlo_or_helo_if_needed()
        esmtp_opts = []
        if isinstance(msg, str):
            # noinspection PyProtectedMember
            msg = smtplib._fix_eols(msg).encode('ascii')
        if self.does_esmtp:
            if self.has_extn('size'):
                esmtp_opts.append('size=%d' % len(msg))
            for option in mail_options:
                esmtp_opts.append(option)
        (code, resp) = self.mail(from_addr, esmtp_opts)
        if code != 250:
            if code == 421:
                self.close()
            else:
                self._rset()
            raise smtplib.SMTPSenderRefused(code, resp, from_addr)
        senderrs = {}
        if isinstance(to_addrs, str):
            to_addrs = [to_addrs]
        for each in to_addrs:
            (code, resp) = self.rcpt(each, rcpt_options)
            if (code != 250) and (code != 251):
                senderrs[each] = (code, resp)
            if code == 421:
                self.close()
                raise smtplib.SMTPRecipientsRefused(senderrs)
        if len(senderrs) == len(to_addrs):
            # the server refused all our recipients
            self._rset()
            raise smtplib.SMTPRecipientsRefused(senderrs)
        (code, resp) = self.data(msg)
        if code != 250:
            if code == 421:
                self.close()
            else:
                self._rset()
            raise smtplib.SMTPDataError(code, resp)
        # if we got here then somebody got our mail
        return senderrs, resp


class LMTPBackend(AbstractBackend):
    """
    This backend passes mail via LMTP to any LMTP server (however, only tested with dovecot)
    Status: Mature
    """
    requiredvars = {
        'lmtp_hosts': {
            'default': '',
            'description': 'comma separated list of LMTP target hostname, hostname:port or path to local LMTP socket (path must start with /)',
        },
        'lmtp_user': {
            'default': '',
            'description': 'LMTP auth user. leave empty if no authentication is needed',
        },
        'lmtp_password': {
            'default': '',
            'description': 'LMTP auth password. leave empty if no authentication is needed',
        },
        'lmtp_sender': {
            'default': '',
            'description': 'LMTP envelope sender. Leave empty for original SMTP envelope sender',
        },
        'lmtp_useoriginal': {
            'default': 'True',
            'description': """should we store the original message as retreived from postfix or store the
                                current state in fuglu (which might have been altered by previous plugins)""",
        },
        'lmtp_headername': {
            'default': 'X-Fuglu-ID',
            'description': 'Name of header containing Fuglu ID when storing via LMTP',
        },
    }

    def _parse_host_port(self, hostdefinition, defaultport=None):
        port = defaultport
        if ':' in hostdefinition:
            host, portstr = hostdefinition.split(':', 1)
            try:
                port = int(portstr)
            except ValueError:
                self.logger.warning(f'port {portstr} found in {hostdefinition} is not a number')
        else:
            host = hostdefinition
        return host, port

    def __init_socket(self):
        lmtp_hosts = self.config.getlist(self.section, 'lmtp_hosts')

        s = None
        if not lmtp_hosts:
            return None
        elif lmtp_hosts[0].startswith('/'):  # unix socket
            if not os.path.exists(lmtp_hosts[0]):
                raise ArchiveException(f'unix socket {lmtp_hosts} not found')
            s = MyLMTP(lmtp_hosts)
        else:
            hosttuples = [self._parse_host_port(h, defaultport=MyLMTP.LMTP_PORT) for h in lmtp_hosts]
            for host, port in hosttuples:
                try:
                    s = MyLMTP(host, port, timeout=30)
                except (socket.error, ConnectionRefusedError):
                    continue
            if s is None and hosttuples:
                raise ArchiveException('no LMTP server is reachable')
        return s

    def __auth(self, lmtp):
        user = self.config.get(self.section, 'lmtp_user')
        password = self.config.get(self.section, 'lmtp_password')
        if user and password:
            lmtp.login(user, password)

    def __do_quarantine(self, suspect, content, retry=3):
        host = 'unknown'
        lmtp_id = None

        lmtpfrom = self.config.get(self.section, 'lmtp_sender')
        if not lmtpfrom:
            lmtpfrom = suspect.from_address

        try:
            lmtp = self.__init_socket()
            # noinspection PyProtectedMember
            host = lmtp._host
            # make sure everything is correctly formatted to use sendmail
            # sendmail_address will make sure address type is correct for Py2/3, unicode/str/bytes
            # force_bString is bytes because we don't want the internal algorithm to play with
            # the message and try to encode it...
            rcpt = dovecot_username(suspect.to_address)
            senderrs, resp = lmtp.sendmail(force_uString(lmtpfrom), force_uString(rcpt), force_bString(content))
            lmtp.quit()
            if rcpt in senderrs:
                raise ArchiveException(f'{suspect.id} LMTP delivery error to {rcpt} on {host}')
            else:
                lmtp_id = self._lmtp_queueid(resp)
                self.logger.info(f'{suspect.id} message delivered to LMTP server {host} with LMTP ID {lmtp_id}')
        except Exception as e:
            if retry > 0:
                self.logger.debug(f'{suspect.id} LMTP delivery failed. try {retry}/3 on {host}. error was: {e.__class__.__name__}: {str(e)}')
                time.sleep(0.1)
                self.__do_quarantine(suspect, content, retry - 1)
            else:
                raise

        return host, lmtp_id

    def _lmtp_queueid(self, resp):
        """
        sample response:
        '2.0.0 <rcpt@example.com> xIZNJoF4p1pDoAAALbRGFw Saved'

        #search msg in imap with this queue id or a message id:
        i = IMAP4('127.0.0.1')
        i.login('username', 'password')
        i.select()
        code, ids = i.uid('search', None, '(HEADER Received 'xIZNJoF4p1pDoAAALbRGFw')') # code is 'OK' if it was sucessful
        code, ids = i.search(None, '(HEADER Received 'xIZNJoF4p1pDoAAALbRGFw')')
        code, ids = i.search(None, '(HEADER Message-ID 'msgid@example.com')')
        code, ids = i.search(None, '(HEADER X-Fuglu-ID '09c68b914d66457508f6ad727d860d5b')')
        code, result = i.fetch(ids, '(RFC822)') # ids must be a set() or a string containing the id
        msgcontent = result[0][1]
        """
        if resp is None:
            return None
        qid = None
        resp = force_uString(resp)
        v = resp.split()
        if len(v) > 3:
            qid = v[2]
        return qid

    def archive(self, suspect, fugluid_override=None):
        original = self.config.getboolean(self.section, 'lmtp_useoriginal')
        content = self._get_msg_source(suspect, original)
        headername = self.config.get(self.section, 'lmtp_headername')
        if headername:
            fugluid = fugluid_override or suspect.id
            content = Suspect.prepend_header_to_source(headername, fugluid, force_bString(content))
        host, lmtp_id = self.__do_quarantine(suspect, content)
        return dict(host=host, lmtp_id=lmtp_id)

    def lint(self):
        if not self.config.get(self.section, 'lmtp_hosts'):
            print('WARNING: LMTP quarantine disabled')
            return True

        try:
            lmtp = self.__init_socket()
            if lmtp is None:
                print('ERROR: no LMTP connection defined')
                return False
            helo = lmtp.docmd('LHLO', get_outgoing_helo(self.config))
            helostr = helo[1].decode('utf-8')
            print(f'LMTP server sez: {helo[0]} {helostr}')
            self.__auth(lmtp)
            lmtp.quit()
            success = True
        except Exception as e:
            print(f'ERROR: LMTP connection error: {e.__class__.__name__}: {str(e)}')
            success = False

        return success


ARCHIVE_BACKENDS = OrderedDict()
ARCHIVE_BACKENDS['localdir'] = LocalDirBackend
ARCHIVE_BACKENDS['lmtp'] = LMTPBackend
ARCHIVE_BACKENDS['elastic'] = ElasticBackend
ARCHIVE_BACKENDS['cassandra'] = CassandraBackend
ARCHIVE_BACKENDS['aios3'] = AIOS3Backend
ARCHIVE_BACKENDS['s3'] = S3Backend
ARCHIVE_BACKENDS['aiowebdav'] = AIOWebDavBackend
ARCHIVE_BACKENDS['webdav'] = WebDavBackend


class ArchivePlugin(ScannerPlugin):
    r"""
This plugin stores a copy of the message if it matches certain criteria (Suspect Filter).
You can use this if you want message archives for your domains, need a quarantine or to debug problems occuring only for certain recipients.
The architecture allows to store data in various backends (databases), either simultaneously or using one backend as main and others as fallback in case the main backend is unavailable.
Currently, the following backends are supported:
- localdir: save mail to a local directory structure. This backend is stable and in active use.
- lmtp: pass message to LMTP server. This backend is stable and in active use.
- elastic: store message in elasticsearch. This backend is in development (2021).
- cassandra: store message in cassandra. This backend is no longer maintained and published mainly for code archival reasons. YMMV.

Examples for the archive.regex filter file:

Archive messages to domain ''test.com'':

``to_domain test\.com``


Archive messages from oli@fuglu.org:


``envelope_from oli@fuglu\.org``


you can also append "yes" and "no" to the rules to create a more advanced configuration. Lets say we want to archive all messages to sales@fuglu.org and all regular messages support@fuglu.org except the ones created by automated scripts like logwatch or daily backup messages etc.

```
envelope_from logwatch@.*fuglu\.org   no
envelope_to sales@fuglu\.org yes
from backups@fuglu\.org no
envelope_to support@fuglu\.org      yes
```

Archive/Quarantine messages that are marked as spam:
```
@spam['spamassassin'] True
@archive.spam True
```

Note: The first rule to match in a message is the only rule that will be applied. Exclusion rules should therefore be put above generic/catch-all rules.
"""

    def __init__(self, config, section=None):
        super().__init__(config, section)

        self.requiredvars = {
            'archiverules': {
                'default': '${confdir}/archive.regex',
                'description': 'Archiving SuspectFilter File',
            },
            'archivebackends': {
                'default': 'localdir',
                'description': 'comma separated list of backends to use. available backends: %s' % ', '.join(list(ARCHIVE_BACKENDS.keys()))
            },
            'multibackend': {
                'default': 'False',
                'description': 'set to True to store mail in all enabled backends. set to False to only use primary and fallback to other backends on error'
            },
            'fugluid_headername': {
                'default': '',
                'description': 'Name of header containing alternative Fuglu ID that overrides storage key',
            },
            'fugluid_headername_skipmissing': {
                'default': 'True',
                'description': 'skip archiving if fugluid_headername is not set',
            },
            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },
        }
        for backend_name in ARCHIVE_BACKENDS:
            self.requiredvars.update(ARCHIVE_BACKENDS[backend_name].requiredvars)

        self.filter = None
        self.logger = self._logger()
        self.backends = OrderedDict()

    def __str__(self):
        return "Archive"

    def _load_backends(self):
        self.backends = OrderedDict()
        backend_names = self.config.getlist(self.section, 'archivebackends')
        for backend_name in backend_names:
            try:
                backendclass = ARCHIVE_BACKENDS[backend_name]
                backend = backendclass(self.config, self.section)
                self.backends[backend_name] = backend
            except KeyError:
                self.logger.error(f'invalid backend name {backend_name}')

    async def do_archive(self, suspect):
        result = {}
        errors = {}

        headername = self.config.get(self.section, 'fugluid_headername')
        if not headername:
            fugluid_override = None
        else:
            # use headeronly message rep in case message is too large
            fugluid_override = suspect.build_headeronly_message_rep().get(headername)
            if fugluid_override is not None:
                fugluid_override = fugluid_override.strip()
            skipmissing = self.config.getboolean(self.section, 'fugluid_headername_skipmissing')
            if not fugluid_override and skipmissing:
                self.logger.info(f'{suspect.id} skip archiving: could not find previous fugluid in {headername}')
                return result, errors
            elif suspect.check_id(fugluid_override) is None:
                errors['preparation'] = f'previous fugluid is not valid: {fugluid_override}'
                return result, errors

        self._load_backends()
        multibackend = self.config.getboolean(self.section, 'multibackend')

        for backend_name in self.backends:
            self.logger.debug(f"{suspect.id} try to archive using backend {backend_name}...")
            backend = self.backends[backend_name]
            try:
                iscoroutine = asyncio.iscoroutinefunction(backend.archive)
                if iscoroutine:
                    response = await backend.archive(suspect, fugluid_override)
                else:
                    response = backend.archive(suspect, fugluid_override)
                result[backend_name] = response
                if not multibackend:
                    break
            except Exception as e:
                self.logger.debug(f'{suspect.id} failed to archive using backend {backend_name} due to {e.__class__.__name__}: {str(e)}')
                errors[backend_name] = f'{e.__class__.__name__}: {str(e)}'
        return result, errors

    def _set_archive_tags(self, suspect):
        suspect.set_tag('archive.ham', suspect.is_ham())
        suspect.set_tag('archive.spam', suspect.is_spam())
        suspect.set_tag('archive.blocked', suspect.is_blocked())
        suspect.set_tag('archive.virus', suspect.is_virus())

    async def _archive(self, suspect):
        self.logger.debug(f"{suspect.id} archive -> set archived tag to false")
        suspect.set_tag('archived', False)
        self.logger.debug(f"{suspect.id} archive -> loading rules")
        archiverules = self.config.get(self.section, 'archiverules')
        if archiverules is None or archiverules == "":
            return DUNNO

        if not os.path.exists(archiverules):
            self.logger.error(f'{suspect.id} Archive Rules file does not exist: {archiverules}')
            return DUNNO

        self.logger.debug(f"{suspect.id} archive -> setup SuspectFilter with arhive rules")
        if self.filter is None:
            self.filter = SuspectFilter(archiverules)

        self.logger.debug(f"{suspect.id} archive -> set_archive_tags")
        self._set_archive_tags(suspect)
        self.logger.debug(f"{suspect.id} archive -> filter match")
        match, arg = self.filter.matches(suspect)
        self.logger.debug(f"{suspect.id} archive -> match:{bool(match)}")
        if match:
            if arg is not None and arg.lower().strip() == 'no':
                suspect.debug("Suspect matches archive exception rule")
                self.logger.debug(f"{suspect.id} Header matches archive exception rule - not archiving")
            else:
                if arg is not None and arg.lower().strip() != 'yes':
                    self.logger.warning(f"{suspect.id} Unknown archive action '{arg}' assuming 'yes'")
                self.logger.debug(f"{suspect.id} Header matches archive rule")
                if suspect.get_tag('debug'):
                    suspect.debug("Suspect matches archiving rule (would be archived it if we weren't in debug mode)" % suspect.id)
                else:
                    result, errors = await self.do_archive(suspect)
                    if result:
                        suspect.set_tag('archived', True)
                        self.logger.info(f"{suspect.id} archived successfully: {result}")
                    if errors:
                        self.logger.warning(f"{suspect.id} archiving errors in backend {','.join(list(errors.keys()))}")
                        for key in errors:
                            self.logger.error(f"{suspect.id} archiving errors in backend {key}: {errors[key]}")
                    suspect.set_tag('archived.result', result)
                    suspect.set_tag('archived.errors', errors)

        else:
            suspect.debug("No archive rule/exception rule applies to this message")
            self.logger.debug(f"{suspect.id} No archive rule/exception rule applies to this message")

    async def examine(self, suspect):
        self.logger.debug(f"{suspect.id} running archive plugin")
        await self._archive(suspect)
        if not suspect.get_tag('archived') and suspect.get_tag('archived.errors'):
            return self._problemcode()
        return DUNNO

    async def process(self, suspect, decision):
        self.logger.debug(f"{suspect.id} running archive plugin")
        await self._archive(suspect)

    def lint_filter(self):
        filterfile = self.config.get(self.section, 'archiverules')
        sfilter = SuspectFilter(filterfile)
        return sfilter.lint()

    def lint(self):
        ok = self.check_config()
        if ok:
            ok = self.lint_filter()
        if ok:
            self._load_backends()
            for backend_name in self.backends:
                backend = self.backends[backend_name]
                backend_ok = backend.lint()
                if not backend_ok:
                    ok = False
        return ok
