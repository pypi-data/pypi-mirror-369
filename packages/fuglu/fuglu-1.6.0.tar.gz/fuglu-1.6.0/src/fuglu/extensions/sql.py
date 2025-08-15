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
# Fuglu SQLAlchemy Extension
#
import configparser
import re
import json
from io import StringIO
import logging
import traceback
import weakref
from fuglu.shared import default_template_values, FuConfigParser, Suspect, deprecated, get_default_cache
from fuglu.utils.version import get_main_version
from fuglu.stringencode import force_uString, force_bString
import typing as tp
import time
import os
import ssl
import urllib.request
import urllib.error
import socket

modlogger = logging.getLogger('fuglu.extensions.sql')
STATUS = "not loaded"

SQL_ALCHEMY_UNKNOWN = sql_alchemy_version = 0
SQL_ALCHEMY_V1 = 1
SQL_ALCHEMY_V2 = 2

try:
    from sqlalchemy import create_engine, text, __version__
    from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
    DeclarativeBase = declarative_base()

    SQL_EXTENSION_ENABLED = True
    STATUS = "available"

    major = int(__version__[0])
    if major == 2:
        sql_alchemy_version = SQL_ALCHEMY_V2
    elif major == 1:
        sql_alchemy_version = SQL_ALCHEMY_V1
    else:
        raise Exception("sql alchemy version not supported")

except ImportError:
    SQL_EXTENSION_ENABLED = False
    STATUS = "sqlalchemy not installed"
    DeclarativeBase = object

    def text(string):
        return string

ENABLED = SQL_EXTENSION_ENABLED  # fuglu compatibility

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


_sessmaker = None
_engines = {}



def _get_session_1(connectstring, **kwargs):
    global SQL_EXTENSION_ENABLED
    global _sessmaker
    global _engines

    if connectstring in _engines:
        engine = _engines[connectstring]
    else:
        engine = create_engine(connectstring, pool_recycle=20)
        _engines[connectstring] = engine

    if _sessmaker is None:
        _sessmaker = sessionmaker(autoflush=True, autocommit=True, **kwargs)

    session = scoped_session(_sessmaker)
    session.configure(bind=engine)
    return session

def _get_session_2(connectstring, **kwargs):
    global SQL_EXTENSION_ENABLED
    global _sessmaker
    global _engines

    if connectstring in _engines:
        engine = _engines[connectstring]
    else:
        engine = create_engine(connectstring, pool_recycle=20)
        _engines[connectstring] = engine

    if _sessmaker is None:
        _sessmaker = sessionmaker(autoflush=True, **kwargs)

    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    session = Session()
    return session

def get_session(connectstring, **kwargs):

    if not SQL_EXTENSION_ENABLED:
        raise Exception("sql extension not enabled")

    if sql_alchemy_version == SQL_ALCHEMY_V2:
        return _get_session_2(connectstring, **kwargs)
    elif sql_alchemy_version == SQL_ALCHEMY_V1:
        return _get_session_1(connectstring, **kwargs)

    raise Exception("sql alchemy version not supported")

def lint_session(connectstring):
    if not connectstring:
        print('INFO: no SQL connection string found, not using SQL database')
        return True

    if not SQL_EXTENSION_ENABLED:
        print('WARNING: SQL extension not enabled, not using SQL database')
        return False

    try:
        dbsession = get_session(connectstring)
        dbsession.execute(text('SELECT 1'))
    except Exception as e:
        print(f'ERROR: failed to connect to SQL database: {e.__class__.__name__}: {str(e)}')
        return False
    return True


class DBFile(object):

    """A DB File allows storing configs in any rdbms. """

    def __init__(self, connectstring, query):
        self.connectstring = connectstring
        # e.g. "select action,regex,description FROM tblname where scope=:scope
        self.query = text(query)
        self.logger = logging.getLogger('fuglu.extensions.sql.dbfile')

    def getContent(self, templatevars=None):
        """Get the content from the database as a list of lines. If the query returns multiple columns, they are joined together with a space as separator
        templatevars: replace placeholders in the originalquery , e.g. select bla from bla where domain=:domain
        """
        if templatevars is None:
            templatevars = {}
        sess = get_session(self.connectstring)
        res = sess.execute(self.query, templatevars)
        self.logger.debug(f'Executing query {self.query} with vars {templatevars}')
        buff = []
        for row in res:
            line = " ".join(filter(None, row))
            buff.append(line)
        sess.close()
        return buff


class RESTAPIError(Exception):
    pass


class RESTAPIConfig(object):
    def __init__(self, config: FuConfigParser, suspectid: str = '<unknown>'):
        self.logger = logging.getLogger('fuglu.extensions.sql.restconfig')
        self.config = config
        self.suspectid = suspectid

    _re_title = re.compile('<title>(.{1,1000})</title>', re.I)

    def _get_errormsg(self, errmsg:str) -> str:
        rgxtitle = self._re_title.search(errmsg)
        if rgxtitle:
            errmsg = rgxtitle.groups()[0]
        return errmsg
    
    def _get_ssl_context(self) -> ssl.SSLContext:
        """
        create SSL context that accepts invalid or self-signed SSL certificates
        :return: ssl context
        """
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def _http_request(self, reqtype:str, jsondata:tp.Optional[bytes], uri:str, headers:dict, verify:bool, timeout:float, retry:int=3) -> tp.Tuple[bytes, int]:
        context = None
        if not verify:
            context = self._get_ssl_context()
        req = urllib.request.Request(url=uri, data=jsondata, method=reqtype)
        if not req.type in ['https', 'http']:
            self.logger.error(f'{self.suspectid} not an http(s) URI: {uri}')
            return b'', -1
        for hdr in headers:
            req.add_header(hdr, headers[hdr])
        ipaddr = 'unknown'
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=context) as urlinfo: # nosemgrep CWE-939
                try:
                    sock = socket.fromfd(urlinfo.fileno(), socket.AF_INET, socket.SOCK_STREAM)
                    ipaddr = sock.getpeername()[0]
                except Exception as e:
                    self.logger.warning(f'{self.suspectid} failed to get connection IP from {uri} due to {e.__class__.__name__}: {str(e)}')
                status = urlinfo.status
                content = urlinfo.read()
                if status != 200:
                    self.logger.warning(f'{self.suspectid} got unexpected status code {status} {self._get_errormsg(force_uString(content))} from {uri} (IP: {ipaddr}) for method {reqtype} and content {force_uString(jsondata)}')
        except urllib.error.HTTPError as e:
            sleeptime = 0.1
            if e.status == 503:
                sleeptime = 2
            if retry > 0:
                time.sleep(sleeptime * (4 - retry))
                try:
                    errdoc = force_uString(e.fp.read())
                    self.logger.debug(f'{self.suspectid} got unexpected status code {status} from {uri} (IP: {ipaddr}) retry {retry} error {errdoc}')
                except Exception as e:
                    self.logger.debug(f'{self.suspectid} got unexpected status code {status} from {uri} (IP: {ipaddr}) retry {retry} error getting error {e.__class__.__name__}: {str(e)}')
                content, status = self._http_request(reqtype, jsondata, uri, headers, verify, timeout, retry=retry - 1)
        return content, status

    def call(self, reqtype:str, jsondata:tp.Optional[bytes], restapi_uri:str, headers:dict, restapi_verify:bool, timeout:float) -> tp.Any:
        try:
            body, status = self._http_request(reqtype, jsondata, restapi_uri, headers, restapi_verify, timeout)
            if status != 200:
                try:
                    err = json.loads(body)
                    errmsg = err['errorMessage']
                except (KeyError, json.JSONDecodeError):
                    errmsg = self._get_errormsg(force_uString(body))
                raise RESTAPIError(errmsg)
            content = json.loads(body)
        except Exception as e:
            self.logger.debug(f'{self.suspectid} got {e.__class__.__name__}: {str(e)} from {restapi_uri} with method {reqtype} and content {force_uString(jsondata)}')
            raise RESTAPIError(f'{e.__class__.__name__}: {str(e)}')
        return content

    def get_headers(self) -> tp.Dict[str,str]:
        restapi_headers = self.config.getlist('databaseconfig', 'restapi_headers', resolve_env=True)
        headers = {
            'User-Agent': f'Fuglu/{get_main_version().strip()}',
            'accept': 'application/json',
            'content-type': 'application/json',
        }
        for item in restapi_headers:
            if not ':' in item:
                self.logger.warning(f'{self.suspectid} invalid header definition {item}')
            else:
                hdr, value = item.split(':', 1)
                headers[hdr] = value
        return headers

    def get(self, endpoint: str, timeout: int = 0):
        if not endpoint:
            return []

        restapi_uri = self.config.get('databaseconfig', 'restapi_uri', resolve_env=True)
        restapi_verify = self.config.getboolean('databaseconfig', 'restapi_verify', fallback=False)
        restapi_timeout = timeout or self.config.getfloat('databaseconfig', 'restapi_timeout', fallback=10)

        headers = self.get_headers()

        if not restapi_uri.endswith('/'):
            restapi_uri = f'{restapi_uri}/'
        restapi_uri = f'{restapi_uri}{endpoint}'

        content = self.call('GET', None, restapi_uri, headers, restapi_verify, restapi_timeout)
        return content

    def put(self, endpoint: str, jsondata, timeout: int = 0):
        if not endpoint:
            raise RESTAPIError('no endpoint specified')

        restapi_uri = self.config.get('databaseconfig', 'restapi_uri', resolve_env=True)
        restapi_verify = self.config.getboolean('databaseconfig', 'restapi_verify', fallback=False)
        restapi_timeout = timeout or self.config.getfloat('databaseconfig', 'restapi_timeout', fallback=10)

        headers = self.get_headers()

        if not restapi_uri.endswith('/'):
            restapi_uri = f'{restapi_uri}/'
        restapi_uri = f'{restapi_uri}{endpoint}'
        
        jsondata = force_bString(json.dumps(jsondata))
        content = self.call('PUT', jsondata, restapi_uri, headers, restapi_verify, restapi_timeout)
        return content


class SectionCacheRow(object):
    def __init__(self, config, scope, option, value):
        optionfield = config.get('databaseconfig', 'option_field', fallback='option')
        scopefield = config.get('databaseconfig', 'scope_field', fallback='scope')
        valuefield = config.get('databaseconfig', 'value_field', fallback='value')
        setattr(self, optionfield, option)
        setattr(self, scopefield, scope)
        setattr(self, valuefield, value)


class DBConfig(FuConfigParser):

    """
    Runtime Database Config Overrides.
    Behaves like a RawConfigParser but returns global database overrides/domainoverrides/useroverrides if available
    """

    def __init__(self, config: FuConfigParser, suspect: tp.Optional[Suspect]):
        super().__init__()
        self.logger = logging.getLogger('fuglu.extensions.sql.dbconfig')
        self.sectioncache = {}
        self.suspect = None
        self.set_suspect(suspect)
        self._clone_from(config)
        self.cache = get_default_cache()
        self.yamldata = {}

    def set_suspect(self, suspect: tp.Optional[Suspect]) -> None:
        if suspect is None:
            suspect = Suspect('', 'postmaster', '/dev/null')
            self._tempsuspect = suspect
        # store weak reference to suspect
        # otherwise (python 3), the instance of DBConfig does not reduce the
        # refcount to suspect even if it goes out of scope and the suspect
        # object does not get freed until a (manual or automatic) run of the
        # garbage collector "gc.collect()"
        self.suspect = weakref.ref(suspect)

    def set_rcpt(self, recipient: str) -> None:
        self._tempsuspect = Suspect('', recipient, '/dev/null')
        self.set_suspect(self._tempsuspect)

    def _clone_from(self, config: FuConfigParser) -> None:
        """Clone this object from a FuConfigParser"""
        stringout = StringIO()
        config.write(stringout)
        stringin = StringIO(stringout.getvalue())
        del stringout
        self.read_file(stringin)
        del stringin
        # copy markers like %{confdir}
        self.markers = config.markers.copy()
        self._defaultdict = config._defaultdict

    def load_section(self, section: str) -> bool:
        """
        load section into local cache.
        :param section: name of section to be loaded
        :return: True if loading was successful
        """
        loaded = False
        if SQL_EXTENSION_ENABLED and self.has_section('databaseconfig') \
                and self.has_option('databaseconfig', 'dbconnectstring') \
                and self.has_option('databaseconfig', 'sqlsection'):
            connectstring = self.parentget('databaseconfig', 'dbconnectstring', fallback='').strip()
            query = self.parentget('databaseconfig', 'sqlsection').strip()
            if connectstring and query:
                session = get_session(connectstring)
                sqlvalues = {
                    'section': section,
                    'globalscope': self.parentget('databaseconfig', 'globalscope', fallback='$GLOBAL'),
                }
                default_template_values(self.suspect(), sqlvalues)
                try:
                    result = session.execute(text(query), sqlvalues).fetchall()
                    self.sectioncache[section] = result
                except Exception:
                    trb = traceback.format_exc()
                    self.logger.error(f'Error getting database config override section data: {trb}')
                loaded = True

        if self.has_section('databaseconfig') \
                and self.has_option('databaseconfig', 'restapi_uri') \
                and self.has_option('databaseconfig', 'restapi_headers') \
                and self.parentget('databaseconfig', 'restapi_uri'):
            content = self._get_rest(section, None)[0]
            cachable_sectiondata = []
            for scope in content:
                scopedata = content[scope]
                for sect in scopedata:
                    if sect == section:
                        sectiondata = scopedata[section]
                        for option in sectiondata:
                            cachable_sectiondata.append(SectionCacheRow(super(), scope, option, sectiondata[option]))
                            try:
                                self.sectioncache[section].extend(cachable_sectiondata)
                            except KeyError:
                                self.sectioncache[section] = cachable_sectiondata
                    else:
                        self.logger.debug(f'ignoring bogus section {section} in loaded rest data')
            loaded = True

        if YAML_AVAILABLE and self.has_section('databaseconfig') \
                and self.has_option('databaseconfig', 'yaml_filepath') \
                and os.path.exists(self.parentget('databaseconfig', 'yaml_filepath')):
            content = self._get_yaml(section, None)[0]
            cachable_sectiondata = []
            for scope in content:
                scopedata = content[scope]
                for option in scopedata:
                    cachable_sectiondata.append(SectionCacheRow(super(), scope, option, scopedata[option]))
                    try:
                        self.sectioncache[section].extend(cachable_sectiondata)
                    except KeyError:
                        self.sectioncache[section] = cachable_sectiondata
            loaded = True

        return loaded

    def _get_cached(self, section: str, option: str):
        suspect = self.suspect()
        if suspect is None:
            return None
        todomain = f'%{suspect.to_domain}'

        optionfield = self.parentget('databaseconfig', 'option_field', fallback='option')
        scopefield = self.parentget('databaseconfig', 'scope_field', fallback='scope')
        valuefield = self.parentget('databaseconfig', 'value_field', fallback='value')

        try:
            for row in self.sectioncache.get(section, []):
                scope = getattr(row, scopefield)
                dboption = getattr(row, optionfield)
                if dboption == option and scope in {suspect.to_address, todomain}:
                    return getattr(row, valuefield)
        except AttributeError as e:
            self.logger.error(f'database layout does not match databaseconfig settings: {str(e)}')
        return None

    def get_cached_options(self, section):
        options = []
        suspect = self.suspect()
        if suspect is None:
            return options

        todomain = f'%{suspect.to_domain}'
        optionfield = self.parentget('databaseconfig', 'option_field', fallback='option')
        scopefield = self.parentget('databaseconfig', 'scope_field', fallback='scope')

        for row in self.sectioncache.get(section, []):
            scope = getattr(row, scopefield)
            dboption = getattr(row, optionfield)
            if scope in {suspect.to_address, todomain}:
                options.append(dboption)
        return options

    def get_override(self, section: str, option: str, **kwargs) -> tp.Any:
        result = None
        priorities = []
        if (self.has_section('databaseconfig')) and (self.has_option('databaseconfig', 'dbpriority')):
            priorities = self.parentgetlist('databaseconfig', 'dbpriority', lower=True)
            #cache_ttl = self.parentgetint('databaseconfig', 'value_cache_ttl', fallback=30)
            # if not 'cache' in priorities and cache_ttl > 0:
            #    priorities.insert(0, 'cache')
        for priority in priorities:
            if priority in {'cache', 'sql', 'rest', 'yaml'}:
                func = getattr(self, f'_get_{priority}')
                result, negcache = func(section, option, **kwargs)
                if result is not None:
                    break
                if negcache is True:
                    break
        return result

    def get(self, section: str, option: str, **kwargs) -> tp.Any:
        override = self.get_override(section, option, **kwargs)
        result = self.parentget(section, option, override=override, **kwargs)
        return result

    def getint(self, section: str, option: str, **kwargs):
        override = self.get_override(section, option, **kwargs)
        result = super().getint(section, option, override=override, **kwargs)
        return result

    def getfloat(self, section: str, option: str, **kwargs):
        override = self.get_override(section, option, **kwargs)
        result = super().getfloat(section, option, override=override, **kwargs)
        return result

    def getboolean(self, section: str, option: str, **kwargs):
        override = self.get_override(section, option, **kwargs)
        result = self.parentgetboolean(section, option, override=override, **kwargs)
        return result

    def getlist(self, section: str, option: str, **kwargs) -> tp.Any:
        override = self.get_override(section, option, **kwargs)
        result = self.parentgetlist(section, option, override=override, **kwargs)
        return result

    def _get_sql(self, section: str, option: str, **kwargs) -> tp.Tuple[tp.Any, bool]:
        if not SQL_EXTENSION_ENABLED or (not self.has_section('databaseconfig')) \
                or (not self.has_option('databaseconfig', 'dbconnectstring')):
            return None, False

        connectstring = self.parentget('databaseconfig', 'dbconnectstring')
        if connectstring.strip() == '':
            return None, False

        query = self.parentget('databaseconfig', 'sql')
        if query.strip() == '':
            return None, False

        if section in self.sectioncache:
            return self._get_cached(section, option)

        if (self.has_section('databaseconfig')) and (self.has_option('databaseconfig', 'globalscope')):
            globalscope = self.parentget('databaseconfig', 'globalscope')
        else:
            globalscope = None

        session = get_session(connectstring)
        sqlvalues = {
            'section': section,
            'option': option,
            'globalscope': globalscope or '$GLOBAL',
        }
        suspect = self.suspect()
        default_template_values(self.suspect(), sqlvalues)

        result = None
        try:
            #self.logger.debug("Executing query '%s' with vars %s"%(query,sqlvalues))
            result = session.execute(text(query), sqlvalues).first()
        except Exception:
            trb = traceback.format_exc()
            self.logger.error(f'{suspect.id} Error getting database config override: {trb}')
        if sql_alchemy_version == SQL_ALCHEMY_V1:
            session.remove()

        cache_ttl = self.parentgetint('databaseconfig', 'value_cache_ttl', fallback=30)
        if result is not None:
            value = result[0]
            self.cache.put_cache(self._mkcachekey(True, suspect.to_address, section, option), value, cache_ttl)
            return value, False
        else:
            self.cache.put_cache(self._mkcachekey(False, suspect.to_address, section, option), True, cache_ttl)
            self.cache.put_cache(self._mkcachekey(False, f'%{suspect.to_domain}', section, option), True, cache_ttl)
            self.cache.put_cache(self._mkcachekey(False, globalscope or '$GLOBAL', section, option), True, cache_ttl)
            return None, False

    def _get_rest(self, section: str, option: tp.Optional[str], **kwargs) -> tp.Tuple[tp.Any, bool]:
        if (not self.has_section('databaseconfig')) \
                or (not self.has_option('databaseconfig', 'restapi_uri')) \
                or (not self.has_option('databaseconfig', 'restapi_headers')):
            try:
                return self.parentget(section, option, **kwargs), False
            except (configparser.NoSectionError, configparser.NoOptionError):
                return None, False

        suspect = self.suspect()
        restapi_uri = self.parentget('databaseconfig', 'restapi_uri', resolve_env=True)
        restapi_endpoint = self.parentget('databaseconfig', 'restapi_endpoint')
        if not restapi_uri or not restapi_endpoint:
            return None, False
        if suspect is None:
            raise RESTAPIError('suspect not set')

        restapi_headers = self.parentgetlist('databaseconfig', 'restapi_headers', resolve_env=True)
        restapi_verify = self.parentgetboolean('databaseconfig', 'restapi_verify', fallback=True)
        restapi_timeout = self.parentgetfloat('databaseconfig', 'restapi_timeout', fallback=10)
        restapi_cachettl = self.parentgetfloat('databaseconfig', 'restapi_cachettl', fallback=300)
        if (self.has_section('databaseconfig')) and (self.has_option('databaseconfig', 'globalscope')):
            globalscope = self.parentget('databaseconfig', 'globalscope')
        else:
            globalscope = None
        headers = {'user-agent': f'Fuglu/{get_main_version().strip()}', 'accept': 'application/json', }
        for item in restapi_headers:
            if not ':' in item:
                self.logger.warning(f'{suspect.id} invalid header definition {item}')
            else:
                hdr, hdrval = item.split(':', 1)
                headers[hdr] = hdrval

        if not restapi_uri.endswith('/'):
            restapi_uri = f'{restapi_uri}/'
        restapi_uri = f'{restapi_uri}{restapi_endpoint}'
        if not restapi_uri.endswith('/'):
            restapi_uri = f'{restapi_uri}/'

        value = None
        scopes = []
        if suspect.to_address and '@' in suspect.to_address:
            scopes.append(suspect.to_address.lower())
        if suspect.to_domain:
            scopes.append(f'%{suspect.to_domain.lower()}')
        if globalscope:
            scopes.append(globalscope)

        content = None
        if restapi_cachettl > 0:
            content = self.cache.get_cache(f'rest-{restapi_uri}')
        if content is None:
            restapi = RESTAPIConfig(config=FuConfigParser(), suspectid=suspect.id)
            # returns data for all scopes from this endpoint
            content = restapi.call('GET', None, restapi_uri, headers, restapi_verify, restapi_timeout)
            self.logger.debug(f'{suspect.id} fetched restapi data')
            if restapi_cachettl > 0:
                self.cache.put_cache(f'rest-{restapi_uri}', content, restapi_cachettl)
        else:
            self.logger.debug(f'{suspect.id} using cached restapi data for section={section} option={option}')

        alldata = {}
        for scope in scopes:
            scopedata = content.get(scope, {})
            if option is None:
                alldata[scope] = scopedata
                continue
            sectiondata = scopedata.get(section, {})
            value = sectiondata.get(option)
            #print(f'URI: {restapi_uri_scope} SECTION: {section} OPTION: {option} RESULT: {value}')
            cache_ttl = self.parentgetint('databaseconfig', 'value_cache_ttl', fallback=30)
            if value is None:
                self.cache.put_cache(self._mkcachekey(False, scope, section, option), True, cache_ttl)
            else:
                self.cache.put_cache(self._mkcachekey(True, scope, section, option), value, cache_ttl)
                break
        if option is None:
            return alldata, False
        return value, False

    def _get_yaml(self, section: str, option: tp.Optional[str], **kwargs) -> tp.Tuple[tp.Any, bool]:
        """
        get config override value from yaml file. yaml file should look like this:
        Section:
          option:
            scope: value

        e.g.
        FileTypePlugin:
          sendbounce:
            user@example.com: false
        """

        if (not YAML_AVAILABLE) or (not self.has_section('databaseconfig')) \
                or (not self.has_option('databaseconfig', 'yaml_filepath')):
            try:
                return self.parentget(section, option, **kwargs), False
            except (configparser.NoSectionError, configparser.NoOptionError):
                return None, False

        if (self.has_section('databaseconfig')) and (self.has_option('databaseconfig', 'globalscope')):
            globalscope = self.parentget('databaseconfig', 'globalscope')
        else:
            globalscope = None
        yaml_filepath = self.parentget('databaseconfig', 'yaml_filepath', resolve_env=True)
        suspect = self.suspect()

        if not os.path.exists(yaml_filepath):
            self.logger.warning(f'{suspect.id} no yaml file {yaml_filepath}')
            try:
                return self.parentget(section, option, **kwargs), False
            except (configparser.NoSectionError, configparser.NoOptionError):
                return None, False

        if not yaml_filepath in self.yamldata:
            with open(yaml_filepath, 'r', encoding='utf-8') as fp:
                try:
                    configdict = yaml.full_load(fp)
                except AttributeError:
                    configdict = yaml.safe_load(fp)
            self.yamldata[yaml_filepath] = configdict
            self.logger.debug(f'{suspect.id} loaded yaml file {yaml_filepath}')

        if option is None:
            alldata = {}
            sectiondata = self.yamldata[yaml_filepath].get(section, {})
            for o in sectiondata:
                optiondata = sectiondata[o]
                for s in optiondata:
                    v = optiondata[s]
                    try:
                        alldata[s.lower()][o.lower()] = v
                    except KeyError:
                        alldata[s.lower()] = {o.lower: v}
            return alldata, False

        scopes = []
        if suspect.to_address and '@' in suspect.to_address:
            scopes.append(suspect.to_address.lower())
        if suspect.to_domain:
            scopes.append(suspect.to_domain.lower())
        if not globalscope:
            scopes.append(globalscope)

        value = None
        for scope in scopes:
            sectiondata = self.yamldata[yaml_filepath].get(section, {})
            value = sectiondata.get(option, {}).get(scope, None)
            if value is not None:
                value = str(value)
                break
        return value, False

    def _get_cache(self, section: str, option: str, **kwargs) -> tp.Tuple[tp.Any, bool]:
        value = None
        negcache = False
        suspect = self.suspect()

        if section in self.sectioncache:
            value = self._get_cached(section, option)
            if value is not None:
                return value, negcache

        scopes = []
        if suspect.to_address and '@' in suspect.to_address:
            scopes.append(suspect.to_address.lower())
        if suspect.to_domain:
            scopes.append(f'{suspect.to_domain.lower()}')
            scopes.append(f'%{suspect.to_domain.lower()}')
        globalscope = self.parentget('databaseconfig', 'globalscope', fallback='$GLOBAL')
        if globalscope:
            scopes.append(globalscope)

        for scope in scopes:
            value = self.cache.get_cache(self._mkcachekey(True, scope, section, option))
            if value is None:
                negcache = self.cache.get_cache(self._mkcachekey(False, scope, section, option)) is True  # True if negcached, False if not negcached
        return value, negcache

    def _mkcachekey(self, pos: bool, scope: str, section: str, option: str) -> str:
        if pos:
            prefix = 'dbconfig-pos'
        else:
            prefix = 'dbconfig-neg'
        return f'{prefix}-{scope}-{section}-{option}'

    def parentget(self, section: str, option: str, **kwargs) -> str:
        return super().get(section, option, **kwargs)

    def parentgetboolean(self, section: str, option: str, **kwargs) -> bool:
        return self._convert_to_boolean(super().get(section, option, **kwargs))

    def parentgetfloat(self, section: str, option: str, **kwargs) -> float:
        return float(super().get(section, option, **kwargs))

    def parentgetint(self, section: str, option: str, **kwargs) -> int:
        return int(super().get(section, option, **kwargs))

    def parentgetlist(self, section: str, option: str, **kwargs) -> tp.List[str]:
        return super().getlist(section, option, **kwargs)


# this function is ugly, use dbconfig instead...
@deprecated
def get_domain_setting(domain, dbconnection, sqlquery, cache, cachename, default_value=None, logger=None):
    if logger is None:
        logger = logging.getLogger('fuglu.extensions.sql.get_domain_setting')

    cachekey = f'{cachename}-{domain}'
    cached = cache.get_cache(cachekey)
    if cached is not None:
        logger.debug(f"got cached setting for {domain}")
        return cached

    settings = default_value

    try:
        session = get_session(dbconnection)

        # get domain settings
        dom = session.execute(text(sqlquery), {'domain': domain}).fetchall()

        if not dom or not dom[0] or len(dom[0]) == 0:
            logger.debug(f"Can not load domain setting - domain {domain} not found. Using default settings.")
        else:
            settings = dom[0][0]

        if sql_alchemy_version == SQL_ALCHEMY_V1:
            session.remove()

    except Exception as e:
        logger.error(f"Exception while loading setting for {domain} : {e.__class__.__name__}: {str(e)}")

    cache.put_cache(cachekey, settings)
    logger.debug(f"refreshed setting for {domain}")
    return settings
