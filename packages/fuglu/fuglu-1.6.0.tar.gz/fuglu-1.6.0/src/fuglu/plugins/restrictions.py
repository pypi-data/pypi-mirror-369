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
import os
import typing as tp

# Python3.6 fix
try:
    _ = tp.OrderedDict
except AttributeError:
    tp.OrderedDict = tp.Dict

import re
import logging
from collections import defaultdict
try:
    from unittest.mock import MagicMock
except ModuleNotFoundError:
    MagicMock = None

from domainmagic.rbl import RBLLookup
from domainmagic.tld import TLDMagic

import libmilter as lm
import fuglu.connectors.milterconnector as sm
import fuglu.connectors.asyncmilterconnector as asm

from fuglu.shared import (
    ScannerPlugin, DUNNO,  Suspect,
    string_to_actioncode, _SuspectTemplate
)
from fuglu.mshared import (
    BMPConnectMixin, BMPHeloMixin, BMPMailFromMixin,
    BMPRCPTMixin, BasicMilterPlugin, retcode2milter, EOM, BMPHeaderMixin,
    BMPEOHMixin
)
from fuglu.stringencode import force_uString
from fuglu.plugins.ratelimit.dynfunction import MultipleFunctionsWrapper
from fuglu.plugins.ratelimit.main import TemplateFunctionWrapper
from fuglu.plugins.ratelimit.helperfuncs import get_ptr as get_ptr_helper

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    yaml = None
    HAVE_YAML = False

BE_VERBOSE = False
regexrule = re.compile(
    r"^/(?P<regex>.{1,200}[^\\])\/(?P<flag>[a-z])?[ \t]{1,150}((?P<astring>[A-Z]{1,8})|(?P<acode>[0-9]{3}))([ \t]{1,150}(?P<msg>.{1,100}))?$")
ifregex = re.compile(r"if /(?P<regex>.{1,200}[^\\])\/(?P<flag>[a-z])?[ \t]{0,150}$")
hashrule = re.compile(r"^(?P<key>\S{1,200})[ \t]{1,150}((?P<astring>[A-Z]{1,8})|(?P<acode>[0-9]{3}))([ \t]{1,150}(?P<msg>.{1,100}))?$")


RESTRICTIONS_TAG = 'AccessRestrictionResults'


class CreateSubdomainListMixin(object):
    def __init__(self, **kwargs):
        self.tldmagic = TLDMagic()
        super().__init__(**kwargs)

    def create_sudomain_list(self, domain: str, reverse: bool = False) -> tp.List[str]:
        """Create subdomain list, from domain to smallest subdomain
        unless reversed.

        Example:
            - in: a.b.c.d.com
              out: [d.com, c.d.com, b.c.d.com, a.b.c.d.com]
            """
        tldcount = self.tldmagic.get_tld_count(domain)
        parts = domain.split('.')

        subrange = range(tldcount + 1, len(parts) + 1)
        checkstrings = []
        for subindex in subrange:
            subdomain = '.'.join(parts[-subindex:])
            checkstrings.append(subdomain)
        if checkstrings and reverse:
            checkstrings = checkstrings[::-1]
        return checkstrings


class MatchRestriction(object):
    def __init__(self,
                 actionstring: str = "REJECT",
                 actioncode: tp.Optional[int] = None,
                 message: tp.Optional[str] = None,
                 **kwargs):
        self.milteraction = retcode2milter[string_to_actioncode(actionstring)] if actionstring else None
        self.actioncode = actioncode
        self.message = message
        self.logger = logging.getLogger(f"fuglu.plugin.restrictions.{self.__class__.__name__}")
        assert bool(self.milteraction) or bool(self.actioncode)
        super().__init__(**kwargs)

    def match(self, inputstring: str) -> bool:
        raise NotImplementedError("Match not implemented!")

    def examine(self, inputstring: str) -> tp.Tuple:
        if self.match(inputstring):
            return self.actioncode if self.actioncode else self.milteraction, self.message
        else:
            return ()


class RegexRestriction(MatchRestriction):

    @staticmethod
    def lines2regex(lines: tp.List[str], ignoreerrors: bool = True, logger=None) -> tp.List[MatchRestriction]:
        """Parse lines from pcre file, create reges options"""
        restrictions = []
        multilineconditions = []
        for line in lines:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            elif line.lower().startswith("if"):
                match = ifregex.match(line)
                regexstring = match['regex']
                flag = match['flag']
                multilineconditions.append((regexstring, flag))
            elif line.lower().startswith("endif"):
                if multilineconditions:
                    _ = multilineconditions.pop()
            else:
                match = regexrule.match(line)
                if match:
                    regexstring = match['regex']
                    actionstring = match['astring']
                    actioncode = match['acode']
                    flag = match['flag']
                    if actioncode:
                        actioncode = int(actioncode)
                    message = match['msg']

                    if multilineconditions:
                        regexstring = [regexstring] + [regstring for regstring, flg in multilineconditions]
                        flag = [flag] + [flg for regstring, flg in multilineconditions]

                    restrictions.append(RegexRestriction(regexstring=regexstring,
                                                         actionstring=actionstring,
                                                         actioncode=actioncode,
                                                         message=message,
                                                         flag=flag,
                                                         ))
                else:
                    if ignoreerrors:
                        if logger:
                            logger.error(f"No match parsing regex line -> ignoreing line:{line}")
                    else:
                        raise ValueError(f"No match parsing regex line -> ignoreing line:{line}")
        return restrictions

    def __init__(self,
                 regexstring: tp.Union[str, tp.List[str]],
                 actionstring: str = "REJECT",
                 actioncode: tp.Optional[int] = None,
                 message: tp.Optional[str] = None,
                 flag: tp.Optional[tp.Union[str, tp.List[str]]] = None):
        super().__init__(actionstring=actionstring, actioncode=actioncode, message=message)
        self.regexstring = regexstring
        if isinstance(regexstring, list) and isinstance(flag, list):
            assert len(regexstring) == len(flag)
            self.regex = []
            for rgxs, flg in zip(regexstring, flag):
                assert flg is None or flg == "i"
                rgx = re.compile(rgxs, flags=0 if flg == "i" else re.IGNORECASE)
                assert bool(rgx)
                self.regex.append(rgx)
        elif not isinstance(regexstring, list) and not isinstance(flag, list):
            assert flag is None or flag == "i"
            # defaut is case insensitive, like postfix...
            # "i" flag toggles case insensitivity
            self.regex = re.compile(regexstring, flags=0 if flag == "i" else re.IGNORECASE)
            assert bool(self.regex)
        else:
            raise ValueError("Either both regexstring and flags are array or both must be string")

    def match(self, inputstring: str) -> bool:
        if isinstance(self.regex, list):
            return all(rgx.search(inputstring) for rgx in self.regex)
        else:
            return bool(self.regex.search(inputstring))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.regexstring})"


class HashCore(MatchRestriction):

    def __init__(self,
                 keystring: str,
                 actionstring: str = "REJECT",
                 actioncode: tp.Optional[int] = None,
                 message: tp.Optional[str] = None,
                 ):
        super().__init__(actionstring=actionstring, actioncode=actioncode, message=message)
        self.keystring = keystring
        assert self.keystring is not None and self.keystring.strip() != ""

    def match(self, inputstring: tp.Union[str, tp.List[str]]) -> tp.Optional[str]:
        """
        Match implementation, returning matching string from input list of strings
        """
        if not inputstring:
            return None

        if isinstance(inputstring, str):
            inputstring = [inputstring]

        for tin in inputstring:
            if tin == self.keystring:
                return tin
        return None

    def examine(self, inputstring: tp.Union[str, tp.List[str]]) -> tp.Tuple:
        """
        Examine, special implementation, getting return of match and return matching string as well
        since input can be a list of strings
        """
        hashmatch = self.match(inputstring)
        if hashmatch:
            hashcore: HashCore
            hashmatch: str
            return self.actioncode if self.actioncode else self.milteraction, self.message, hashmatch
        else:
            return ()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.keystring})"


class HashTable(MatchRestriction):
    def __init__(self, filename: str):
        super().__init__(actionstring='REJECT')
        self.filename = filename
        self.restrictions = self.loadhashesfromfile(self.filename, ignoreerrors=True)

    def loadhashesfromfile(self, filename: str, ignoreerrors: bool = True) -> tp.Dict[str, HashCore]:
        try:
            lines = RestrictionSet._file2lines(filename=filename)
            hashcore_objects = HashTable.lines2hashcores(lines, ignoreerrors=ignoreerrors, logger=self.logger)
            self.logger.info(f"Loaded {len(hashcore_objects)} hash rules from {filename}")

        except Exception as e:
            hashcore_objects = {}
            self.logger.error(f"Parsing error for file {filename}: {str(e)}")
            if not ignoreerrors:
                raise Exception(str(e)).with_traceback(e.__traceback__)
        return hashcore_objects

    @staticmethod
    def lines2hashcores(lines: tp.List[str], ignoreerrors: bool = True, logger=None) -> tp.Dict[str, HashCore]:
        """Parse lines from hash file, create HashCore objects, put then in dict"""
        restrictions = {}
        for line in lines:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            else:
                match = hashrule.match(line)
                if match:
                    keystring = match['key']
                    actionstring = match['astring']
                    actioncode = match['acode']
                    if actioncode:
                        actioncode = int(actioncode)
                    message = match['msg']

                    if not keystring:
                        if ignoreerrors:
                            if logger:
                                logger.warning(f"No key extracted for line: '{line}' -> ignore")
                        else:
                            raise ValueError(f"No key extracted for line: '{line}' -> ignore")
                    restrictions[keystring] = HashCore(keystring=keystring,
                                                       actionstring=actionstring,
                                                       actioncode=actioncode,
                                                       message=message)
                else:
                    if ignoreerrors:
                        if logger:
                            logger.error(f"No match parsing regex line -> ignoreing line:{line}")
                    else:
                        raise ValueError(f"No match parsing regex line -> ignoreing line:{line}")
        return restrictions

    def match(self, inputstring: tp.Union[str, tp.List[str]]) -> tp.Optional[tp.Tuple[HashCore, str]]:
        """
        Match implementation, returning HashCore object of match as wel as matching string from
        input list of strings
        """
        if not inputstring:
            return None

        if isinstance(inputstring, str):
            inputstring = [inputstring]
        for tin in inputstring:
            obj = self.restrictions.get(tin)
            if obj:
                return (obj, tin)
        return None

    def examine(self, inputstring: tp.Union[str, tp.List[str]]) -> tp.Tuple:
        """
        Examine, special implementation, getting return of match and return matching string as well
        since input can be a list of strings
        """
        match = self.match(inputstring)
        if match:
            hashcore, hashmatch = match
            hashcore: HashCore
            hashmatch: str
            return hashcore.actioncode if hashcore.actioncode else hashcore.milteraction, hashcore.message, hashmatch
        else:
            return ()


class RBLRestriction(MatchRestriction):
    def __init__(self,
                 providertype: str,
                 searchdomain: str,
                 resultconfig: tp.List[str],
                 actionstring: str = 'REJECT',
                 actioncode: tp.Optional[int] = None,
                 message: tp.Optional[str] = None,
                 checksubdomains: tp.Optional[bool] = None,
                 ):
        super().__init__(actionstring=actionstring, actioncode=actioncode, message=message)
        self.providertype = providertype
        self.searchdomain = searchdomain
        self.resultconfig = resultconfig
        assert bool(self.providertype) and bool(self.searchdomain) and bool(self.resultconfig)
        self.rbllookup = self._create_rbl()
        if self.message:
            if "${output}" in self.message:
                self.message = self.message.replace("${output}", "${input} is listed on ${rbldomain} (${identifier})")
            self.rbllookup.providers[0].descriptiontemplate = self.message
            self.message = None
        assert bool(self.rbllookup)
        self.checksubdomains = bool(checksubdomains)
        self.tldmagic = TLDMagic() if self.checksubdomains else None

    def _create_rbl(self):
        rbl = RBLLookup()
        if self.providertype not in rbl.providermap:
            self.logger.error(f"unknown provider type {self.providertype} for {self.searchdomain}")
            return None

        providers = []
        providerclass = rbl.providermap[self.providertype]
        providerinstance = providerclass(self.searchdomain, timeout=rbl.timeout, lifetime=rbl.lifetime)

        # set bitmasks and filters
        for res in self.resultconfig:
            filters = None
            if ':' in res:
                fields = res.split(':')
                try:
                    code = int(fields[0])
                except (ValueError, TypeError):
                    # fixed value
                    code = fields[0]
                identifier = fields[1]
                if len(fields) > 2:
                    filters = fields[2:]
            else:
                identifier = res
                code = 2

            providerinstance.add_replycode(code, identifier)
            providerinstance.add_filters(filters)
        providers.append(providerinstance)

        rbl.providers = providers
        self.logger.debug("Providerlist from configfile: {providers}")
        return rbl

    def match(self, inputstring: str) -> str:
        if self.checksubdomains:
            tldcount = self.tldmagic.get_tld_count(inputstring)
            parts = inputstring.split('.')

            subrange = range(tldcount + 1, len(parts) + 1)
            checkstrings = []
            for subindex in subrange:
                subdomain = '.'.join(parts[-subindex:])
                checkstrings.append(subdomain)
        else:
            checkstrings = [inputstring]

        for cstring in checkstrings:
            listings = self.rbllookup.listings(cstring)
            for identifier, humanreadable in listings.items():
                self.logger.debug(f"RBL hit: input={cstring} idendifier={identifier} info={humanreadable}")
                return humanreadable
        return ""

    def examine(self, inputstringlist: tp.Union[tp.List[str], str]) -> tp.Tuple:
        inputstringlist = [inputstringlist] if isinstance(inputstringlist, str) else inputstringlist
        for inputstring in inputstringlist:
            msg = self.match(inputstring)
            if msg:
                # if there's a message defined, the rbl output can be customized, use ${output}
                # in the message to place the rbl output
                if self.message:
                    template = _SuspectTemplate(self.message)
                    output = {'output': msg}
                    msg = template.safe_substitute(output)
                return self.actioncode if self.actioncode else self.milteraction, msg
        return ()

    def _str_(self) -> str:
        return f"{self.__class__.__name__}({self.providertype}/{self.searchdomain})"


class RestrictionSet(object):
    # default variables to test in the stages if not given differently
    DEFAULT_STAGE_ATTRS = {
        sm.CONNECT: "addr",
        sm.HELO: "heloname",
        sm.MAILFROM: "from_address",
        sm.RCPT: "to_address",
        sm.HEADER: None,
        sm.EOH: None
    }

    """Stores a set of restrictions, for example regex list defined in a file"""

    def __init__(self, name: str, config: tp.Dict, ignoreerrors: bool = True):
        self.name = name
        self.config = config
        self.restrictions = []
        self.regexfile = config.get("regexfile")
        self.hashfile = config.get("hashfile")
        self.logger = logging.getLogger(f"fuglu.plugin.restrictions.RestrictionSet({self.name})")
        self.rblconfig = config.get('rbl', None)
        self.hashconfig = config.get('hash', None)
        if self.regexfile:
            self.restrictions = self.loadregexfile(filename=self.regexfile, ignoreerrors=ignoreerrors)
        elif self.rblconfig:
            assert bool(self.rblconfig.get("providertype")) and bool(self.rblconfig.get("searchdomain")) and bool(self.rblconfig.get("resultconfig"))

            rbl = RBLRestriction(providertype=self.rblconfig.get("providertype"),
                                 searchdomain=self.rblconfig.get("searchdomain"),
                                 resultconfig=self.rblconfig.get("resultconfig"),
                                 checksubdomains=self.rblconfig.get("checksubdomains"),
                                 message=self.rblconfig.get("message")
                                 )
            self.restrictions = [rbl]
        elif self.hashfile:
            hsh = HashTable(filename=self.hashfile)
            self.restrictions = [hsh]
        elif self.hashconfig:
            hshcore = HashCore(
                keystring=self.hashconfig.get('match', None),
                actionstring=self.hashconfig.get('action', "REJECT"),
                message=self.hashconfig.get('message', "")
            )
            self.restrictions = [hshcore]

    @staticmethod
    def _file2lines(filename: str) -> tp.List[str]:
        """Load regexfile"""
        with open(filename, 'r') as f:
            lines = f.readlines()
        return lines

    def loadregexfile(self, filename: str, ignoreerrors: bool = True):
        try:
            lines = RestrictionSet._file2lines(filename=filename)
            regex_objects = RegexRestriction.lines2regex(lines, ignoreerrors=ignoreerrors, logger=self.logger)
            self.logger.info(f"Loaded {len(regex_objects)} regex rules from {filename}")

        except Exception as e:
            regex_objects = []
            self.logger.error(f"Parsing error for file {filename}: {str(e)}")
            if not ignoreerrors:
                raise Exception(str(e)).with_traceback(e.__traceback__)
        return regex_objects

    def examine(self, inputstring: str):
        for r in self.restrictions:
            r: MatchRestriction
            out = r.examine(inputstring)
            if BE_VERBOSE:
                self.logger.debug(f"RestrictionSet({self.name}), Restriction({str(r)}) ->teststring={inputstring} -> out:{out}")
            if out:
                return out
        return None


class AccessRestrictions(BMPConnectMixin, BMPHeloMixin, BMPMailFromMixin, BMPRCPTMixin,
                         BMPHeaderMixin, BMPEOHMixin, ScannerPlugin, BasicMilterPlugin):
    """
    Restrict mail access based on complex rulesets. Upon rule hit, mail can be rejected or deferred.

    Rules are read from yaml-file, thus python-yaml is a required dependency.
    """

    DEFAULTSTATES = [sm.CONNECT, sm.HELO, sm.MAILFROM, sm.RCPT, sm.HEADER, sm.EOH]

    # states
    #CONNECT = "connect"
    #HELO = "helo"
    #MAILFROM = "mailfrom"
    #RCPT = "rcpt"
    #HEADER = "header"
    #EOH = "eoh"
    #EOB = "eob"

    DELAY_REJ_BEFORE = 1
    DELAY_REJ_STATE = 2
    DELAY_REJ_AFTER = 3
    DELAY_REJ_TAG = 'AccessRestrictions.delayedreject'

    get_ptr = get_ptr_helper  # define here for easy monkey patching in unit tests

    @staticmethod
    def _load_yamlfile(filename: str) -> tp.Union[tp.Dict, tp.OrderedDict]:
        if not os.path.exists(filename):
            raise OSError(f"File {filename} does not exist!")

        # load yaml config file
        with open(filename, 'r', encoding='utf-8') as fp:
            try:
                configdict = yaml.full_load(fp)
            except AttributeError:
                configdict = yaml.safe_load(fp)
        return configdict

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars = {
            'restrictionfile': {
                'default': '${confdir}/accessrestrictions.yml',
                'description': 'access restrictions yaml-file with "restrictions"-array and "setup"-dict',
            },
            'delay_rejects': {
                'default': 'rcpt',
                'description': f'Delay reject to this state, empty means immediate reject'
            },
            'eom_trigger_header': {
                'default': '',
                'description': f'If defined, only run plugin end-of-message if header is present'
            },
            'state': {
                'default': ','.join(AccessRestrictions.DEFAULTSTATES),
                'description': f'comma/space separated list of milter states this plugin should be '
                               f'applied ({",".join(AccessRestrictions.DEFAULTSTATES)})'
            }
        }
        self.logger = self._logger()
        self.delay_rejects = self._set_delay_reject()
        self.delay_rejects_statedict = self._set_delay_state_dict(self.delay_rejects)
        self.restrictions_sets, self.setupdict = self._create_dicts(ignoreerrors=True)

    def _set_delay_state_dict(self, delay_reject_state: tp.Optional[str]):
        delay_state_dict = {}
        if delay_reject_state:
            # it's only possible to delay to an active state of the plugin
            allstates_sorted = [asm.CONNECT, asm.HELO, asm.MAILFROM, asm.RCPT, asm.HEADER, asm.EOH, asm.EOB]
            allstates_sorted = [s for s in allstates_sorted if s in self.state]

            setpos = AccessRestrictions.DELAY_REJ_AFTER
            # go backwards
            for s in allstates_sorted[::-1]:
                if s == delay_reject_state:
                    delay_state_dict[s] = AccessRestrictions.DELAY_REJ_STATE
                    setpos = AccessRestrictions.DELAY_REJ_BEFORE
                else:
                    delay_state_dict[s] = setpos

        return delay_state_dict

    def _set_transformations(self, stringlist: tp.Union[tp.List[str]], ignoreerrors: bool = True):
        try:
            funclist = force_uString([stringlist] if isinstance(stringlist, str) else stringlist)
            trans = MultipleFunctionsWrapper(funclist=funclist, DefaultProcessorClass=TemplateFunctionWrapper)
        except Exception as e:
            if ignoreerrors:
                trans = None
            else:
                raise Exception(str(e)).with_traceback(e.__traceback__)
        return trans

    def _create_dicts(self, ignoreerrors: bool = True) \
            -> tp.Tuple[tp.Dict[str, RestrictionSet], tp.DefaultDict[str, tp.List[str]]]:
        # return default dict with empty list by default
        restrictions_sets = {}
        setupdict = defaultdict(list)

        filename = self.config.get(self.section, 'restrictionfile', fallback='')
        if not filename or not filename.strip():
            # no definitions -> return empty
            if ignoreerrors:
                self.logger.warning(f"No config yaml file to load, plugin will not do anything")
            else:
                raise ValueError(f"No config yaml file to load!")
            return restrictions_sets, setupdict

        try:
            configdict = AccessRestrictions._load_yamlfile(filename)
        except Exception as e:
            if ignoreerrors:
                self.logger.warning(f"File does not exists or problem while loading: {filename} "
                                    f"-> plugin will not do anything")
                return restrictions_sets, setupdict
            else:
                raise Exception(str(e)).with_traceback(e.__traceback__)

        restrictions = configdict.get("restrictions", {})
        if not restrictions:
            self.logger.warning(f"No restrictions to load defined in {filename}, plugin will not do anything")
            return restrictions_sets, setupdict

        setup = configdict.get("setup")
        if not setup:
            if ignoreerrors:
                self.logger.warning(f"Missing setup key load in {filename}, plugin will not do anything")
            else:
                raise ValueError(f"No setup to load defined in {filename}!")
            return restrictions_sets, setupdict

        force_state = self.config.get(self.section, 'force_state', fallback=None)
        if force_state:
            oldsetup = setup
            setup = {force_state: []}
            for v in oldsetup.values():
                # vis an array of dicts defining where a restriction is applied
                # -> check if dict is already in array, add only if new because they are now all
                #     in the same state
                for definition in v:
                    if definition not in setup[force_state]:
                        setup[force_state].append(definition)
            self.logger.debug(f"Forced setup states to force_state={force_state}")

        if not isinstance(restrictions, list):
            self.logger.debug(f"Only one restriction, set as array")
            restrictions = [restrictions]

        for rdef in restrictions:
            # there has to be a name defined
            name = rdef.get('name')
            if not name:
                self.logger.error("No name defined for entry in restrictions!")
                if not ignoreerrors:
                    raise ValueError("No name defined for entry in restrictions!")

            if name in restrictions_sets:
                if ignoreerrors:
                    self.logger.warning(f"Restriction name \"{name}\" is defined multiple times, "
                                        f"only last one will be applied!")
                else:
                    self.logger.error(f"Restriction name \"{name}\" is defined multiple times!")
                    raise KeyError(f"Restriction name \"{name}\" is defined multiple times!")
            restrictions_sets[name] = RestrictionSet(name=name, config=rdef, ignoreerrors=ignoreerrors)

        for state, resdefinitions in setup.items():
            if not resdefinitions:
                if ignoreerrors:
                    self.logger.warning(f"Given setup state:{state} doesn't have config... -> ignore")
                    continue
                else:
                    self.logger.error(f"Given setup state:{state} doesn't have config...!")
                    raise ValueError(f"Given setup state:{state} doesn't have config...!")

            for resdef in resdefinitions:
                # if state is not available
                if state not in AccessRestrictions.DEFAULTSTATES and state != EOM:
                    if ignoreerrors:
                        self.logger.warning(f"Given setup state:{state} not available: {self.state} -> ignoring")
                        continue
                    else:
                        self.logger.error(f"Given setup state:{state} not available: {self.state}")
                        raise ValueError(f"Given setup state:{state} not available: {self.state}")

                name = resdef.get('name')
                available_restriction_names = list(restrictions_sets.keys())
                if name not in available_restriction_names:
                    if ignoreerrors:
                        self.logger.warning(f"State:{state} -> Restrictionset name:{name} not available: {available_restriction_names} -> ignoring")
                        continue
                    else:
                        self.logger.error(f"State:{state} -> Restrictionset name:{name} not available: {available_restriction_names}")
                        raise ValueError(f"State:{state} -> Restrictionset name:{name} not available: {available_restriction_names}")

                input = resdef.get('input')
                if not input or not input.strip():
                    input = RestrictionSet.DEFAULT_STAGE_ATTRS[state]

                # None is possible here for headers
                if state == EOM:
                    inputs_possible = list(self._gen_suspect_attrdict(
                        Suspect("from@fuglu.org", "to@fuglu.org", "/dev/null"), setall=True).keys())
                    inputs_possible.append("headers")
                elif state == asm.EOH:
                    inputs_possible = ["headers"]
                else:
                    if MagicMock:
                        inputs_possible = list(asm.MilterSession(MagicMock(), MagicMock()).get_templ_dict(setall=True).keys())
                    else:
                        inputs_possible = None

                if input is not None and inputs_possible is not None and input not in inputs_possible:
                    if ignoreerrors:
                        self.logger.warning(f"State:{state} -> Restrictionset input:{input} not available: {inputs_possible} -> ignoring")
                        continue
                    else:
                        self.logger.error(f"State:{state} -> Restrictionset input:{input} not available: {inputs_possible}")
                        raise ValueError(f"State:{state} -> Restrictionset input:{input} not available: {inputs_possible}")

                transformations = resdef.get('transformations')
                if transformations:
                    transformations = self._set_transformations(stringlist=transformations, ignoreerrors=ignoreerrors)

                setupdict[state].append({
                    'name': name,
                    'input': input,
                    'transformations': transformations
                })

        return restrictions_sets, setupdict

    def _set_delay_reject(self, ignoreerrors: bool = True) -> tp.Optional[str]:
        delay_rejects = None
        try:
            delay_rejects = self.config.get(self.section, 'delay_rejects')
            if delay_rejects:
                delay_rejects = delay_rejects.lower()
                valid_milter_states = AccessRestrictions.DEFAULTSTATES
                assert delay_rejects in valid_milter_states, f"delay_rejects state({delay_rejects}) not valid (choices: {valid_milter_states})"
                assert delay_rejects in self.state, f"delay_rejects state({delay_rejects}) is not in plugin states: {self.state}"
                assert isinstance(self, BasicMilterPlugin.ALL_STATES[delay_rejects]), f"delay_rejects state({delay_rejects}) state is not implemented"
        except Exception as e:
            if ignoreerrors:
                pass
            else:
                raise Exception(str(e)).with_traceback(e.__traceback__)
        return delay_rejects

    def _gen_suspect_attrdict(self, suspect: Suspect, setall: bool = False) -> tp.Dict[str, str]:
        attrdict = {}
        cinfo = suspect.get_client_info()
        if cinfo:
            (helo, ip, reversedns) = cinfo
        else:
            helo = ip = reversedns = None

        if setall or helo:
            attrdict['heloname'] = helo
        if setall or ip:
            attrdict['addr'] = ip

        ptr = AccessRestrictions.get_ptr(ip) if ip else None
        if setall or ptr:
            attrdict['ptr'] = ptr

        if setall or reversedns:
            attrdict['fcrdns'] = reversedns
        attrdict["from_address"] = suspect.from_address
        attrdict["from_domain"] = suspect.from_domain
        attrdict["to_address"] = suspect.to_address
        attrdict["to_domain"] = suspect.to_domain
        return attrdict

    def _examine_general(self, sess: tp.Union[sm.MilterSession, asm.MilterSession, Suspect], state: str,
                         inputstring: tp.Optional[str] = None)\
            -> tp.Union[bytes, int, tp.Tuple[tp.Union[bytes, int], str]]:
        """
        - delay_rejects is enabled
          - this is not the state to reject        [[state < reject_state]]
             - reject already set, skip tests SKIP_TESTS
             - no reject set yet, run plugin(mode:SET_REJECT_TAG)
          - this is the reject state               [[state == reject_state]]
             - reject tag already set, return REJECT_FROM_TAG
             - no reject set yet, run plugin(mode:REJECT_DIRECTLY)
          - this is after the reject state         [[state == reject_state]]
             - run plugin(mode:REJECT_DIRECTLY)
        - delay_rejects is disabled, run plugin(mode:REJECT_DIRECTLY)
        """
        if not HAVE_YAML:
            return sm.CONTINUE

        position = self.delay_rejects_statedict.get(state, AccessRestrictions.DELAY_REJ_AFTER)
        previous_reject_tag = sess.tags.get(self.DELAY_REJ_TAG)

        if previous_reject_tag:
            if position == AccessRestrictions.DELAY_REJ_BEFORE:
                self.logger.debug(f"{sess.id} state:{state} -> reject flag is set, skip tests for a later reject")
                return sm.CONTINUE
            else:
                # it's time to reject
                return previous_reject_tag

        # let's see if there are any rules
        rules = self.setupdict.get(state, [])
        rules: tp.List[tp.Dict]
        if rules:
            if inputstring:
                attrdict = {}
            elif isinstance(sess, Suspect):
                attrdict = self._gen_suspect_attrdict(suspect=sess)
            else:
                attrdict = sess.get_templ_dict()

            for rule in rules:
                rname: str = rule['name']
                rinput: str = rule['input']
                transformations: tp.Optional[MultipleFunctionsWrapper] = rule.get('transformations')

                if inputstring:
                    checkstrings = inputstring
                elif isinstance(sess, Suspect) and rinput.startswith("header"):
                    # create array with headers
                    checkstrings = []
                    for k, v in sess.get_message_rep().items():
                        checkstrings.append(f"{k}: {str(v)}")
                    self.logger.debug(f"{sess.id} Created {len(checkstrings)} headers to check")
                else:
                    checkstrings = attrdict.get(rinput)

                if checkstrings and not isinstance(checkstrings, list):
                    checkstrings = [checkstrings]

                if BE_VERBOSE:
                    self.logger.debug(f"{sess.id} Test:{rinput} for Restriction({rname}) ->teststring={checkstrings}")

                if checkstrings:
                    for checkstring in checkstrings:
                        # apply transformations here
                        if transformations:
                            checkstring = transformations(checkstring, map=attrdict, suspect=sess)
                            # using transformations we might end up with None as a result
                            # don't run checks if checkstring is not defined
                            if checkstring is None:
                                continue

                        checkstringhit = checkstring
                        restrictionset: RestrictionSet = self.restrictions_sets[rname]
                        res = restrictionset.examine(inputstring=checkstring)
                        if isinstance(res, tuple):
                            if len(res) == 3:
                                res, msg, checkstringhit = res
                            else:
                                res, msg = res
                        else:
                            msg = None
                        self.logger.debug(f"{sess.id} Test:{rinput} with input:{checkstring} for Restriction({rname}): {res}")
                        try:
                            sess.tags[RESTRICTIONS_TAG][rname] = res
                        except KeyError as e:
                            sess.tags[RESTRICTIONS_TAG] = dict(rname=res)

                        # --- #
                        # hit #
                        # --- #
                        if res:
                            # make sure to have milter returncode for decision
                            resmilter, resint = asm.MilterSession.milter_return_code(res)
                            if resmilter != sm.CONTINUE:
                                if msg:
                                    template = _SuspectTemplate(msg)
                                    attrdict["input"] = checkstringhit
                                    # update attribute dict by tags which might have been set during
                                    # evaluation of restrictions
                                    if isinstance(sess, (sm.MilterSession, asm.MilterSession)):
                                        attrdict2 = sess.get_templ_dict()
                                        attrdict.update(attrdict2)

                                    # replace double quotes by single quotes since
                                    # we need double quotes for logstash parsing
                                    attrmap = {}
                                    for k, v in attrdict.items():
                                        attrmap[k] = v.replace('"', "'") if isinstance(v, str) else v
                                    msg = template.safe_substitute(attrmap)
                                    # clean message and remove newlines (might be in header parsing output):
                                    msg = msg.replace('\r\n', '\n').replace('\n', '')

                                # all except continue should set a tag
                                sess.tags[self.DELAY_REJ_TAG] = (res, msg)

                                if position == AccessRestrictions.DELAY_REJ_BEFORE \
                                        and resmilter in [lm.REJECT, lm.TEMPFAIL]:
                                    # if it's a reject then continue so it could be welcomlisted
                                    return sm.CONTINUE
                                else:
                                    return res, msg

        return sm.CONTINUE

    def examine_connect(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], host: bytes, addr: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._examine_general(sess=sess, state=asm.CONNECT)

    def examine_helo(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], helo: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._examine_general(sess=sess, state=asm.HELO)

    def examine_mailfrom(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], sender: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._examine_general(sess=sess, state=asm.MAILFROM)

    def examine_rcpt(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._examine_general(sess=sess, state=asm.RCPT)

    def examine_header(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], key: bytes, value: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._examine_general(sess=sess, state=asm.HEADER,
                                     inputstring=f"{force_uString(key, convert_none=True)}: {force_uString(value, convert_none=True)}")

    def examine_eoh(self, sess: tp.Union[sm.MilterSession, asm.MilterSession]) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        # extra package input so it is passed as one thing
        return self._examine_general(sess=sess, state=asm.EOH, inputstring=(sess.original_headers, ))

    def examine(self, suspect: Suspect):
        if not HAVE_YAML:
            return DUNNO
        msg = suspect.get_message_rep()
        # if there is a trigger header defined, check if it is set and run checks only if present
        #
        # this can be used to combine a fuglu-milter which rejects
        # with a post-queue fuglu running later to skip some rejects
        # and apply them later, for example to quarantine a message

        headername = self.config.get(self.section, 'eom_trigger_header')
        if not headername or headername in msg:
            self.logger.info(f"{suspect.id} {headername if headername else '<undefined>'} header "
                             f"found ({headername and headername in msg}) "
                             f"or undefined ({not headername}) -> checking")
            _ = self._examine_general(sess=suspect, state=EOM)
            restag = suspect.tags.get(self.DELAY_REJ_TAG)
            if restag:
                res, msg = restag
                resstring = asm.RETCODE2STR.get(res, f'unknown(orig:{res})')
                self.logger.info(f"{suspect.id} -> restrictions say: ({resstring}, {msg})")

                self.logger.warning(f"{suspect.id} Block because milter AccessRestrictions would reject with:{msg}")
                blockinfo = {'AccessRestrictions': msg}
                self._blockreport(suspect, blockinfo, enginename='AccessRestrictions')
                suspect.tags['AccessRestrictions.errormessage'] = msg  # deprecated
        return DUNNO

    def lint(self, state=EOM) -> bool:
        from fuglu.funkyconsole import FunkyConsole

        if state and state not in self.state and state != EOM:
            # not active in current state
            return True

        fc = FunkyConsole()
        if not HAVE_YAML:
            print(fc.strcolor("ERROR", "red"), 'yaml module not found, this plugin will not do anything')
            return False

        check_config = super().lint()
        if not check_config:
            print(fc.strcolor("ERROR - config check", "red"))
            return False

        # try to create regex rules dict, raise exception on error
        try:
            _ = self._set_delay_reject(ignoreerrors=False)
            _ = self._create_dicts(ignoreerrors=False)
        except Exception as e:
            print(fc.strcolor("ERROR", "red"), str(e))
            return False

        return True


class AccessRestrictionsNWL(AccessRestrictions):
    """
    None welcomelistable version of AccessRestrictions

    This is useful if a plugin skipper is used which can skip AccessRestrictions based
    on some rules while there should still be AccessRestrctions that can not be skipped
    """
    DELAY_REJ_TAG = 'AccessRestrictionsNWL.delayedreject'
    pass
