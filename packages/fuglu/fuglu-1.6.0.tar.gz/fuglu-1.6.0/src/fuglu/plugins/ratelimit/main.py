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
# based on the ratelimit plugin in the postomaat project (https://gitlab.com/fumail/postomaat)
# developed by @ledgr

import logging
import re
import os
import typing as tp
import ipaddress as ia
import asyncio
import copy
import time
try:
    _ = tp.OrderedDict
except AttributeError:
    # python 3.6 doesn't have a type for the OrderedDict, use normal Dict for typing
    tp.OrderedDict = tp.Dict

from collections import OrderedDict

from fuglu.shared import (
    ScannerPlugin, DUNNO, apply_template, Suspect,
    string_to_actioncode, _SuspectTemplate, default_template_values
)
from fuglu.mshared import (
    BMPConnectMixin, BMPHeloMixin, BMPMailFromMixin,
    BMPRCPTMixin, BMPHeaderMixin, BMPEOHMixin, BMPEOBMixin,
    BasicMilterPlugin, retcode2milter, EOM
)
import fuglu.connectors.milterconnector as sm
from fuglu.connectors.milterconnector import (
    CONNECT, HELO, MAILFROM,
    RCPT, HEADER, EOH, EOB
)
import fuglu.connectors.asyncmilterconnector as asm
from fuglu.stringencode import force_uString

from .strategies import AVAILABLE_STRATEGIES, AVAILABLE_BACKENDS
from .strategies.backendint import BackendInterface
from .dynfunction import FunctionWrapperInt, MultipleFunctionsWrapper

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    yaml = None
    HAVE_YAML = False

ALLSTATES = list(BasicMilterPlugin.ALL_STATES.keys()) + [EOM]
BE_VERBOSE = False  # enable for debugging


SKIP = -100

FIELDVALUEIGNORE = "((ignore))"  # put this value as key to ignore a field in the rediskey

class TemplateFunctionWrapper(FunctionWrapperInt):
    def __init__(self, definitionstring: str, **kwargs):
        """Load a function (and keyword args) from a string"""
        super().__init__(definitionstring=definitionstring, **kwargs)
        self._template = _SuspectTemplate(definitionstring)

    def __call__(self, *args, **kwargs):
        if kwargs and 'map' in kwargs:
            map = kwargs['map']
        else:
            map = {}

        message = self._template.safe_substitute(map)
        return message


class CounterInt(object):
    # Target object class (required for lint)
    targetSuspects = ()

    """Interface for a counter"""

    def __init__(self, fieldname: str, setupdict: tp.Dict):
        self.fieldname = fieldname
        self.setupdict = setupdict
        self.regex = CounterInt._parse_regex(setupdict.get('regex', []))
        self.ipmatch = CounterInt._parse_ipmatch(setupdict.get('ipmatch', []))
        self.key = setupdict.get("key")
        self.keyfunction = None
        if self.key:
            funclist = CounterInt.parse_option_stringlist(self.key)
            self.keyfunction = MultipleFunctionsWrapper(funclist=funclist,
                                                        DefaultProcessorClass=TemplateFunctionWrapper)

        self.field = setupdict.get("field")
        self.fieldfunction = None
        if self.field:
            funclist = CounterInt.parse_option_stringlist(self.field)
            self.fieldfunction = MultipleFunctionsWrapper(funclist=funclist,
                                                          DefaultProcessorClass=TemplateFunctionWrapper)

        self.invert = bool(setupdict.get("invert"))
        self._lint = setupdict.get('lint', [])

        loggername = "%s.limiter.%s" % (__package__ if __package__ else "fuglu", self.__class__.__name__)
        self.logger = logging.getLogger(loggername)

    def lint(self) -> int:
        """Lint counter rules if defined"""

        from fuglu.funkyconsole import FunkyConsole
        fc = FunkyConsole()

        if not HAVE_YAML:
            print(fc.strcolor("ERROR", "red"), 'yaml module not found, this plugin will not do anything')
            return False
        
        try:
            from unittest.mock import patch, MagicMock
        except (ModuleNotFoundError, AttributeError):
            print(fc.strcolor('WARNING', 'yellow'),
                  f"LINT \"RateLimitPlugin -> Limiter -> Counter\" requires python package 'mock' or 'unittest' for proper linting capabilities")
            MagicMock = None
            patch = None

        try:
            from collections import defaultdict
        except ModuleNotFoundError:
            print("LINT \"RateLimitPlugin -> Limiter -> Counter\" requires python package 'collections'")
            return 1

        if not self.fieldfunction and MagicMock is not None:
            # if there's no fieldfuncion, the attribute
            # should exist in the Session/Suspect object
            for tClass in self.targetSuspects:
                if tClass == asm.MilterSession:
                    t = tClass(MagicMock(), MagicMock())
                elif tClass == Suspect:
                    t = tClass("from@domain.invalid", "to@domain.invalid", None, inbuffer=b"empty")
                else:
                    t = tClass(MagicMock())
                try:
                    # if there are field functions, then ignore
                    self.get_field(suspect=t, ignore_errors=False)
                except Exception as e:
                    print(fc.strcolor('ERROR', 'red'), f" Lint ({self.fieldname}): {str(e)}")
                    return 1

        err_count = 0
        for test in self._lint:
            input = test.get('input')
            examine = test.get('examine')
            templatedict = test.get('templatedict')
            fieldout = test.get('fieldout')
            keyout = test.get('keyout')
            out_field = None
            out_key = None
            out_examine = None
            inputkeys = list(test.keys())
            unknownkeys = [k for k in inputkeys if k not in ['input', 'examine', 'templatedict', 'fieldout', 'keyout']]
            if unknownkeys:
                print("   ",
                      fc.strcolor('FAIL', 'red'),
                      f" Lint ({self.fieldname}): unknown keys={unknownkeys}"
                      )
                err_count += 1
                continue

            if (input is None and templatedict is None) or \
               (examine is None and fieldout is None and keyout is None):
                print("   ",
                      fc.strcolor('FAIL', 'red'),
                      f" Lint ({self.fieldname}): input={input},templatedict={templatedict} -> examine={examine},keyout={keyout},fieldout={fieldout}"
                      )
                err_count += 1
                continue

            if patch is not None:
                with patch.object(self, '_get_field', return_value=input):
                    if templatedict is not None:
                        d = templatedict
                    else:
                        d = defaultdict(lambda: input)
                    with patch.object(self, 'get_suspect_dict', return_value=d):
                        out_field = self.get_field(suspect=None)
                        out_key = self.get_key(suspect=None)
                        out_examine = self.examine(suspect=None)

                if fieldout is not None:
                    print("   ",
                          fc.strcolor('PASS', 'green') if fieldout == out_field else fc.strcolor('FAIL', 'red'),
                          f" Lint fieldout ({self.fieldname}): input={input}, field={out_field}, expected={fieldout}"
                          )
                    if fieldout != out_field:
                        err_count += 1

                if keyout is not None:
                    print("   ",
                          fc.strcolor('PASS', 'green') if keyout == out_key else fc.strcolor('FAIL', 'red'),
                          f" Lint keyout ({self.fieldname}): input={input}, field={out_field}, key={out_key}, expected={keyout}"
                          )
                    if keyout != out_key:
                        err_count += 1

                if examine is not None:
                    print("   ",
                          fc.strcolor('PASS', 'green') if examine == out_examine else fc.strcolor('FAIL', 'red'),
                          f" Lint examine ({self.fieldname}): input={input}, field={out_field}, examine={out_examine}, expected={examine}"
                          )
                    if examine != out_examine:
                        err_count += 1
        return err_count

    def _invert(self, res: bool):
        if self.invert:
            return not res
        else:
            return res

    def get_suspect_dict(self, suspect: tp.Union[asm.MilterSession, sm.MilterSession]) -> tp.Dict:
        return {}

    def get_key(self, suspect: tp.Union[Suspect, asm.MilterSession, sm.MilterSession]) -> str:
        """Get the key for this counter (equal to field entry unless specifically defined)"""
        out = self.key if self.key else self.get_field(suspect=suspect)
        if self.keyfunction:
            field = self.get_field(suspect=suspect)
            susmap = self.get_suspect_dict(suspect=suspect)
            out = self.keyfunction(field, map=susmap, suspect=suspect)
        return force_uString(out)

    def get_field(self, suspect: tp.Union[Suspect, asm.MilterSession, sm.MilterSession], ignore_errors: bool = True) -> str:
        field = self._get_field(suspect=suspect, ignore_errors=ignore_errors)
        if self.fieldfunction:
            susmap = self.get_suspect_dict(suspect=suspect)
            field = force_uString(self.fieldfunction(field, map=susmap, suspect=suspect))
        return field

    def _get_field(self, suspect: tp.Union[Suspect, asm.MilterSession, sm.MilterSession], ignore_errors: bool = True) -> str:
        """Get field for counter, has to be implemented for each subclass"""
        raise NotImplementedError()

    def examine(self, suspect: tp.Union[Suspect, asm.MilterSession, sm.MilterSession], ignore_errors: bool = True) -> bool:
        """Examine field, return True on hit"""
        field = self.get_field(suspect=suspect, ignore_errors=ignore_errors)

        # convert a list to a single string
        if isinstance(field, (list, tuple)):
            field = " ".join(field)

        if field is None:
            # field not found/given/set skip this counter
            return self._invert(False)

        if self.regex:
            # If there is one (or several) regex defined,
            # only count on match
            for r in self.regex:
                if r.match(field):
                    return self._invert(True)
            return self._invert(False)
        elif self.ipmatch:
            # If there is one (or several) network ranges defined,
            # only count if ip is in net

            try:
                # create ip
                ip = ia.ip_address(field)
            except ValueError as e:
                self.logger.error(str(e))
            else:
                # check if ip is in net
                for net in self.ipmatch:
                    if ip in net:
                        return self._invert(True)

            return self._invert(False)
        else:
            # default is True, always count
            return self._invert(True)

    @staticmethod
    def parse_option_stringlist(stringlist: tp.Optional[tp.Union[str, list]]) -> tp.List[str]:
        """Handle yml option which is string or list of strings, return list of strings"""
        assert isinstance(stringlist, (str, list)) or stringlist is None
        if stringlist is None:
            return []
        else:
            return force_uString([stringlist] if isinstance(stringlist, str) else stringlist)

    @staticmethod
    def _parse_regex(regex: tp.Union[str, list]) -> tp.List:
        """Compile regex string (or list of regex strings)"""
        assert isinstance(regex, (str, list))
        rlist = []

        inlist = [regex] if isinstance(regex, str) else regex
        for reg in inlist:
            try:
                compiled_regex = re.compile(reg, re.IGNORECASE)
                rlist.append(compiled_regex)
            except Exception as e:
                raise Exception(f"Orig regex: \"{reg}\" Erro: {e}").with_traceback(e.__traceback__)
        return rlist

    @staticmethod
    def _parse_ipmatch(netstring: tp.Union[str, list]) -> tp.List:
        """Parse ip network string"""
        assert isinstance(netstring, (str, list))
        nlist = []

        inlist = [netstring] if isinstance(netstring, str) else netstring
        for net in inlist:
            try:
                netobj = ia.ip_network(net, strict=False)
                nlist.append(netobj)
            except Exception as e:
                raise Exception(f"Orig network def: \"{net}\" Erro: {e}").with_traceback(e.__traceback__)
        return nlist


class CounterSuspectAttr(CounterInt):
    targetSuspects = (Suspect,)

    """Use an attribute of the Suspect"""

    def _get_field(self, suspect: Suspect, ignore_errors: bool = True):
        try:
            return force_uString(getattr(suspect, self.fieldname))
        except AttributeError:
            if ignore_errors:
                return None
            else:
                raise

    def get_suspect_dict(self, suspect: Suspect) -> tp.Dict:
        return default_template_values(suspect=suspect)


class CounterSuspectAttrRaw(CounterInt):
    """Like CounterSuspectAttr but _get_field doesn't return pure string"""
    targetSuspects = (Suspect,)

    """Use an attribute of the Suspect"""

    def _get_field(self, suspect: Suspect, ignore_errors: bool = True):
        try:
            return getattr(suspect, self.fieldname)
        except AttributeError:
            if ignore_errors:
                return None
            else:
                raise

    def get_suspect_dict(self, suspect: Suspect) -> tp.Dict:
        return default_template_values(suspect=suspect)


class CounterSuspectTag(CounterInt):
    targetSuspects = (Suspect,)
    """Use a tag of the Suspect"""

    def _get_field(self, suspect: Suspect, ignore_errors: bool = True):
        return force_uString(suspect.get_tag(self.fieldname, None))


class CounterSuspectTagRaw(CounterInt):
    """Like CounterSuspectTag but return raw content of tag without converting to str"""
    targetSuspects = (Suspect,)
    """Use a tag of the Suspect"""

    def _get_field(self, suspect: Suspect, ignore_errors: bool = True):
        return suspect.get_tag(self.fieldname, None)


class MilterSessionAttr(CounterInt):
    targetSuspects = (sm.MilterSession, asm.MilterSession)

    """Use an attribute of the Suspect"""

    def get_suspect_dict(self, suspect: tp.Union[asm.MilterSession, sm.MilterSession]) -> tp.Dict:
        return suspect.get_templ_dict()

    def _get_field(self, suspect: tp.Union[asm.MilterSession, sm.MilterSession], ignore_errors: bool = True):
        try:
            return force_uString(getattr(suspect, self.fieldname))
        except AttributeError:
            if ignore_errors:
                return None
            else:
                raise


class Limiter(object):
    """Rule for RateLimiter"""
    CTYPE = {'suspect': CounterSuspectAttr,
             'miltersession': MilterSessionAttr,
             'suspecttag': CounterSuspectTag,
             'suspectraw': CounterSuspectAttrRaw,
             'suspecttagraw': CounterSuspectTagRaw,
             }

    """Rule for ratelimit"""

    def __init__(self, name: str, setupdict: tp.Dict):
        # set priority, default is 0
        self.priority = setupdict.get('priority', None)
        self.priority = 0 if self.priority is None else int(self.priority)

        self.name = name
        self.number = None
        self.frame = None

        action = setupdict.get('action', "DUNNO").lower()
        self.action = SKIP if action == "skip" else string_to_actioncode(action)
        self.bounceaction = setupdict.get('bounceaction', None)

        if self.bounceaction:
            bounceaction = self.bounceaction.lower()
            self.bounceaction = SKIP if action == "skip" else string_to_actioncode(bounceaction)
        else:
            self.bounceaction = self.action

        loggername = "%s.limiter.%s" % (__package__ if __package__ else "fuglu", self.__class__.__name__)
        self.logger = logging.getLogger(loggername)

        self.counters = OrderedDict()
        self.strategy = setupdict.get('strategy', 'fixed')
        self._key = setupdict.get('key', None)
        assert self.strategy in AVAILABLE_STRATEGIES, \
            f"{name}: \"{self.strategy}\" is not in available strategies \"{AVAILABLE_STRATEGIES}\""

        # extract rate
        self.number, self.frame = Limiter._parse_rate(setupdict.get('rate', ""))
        self.states = Limiter._parse_state(setupdict.get('state'))

        # reject message
        self.message = setupdict.get("message", "RateLimited")

        # add counters
        counters = setupdict.get('count', {})
        for cname, cdict in counters.items():
            self.counters[cname] = self.add_counter(countername=cname, counterdict=cdict)

        # setup sum method, default is 'event'
        self._sum_impl = {
            'size': Limiter._sum_size,
            'data': Limiter._sum_data,
            'recipients': Limiter._sum_recipients,
            'event': Limiter._sum_event,
            'event_sub': Limiter._sum_event_sub,
            'zero': Limiter._sum_zero,
        }.get(setupdict.get('sum', 'event'), Limiter._sum_event)

    def lint(self) -> int:
        """Lint all the counters and return number of falied counter lints"""
        ierr = 0
        for cname, counter in self.counters.items():
            ierr += counter.lint()
        return ierr

    @property
    def key(self):
        return self._key if self._key else self.name

    def _sum_event(self, suspect: tp.Union[Suspect, sm.MilterSession, asm.MilterSession]) -> int:
        """Sum events, called by 'sum'"""
        return 1

    def _sum_event_sub(self, suspect: tp.Union[Suspect, sm.MilterSession, asm.MilterSession]) -> int:
        """Subtract events, called by 'sum'"""
        return -1

    def _sum_zero(self, suspect: tp.Union[Suspect, sm.MilterSession, asm.MilterSession]) -> int:
        """Sum 0 (just check if already over), called by 'sum'"""
        return 0

    def _sum_recipients(self, suspect: tp.Union[Suspect, asm.MilterSession, sm.MilterSession]) -> int:
        """Sum recipients (useful if called end-of-data), called by 'sum'"""
        numrecipients = len(suspect.recipients)
        return numrecipients

    def _sum_data(self, suspect: tp.Union[Suspect, asm.MilterSession, sm.MilterSession]) -> int:
        """Sum message data (size*number of recipients), called by 'sum'"""
        size = suspect.size
        numrecipients = self._sum_recipients(suspect=suspect)
        return numrecipients*size

    def _sum_size(self, suspect: tp.Union[Suspect, asm.MilterSession, sm.MilterSession]) -> int:
        """Sum message data, called by 'sum'"""
        return suspect.size

    def sum(self, suspect: tp.Union[Suspect, asm.MilterSession, sm.MilterSession]) -> int:
        """Select correct method to sum"""
        return self._sum_impl(self, suspect=suspect)

    @staticmethod
    def _parse_rate(rate: tp.Union[tp.Dict[str, str], str]) -> tp.Tuple[tp.Optional[float], tp.Optional[float]]:
        """parse rate (number of messages in timeframe) which can be given as string or dict"""
        number, frame = None, None
        if isinstance(rate, str):
            if rate.count('/') != 1:
                raise ValueError("Define rate as x/y or use dict 'number: x, frame: y'")
            number, frame = [float(a) for a in rate.split('/')]
        elif isinstance(rate, dict):
            number = float(rate.get("number", None))
            number = float(number) if number else None
            frame = float(rate.get("frame", None))
            frame = float(frame) if frame else None
        return number, frame

    @staticmethod
    def _parse_prefix(configdict: tp.Optional[tp.Dict[str, str]]) -> tp.Optional[tp.Tuple[str, tp.Optional[float], tp.Optional[float], tp.Optional[str], tp.Optional[tp.Dict[str, str]], tp.Optional[str]]]:
        if not configdict:
            return None
        assert "name" in configdict and ("rate" in configdict or "action" in configdict or "count" in configdict)
        name = configdict['name']
        assert name
        if name.startswith("$"):
            name = os.getenv(name[1:])
        number, frame = Limiter._parse_rate(configdict.get('rate'))
        message = configdict.get("message")
        count = configdict.get("count")
        action = configdict.get("action")
        return name, number, frame, message, count, action

    @staticmethod
    def _parse_state(state: tp.Optional[tp.Union[str, list]] = None) -> tp.List:
        """"""
        assert isinstance(state, (str, list)) or state is None
        if isinstance(state, str):
            rlist = Suspect.getlist_space_comma_separated(state)
        else:
            rlist = state
        if not rlist:
            # empty list -> set to all
            rlist = ALLSTATES
        return rlist

    def add_counter(self, countername: str, counterdict: tp.Dict) -> CounterInt:
        """Extract type of counter, create object and store it in counters"""
        ctype = counterdict.get("type", '<not given>').lower()

        try:
            return Limiter.CTYPE[ctype](countername, counterdict)
        except (AttributeError, KeyError):
            raise ValueError(f"type \"{ctype}\" not a valid type for counter \"{countername}\", valid types are {list(Limiter.CTYPE.keys())}")

    def examine(self, suspect: tp.Union[Suspect, asm.MilterSession, sm.MilterSession], ignore_errors: bool = True):
        for i, (cname, counter) in enumerate(self.counters.items(), 1):
            if counter.examine(suspect=suspect, ignore_errors=ignore_errors):
                self.logger.debug(f"{suspect.id} counter \"{cname}\" match {i}/{len(self.counters)} for limiter \"{self.name}\"")
            else:
                if BE_VERBOSE:
                    self.logger.debug(f"{suspect.id} counter \"{cname}\" DOESNT match {i}/{len(self.counters)} for limiter \"{self.name}\"")
                return False
        return True

    def get_fieldvaluesdict(self, suspect: tp.Union[Suspect, asm.MilterSession, sm.MilterSession], use_keys: bool = False) -> OrderedDict:
        """Create a dict with fieldname,fieldnamevalue for all limiters """
        valdict = OrderedDict()
        for fieldname, count in self.counters.items():
            # return key values for f
            if use_keys:
                # get the key identifier for counter (equal to
                # field if not specifically defined)
                fieldvalue = count.get_key(suspect=suspect)
            else:
                fieldvalue = count.get_field(suspect=suspect)
            if fieldvalue is not None and fieldvalue != FIELDVALUEIGNORE:
                valdict[fieldname] = fieldvalue
        return valdict

    def rejectmessage(self, suspect: Suspect):
        """Create rejectmessage, apply template"""
        return apply_template(self.message, suspect, values=self.get_fieldvaluesdict(suspect=suspect))


class RateLimitPlugin(BMPConnectMixin, BMPHeloMixin, BMPMailFromMixin,
                      BMPRCPTMixin, BMPHeaderMixin, BMPEOHMixin, BMPEOBMixin,
                      ScannerPlugin, BasicMilterPlugin):
    """Implement ALL milter states as well as the basic Scanner plugin"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars = {

            'limiterfile': {
                'default': '${confdir}/ratelimit.yml',
                'description': 'file based rate limits',
            },

            'backendtype': {
                'default': 'memory',
                'description': 'type of backend where the events are stored. memory is only recommended for low traffic standalone systems. alternatives are: redis, sqlalchemy, aioredis'  # pylint: disable=C0301
            },

            'backendconfig': {
                'default': '',
                'description': 'backend specific configuration. sqlalchemy: the database url, redis: redis://:[password]@hostname:6379/0'  # pylint: disable=C0301
            },

            'state': {
                'default': ','.join(BasicMilterPlugin.ALL_STATES.keys()),
                'description': f'comma/space separated list of milter states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            },

            'timeout': {
                'default': "10",
                'description': 'Processing timeout, abort further lookups when exceeded'
            }

        }

        self.logger = self._logger()
        self.logger.info("RateLimit plugin available backends: %s",
                         ' '.join([str(k) + " => " + str(AVAILABLE_BACKENDS[k].keys()) for k in AVAILABLE_BACKENDS.keys()]))

        # load limiters
        self.backends = {}
        self.logger.debug(f"Loading limiters")
        self.limiters = self.load_limiters()
        self.logger.debug(f"Loaded {len(self.limiters)} limiters")

        # after limiters, load backends for given backend and limiter strategies
        self.logger.debug(f"Loading backends")
        self.backends = self.load_backends()
        self.logger.debug(f"Init done")

    @staticmethod
    def yamlfile2dict(filename: str) -> tp.Dict:
        """Read yml file, return dict"""
        if not os.path.exists(filename):
            raise OSError(f"File {filename} does not exist!")
        with open(filename, 'r', encoding='utf-8') as fp:
            try:
                rawdict = yaml.full_load(fp)
            except AttributeError:
                rawdict = yaml.safe_load(fp)
        return rawdict

    def load_limiters(self, catch_exceptions: bool = True) -> tp.OrderedDict[str, Limiter]:
        # load file to dict, setup Limiters
        limiterdict = OrderedDict()
        try:
            # several files can be given
            limfiles = self.config.get(self.section, 'limiterfile')
            if limfiles:
                limfiles = Suspect.getlist_space_comma_separated(limfiles)
            else:
                limfiles = []

            rawdict = OrderedDict()
            for limfile in limfiles:
                rawdict_forfile = RateLimitPlugin.yamlfile2dict(limfile)
                if rawdict_forfile:
                    rawdict.update(rawdict_forfile)
            if rawdict is None:
                rawdict = OrderedDict()
            self.logger.info(f"Loaded {len(rawdict)} limiters in dict")

            # now build dict
            odict = OrderedDict()
            prios = set()
            for lname, ldict in rawdict.items():
                if BE_VERBOSE:
                    self.logger.debug(f"Create limiter for \"{lname}\"")
                newlimiter = Limiter(name=lname, setupdict=ldict)

                # prefix extension
                prefixdef = ldict.get("prefix")
                if prefixdef:
                    pldict = copy.deepcopy(ldict)
                    pprefname, pnumber, pframe, pmessage, count, action = Limiter._parse_prefix(prefixdef)
                    # modify the dict for the prefixed version
                    pname = f"{lname}-{pprefname}"
                    if 'key' in pldict:
                        pldict['key'] = f"{pldict['key']}-{pprefname}"
                    if pnumber is not None and pframe is not None:
                        pldict['rate'] = f"{pnumber}/{pframe}"
                    if pmessage:
                        pldict['message'] = pmessage
                    if count:
                        pldict['count'].update(count)
                    if action:
                        pldict['action'] = action

                    newplimiter = Limiter(name=pname, setupdict=pldict)
                    odict[pname] = newplimiter

                # prefix should be placed before original limiter
                odict[lname] = newlimiter
                prios.add(newlimiter.priority)

            if len(prios) > 1:
                self.logger.info("Different prios found -> sorting")
                limiterdict = OrderedDict(sorted(odict.items(), key=lambda kv: kv[1].priority))
            else:
                self.logger.info("No prios -> no sorting")
                limiterdict = OrderedDict(odict)
        except Exception as e:
            self.logger.error(str(e))
            if not catch_exceptions:
                raise Exception(str(e)).with_traceback(e.__traceback__)
        return limiterdict

    async def examine(self, suspect: Suspect):
        try:
            out = await self.core(suspect=suspect, state=EOM)
            return out
        except OSError as e:
            self.logger.warning(f"EOM asyncio-run(EOM) plugin got error {str(e)} -> retrying")

        out = await self.core(suspect=suspect, state=EOM)
        return out

    async def core(self, suspect: tp.Union[Suspect, asm.MilterSession, sm.MilterSession], state: str = EOM) -> tp.Union[int, tp.Tuple[int, str]]:
        """Main routine examining suspect, returncode from config if one limiter is exceeded"""
        if not HAVE_YAML:
            return DUNNO

        self.logger.debug(
            f"{suspect.id} -> state={state} -> limiters to check {[lname for lname,l in self.limiters.items() if state in l.states and l.number ]}")
        timeout = self.config.getfloat(self.section, 'timeout')
        starttime = time.time()
        errors = 0
        for lname, limiter in self.limiters.items():
            if BE_VERBOSE:
                self.logger.debug(f"{suspect.id} state={state} check limiter \"{lname}\"")
            if state not in limiter.states:
                if BE_VERBOSE:
                    self.logger.debug(f"{suspect.id} {state}-Limiter {lname} is not active for state {state}")
                continue
            if limiter.number is None or limiter.number <= 0:
                if BE_VERBOSE:
                    self.logger.debug(f"{suspect.id} {state}-Limiter {lname} is disabled (number={limiter.number})")
                continue
            if not limiter.examine(suspect=suspect):
                # limiter does not apply to this suspect
                if BE_VERBOSE:
                    self.logger.debug(f"{suspect.id} {state}-Limiter {lname} does NOT apply to this suspect")
                continue
            else:
                # limiter applies to this suspect
                self.logger.debug(f"{suspect.id} {state}-Limiter {lname} applies to this suspect")

            fieldvalues = list(limiter.get_fieldvaluesdict(suspect=suspect, use_keys=True).values())

            checkval = ','.join(fieldvalues)

            eventname = limiter.key + checkval
            timespan = limiter.frame

            try:
                increment = limiter.sum(suspect=suspect)
                curbackend = self.backends[limiter.strategy]
                iscoroutine = asyncio.iscoroutinefunction(curbackend.check_allowed)
                self.logger.debug(f'{suspect.id} {state}-Limiter event {eventname} -> run (async={iscoroutine})')
                if iscoroutine:
                    (allow, count) = await curbackend.check_allowed(eventname, limiter.number, timespan, increment)
                else:
                    (allow, count) = curbackend.check_allowed(eventname, limiter.number, timespan, increment)
                if count < 0:
                    errors += 1
                self.logger.debug(
                    f'{suspect.id} {state}-Limiter event {eventname} (allow={allow},DUNNO={limiter.action == DUNNO}),SKIP={limiter.action == SKIP} count: {count}')

                limiteraction = limiter.action if suspect.from_address else limiter.bounceaction
                if not allow and limiteraction == SKIP:
                    self.logger.info(f"{suspect.id} (state={state}) SKIP remaining ratelimit tests for this state")
                    return DUNNO
                if not allow and limiteraction != DUNNO:
                    self.logger.debug(f'{suspect.id} {state}-Limiter: instance is of type {suspect.__class__.__name__}')
                    if isinstance(suspect, Suspect):
                        return limiteraction, apply_template(limiter.message, suspect, values=limiter.get_fieldvaluesdict(suspect=suspect, use_keys=True))
                    elif isinstance(suspect, (asm.MilterSession, sm.MilterSession)):
                        try:
                            self.logger.debug(f'{suspect.id} {state}-Limiter: MilterSession -> create SuspectTemplate with message {limiter.message}')
                            template = _SuspectTemplate(limiter.message)
                        except Exception as e:
                            self.logger.debug(f'{suspect.id} {state}-Limiter: exception=\"{str(e)}\"', exc_info=e)
                            template = _SuspectTemplate('')

                        try:
                            # python 3.9
                            self.logger.debug(f'{suspect.id} {state}-Limiter: MilterSession -> create SuspectTemplate MAP(Python 3.9)')
                            map = suspect.get_templ_dict() | limiter.get_fieldvaluesdict(suspect=suspect, use_keys=True)
                        except Exception:
                            # python >= 3.5
                            self.logger.debug(f'{suspect.id} {state}-Limiter: MilterSession -> create SuspectTemplate MAP(Python 3.5)')
                            map = {**suspect.get_templ_dict(), **limiter.get_fieldvaluesdict(suspect=suspect, use_keys=True)}

                        self.logger.debug(f"{suspect.id} (state={state}) mapping for templated return message: {map}")
                        message = template.safe_substitute(map)
                        self.logger.debug(f"{suspect.id} (state={state}) message generated: {message}")
                        return limiteraction, message
            except ConnectionResetError as ex:
                error = type(ex).__name__, str(ex)
                self.logger.warning(f'{suspect.id} (state={state}) Failed to run limiter backend for strategy '
                                    f'"{limiter.strategy}" eventname {eventname} error {error}'
                                    )
            except Exception as ex:
                error = type(ex).__name__, str(ex)
                self.logger.error(f'{suspect.id} (state={state}) Failed to run limiter backend for strategy '
                                  f'"{limiter.strategy}" eventname {eventname} error {error}'
                                  )
                self.logger.debug(f"{suspect.id} (state={state}) error traceback...", exc_info=ex)

            timediff = time.time() - starttime
            if timediff > timeout:
                self.logger.warning(f'{suspect.id} timeout exceeded after %.2fs, aborting further lookups, errors={errors}' % timediff)
                break
            elif errors > 3:
                self.logger.warning(f'{suspect.id} error count exceeded after %.2fs, aborting further lookups, errors={errors}' % timediff)
                break

        return DUNNO

    @property
    def required_strategies(self) -> tp.List:
        # return list with strategies for limiters registered
        return self.get_strategy_list()

    def get_strategy_list(self, limiters: tp.Optional[tp.Dict[str, Limiter]] = None) -> tp.List[str]:
        # if dict with limiters is given use this limiter, otherwise use limiters registered
        llist = limiters if limiters is not None else self.limiters
        blist = [l.strategy for l in llist.values()]
        return list(set(blist))

    def load_backends(self,
                      inlimitersdict: tp.Optional[tp.Dict[str, Limiter]] = None,
                      catch_exceptions: bool = True
                      ) -> tp.Dict[str, BackendInterface]:
        """ Of all the AVAILABLE_BACKENDS
        load only the backends required by limiters
        """
        if inlimitersdict:
            limitersdict = inlimitersdict
            required_strategies = self.get_strategy_list(limiters=limitersdict)
        else:
            limitersdict = self.limiters
            required_strategies = self.required_strategies

        backends = {}
        self.logger.debug(f"Loading backend for strategies: {required_strategies}")
        for strategy in required_strategies:
            self.logger.debug(f"Loading strategy \"{strategy}\"")
            btype = self.config.get(self.section, 'backendtype')
            if strategy in self.backends:
                # next loop for next strategy
                continue

            if btype not in AVAILABLE_BACKENDS[strategy]:
                errormsg = f'RateLimit backend {btype} not available for strategy {strategy}'
                self.logger.error(errormsg)
                if not catch_exceptions:
                    raise ValueError(errormsg)
                else:
                    continue
            backendconfig = self.config.get(self.section, 'backendconfig')

            try:
                backend_instance = AVAILABLE_BACKENDS[strategy][btype](backendconfig)
                backends.update(
                    {
                        strategy: backend_instance
                    }
                )
            except Exception as ex:
                error = type(ex).__name__, str(ex)
                errormsg = f'Failed to load backend {strategy}.{btype} error {error}'
                self.logger.error(errormsg)
                if not catch_exceptions:
                    raise Exception(errormsg).with_traceback(ex.__traceback__)
        return backends

    def lint(self, state=EOM) -> bool:
        from fuglu.funkyconsole import FunkyConsole

        if state and state not in self.state and state != EOM:
            # not active in current state
            return True

        fc = FunkyConsole()
        check_config = super().lint()
        if not check_config:
            print(fc.strcolor("ERROR - config check", "red"))
            return False
        try:
            alllimiters = self.load_limiters(catch_exceptions=False)
            if state:
                limiters = OrderedDict()
                for lname, lim in alllimiters.items():
                    if state in lim.states:
                        limiters[lname] = lim
            else:
                limiters = alllimiters

            print(f"Loading ({len(limiters)}) limiters: ok")

            for lname, limiter in limiters.items():
                print(f"- Limiter", fc.strcolor(str(lname), 'cyan'), ':')
                if limiter.lint() > 0:
                    print(fc.strcolor(f"ERROR - linting counters of limiter {lname}", "red"))
                    return False
        except Exception as e:
            print(f"Error loading limiters: {str(e)}")
            print(fc.strcolor("ERROR - loading limiters", "red"))
            if BE_VERBOSE:
                import traceback
                traceback.print_exc()
            return False

        try:
            required_strategies = self.get_strategy_list(limiters=limiters)
            print(f"Strategies ({len(required_strategies)}): {required_strategies}")
        except Exception as e:
            print(f"Error loading strategies: {str(e)}")
            print(fc.strcolor("ERROR - loading strategies", "red"))
            return False

        try:
            backends = self.load_backends(inlimitersdict=limiters, catch_exceptions=False)
            print("Loading backends: ok")
        except Exception as e:
            print(f"Error loading backends: {str(e)}")
            print(fc.strcolor("ERROR - loading backends", "red"))
            return False
        return True

    def _convert_return2milter(self, ret: tp.Union[int, tp.Tuple[int, str]])\
            -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        if isinstance(ret, tuple):
            return retcode2milter[ret[0]], ret[1]
        elif isinstance(ret, int):
            return retcode2milter[ret]
        else:
            raise ValueError(f"ret type should be tuple(int, str) or int -> but is {type(ret)}")

    async def examine_connect(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], host: bytes, addr: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._convert_return2milter(await self.core(suspect=sess, state=CONNECT))

    async def examine_helo(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], helo: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._convert_return2milter(await self.core(suspect=sess, state=HELO))

    async def examine_mailfrom(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], sender: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._convert_return2milter(await self.core(suspect=sess, state=MAILFROM))

    async def examine_rcpt(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        # called before recipient is added to sess.recipients, we need a special temp object to make ratelimit work...
        original_recipients = list(sess.recipients)
        try:
            if recipient:
                sess.recipients.append(recipient)
            out = self._convert_return2milter(await self.core(suspect=sess, state=RCPT))
        except Exception:
            if recipient:
                sess.recipients = original_recipients
            raise
        else:
            if recipient:
                sess.recipients = original_recipients
        return out

    async def examine_header(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], key: bytes, value: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._convert_return2milter(await self.core(suspect=sess, state=HEADER))

    async def examine_eoh(self, sess: tp.Union[asm.MilterSession, sm.MilterSession]) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._convert_return2milter(await self.core(suspect=sess, state=EOH))

    async def examine_eob(self, sess: tp.Union[asm.MilterSession, sm.MilterSession]) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._convert_return2milter(await self.core(suspect=sess, state=EOB))
