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
import traceback
from fuglu.shared import Suspect, ScannerPlugin, DELETE, DUNNO, REJECT, string_to_actioncode, \
    FileList, get_outgoing_helo, actioncode_to_string, get_default_cache, _SuspectTemplate, \
    SuspectFilter, apply_template
from fuglu.bounce import Bounce
from fuglu.stringencode import force_uString, force_bString
from fuglu.extensions.sql import SQL_EXTENSION_ENABLED, DBFile, DBConfig, RESTAPIError
from fuglu.extensions.aioredisext import AIORedisMixin, ENABLED as REDIS_ENABLED
from fuglu.extensions.filearchives import Archivehandle
from fuglu.extensions.filetype import filetype_handler
from fuglu.mailattach import NoExtractInfo, Mailattachment
import re
import os
import os.path
import logging
import email
import hashlib
import json
from threading import Lock
try:
    from domainmagic.rbl import RBLLookup
    DOMAINMAGIC_AVAILABLE = True
except ImportError:
    DOMAINMAGIC_AVAILABLE = False
try:
    import six
    import sys
    if sys.version_info >= (3, 12, 0): # https://github.com/dpkp/kafka-python/issues/2401#issuecomment-1760208950
        sys.modules['kafka.vendor.six.moves'] = six.moves
    import kafka
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False


FUATT_NAMESCONFENDING = "-filenames.conf"
FUATT_CTYPESCONFENDING = "-filetypes.conf"
FUATT_ARCHIVENAMESCONFENDING = "-archivenames.conf"
FUATT_ARCHIVENAMES_CRYPTO_CONFENDING = "-archivenames-crypto.conf"
FUATT_ARCHIVECTYPESCONFENDING = "-archivefiletypes.conf"

FUATT_DEFAULT = 'default'

FUATT_ACTION_ALLOW = 'allow'
FUATT_ACTION_DENY = 'deny'
FUATT_ACTION_DELETE = 'delete'

FUATT_CHECKTYPE_FN = 'filename'
FUATT_CHECKTYPE_CT = 'contenttype'

FUATT_CHECKTYPE_ARCHIVE_CRYPTO_FN = 'archive-crypto-filename'
FUATT_CHECKTYPE_ARCHIVE_FN = 'archive-filename'
FUATT_CHECKTYPE_ARCHIVE_CT = 'archive-contenttype'

ATTACHMENT_DUNNO = 0
ATTACHMENT_BLOCK = 1
ATTACHMENT_OK = 2
ATTACHMENT_SILENTDELETE = 3

KEY_NAME = "name"
KEY_CTYPE = "ctype"
KEY_ARCHIVENAME = "archive-name"
KEY_ARCHIVECTYPE = "archive-ctype"
KEY_ENCARCHIVENAME = "enc-archive-name"  # name rules for files in password-protected archives


class RulesCache(object):

    """caches rule files"""

    __shared_state = {}

    def __init__(self, rulesdir, nocache: bool = False):
        """Nocache option can be useful for testing"""
        self.__dict__ = self.__shared_state
        if not hasattr(self, 'rules'):
            self.rules = {}
        if not hasattr(self, 'lock'):
            self.lock = Lock()
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(f'fuglu.plugin.attachment.{self.__class__.__name__}')
        if not hasattr(self, 'lastreload'):
            self.lastreload = 0
        self.rulesdir = rulesdir
        self._nocache = nocache
        self.reloadifnecessary()

    def getRules(self, ruletype, key):
        self.logger.debug('Rule cache request: [%s] [%s]' % (ruletype, key))
        if ruletype not in self.rules:
            self.logger.error('Invalid rule type requested: %s' % ruletype)
            return None
        if key not in self.rules[ruletype]:
            self.logger.debug('Ruleset not found : [%s] [%s]' % (ruletype, key))
            return None
        self.logger.debug('Ruleset found : [%s] [%s] ' % (ruletype, key))

        ret = self.rules[ruletype][key]
        return ret

    def getCTYPERules(self, key):
        return self.getRules(KEY_CTYPE, key)

    def getARCHIVECTYPERules(self, key):
        return self.getRules(KEY_ARCHIVECTYPE, key)

    def getNAMERules(self, key):
        return self.getRules(KEY_NAME, key)

    def getARCHIVENAMERules(self, key):
        return self.getRules(KEY_ARCHIVENAME, key)

    def getEcryptedARCHIVENAMERules(self, key):
        return self.getRules(KEY_ENCARCHIVENAME, key)

    def reloadifnecessary(self):
        """reload rules if file changed"""
        if not self.rulesdirchanged():
            return
        if not self.lock.acquire():
            return
        try:
            self._loadrules()
        finally:
            self.lock.release()

    def rulesdirchanged(self):
        dirchanged = False
        # if _nocache is True never cache (debugging only)
        if self._nocache:
            return True
        try:
            statinfo = os.stat(self.rulesdir)
        except FileNotFoundError:
            pass
        else:
            ctime = statinfo.st_ctime
            if ctime > self.lastreload:
                dirchanged = True
        return dirchanged

    def _loadrules(self):
        """effectively loads the rules, do not call directly, only through reloadifnecessary"""
        self.logger.debug('Reloading attachment rules...')

        # set last timestamp
        statinfo = os.stat(self.rulesdir)
        ctime = statinfo.st_ctime
        self.lastreload = ctime

        filelist = os.listdir(self.rulesdir)

        newruleset = {KEY_NAME: {}, KEY_CTYPE: {},
                      KEY_ARCHIVENAME: {}, KEY_ARCHIVECTYPE: {},
                      KEY_ENCARCHIVENAME: {}}

        rulecounter = 0
        okfilecounter = 0
        ignoredfilecounter = 0

        for filename in filelist:
            endingok = False
            for ending in FUATT_NAMESCONFENDING, FUATT_CTYPESCONFENDING, FUATT_ARCHIVENAMESCONFENDING, FUATT_ARCHIVECTYPESCONFENDING, FUATT_ARCHIVENAMES_CRYPTO_CONFENDING:
                if filename.endswith(ending):
                    endingok = True
                    break

            if endingok:
                okfilecounter += 1
            else:
                ignoredfilecounter += 1
                self.logger.debug('Ignoring file %s' % filename)
                continue

            ruleset = self._loadonefile("%s/%s" % (self.rulesdir, filename))
            if ruleset is None:
                continue
            rulesloaded = len(ruleset)
            self.logger.debug('%s rules loaded from file %s' %
                              (rulesloaded, filename))
            ruletype = KEY_NAME
            key = filename[0:-len(FUATT_NAMESCONFENDING)]
            if filename.endswith(FUATT_CTYPESCONFENDING):
                ruletype = KEY_CTYPE
                key = filename[0:-len(FUATT_CTYPESCONFENDING)]
            elif filename.endswith(FUATT_ARCHIVENAMESCONFENDING):
                ruletype = KEY_ARCHIVENAME
                key = filename[0:-len(FUATT_ARCHIVENAMESCONFENDING)]
            elif filename.endswith(FUATT_ARCHIVENAMES_CRYPTO_CONFENDING):
                ruletype = KEY_ENCARCHIVENAME
                key = filename[0:-len(FUATT_ARCHIVENAMES_CRYPTO_CONFENDING)]
            elif filename.endswith(FUATT_ARCHIVECTYPESCONFENDING):
                ruletype = KEY_ARCHIVECTYPE
                key = filename[0:-len(FUATT_ARCHIVECTYPESCONFENDING)]

            newruleset[ruletype][key] = ruleset
            self.logger.debug('Updating cache: [%s][%s]' % (ruletype, key))
            rulecounter += rulesloaded

        self.rules = newruleset
        self.logger.info('Loaded %s rules from %s files in %s (%s files ignored)' %
                         (rulecounter, okfilecounter,  self.rulesdir, ignoredfilecounter))

    def _loadonefile(self, filename):
        """returns all rules in a file"""
        if not os.path.exists(filename):
            self.logger.error('Rules File %s does not exist' % filename)
            return None
        if not os.path.isfile(filename):
            self.logger.warning('Ignoring file %s - not a file' % filename)
            return None
        with open(filename) as handle:
            rules = self.get_rules_from_config_lines(handle.readlines())
        return rules

    def get_rules_from_config_lines(self, lineslist):
        ret = []
        for line in lineslist:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            tpl = line.split(None, 2)
            if len(tpl) != 3:
                self.logger.debug('Ignoring invalid line  (length %s): %s' % (len(tpl), line))
                continue
            (action, regex, description) = tpl
            action = action.lower()
            if action not in [FUATT_ACTION_ALLOW, FUATT_ACTION_DENY, FUATT_ACTION_DELETE]:
                self.logger.error('Invalid rule action: %s' % action)
                continue

            tp = (action, regex, description)
            ret.append(tp)
        return ret


class FiletypePlugin(ScannerPlugin):

    r"""This plugin checks message attachments. You can configure what filetypes or filenames are allowed to pass through fuglu. If an attachment is not allowed, the message is deleted and the sender receives a bounce error message. The plugin uses the '''file''' library to identify attachments, so even if a smart sender renames his executable to .txt, fuglu will detect it.

Attachment rules can be defined globally, per domain or per user.

Actions: This plugin will delete messages if they contain blocked attachments.

Prerequisites: You must have the python ``file`` or ``magic`` module installed. Additionaly, for scanning filenames within rar archives, fuglu needs the python ``rarfile`` module.


The attachment configuration files are in ``${confdir}/rules``. You should have two default files there: ``default-filenames.conf`` which defines what filenames are allowed and ``default-filetypes.conf`` which defines what content types an attachment may have.

For domain rules, create a new file ``<domainname>-filenames.conf`` / ``<domainname>-filetypes.conf`` , eg. ``fuglu.org-filenames.conf`` / ``fuglu.org-filetypes.conf``

For individual user rules, create a new file ``<useremail>-filenames.conf`` / ``<useremail>-filetypes.conf``, eg. ``oli@fuglu.org-filenames.conf`` / ``oli@fuglu.org-filetypes.conf``

To scan filenames or even file contents within archives (zip, rar), use ``<...>-archivefilenames.conf`` and ``<...>-archivefiletypes.conf``.


The format of those files is as follows: Each line should have three parts, seperated by tabs (or any whitespace):
``<action>``    ``<regular expression>``   ``<description or error message>``

``<action>`` can be one of:
 * allow : this file is ok, don't do further checks (you might use it for safe content types like text). Do not blindly create 'allow' rules. It's safer to make no rule at all, if no other rules hit, the file will be accepted
 * deny : delete this message and send the error message/description back to the sender
 * delete : silently delete the message, no error is sent back, and 'blockaction' is ignored


``<regular expression>`` is a standard python regex. in ``x-filenames.conf`` this will be applied to the attachment name . in ``x-filetypes.conf`` this will be applied to the mime type of the file as well as the file type returned by the ``file`` command.

Example of ``default-filetypes.conf`` :

::

    allow    text        -        
    allow    \bscript    -        
    allow    archive        -            
    allow    postscript    -            
    deny    self-extract    No self-extracting archives
    deny    executable    No programs allowed
    deny    ELF        No programs allowed
    deny    Registry    No Windows Registry files allowed



A small extract from ``default-filenames.conf``:

::

    deny    \.ico$            Windows icon file security vulnerability    
    deny    \.ani$            Windows animated cursor file security vulnerability    
    deny    \.cur$            Windows cursor file security vulnerability    
    deny    \.hlp$            Windows help file security vulnerability

    allow    \.jpg$            -    
    allow    \.gif$            -    



Note: The files will be reloaded automatically after a few seconds (you do not need to kill -HUP / restart fuglu)

Per domain/user overrides can also be fetched from a database instead of files (see dbconnectstring / query options).
The query must return the same rule format as a file would. Multiple columns in the resultset will be concatenated.

The default query assumes the following schema:

::

    CREATE TABLE `attachmentrules` (
      `rule_id` int(11) NOT NULL AUTO_INCREMENT,
      `action` varchar(10) NOT NULL,
      `regex` varchar(255) NOT NULL,
      `description` varchar(255) DEFAULT NULL,
      `scope` varchar(255) DEFAULT NULL,
      `checktype` varchar(20) NOT NULL,
      `prio` int(11) NOT NULL,
      PRIMARY KEY (`rule_id`)
    )

*action*: ``allow``, ``deny``, or ``delete``

*regex*: a regular expression

*description*: description/explanation of this rule which is optionally sent back to the sender if bounces are enabled

*scope*: a domain name or a recipient's email address

*checktype*: one of ``filename``,``contenttype``,``archive-filename``,``archive-contenttype``

*prio*: order in which the rules are run

The bounce template (eg ``${confdir}/templates/blockedfile.tmpl`` ) should
start by defining the headers, followed by a blank line, then the message body for your bounce message. Something like this:

::

    To: ${from_address}
    Subject: Blocked attachment

    Your message to ${to_address} contains a blocked attachment and has not been delivered.

    ${blockinfo}



``${blockinfo}`` will be replaced with the text you specified in the third column of the rule that blocked this message.

The other common template variables are available as well.


"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars = {
            'template_blockedfile': {
                'default': '${confdir}/templates/blockedfile.tmpl',
                'description': 'Mail template for the bounce to inform sender about blocked attachment',
            },

            'sendbounce': {
                'default': 'True',
                'description': 'inform the sender about blocked attachments.\nIf a previous plugin tagged the message as spam or infected, no bounce will be sent to prevent backscatter',
            },
            
            'nobouncerules': {
                'default': '${confdir}/archive.regex',
                'description': 'No send bounce SuspectFilter File. Only evaluated if sendbounce is set to True. Preferrably set to same config file as used by archive plugin',
            },

            'rulesdir': {
                'default': '${confdir}/rules',
                'description': 'directory that contains attachment rules',
            },

            'blockaction': {
                'default': 'DELETE',
                'description': 'what should the plugin do when a blocked attachment is detected\nREJECT : reject the message (recommended in pre-queue mode)\nDELETE : discard messages\nDUNNO  : mark as blocked but continue anyway (eg. if you have a later quarantine plugin)',
            },
            
            'block_encrypted': {
                'default': 'False',
                'description': 'block encrypted archives',
            },
            
            'rejectmessage_encrypted': {
                'default': 'Encrypted archive ${attname} not permitted',
                'description': 'Reject message when encrypted archives should be blocked',
            },
            
            'overrides_source': {
                'default': '',
                'description': """
                    override certain user config, either using dbconfig or tag:
                    e.g.
                    dbconfig (uses databaseconfig settings)
                    tag:filtersettings (get from p_blwl FilterSettings backend tag subvalues. use ${domain} and ${recipient} in tag name for specific per domain/recipient overrides)
                    """
            },

            'dbconnectstring': {
                'default': '',
                'description': 'sqlalchemy connectstring to load rules from a database and use files only as fallback. requires SQL extension to be enabled',
                'confidential': True,
            },

            'query': {
                'default': 'SELECT action,regex,description FROM attachmentrules WHERE scope=:scope AND checktype=:checktype ORDER BY prio',
                'description': "sql query to load rules from a db. #:scope will be replaced by the recipient address first, then by the recipient domain\n:check will be replaced 'filename','contenttype','archive-filename' or 'archive-contenttype'",
            },

            'config_section_filename': {
                'default': '',
                'description': 'load additional rules from filter config overrides databases (e.g. from fuglu.conf, yaml, rest api or sql backend)',
            },

            'config_section_filetype': {
                'default': '',
                'description': 'load additional rules from filter config overrides databases (e.g. from fuglu.conf, yaml, rest api or sql backend)',
            },

            'config_section_archivename': {
                'default': '',
                'description': 'load additional rules from filter config overrides databases (e.g. from fuglu.conf, yaml, rest api or sql backend)',
            },

            'config_section_archivecryptoname': {
                'default': '',
                'description': 'load additional rules from filter config overrides databases (e.g. from fuglu.conf, yaml, rest api or sql backend)',
            },

            'config_section_archivetype': {
                'default': '',
                'description': 'load additional rules from filter config overrides databases (e.g. from fuglu.conf, yaml, rest api or sql backend)',
            },
            
            'rulestag': {
                'default': '',
                'description': 'load additional rules from tag'
            },

            'checkarchivenames': {
                'default': 'False',
                'description': "enable scanning of filenames within archives (zip,rar). This does not actually extract the files, it just looks at the filenames found in the archive."
            },

            'checkarchivecontent': {
                'default': 'False',
                'description': 'extract compressed archives(zip,rar) and check file content type with libmagics\nnote that the files will be extracted into memory - tune archivecontentmaxsize  accordingly.\nfuglu does not extract archives within the archive(recursion)',
            },

            'archivecontentmaxsize': {
                'default': '5000000',
                'description': 'only extract and examine files up to this amount of (uncompressed) bytes',
            },

            'archiveextractlevel': {
                'default': '1',
                'description': 'recursive extraction level for archives. Undefined or negative value means extract until it\'s not an archive anymore'
            },
            
            'archive_passwords': {
                'default': '',
                'description': 'list of additional passwords to try extraction of archives',
            },
            
            'archive_passwords_maxbodywords': {
                'default': '0',
                'description': 'maximum number of words extracted from text content that could be used as password candidates',
            },
            
            'archive_passwords_minwordlength': {
                'default': '4',
                'description': 'minimal number of characters in a word extracted from text content to be considered as password candidate',
            },
            
            'archive_passwords_maxtextpartlength': {
                'default': '2048',
                'description': 'maximum number of characters per text content part to be parsed for password candidates',
            },

            'enabledarchivetypes': {
                'default': '',
                'description': 'comma separated list of archive extensions. do only process archives of given types. leave empty to use all available',
            },
            
            'disabledarchivetypes': {
                'default': '',
                'description': 'comma separated list of disabled archive extensions. use all available except those listed here.',
            },

            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },

            'verbose': {
                'default': 'False',
                'description': 'extra verbose output (for debugging)'
            },

            'ignore_signature': {
                'default': 'False',
                'description': 'Ignore filetype check for smime signature'
            },

        }

        self.logger = self._logger()
        self.rulescache = None
        self.regexcache = get_default_cache()
        self.enginename = 'FiletypePlugin'
        self.nobouncerules = None

        # copy dict with available extensions from Archivehandle
        # (deepcopy is not needed here although in general it is a good idea
        # to use it in case a dict contains another dict)
        #
        # key: file ending, value: archive type
        self.active_archive_extensions = dict(Archivehandle.avail_archive_extensions)
    
    
    def _init_cache(self):
        if self.rulescache is None:
            self.rulescache = RulesCache(self.config.get(self.section, 'rulesdir'))
        if self.nobouncerules is None:
            nobouncerules = self.config.get(self.section, 'nobouncerules')
            if nobouncerules:
                self.nobouncerules = SuspectFilter(nobouncerules)
        
        
    def _value_from_tags(self, suspect, keylist, key, datatypes, fallback):
        value = suspect.tags.copy()
        keylist.append(key)
        for key in keylist:
            if key.startswith('$'):
                template = _SuspectTemplate(key)
                key = template.safe_substitute({'recipient': suspect.to_address, 'domain': suspect.to_domain})
            value = value.get(key, {})
            if isinstance(value, datatypes):
                break
        else:
            value = fallback
        return value
    
    
    def examine(self, suspect):
        self._init_cache()

        try:
            enabledarchivetypes = self.config.getlist(self.section, 'enabledarchivetypes', lower=True)
            disabledarchivetypes = self.config.getlist(self.section, 'disabledarchivetypes', lower=True)
            checkarchivenames = self.config.getboolean(self.section, 'checkarchivenames')
            checkarchivecontent = self.config.getboolean(self.section, 'checkarchivecontent')
            sendbounce = self.config.getboolean(self.section, 'sendbounce')
            blockedfiletemplate = self.config.get(self.section, 'template_blockedfile')
            
            overrides_source = self.config.get(self.section, 'overrides_source')
            if overrides_source == 'dbconfig':
                runtimeconfig = DBConfig(self.config, suspect)
                checkarchivenames = runtimeconfig.getboolean(self.section, 'checkarchivenames')
                checkarchivecontent = runtimeconfig.getboolean(self.section, 'checkarchivecontent')
                sendbounce = runtimeconfig.getboolean(self.section, 'sendbounce')
                enabledarchivetypes = runtimeconfig.getlist(self.section, 'enabledarchivetypes')
                disabledarchivetypes = runtimeconfig.getlist(self.section, 'disabledarchivetypes')
                blockedfiletemplate = runtimeconfig.get(self.section, 'template_blockedfile')
            elif overrides_source.startswith('tag:'):
                keylist = overrides_source.split(':')[1:]
                enabledarchivetypes = self._value_from_tags(suspect, keylist, 'filetype_enabledarchivetypes', list, enabledarchivetypes)
                disabledarchivetypes = self._value_from_tags(suspect, keylist, 'filetype_disabledarchivetypes', list, disabledarchivetypes)
                checkarchivenames = self._value_from_tags(suspect, keylist, 'filetype_checkarchivenames', bool, checkarchivenames)
                checkarchivecontent = self._value_from_tags(suspect, keylist, 'filetype_checkarchivecontent', bool, checkarchivecontent)
                sendbounce = self._value_from_tags(suspect, keylist, 'sendbounce', bool, sendbounce)
                blockedfiletemplate = self._value_from_tags(suspect, keylist, 'filetype_blockedfiletemplate', str, blockedfiletemplate)
                
            if enabledarchivetypes:
                archtypes = list(self.active_archive_extensions.keys())
                for archtype in archtypes:
                    if archtype not in enabledarchivetypes:
                        del self.active_archive_extensions[archtype]
            if disabledarchivetypes:
                archtypes = list(self.active_archive_extensions.keys())
                for archtype in disabledarchivetypes:
                    if archtype in archtypes:
                        del self.active_archive_extensions[archtype]
            action, message = self.walk(suspect, checkarchivenames, checkarchivecontent, sendbounce, blockedfiletemplate)
        except RESTAPIError as e:
            action = self._problemcode()
            self.logger.warning(f'{suspect.id} {actioncode_to_string(action)} due to RESTAPIError: {str(e)}')
            message = 'Internal Server Error'

        return action, message

    def asciionly(self, stri):
        """return stri with all non-ascii chars removed"""
        if isinstance(stri, str):
            return stri.encode('ascii', 'ignore').decode()
        elif isinstance(stri, bytes):  # python3
            # A bytes object therefore already ascii, but not a string yet
            return stri.decode('ascii', 'ignore')
        return "".join([x for x in stri if ord(x) < 128])
    
    def _check_sendbounce(self, suspect) -> bool:
        if suspect.is_spam() or suspect.is_virus():
            self.logger.info(f"{suspect.id} backscatter prevention: not sending attachment block bounce to {suspect.from_address} - the message is tagged spam or virus")
            return False
        if not suspect.from_address:
            self.logger.warning(f"{suspect.id} not sending attachment block bounce to empty recipient")
            return False
        queueid = suspect.get_tag('Attachment.bounce.queueid')
        if queueid:
            self.logger.info(f'{suspect.id} already sent attachment block bounce to {suspect.from_address} with queueid {queueid}')
            return False
        if self.nobouncerules is not None:
            match, arg = self.nobouncerules.matches(suspect)
            self.logger.debug(f"{suspect.id} archive -> match:{bool(match)}")
            if match:
                if arg is not None and arg.lower().strip() == 'no':
                    self.logger.debug(f"{suspect.id} Suspect matches bounce exception rule - not sending attachment block bounce")
                    return False
        return True

    def match_rules(self, ruleset, obj, suspect, sendbounce, blockedfiletemplate, attachmentname):
        if attachmentname is None:
            attachmentname = ""
        attachmentname = self.asciionly(attachmentname)

        if obj is None:
            self.logger.warning(f"{suspect.id}: message has unknown name or content-type attachment {attachmentname}")
            return ATTACHMENT_DUNNO

        # remove non ascii chars
        asciirep = self.asciionly(obj)

        displayname = attachmentname
        if asciirep == attachmentname:
            displayname = ''

        if ruleset is None:
            return ATTACHMENT_DUNNO

        for action, regex, description in ruleset:
            # database description, displayname and asciirep may be unicode
            description = force_uString(description)
            displayname = force_uString(displayname)
            asciirep = force_uString(asciirep)
            obj = force_uString(obj)

            prog = self.regexcache.get_cache(f'attre-{regex}')
            if prog is None:
                prog = re.compile(regex, re.I)
                self.regexcache.put_cache(f'attre-{regex}', prog, ttl=3600)
            if self.config.getboolean(self.section, 'verbose'):
                self.logger.debug(f'{suspect.id} Attachment {obj} Rule {regex}')
            if prog.search(obj):
                self.logger.debug(f'{suspect.id} Rulematch: Attachment={obj} Rule={regex} Description={description} Action={action}')
                suspect.debug(f'Rulematch: Attachment={obj} Rule={regex} Description={description} Action={action}')
                if action == 'deny':
                    self.logger.info(f'{suspect.id} contains blocked attachment {displayname} {asciirep}')
                    blockinfo = {f'{displayname} {asciirep}': description}
                    self._blockreport(suspect, blockinfo, enginename=self.enginename)
                    blockinfo = f"{displayname} {asciirep}: {description}".strip()
                    suspect.tags[f'{self.enginename}.errormessage'] = blockinfo  # deprecated
                    if sendbounce and self._check_sendbounce(suspect):
                        self.logger.debug(f"{suspect.id} sending attachment block bounce to {suspect.from_address}")
                        bounce = Bounce(self.config)
                        queueid = bounce.send_template_file(suspect.from_address,
                                                            blockedfiletemplate,
                                                            suspect,
                                                            dict(blockinfo=blockinfo))
                        self.logger.info(f'{suspect.id} sent attachment block bounce to {suspect.from_address} with queueid {queueid}')
                        suspect.set_tag('Attachment.bounce.queueid', queueid)
                    return ATTACHMENT_BLOCK

                if action == 'delete':
                    self.logger.info(f'{suspect.id} contains blocked attachment {displayname} {asciirep} -- SILENT DELETE! --')
                    return ATTACHMENT_SILENTDELETE

                if action == 'allow':
                    return ATTACHMENT_OK
        return ATTACHMENT_DUNNO

    def match_multiple_sets(self, setlist, obj, suspect, sendbounce, blockedfiletemplate, attachmentname=None):
        """run through multiple sets and return the first action which matches obj"""
        self.logger.debug(f'{suspect.id} Checking object {obj} against attachment rulesets')
        for ruleset in setlist:
            res = self.match_rules(ruleset, obj, suspect, sendbounce, blockedfiletemplate, attachmentname)
            if res != ATTACHMENT_DUNNO:
                return res
        return ATTACHMENT_DUNNO

    def _load_rules(self, suspect):
        user_names = []
        user_ctypes = []
        user_archive_names = []
        user_archive_crypto_names = []
        user_archive_ctypes = []
        domain_names = []
        domain_ctypes = []
        domain_archive_names = []
        domain_archive_crypto_names = []
        domain_archive_ctypes = []

        for func in [self._load_rules_db, self._load_rules_conf, self._load_rules_file, self._load_rules_tags]:
            data = func(suspect)
            if data is None:
                continue

            f_user_names, f_user_ctypes, f_user_archive_names, f_user_archive_crypto_names, f_user_archive_ctypes, \
                f_domain_names, f_domain_ctypes, f_domain_archive_names, f_domain_archive_crypto_names, f_domain_archive_ctypes \
                = data
            if f_user_names is not None:
                user_names.extend(f_user_names)
            if f_user_ctypes is not None:
                user_ctypes.extend(f_user_ctypes)
            if f_user_archive_names is not None:
                user_archive_names.extend(f_user_archive_names)
            if f_user_archive_crypto_names is not None:
                user_archive_crypto_names.extend(f_user_archive_crypto_names)
            if f_user_archive_ctypes is not None:
                user_archive_ctypes.extend(f_user_archive_ctypes)
            if f_domain_names is not None:
                domain_names.extend(f_domain_names)
            if f_domain_ctypes is not None:
                domain_ctypes.extend(f_domain_ctypes)
            if f_domain_archive_names is not None:
                domain_archive_names.extend(f_domain_archive_names)
            if f_domain_archive_crypto_names is not None:
                domain_archive_crypto_names.extend(f_domain_archive_crypto_names)
            if f_domain_archive_ctypes is not None:
                domain_archive_ctypes.extend(f_domain_archive_ctypes)

        return user_names, user_ctypes, user_archive_names, user_archive_crypto_names, user_archive_ctypes, \
            domain_names, domain_ctypes, domain_archive_names, domain_archive_crypto_names, domain_archive_ctypes
    
    def _load_rules_tags(self, suspect):
        rulestag = self.config.get(self.section, 'rulestag')
        keylist = rulestag.split(':')[1:]
        user_names = []
        user_ctypes = []
        user_archive_names = []
        user_archive_crypto_names = []
        user_archive_ctypes = []
        domain_names = []
        domain_ctypes = []
        domain_archive_names = []
        domain_archive_crypto_names = []
        domain_archive_ctypes = []
        sections = {
            'attrules_filename': user_names,
            'attrules_filetype': user_ctypes,
            'attrules_archivename': user_archive_names,
            'attrules_archivecryptoname': user_archive_crypto_names,
            'attrules_archivetype': user_archive_ctypes,
        }
        
        for section in sections:
            values = self._value_from_tags(suspect, keylist, section, str, '')
            for value in values.split('\n'):
                if value:
                    try:
                        action, regex, description = value.split(None,2)
                        tp = (action, regex, description)
                        sections[section].append(tp)
                    except ValueError:
                        self.logger.warning(f'{suspect.id} ignoring invalid rule definition from tag {":".join(keylist)} {section}: {value}')

        return user_names, user_ctypes, user_archive_names, user_archive_crypto_names, user_archive_ctypes, \
            domain_names, domain_ctypes, domain_archive_names, domain_archive_crypto_names, domain_archive_ctypes
    
    def _load_rules_file(self, suspect):
        rulesdir = self.config.get(self.section, 'rulesdir')
        self.logger.debug(f'{suspect.id} Loading attachment rules from filesystem dir {rulesdir}')
        user_names = self.rulescache.getNAMERules(suspect.to_address)
        user_ctypes = self.rulescache.getCTYPERules(suspect.to_address)
        user_archive_names = self.rulescache.getARCHIVENAMERules(suspect.to_address)
        user_archive_crypto_names = self.rulescache.getEcryptedARCHIVENAMERules(suspect.to_address)
        user_archive_ctypes = self.rulescache.getARCHIVECTYPERules(suspect.to_address)

        domain_names = self.rulescache.getNAMERules(suspect.to_domain)
        domain_ctypes = self.rulescache.getCTYPERules(suspect.to_domain)
        domain_archive_names = self.rulescache.getARCHIVENAMERules(suspect.to_domain)
        domain_archive_crypto_names = self.rulescache.getEcryptedARCHIVENAMERules(suspect.to_domain)
        domain_archive_ctypes = self.rulescache.getARCHIVECTYPERules(suspect.to_domain)

        return user_names, user_ctypes, user_archive_names, user_archive_crypto_names, user_archive_ctypes, \
            domain_names, domain_ctypes, domain_archive_names, domain_archive_crypto_names, domain_archive_ctypes

    def _load_rules_db(self, suspect):
        dbconn = ''
        if self.config.has_option(self.section, 'dbconnectstring'):
            dbconn = self.config.get(self.section, 'dbconnectstring')

        if dbconn.strip() == '':
            return None

        self.logger.debug(f'{suspect.id} Loading attachment rules from database')
        query = self.config.get(self.section, 'query')
        dbfile = DBFile(dbconn, query)
        user_names = self.rulescache.get_rules_from_config_lines(
            dbfile.getContent({'scope': suspect.to_address, 'checktype': FUATT_CHECKTYPE_FN}))
        user_ctypes = self.rulescache.get_rules_from_config_lines(
            dbfile.getContent({'scope': suspect.to_address, 'checktype': FUATT_CHECKTYPE_CT}))
        user_archive_names = self.rulescache.get_rules_from_config_lines(
            dbfile.getContent({'scope': suspect.to_address, 'checktype': FUATT_CHECKTYPE_ARCHIVE_FN}))
        user_archive_crypto_names = self.rulescache.get_rules_from_config_lines(
            dbfile.getContent({'scope': suspect.to_address, 'checktype': FUATT_CHECKTYPE_ARCHIVE_CRYPTO_FN}))
        user_archive_ctypes = self.rulescache.get_rules_from_config_lines(
            dbfile.getContent({'scope': suspect.to_address, 'checktype': FUATT_CHECKTYPE_ARCHIVE_CT}))
        self.logger.debug(f'{suspect.id} Found {len(user_names)} filename rules, {len(user_ctypes)} content-type rules, {len(user_archive_names)} archive filename rules, {len(user_archive_crypto_names)} archive crypto rules, {len(user_archive_ctypes)} archive content rules for address {suspect.to_address}')

        domain_names = self.rulescache.get_rules_from_config_lines(
            dbfile.getContent({'scope': suspect.to_domain, 'checktype': FUATT_CHECKTYPE_FN}))
        domain_ctypes = self.rulescache.get_rules_from_config_lines(
            dbfile.getContent({'scope': suspect.to_domain, 'checktype': FUATT_CHECKTYPE_CT}))
        domain_archive_names = self.rulescache.get_rules_from_config_lines(
            dbfile.getContent({'scope': suspect.to_domain, 'checktype': FUATT_CHECKTYPE_ARCHIVE_FN}))
        domain_archive_crypto_names = self.rulescache.get_rules_from_config_lines(
            dbfile.getContent({'scope': suspect.to_domain, 'checktype': FUATT_CHECKTYPE_ARCHIVE_CRYPTO_FN}))
        domain_archive_ctypes = self.rulescache.get_rules_from_config_lines(
            dbfile.getContent({'scope': suspect.to_domain, 'checktype': FUATT_CHECKTYPE_ARCHIVE_CT}))
        self.logger.debug(f'{suspect.id} Found {len(domain_names)} filename rules, {len(domain_ctypes)} content-type rules, {len(domain_archive_names)} archive filename rules, {len(domain_archive_crypto_names)} archive crypto rules, {len(domain_archive_ctypes)} archive content rules for domain {suspect.to_domain}')

        return user_names, user_ctypes, user_archive_names, user_archive_crypto_names, user_archive_ctypes, \
            domain_names, domain_ctypes, domain_archive_names, domain_archive_crypto_names, domain_archive_ctypes

    def _load_rules_conf(self, suspect):
        user_names = []
        user_ctypes = []
        user_archive_names = []
        user_archive_crypto_names = []
        user_archive_ctypes = []
        domain_names = []
        domain_ctypes = []
        domain_archive_names = []
        domain_archive_crypto_names = []
        domain_archive_ctypes = []
        sections = {
            'config_section_filename': user_names,
            'config_section_filetype': user_ctypes,
            'config_section_archivename': user_archive_names,
            'config_section_archivecryptoname': user_archive_crypto_names,
            'config_section_archivetype': user_archive_ctypes,
        }
        
        overrides_source = self.config.get(self.section, 'overrides_source')
        if overrides_source == 'dbconfig':
            runtimeconfig = DBConfig(self.config, suspect)
            for section in sections:
                runtimeconfig.load_section(section)
                options = runtimeconfig.get_cached_options(section)
                for regex in options:
                    value = runtimeconfig.get(section, regex)
                    action, description = value.split(None, 1)
                    tp = (action, regex, description)
                    sections[section].append(tp)

        return user_names, user_ctypes, user_archive_names, user_archive_crypto_names, user_archive_ctypes, \
            domain_names, domain_ctypes, domain_archive_names, domain_archive_crypto_names, domain_archive_ctypes
    
    
    def _get_body_words(self, suspect: Suspect):
        maxwordcount = self.config.getint(self.section, 'archive_passwords_maxbodywords')
        words = set()
        if maxwordcount > 0:
            minwordlength = self.config.getint(self.section, 'archive_passwords_minwordlength')
            maxtextpartlength = self.config.getint(self.section, 'archive_passwords_maxtextpartlength')
            
            textparts = [force_uString(suspect.get_header('subject', ''))]
            sf = SuspectFilter()
            textparts.extend(sf.get_decoded_textparts(suspect, attachment=False))
            for textpart in textparts:
                words.update({w for w in textpart[:maxtextpartlength].split() if len(w)>=minwordlength})
        return list(words)[:maxwordcount]
        
    
    def _get_archive_passwords(self, suspect: Suspect):
        pwd = ['123456', '1234', 'asdf', 'abcd', 'password', ]
        archive_passwords = self.config.getlist(self.section, 'archive_passwords')
        pwd.extend(archive_passwords)
        pwd.extend(suspect.get_tag('archive_passwords', []))
        pwd.extend(self._get_body_words(suspect))
        return pwd

    def walk(self, suspect, checkarchivenames, checkarchivecontent, sendbounce, blockedfiletemplate):
        """walks through a message and checks each attachment according to the rulefile specified in the config"""

        blockaction = self.config.get(self.section, 'blockaction')
        blockactioncode = string_to_actioncode(blockaction)

        user_names, user_ctypes, user_archive_names, user_archive_crypto_names, user_archive_ctypes, \
            domain_names, domain_ctypes, domain_archive_names, domain_archive_crypto_names, domain_archive_ctypes \
            = self._load_rules(suspect)

        # always get defaults from file
        default_names = self.rulescache.getNAMERules(FUATT_DEFAULT)
        default_ctypes = self.rulescache.getCTYPERules(FUATT_DEFAULT)
        default_archive_names = self.rulescache.getARCHIVENAMERules(FUATT_DEFAULT)
        default_archive_crypto_names = self.rulescache.getEcryptedARCHIVENAMERules(FUATT_DEFAULT)
        default_archive_ctypes = self.rulescache.getARCHIVECTYPERules(FUATT_DEFAULT)

        # get mail attachment objects (only directly attached objects)
        for attObj in suspect.att_mgr.get_objectlist():
            contenttype_mime = attObj.contenttype_mime
            att_name = attObj.filename

            if attObj.is_inline or attObj.is_attachment or not attObj.filename_generated:
                # process all attachments marked as "inline", "attachment" or parts
                # with filenames that are not auto-generated
                pass
            else:
                self.logger.debug(f'{suspect.id} Skip message object: {att_name} (attachment: {attObj.is_attachment}, inline: {attObj.is_inline}, auto-name: {attObj.filename_generated}')
                continue

            att_name = self.asciionly(att_name)

            res = self.match_multiple_sets([user_names, domain_names, default_names], att_name, suspect, sendbounce, blockedfiletemplate, att_name)
            if res == ATTACHMENT_SILENTDELETE:
                self._debuginfo(suspect, f"Attachment name={att_name} SILENT DELETE : blocked by name")
                return DELETE, None
            if res == ATTACHMENT_BLOCK:
                self._debuginfo(suspect, f"Attachment name={att_name} : blocked by name)")
                message = suspect.tags[f'{self.enginename}.errormessage']
                return blockactioncode, message

            # go through content type rules
            res = self.match_multiple_sets([user_ctypes, domain_ctypes, default_ctypes], contenttype_mime, suspect, sendbounce, blockedfiletemplate, att_name)
            if res == ATTACHMENT_SILENTDELETE:
                self._debuginfo(
                    suspect, f"Attachment name={att_name} content-type={contenttype_mime} SILENT DELETE: blocked by mime content type (message source)")
                return DELETE, None
            if res == ATTACHMENT_BLOCK:
                self._debuginfo(suspect, f"Attachment name={att_name} content-type={contenttype_mime} : blocked by mime content type (message source)")
                message = suspect.tags[f'{self.enginename}.errormessage']
                return blockactioncode, message

            contenttype_magic = attObj.contenttype
            if contenttype_magic is not None:
                ignore = False
                if self.config.getboolean(self.section, 'ignore_signature'):
                    # check if mail is signed
                    msg = suspect.get_message_rep() if suspect.has_message_rep() else suspect.build_headeronly_message_rep()
                    if msg.is_multipart() and msg.get_content_subtype() == "signed" and (
                            att_name == "smime.p7s" or contenttype_mime == 'application/pkcs7-signature'):
                        self.logger.info(f"{suspect.id} Ignoring contenttype tests for "
                                         f"name={att_name} due to content-type={contenttype_magic} "
                                         f"because this has been detected as a signature "
                                         f"and ignore_signature is True.")
                        ignore = True
                if ignore:
                    res = ATTACHMENT_DUNNO
                else:
                    res = self.match_multiple_sets([user_ctypes, domain_ctypes, default_ctypes], contenttype_magic,
                                                   suspect, sendbounce, blockedfiletemplate, att_name)
                if res == ATTACHMENT_SILENTDELETE:
                    self._debuginfo(suspect, f"Attachment name={att_name} content-type={contenttype_magic} SILENT DELETE: blocked by mime content type (magic)")
                    return DELETE, None
                if res == ATTACHMENT_BLOCK:
                    self._debuginfo(suspect, f"Attachment name={att_name} content-type={contenttype_magic} : blocked by mime content type (magic)")
                    message = suspect.tags[f'{self.enginename}.errormessage']
                    return blockactioncode, message

            # archives
            if checkarchivenames or checkarchivecontent:

                # if archive_type is not None:
                if attObj.is_archive:
                    attObj.archive_passwords = self._get_archive_passwords(suspect)
                    # check if extension was used to determine archive type and
                    # if yes, check if extension is enabled. This code
                    # is here to remain backward compatible in the behavior. It
                    # is recommended to define inactive archive-types and -extensions
                    # differently
                    if attObj.atype_fromext() is not None:
                        if not attObj.atype_fromext() in self.active_archive_extensions.keys():
                            # skip if extension is not in active list
                            continue

                    self.logger.debug(f'{suspect.id} Extracting {att_name} as {attObj.archive_type}')
                    archivecontentmaxsize = self.config.getint(self.section, 'archivecontentmaxsize')
                    try:
                        archiveextractlevel = self.config.getint(self.section, 'archiveextractlevel')
                        if archiveextractlevel < 0:  # value must be greater or equals 0
                            archiveextractlevel = None
                    except Exception:
                        archiveextractlevel = None

                    try:
                        if checkarchivenames:
                            # here, check all the filenames, independent of how many files we would extract
                            # by the limits (att_mgr_default_maxnfiles, att_mgr_hard_maxnfiles)
                            if checkarchivecontent:
                                namelist = attObj.get_fileslist(0, archiveextractlevel, archivecontentmaxsize, None)
                            else:
                                namelist = attObj.fileslist_archive
                            self.logger.debug(f'{suspect.id} archive {attObj.filename} namelist {namelist}')
                            passwordprotected = attObj.is_protected_archive
                            ruleset = [user_archive_names, domain_archive_names, default_archive_names]
                            if passwordprotected:
                                ruleset.extend([user_archive_crypto_names, domain_archive_crypto_names, default_archive_crypto_names])
                                matching_password = attObj.get_archive_password
                                self.logger.debug(f"{suspect.id} Is {att_name} password protected: {passwordprotected} with password: {matching_password}")
                                archive_passwords = suspect.get_tag('archive_password', [])
                                archive_passwords.append(matching_password)
                                suspect.set_tag('archive_password', archive_passwords)
                                if suspect.get_tag('filetype_blockarchiveencrypted') is True or self.config.getboolean(self.section, 'block_encrypted'):
                                    blockinfo = {f'{att_name}': 'encrypted'}
                                    self._blockreport(suspect, blockinfo, enginename=self.enginename)
                                    self._debuginfo(suspect, f"password protected archive {att_name}", logging.WARNING)
                                    template = _SuspectTemplate(self.config.get(self.section, 'rejectmessage_encrypted'))
                                    msg = template.safe_substitute({'attname': att_name, 'recipient': suspect.to_address, 'domain': suspect.to_domain})
                                    return blockaction, msg
                            else:
                                self.logger.debug(f"{suspect.id} Is {att_name} password protected: {passwordprotected}")
                                

                            for name in namelist:
                                res = self.match_multiple_sets(ruleset, name, suspect, sendbounce, blockedfiletemplate, name)
                                if res == ATTACHMENT_SILENTDELETE:
                                    self._debuginfo(suspect, f"Blocked filename in archive {att_name} SILENT DELETE")
                                    return DELETE, None
                                if res == ATTACHMENT_BLOCK:
                                    self._debuginfo(suspect, f'Blocked filename in archive {att_name}', logging.WARNING)
                                    message = suspect.tags[f'{self.enginename}.errormessage']
                                    return blockactioncode, message

                        if filetype_handler.available() and checkarchivecontent:
                            maxnfiles2extract = suspect.att_mgr.get_maxfilenum_extract(None)
                            nocheckinfo = NoExtractInfo()
                            for archObj in attObj.get_objectlist(0, archiveextractlevel, archivecontentmaxsize, maxnfiles2extract, noextractinfo=nocheckinfo):
                                safename = self.asciionly(archObj.filename)
                                contenttype_magic = archObj.contenttype

                                # Keeping this check for backward compatibility
                                # This could easily be removed since memory is used anyway
                                #if archivecontentmaxsize is not None and archObj.filesize > archivecontentmaxsize:
                                #    nocheckinfo.append(archObj.filename, "toolarge",
                                #                       "already extracted but too large for check: %u > %u"
                                #                       % (archObj.filesize, archivecontentmaxsize))
                                #    continue

                                res = self.match_multiple_sets(
                                    [user_archive_ctypes, domain_archive_ctypes, default_archive_ctypes],
                                    contenttype_magic, suspect, sendbounce, blockedfiletemplate, safename)
                                if res == ATTACHMENT_SILENTDELETE:
                                    self._debuginfo(
                                        suspect, f"Extracted file {safename} from archive {att_name} content-type={contenttype_magic} SILENT DELETE: blocked by mime content type (magic)")
                                    return DELETE, None
                                if res == ATTACHMENT_BLOCK:
                                    self._debuginfo(
                                        suspect, f"Extracted file {safename} from archive {att_name} content-type={contenttype_magic} : blocked by mime content type (magic)")
                                    message = suspect.tags[f'{self.enginename}.errormessage']
                                    return blockactioncode, message

                            for item in nocheckinfo.get_filtered():
                                try:
                                    self._debuginfo(suspect, f'Archive File not checked: reason: {item[0]} -> {item[1]}')
                                except Exception as e:
                                    self._debuginfo(suspect, f'Archive File not checked: {e.__class__.__name__}: {str(e)}')

                    except Exception as e:
                        self.logger.debug(traceback.format_exc())
                        self.logger.error(f'{suspect.id} archive scanning failed in attachment {att_name} due to {e.__class__.__name__}: {str(e)}')
        return DUNNO, None

    def walk_all_parts(self, message):
        """Like email.message.Message's .walk() but also tries to find parts in the message's epilogue"""
        for part in message.walk():
            yield part

        boundary = message.get_boundary()
        epilogue = message.epilogue
        if epilogue is None or boundary not in epilogue:
            return

        candidate_parts = epilogue.split(boundary)
        for candidate in candidate_parts:
            try:
                part_content = candidate.strip()
                if part_content.lower().startswith('content'):
                    message = email.message_from_string(part_content)
                    yield message

            except Exception as e:
                self.logger.info(f'hidden part extraction failed due to {e.__class__.__name__}: {str(e)}')

    def _debuginfo(self, suspect, message, loglevel=logging.DEBUG):
        """Debug to log and suspect"""
        suspect.debug(message)
        self.logger.log(loglevel, f'{suspect.id} {message}')

    def __str__(self):
        return "Attachment Blocker"

    def lint(self):
        from fuglu.funkyconsole import FunkyConsole
        fc = FunkyConsole()
        allok = self.check_config() and self.lint_files(fc) and self.lint_magic() and self.lint_sql(fc) and self.lint_archivetypes(fc)
        return allok
    
    def lint_files(self, fc):
        ok = True
        rulesdir = self.config.get(self.section, 'rulesdir')
        if not os.path.exists(rulesdir):
            print(fc.strcolor("ERROR:", "red"),f' rulesdir {rulesdir} does not exist')
            ok = False
        else:
            try:
                RulesCache(rulesdir)
            except Exception as e:
                print(fc.strcolor("ERROR:", "red"),f' failed to load rulesdir {rulesdir} due to {e.__class__.__name__}: {str(e)}')
                ok = False
        nobouncerules = self.config.get(self.section, 'nobouncerules')
        if not os.path.exists(rulesdir):
            print(fc.strcolor("ERROR:", "red"),f' nobouncerules file {nobouncerules} does not exist')
            ok = False
        elif nobouncerules:
            print(fc.strcolor("WARNING:", "yellow"),f' nobouncerules file not defined')
        else:
            try:
                SuspectFilter(nobouncerules)
            except Exception as e:
                print(fc.strcolor("ERROR:", "red"),f' failed to load nobouncerules {nobouncerules} due to {e.__class__.__name__}: {str(e)}')
                ok = False
        return ok
        

    def lint_magic(self):
        # the lint routine for magic is now implemented in "filetype.ThreadLocalMagic.lint" and can
        # be called using the global object "filetype_handler"
        return filetype_handler.lint()

    def lint_archivetypes(self, fc):
        ok = True
        if not Archivehandle.avail('rar'):
            print(fc.strcolor("WARNING:", "yellow")," rarfile library not found, RAR support disabled")
        else:
            ok = self._lint_rar(fc)
        if not Archivehandle.avail('7z'):
            print(fc.strcolor("WARNING:", "yellow"), " pylzma/py7zlib or py7zr library not found, 7z support disabled")
        print("INFO: Archive scan, available file extensions: %s" % (",".join(sorted(Archivehandle.avail_archive_extensions_list))))
        print("INFO: Archive scan, active file extensions:    %s" % (",".join(sorted(self.active_archive_extensions.keys()))))
        return ok
    
    def _lint_rar(self, fc):
        from io import BytesIO
        archive = b"Rar!\x1a\x07\x01\x003\x92\xb5\xe5\n\x01\x05\x06\x00\x05\x01\x01\x80\x80\x00\xce%\xdd\xf0'\x02\x03\x0b\x8c\x00\x04\x8c\x00\xa4\x83\x02\xb6\xc9\xf0E\x80\x00\x01\tfuglu.txt\n\x03\x13bTodb0\xdd\x13fuglu rocks\n\x1dwVQ\x03\x05\x04\x00"
        handle = Archivehandle('rar', BytesIO(archive), archivename='lint.rar')
        names = handle.namelist()
        for name in names:
            try:
                handle.extract(name, 0)
            except Exception as e:
                print(fc.strcolor("ERROR:", "red"), f' failed to extract rar file due do {e.__class__.__name__}: {str(e)}')
                return False
        return True

    def lint_sql(self, fc):
        dbconn = ''
        if self.config.has_option(self.section, 'dbconnectstring'):
            dbconn = self.config.get(self.section, 'dbconnectstring')
        if dbconn.strip() != '':
            if not SQL_EXTENSION_ENABLED:
                print(fc.strcolor("WARNING:", "yellow"), " Fuglu SQL Extension not available, cannot load attachment rules from database")
                return False
            query = self.config.get(self.section, 'query')
            dbfile = DBFile(dbconn, query)
            try:
                dbfile.getContent({'scope': 'lint', 'checktype': FUATT_CHECKTYPE_FN})
            except Exception as e:
                import traceback
                print(fc.strcolor("ERROR:", "red"), f" Could not get attachment rules from database. Exception: {e.__class__.__name__}: {str(e)}")
                print(traceback.format_exc())
                return False
            else:
                print("INFO: Reading per user/domain attachment rules from database")
        else:
            print(f"INFO: No database configured. Using per user/domain file configuration from {self.config.get(self.section, 'rulesdir')}")
        return True


class AttHashAction(ScannerPlugin):
    """
    query attachment hashes against hashbl (e.g. spamhaus or abusix)
    spamhaus: sha256 / b32
    abusix: sha1 / hex
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.rbllookup = None
        self.requiredvars = {
            'blocklistconfig': {
                'default': '${confdir}/rblatthash.conf',
                'description': 'Domainmagic RBL lookup config file',
            },
            'hashalgorithm': {
                'default': 'sha256',
                'description': 'what hash algorithm to use, any supported by hashlib',
            },
            'hashencoding': {
                'default': 'b32',
                'description': 'what hash encoding to use, e.g. hex, b64, b32',
            },
            'enginename': {
                'default': '',
                'description': 'set custom engine name',
            },
            'testhash': {
                'default': 'E5NAEG57WZEJ4VGUOGEZ67NZ2FTD7RUV5QX6FIWEKOFKX5SR7UHQ',
                'description': 'test record in database, used by lint',
            },
        }

    def _init_rbllookup(self):
        if self.rbllookup is None:
            blocklistconfig = self.config.get(self.section, 'blocklistconfig')
            if os.path.exists(blocklistconfig):
                self.rbllookup = RBLLookup()
                self.rbllookup.from_config(blocklistconfig)

    def _check_hash_rbl(self, myhash):
        result = self.rbllookup.listings(myhash)
        return result

    def lint(self):
        ok = self.check_config()
        if ok and not DOMAINMAGIC_AVAILABLE:
            print('ERROR: domainmagic not available - this plugin will do nothing')
            ok = False

        hashenc = self.config.get(self.section, 'hashencoding').lower()
        encoders = [Mailattachment.HASHENC_HEX, Mailattachment.HASHENC_B32, Mailattachment.HASHENC_B64]
        if ok and hashenc not in encoders:
            print(f'ERROR: invalid hashencoding {hashenc}, use one of {", ".join(encoders)}')
            ok = False

        hashalgo = self.config.get(self.section, 'hashalgorithm').lower()
        if hashalgo not in hashlib.algorithms_available:
            print(f'ERROR: invalid hash algorithm {hashalgo}, use one of {", ".join(hashlib.algorithms_available)}')
            ok = False

        if ok:
            self._init_rbllookup()
            if self.rbllookup is None:
                blocklistconfig = self.config.get(self.section, 'blocklistconfig')
                print(f'ERROR: failed to load rbl config from file {blocklistconfig}')
                ok = False

        if ok:
            testhash = self.config.get(self.section, 'testhash')
            result = self._check_hash_rbl(testhash)
            if not result:
                print(f'ERROR: Hash {testhash} not detected in rbl check')
                ok = False

        return ok

    def examine(self, suspect):
        if not DOMAINMAGIC_AVAILABLE:
            return DUNNO
        self._init_rbllookup()
        if self.rbllookup is None:
            self.logger.error(f'{suspect.id} Not scanning - blocklistconfig could not be loaded')
            return DUNNO

        for attobj in suspect.att_mgr.get_objectlist(level=0):
            filename = attobj.filename

            if not attobj.is_attachment:
                self.logger.debug(f'{suspect.id} Skipping inline part with filename: {filename}')
                continue

            hashalgo = self.config.get(self.section, 'hashalgorithm').lower()
            hashenc = self.config.get(self.section, 'hashencoding').lower()
            myhash = attobj.get_checksum(hashalgo, hashenc, strip=True)

            result = self._check_hash_rbl(myhash)
            for blockname in result.keys():
                blockinfo = {filename: f'{blockname} {myhash}'}
                enginename = self.config.get(self.section, 'enginename') or None
                self._blockreport(suspect, blockinfo, enginename=enginename)
                self.logger.info(f'{suspect.id} attachment hash found: {myhash} in {filename}')
                break
            if not result:
                self.logger.debug(f'{suspect.id} no matching hash found for {filename} with hash {myhash}')

            if suspect.is_blocked():
                break
        else:
            self.logger.debug(f'{suspect.id} no attachment to check')

        return DUNNO


class FileHashCheck(AIORedisMixin, ScannerPlugin):
    """
    Check filehash against Redis database. If hash is found, mail will be marked as blocked.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'redis_conn': {
                'default': '',
                'description': 'redis backend database connection: redis://host:port/dbid',
            },
            'timeout': {
                'default': '2',
                'description': 'redis/kafka timeout in seconds'
            },
            'hashtype': {
                'default': 'MD5',
                'description': 'the hashing algorithm to be used',
            },
            'extensionsfile': {
                'default': '${confdir}/conf.d/filehash_extensions.txt',
                'description': 'path to file containing accepted file extensions. One per line, comments start after #',
            },
            'hashskiplistfile': {
                'default': '${confdir}/conf.d/filehash_skiphash.txt',
                'description': 'path to file containing skiplisted hashes. One hash per line, comments start after #',
            },
            'filenameskipfile': {
                'default': '${confdir}/conf.d/filehash_skipfilename.txt',
                'description': 'path to file containing file name fragments of file names to be skipped. One per line, comments start after #',
            },
            'allowmissingextension': {
                'default': 'False',
                'description': 'check files without extensions',
            },
            'minfilesize': {
                'default': '100',
                'description': 'minimal size of a file to be checked',
            },
            'minfilesizebyext': {
                'default': 'zip:40',
                'description': 'comma separated list of file type specific min file size overrides. specifiy as ext:size',
            },
            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },

        }

        self.minfilesizebyext = None
        self.hashskiplist = None
        self.extensions = None
        self.filenameskip = None
        self.allowmissingextension = False
        self.minfilesize = 100

    def _to_int(self, value, default=None):
        try:
            value = int(value)
        except ValueError:
            value = default
        return value

    def _init_databases(self):
        if self.minfilesizebyext is None:
            minfilesizebyext = self.config.getlist(self.section, 'minfilesizebyext')
            self.minfilesizebyext = {}
            for item in minfilesizebyext:
                if not ':' in item:
                    self.logger.error(f'minfilesizebyext {item} is not a valid specification')
                k, v = item.split(':', 1)
                try:
                    v = int(v)
                except ValueError:
                    self.logger.error(f'minfilesizebyext value {v} for {k} is not an integer')
                    continue
                self.minfilesizebyext[k.lower()] = v
        if self.extensions is None:
            filepath = self.config.get(self.section, 'extensionsfile')
            if filepath and os.path.exists(filepath):
                self.extensions = FileList(filename=filepath,
                                           lowercase=True, additional_filters=[FileList.inline_comments_filter])
            else:
                self.logger.error(f'extensionfile {filepath} does not exist')
        if self.hashskiplist is None:
            filepath = self.config.get(self.section, 'hashskiplistfile')
            if filepath and os.path.exists(filepath):
                self.hashskiplist = FileList(filename=filepath,
                                             lowercase=True, additional_filters=[FileList.inline_comments_filter])
            else:
                self.logger.error(f'hashskiplistfile {filepath} does not exist')
        if self.filenameskip is None:
            filepath = self.config.get(self.section, 'filenameskipfile')
            if filepath and os.path.exists(filepath):
                self.filenameskip = FileList(filename=filepath,
                                             lowercase=True, additional_filters=[FileList.inline_comments_filter])
            else:
                self.logger.error(f'filenameskipfile {filepath} does not exist')
        self.allowmissingextension = self.config.getboolean(self.section, 'allowmissingextension')
        self.minfilesize = self.config.getint(self.section, 'minfilesize')

        
    async def examine(self, suspect):
        if not REDIS_ENABLED:
            return DUNNO

        hashtype = self.config.get(self.section, 'hashtype')
        hashtype = hashtype.lower()
        if not hasattr(hashlib, hashtype):
            self.logger.error(f'{suspect.id} invalid hash type {hashtype}')

        self._init_databases()

        if self.hashskiplist:
            hashskiplist = self.hashskiplist.get_list()
        else:
            hashskiplist = []

        for attobj in suspect.att_mgr.get_objectlist(level=0):
            filesize = attobj.filesize or 0
            
            if not attobj.is_attachment:
                self.logger.debug(f'{suspect.id} Skipping inline part with filename: {attobj.filename}')
                continue

            if not self._check_filename(suspect.id, attobj.filename, filesize):
                self.logger.debug(f'{suspect.id} Skipping attachment size {filesize} with filename: {attobj.filename}')
                continue

            myhash = attobj.get_checksum(hashtype)
            if myhash in hashskiplist:
                self.logger.debug(f'{suspect.id} Skiplisted hash: {myhash}')
                continue

            try:
                virusname = await self._check_hash_redis(suspect, myhash)
                if virusname is not None:
                    blockinfo = {attobj.filename: f'{virusname} {myhash}'}
                    self._blockreport(suspect, blockinfo)
                    break
                else:
                    self.logger.debug(f'{suspect.id} no matching hash found for {attobj.filename} with hash {myhash}')
            except Exception as e:
                self.logger.error(f'{suspect.id} failed to retrieve hash due to {e.__class__.__name__}: {str(e)}')
                action = self._problemcode()
                message = 'Internal Server Error'
                return action, message

        return DUNNO, None

    def _check_skip(self, suspect):
        skip = None
        if suspect.is_blocked():
            skip = 'blocked'
        elif suspect.is_spam():
            skip = 'spam'
        elif suspect.is_virus():
            skip = 'virus'
        return skip

    async def _lint_redis(self):
        success = True
        redis_conn = self.config.get(self.section, 'redis_conn')
        if redis_conn and not REDIS_ENABLED:
            print('ERROR: redis not available')
            success = False
        elif redis_conn:
            if self.aioredisbackend is None:
                success = False
                print(f'ERROR: could not connect to redis server: {redis_conn}')
            else:
                try:
                    reply = await self.aioredisbackend.ping()
                    if reply:
                        print('OK: redis server replied to ping')
                    else:
                        print('ERROR: redis server did not reply to ping')

                except Exception as e:
                    success = False
                    print(f'ERROR: failed to talk to redis server: {e.__class__.__name__}: {str(e)}')
        else:
            print('INFO: redis disabled')
        return success

    async def lint(self):
        success = self.check_config()
        if not success:
            return success
        
        success = await self._lint_redis()

        hashtype = self.config.get(self.section, 'hashtype')
        hashtype = hashtype.lower()
        if not hasattr(hashlib, hashtype):
            print(f'ERROR: invalid hash type {hashtype}')
            success = False

        self.hashskiplist = FileList(filename=self.config.get(self.section, 'hashskiplistfile'), lowercase=True,
                                     additional_filters=[FileList.inline_comments_filter])
        if self.hashskiplist.get_list():
            print('WARNING: empty hash skiplist')

        self.extensions = FileList(filename=self.config.get(self.section, 'extensionsfile'), lowercase=True,
                                   additional_filters=[FileList.inline_comments_filter])
        ext = self.extensions.get_list()
        if len(ext) == 0:
            success = False
            print('WARNING: extensions list is empty')
        else:
            print(f'INFO: checking {len(ext)} extensions')

        self.filenameskip = FileList(filename=self.config.get(self.section, 'filenameskipfile'),
                                     lowercase=True, additional_filters=[FileList.inline_comments_filter])
        if len(self.filenameskip.get_list()) == 0:
            success = False
            print('WARNING: extensions list is empty')

        return success

    async def _check_hash_redis(self, suspect, myhash):
        virusname = None

        if self.aioredisbackend is not None:
            try:
                timeout = self.config.getint(self.section, 'timeout')
                result = await self.aioredisbackend.hmget(myhash, ['virusname'], timeout=timeout)
                if result:
                    virusname = force_uString(result[0])
            except Exception as e:
                self.logger.error(f"{suspect.id} problem getting virusname for hash {myhash} due to {self.__class__.__name__}: {str(e)}")
        return virusname

    def _check_filename(self, suspectid, filename, filesize, force=False, ignore_upn=False, ignore_dotfiles=False):
        ok = True

        if ignore_upn:
            for i in filename:
                if ord(i) > 128:
                    self.logger.debug(f'{suspectid} skipping file {filename} - name contains upn')
                    ok = False
                    break

        if ok and filename in ['unnamed.htm', 'unnamed.txt']:  # ignore text and html parts of mail
            ok = False

        if ok and ignore_dotfiles and filename.startswith('.'):
            self.logger.debug(f'{suspectid} skipping file {filename} - is hidden')
            ok = False

        lowerfile = filename.lower()
        try:
            ext = lowerfile.rsplit('.', 1)[1]
        except IndexError:
            ext = ''

        if ok and self.extensions and ext != '':
            if ext not in self.extensions.get_list() and not force:
                self.logger.debug(f'{suspectid} skipping file {filename} - extension not in my list')
                ok = False
        elif ok:
            if not self.allowmissingextension and not force:
                self.logger.debug(f'{suspectid} skipping file {filename} with missing extension')
                ok = False

        if ok and self.filenameskip and not force:
            for badword in self.filenameskip.get_list():
                if badword in lowerfile:
                    self.logger.debug(f'{suspectid} filename {filename} contains bad word {badword} - skipping')
                    ok = False
                    break

            if ok and ext in self.minfilesizebyext:
                if filesize < self.minfilesizebyext[ext]:
                    self.logger.debug(f'{suspectid} file {filename} too small for extension {ext} with size {filesize} bytes')
                    ok = False
            elif ok and filesize < self.minfilesize:
                self.logger.debug(f'{suspectid} ignoring small file {filename} with size {filesize} bytes')
                ok = False

        return ok


class FileHashRedis(object):
    def __init__(self, aioredisbackend, ttl:int, timeout:int, logger, logprefix:str='(n/a)'):
        self.aioredisbackend = aioredisbackend
        self.ttl = ttl
        self.timeout = timeout
        self.logger = logger
        self.logprefix = logprefix

    async def insert(self, myhash, messagebytes, age=0):
        values = json.loads(messagebytes)
        filename = values.get('filename')
        virusname = values.get('virusname')
        filesize = values.get('filesize')

        td = int(self.ttl-age)
        if td <= 0:
            self.logger.debug(f'{self.logprefix} skipping old hash {myhash} with age {age}')
            return

        try:
            result = await self.aioredisbackend.hmget(myhash, ['virusname', 'filesize'], timeout=self.timeout)
            if result and result[1] == filesize:
                virusname = result[0]
                self.logger.debug(f'{self.logprefix} known hash {myhash} has virus name {virusname}')
                await self.aioredisbackend.expire(myhash, ttl=td, timeout=self.timeout)
            else:
                mapping = dict(filename=filename, filesize=filesize, virusname=virusname)
                await self.aioredisbackend.hset(myhash, mapping=mapping, ttl=td, timeout=self.timeout)
        except Exception as e:
            self.logger.warning(f'{self.logprefix} failed to insert hash in redis due to {e.__class__.__name__}: {str(e)}')


class FileHashFeeder(FileHashCheck):
    """
    Write filehashes to redis datbase or Kafka. Training plugin for FileHashCheck plugin.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

        requiredvars = {
            'prefix': {
                'default': 'FH.GEN',
                'description': 'virus name prefix',
            },
            'expirationdays': {
                'default': '3',
                'description': 'days until hash expires',
            },
            'kafkahosts': {
                'default': '',
                'description:': 'kafka bootstrap hosts: host1:port host2:port'
            },
            'kafkatopic': {
                'default': 'filehash',
                'description': 'name of kafka topic'
            },
            'kafkausername': {
                'default': '',
                'description:': 'kafka sasl user name for this producer'
            },
            'kafkapassword': {
                'default': '',
                'description': 'kafka sals password for this producer'
            },
        }
        self.requiredvars.update(requiredvars)

        self.kafkaproducer = None
        self.kafkatopic = None
        self.delta_expiration = 0

    def lint(self):
        success = FileHashCheck.lint(self)
        expirationdays = self.config.get(self.section, 'expirationdays')
        try:
            int(expirationdays)
        except ValueError:
            success = False
            print(f'ERROR: expirationdays must be a number. current value: {expirationdays}')
        if self.config.get(self.section, 'kafkahosts'):
            try:
                self._init_kafka()
            except kafka.errors.KafkaError as e:
                print(f'ERROR: failed to connect to kafka: {str(e)}')
                success = False
            except Exception as e:
                print(f'ERROR: Error connecting to kafka: {str(e)}')
                self.logger.exception(e)
                success = False
        else:
            print('INFO: kafka disabled')
        return success

    async def process(self, suspect, decision):
        await self._run(suspect)

    async def examine(self, suspect):
        await self._run(suspect)
        return DUNNO, None

    async def _run(self, suspect):
        hashtype = self.config.get(self.section, 'hashtype')
        hashtype = hashtype.lower()
        if not hasattr(hashlib, hashtype):
            self.logger.error(f'{suspect.id} invalid hash type {hashtype}')
            return

        self._init_databases()
        self.delta_expiration = self.config.getint(self.section, 'expirationdays') * 86400

        if self.hashskiplist:
            hashskiplist = self.hashskiplist.get_list()
        else:
            hashskiplist = []

        for attobj in suspect.att_mgr.get_objectlist(level=0):
            filesize = attobj.filesize or 0
            
            if not attobj.is_attachment:
                self.logger.debug(f'{suspect.id} Skipping inline part with filename: {attobj.filename}')
                continue
                
            if not self._check_filename(suspect.id, attobj.filename, filesize):
                continue

            myhash = attobj.get_checksum(hashtype)
            if myhash in hashskiplist:
                self.logger.debug(f'{suspect.id} Skiplisted hash: {myhash}')
                continue

            virusname = attobj.get_mangled_filename(prefix=self.config.get(self.section, 'prefix'))
            messagebytes = json.dumps({'filename': attobj.filename, 'virusname': virusname, 'filesize': filesize, 'filehash': myhash}).encode()
            if self.config.get(self.section, 'redis_conn'):
                await self._insert_redis(myhash, messagebytes, suspect)
            if self.config.get(self.section, 'kafkahosts'):
                try:
                    self._insert_kafka(myhash, messagebytes)
                    self.logger.info(f'{suspect.id} logged hash {myhash} to kafka')
                except Exception as e:
                    self.logger.error(f'{suspect.id} failed to log hash {myhash} due to {e.__class__.__name__}: {str(e)}')

    async def _insert_redis(self, myhash, messagebytes, suspect):
        timeout = self.config.get(self.section, 'timeout')
        redisbackend = FileHashRedis(self.aioredisbackend, self.delta_expiration, timeout, self.logger, suspect.id)
        await redisbackend.insert(myhash, messagebytes, 0)

    def _init_kafka(self):
        if self.kafkaproducer is not None:
            return
        self.bootstrap_servers = self.config.getlist(self.section, 'kafkahosts')
        if self.bootstrap_servers:
            self.kafkatopic = self.config.get(self.section, 'kafkatopic')
            timeout = self.config.getint(self.section, 'timeout')
            username = self.config.get(self.section, 'kafkausername')
            password = self.config.get(self.section, 'kafkapassword')
            clientid = f'prod-fuglu-{self.__class__.__name__}-{get_outgoing_helo(self.config)}'
            self.kafkaproducer = kafka.KafkaProducer(bootstrap_servers=self.bootstrap_servers, api_version=(0, 10, 1), client_id=clientid,
                                                     request_timeout_ms=timeout*1000, sasl_plain_username=username, sasl_plain_password=password)

    def _insert_kafka(self, myhash, messagebytes):
        if self.kafkaproducer is None:
            self._init_kafka()
        try:
            self.kafkaproducer.send(self.kafkatopic, value=messagebytes, key=force_bString(myhash))
        except Exception as e:
            self.kafkaproducer = None
            raise e


class EncryptedArchives(ScannerPlugin):
    """Block password-protected archives"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars = {
            'archivecontentmaxsize': {
                'default': '5000000',
                'description': 'only extract and examine files up to this amount of (uncompressed) bytes',
            },
            'template_blockedfile': {
                'default': '${confdir}/templates/blockedfile.tmpl',
                'description': 'Mail template for the bounce to inform sender about blocked attachment',
            },
            'sendbounce': {
                'default': 'True',
                'description': 'inform the sender about blocked attachments.\nIf a previous plugin tagged the message as spam or infected, no bounce will be sent to prevent backscatter',
            },
            'blockaction': {
                'default': 'DELETE',
                'description': 'what should the plugin do when a blocked attachment is detected\n'
                               'REJECT : reject the message (recommended in pre-queue mode)\n'
                               'DELETE : discard messages\n'
                               'DUNNO  : mark as blocked but continue anyway '
                               '(eg. if you have a later quarantine plugin)',
            },
        }
        self.logger = self._logger()

    def examine(self, suspect: Suspect):
        """Exampine suspect"""
        blockaction = self.config.get(self.section, 'blockaction')
        archivecontentmaxsize = self.config.getint(self.section, 'archivecontentmaxsize')

        # NoExtractInfo object will collect information about files in archives (or the archive itself)
        # if something could not be extracted
        noextractinfo = NoExtractInfo()

        # get list of direct attachments as well as extracted files if direct attachment is an archive
        _ = suspect.att_mgr.get_objectlist(level=1, maxsize_extract=archivecontentmaxsize, include_parents=True, noextractinfo=noextractinfo)

        # get all reasons why content was not extracted except due to level
        noextractlist = noextractinfo.get_filtered(minus_filters=["level"])
        blockinfo = {}
        for file, message in noextractlist:
            if message == "Password protected archive (data + meta)":
                self.logger.info()
                # filelists are protected as well
                blockinfo = {f'{file}': f"Attachment {file} is a password protected archive (data + meta)"}

            elif "password" in message.lower():
                # filelists are not protected, only data
                self.logger.info(f"Password protected file {file} in archive, msg: {message}")
                blockinfo = {f'{file}': f"Password protected file {file} in archive"}

        if blockinfo:
            # Blocked attachments contained...
            self._blockreport(suspect, blockinfo, enginename='EncryptedArchives')
            sendbounce = self.config.getboolean(self.section, 'sendbounce')
            if sendbounce:
                if suspect.is_spam() or suspect.is_virus():
                    self.logger.info(f"{suspect.id} backscatter prevention: not sending attachment block "
                                     f"bounce to {suspect.from_address} - the message is tagged spam or virus")
                elif not suspect.from_address:
                    self.logger.warning(f"{suspect.id} not sending attachment block bounce to empty recipient")
                else:
                    # check if another attachment blocker has already sent a bounce
                    queueid = suspect.get_tag('Attachment.bounce.queueid')
                    if queueid:
                        self.logger.info(f'{suspect.id} already sent attachment block bounce '
                                         f'to {suspect.from_address} with queueid {queueid}')
                    else:
                        self.logger.debug(f"{suspect.id} sending attachment block "
                                          f"bounce to {suspect.from_address}")
                        bounce = Bounce(self.config)
                        blockedfiletemplate = self.config.get(self.section, 'template_blockedfile')
                        blockinfostr = '\n'.join([f'{x}: {y}' for x,y in blockinfo.items()])
                        queueid = bounce.send_template_file(suspect.from_address,
                                                            blockedfiletemplate,
                                                            suspect,
                                                            {'blockinfo': blockinfostr})
                        self.logger.info(f'{suspect.id} sent attachment block bounce '
                                         f'to {suspect.from_address} with queueid {queueid}')
                        suspect.set_tag('Attachment.bounce.queueid', queueid)

            blockactioncode = string_to_actioncode(blockaction)
            return blockactioncode, "Password protected archives found!"
        return DUNNO


class AttachmentLimit(ScannerPlugin):
    """
    limit number of direct attachments.
    some big mail hosters limit the number of attachments, e.g. M365 sets the limit to 1000:
    host foobar-ch.mail.protection.outlook.com[52.101.187.1] said: 554 5.6.211 Invalid MIME Content: Number of MimePart objects (1001) exceeded allowed maximum (1000).
    """
    
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'limit': {
                'default': '1000',
                'description': 'maximum number of permitted attachments',
            },
            'rejectmessage': {
                'default': 'too many attachments: ${count}>${limit}',
                'description': 'reject message if number of attachments is above limit'
            },
        }
    
    def examine(self, suspect):
        att_limit = self.config.getint(self.section, 'limit')
        attachmentlist = suspect.att_mgr.get_objectlist(level=0)
        count = len(attachmentlist)
        if count > att_limit:
            values = {'count': count, 'limit': att_limit}
            message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, values)
            return REJECT, message
        return DUNNO
    
    
    def lint(self):
        ok = self.check_config()
        if ok:
            att_limit = self.config.getint(self.section, 'limit')
            if att_limit < 0:
                ok = False
                print('limit must be > 0')
        return ok
