# -*- coding: utf-8 -*-
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
import os
from fuglu.shared import Suspect, ScannerPlugin, DUNNO
try:
    from geoip2 import database
    HAVE_GEOIP2 = True
except ImportError:
    database = None
    HAVE_GEOIP2 = False


class GeoIPLookup(ScannerPlugin):
    """
    Lookup clientip GeoIP data from maxmind databases. Requires pygeoip2
    
    can set one header/tag containing the two-letter country code (cc) e.g. de, us, eu, cn, ...
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'headernames': {
                'default': 'X-Geo-Country',
                'description': 'list of header names for spamassassin temp headers',
            },
            'tagnames': {
                'default': 'geoip.countrycode',
                'description': 'list of tag name',
            },
            'database': {
                'default': '',
                'description': 'path to geoip database',
            },
            'debug': {
                'default': 'False',
                'description': 'enable additional debugging output',
            },
        }
        self.geoip = None

    def _init_geoip(self):
        filename = self.config.get(self.section, 'database')
        if self.geoip is None and filename:
            if os.path.exists(filename):
                self.geoip = database.Reader(filename)

    def _get_clientip(self, suspect):
        clientinfo = suspect.get_client_info(self.config)
        if clientinfo is not None:
            helo, clientip, clienthostname = clientinfo
        else:
            helo, clientip, clienthostname = None, None, None
        return clientip

    def _get_geodata(self, clientip, fugluid='n/a'):
        cc = None
        try:
            data = self.geoip.country(clientip)
            cc = data.country.iso_code
            if cc is None:
                cc = data.continent.code
            cc = cc.lower()
        except Exception as e:
            self.logger.debug(f'{fugluid} failed to get GeoIP information for IP {clientip} due to {e.__class__.__name__} {str(e)}')
        return cc, None

    def _run(self, suspect: Suspect):
        if not HAVE_GEOIP2:
            return DUNNO

        self._init_geoip()
        debug = self.config.getboolean(self.section, 'debug')
        
        if self.geoip is not None:
            clientip = self._get_clientip(suspect)
            if clientip is not None:
                values = self._get_geodata(clientip, suspect.id)
                debug and self.logger.debug(f'{suspect.id} clientip {clientip} has values {values}')
                if values[0] is not None:
                    headernames = self.config.getlist(self.section, 'headernames')
                    for hn, val in zip(headernames, values):
                        suspect.write_sa_temp_header(hn, val)
                        debug and self.logger.debug(f'{suspect.id} set sa temp header {hn} with value {val}')
                    tagnames = self.config.getlist(self.section, 'tagnames')
                    for tn, val in zip(tagnames, values):
                        suspect.set_tag(tn, val)
                        debug and self.logger.debug(f'{suspect.id} set tag {tn} with value {val}')
            else:
                self.logger.debug(f'{suspect.id} no clientip found')
            
            originip = suspect.get_tag('origin.ip') # from dnsdata.GetOrigin
            if originip is not None:
                values = self._get_geodata(originip, suspect.id)
                debug and self.logger.debug(f'{suspect.id} originip {originip} has values {values}')
                if values[0] is not None:
                    tagname = 'origin.cc'
                    if self.__class__.__name__ == 'ASNLookup':
                        suspect.set_tag('origin.org', values[1])
                        tagname = 'origin.asn'
                    suspect.set_tag(tagname, values[0])
                    
        return DUNNO

    def examine(self, suspect):
        return self._run(suspect)

    def process(self, suspect, decision):
        self._run(suspect)

    def _lint(self):
        ok = True
        checks = [('8.8.8.8', 'us')]
        for ip, exp in checks:
            cc, _ = self._get_geodata(ip)
            if cc != exp:
                print(f'ERROR: IP={ip} got={cc} expected={exp}')
                ok = False
        return ok

    def lint(self):
        if not HAVE_GEOIP2:
            print('ERROR: geoip2 module not found. this plugin will do nothing')

        ok = self.check_config()
        if ok:
            filename = self.config.get(self.section, 'database')
            if not filename:
                print(f'ERROR: geoip database file name not defined')
                ok = False
            elif not os.path.exists(filename):
                print(f'ERROR: Could not find geoip database {filename}')
                ok = False
            else:
                self._init_geoip()
                if self.geoip is None:
                    print('ERROR: geoip not initialized')
                    ok = False
                else:
                    ok = self._lint()
        return ok


class ASNLookup(GeoIPLookup):
    """
    Lookup clientip ASN data from maxmind databases. Requires pygeoip2
    
    can set two headers/tags containing the AS number and the AS org name
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars.update({
            'headernames': {'default': 'X-Geo-ASN, X-Geo-Org'},
            'tagnames': {'default': 'geoip.asn, geoip.org'},
        })
        self.geoip = None

    def _get_geodata(self, clientip, fugluid='n/a'):
        asn = None
        org = None
        try:
            data = self.geoip.asn(clientip)
            asn = data.autonomous_system_number
            org = data.autonomous_system_organization
        except Exception as e:
            self.logger.debug(f'{fugluid} failed to get ASN information for IP {clientip} due to {e.__class__.__name__} {str(e)}')
        return asn, org

    def _lint(self):
        ok = True
        checks = [('8.8.8.8', 15169)]
        for ip, exp in checks:
            asn, org = self._get_geodata(ip)
            if asn != exp:
                print(f'ERROR: IP={ip} got={asn} expected={exp}')
                ok = False
        return ok
