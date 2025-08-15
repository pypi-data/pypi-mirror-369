#   Copyright Oli Schacher, Fumail Project #
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

import logging
import sys
import traceback
import tempfile
import time
import os
import asyncio
import functools
import typing as tp

from fuglu.stats import Statskeeper, StatDelta
from fuglu.shared import DUNNO, ACCEPT, REJECT, DEFER, DELETE, utcnow
from fuglu.connectors.check import HealthCheckSuspect
from fuglu.debug import CrashStore
from collections import defaultdict


class TrackTimings(object):
    def __init__(self, enable=False, port=-1):
        """
        Constructor, setting function handles to real functions or dummies

        Args:
            enable (bool): enable/disable time tracker
            port (int): incoming port
        """
        self.timings_logger = logging.getLogger(f"{__package__}.Timings")

        # timings
        self._enabletimetracker = False
        self.enabletimetracker = enable

        self.timetracker = time.time()

        # starttime and realtime will be used for async
        self.starttime = self.timetracker
        self.realtime = 0
        self.asynctime = defaultdict(lambda: 0.0)

        self.port = port if port is not None else -1
        # name is used as hash, so it's possible to add to an existing timer by same name
        self.timingshash = {}

    def resettimer(self):
        """Reset time tracker"""
        if self.enabletimetracker:
            self.timetracker = time.time()
            self.starttime = self.timetracker
            self.realtime = 0
            self.asynctime = defaultdict(lambda: 0.0)
            self.timingshash = {}

    def sum_asynctime(self, delta: tp.Union[float, int], key: tp.Optional[str] = None, logid: tp.Optional[str] = None):
        #oldval = self.asynctime[key]
        self.asynctime[key] += delta
        #self.timings_logger.debug(f"{logid+' ' if logid else ''}Adding {delta} to {oldval} -> asyncdict[{key}]={self.asynctime[key]}")

    @property
    def enabletimetracker(self):
        return self._enabletimetracker

    @enabletimetracker.setter
    def enabletimetracker(self, enabled):
        if not enabled:
            self._enabletimetracker = False
        else:
            self._enabletimetracker = True
            self.timetracker = time.time()
            self.timingshash = {}

    def tracktime(self, tagname, plugin=False, prepender=False, appender=False, mplugin=False):
        return self._tracktime(tagname, plugin=plugin, prepender=prepender, appender=appender, mplugin=mplugin) if self.enabletimetracker else None

    def gettime(self, plugins=None, prependers=None, appenders=None, mplugins=None):
        return self._gettime(plugins=plugins, prependers=prependers, appenders=appenders, mplugins=mplugins) if self.enabletimetracker else []

    def gettime_dict(self, plugins=None, prependers=None, appenders=None, mplugins=None):
        """Extract timing dict"""
        timedict = {}
        try:
            basedata = self._gettime(plugins=plugins, prependers=prependers, appenders=appenders, mplugins=mplugins) \
                if self.enabletimetracker else []
            for entry in basedata:
                tagname, timing = entry
                timedict[tagname] = timing
        except Exception as e:
            logging.getLogger("fuglu.TrackTimings.gettime_dict").error(f"Problem extracting/parsing timings", exc_info=e)
        return timedict

    def sumtime(self, plugins=None, prependers=None, appenders=None, mplugins=None):
        return self._sumtime(plugins=plugins, prependers=prependers, appenders=appenders, mplugins=mplugins) if self.enabletimetracker else 0.0

    def report_timings(self, suspectid, withrealtime=False, end=True):
        return self._report_timings(suspectid, withrealtime=withrealtime, end=end) if self.enabletimetracker else None

    def report_plugintime(self, suspectid, pluginname, end=True):
        return self._report_plugintime(suspectid, pluginname, end=end) if self.enabletimetracker else None

    def _tracktime(self, tagname, plugin=False, prepender=False, appender=False, mplugin=False):
        """
        Given a tag name, track and store time since last call of same function

        Args:
            tagname (str): String with tag name

        Keyword Args:
            plugin (bool): tag belongs to plugin timing (default=False)
            prepender (bool): tag belongs to prepender timing (default=False)
            appender (bool): tag belongs to appender timing (default=False)
            mplugin (bool): tag belongs to milterplugin timing (default=False)
        """
        newtime = time.time()
        difftime = newtime - self.timetracker
        self.realtime = newtime - self.starttime
        self.timetracker = newtime
        hsh = (tagname, plugin, prepender, appender, mplugin)
        existing = self.timingshash.get(hsh)
        if existing:
            _, e_difftime, _, _, _, _ = existing
            difftime = e_difftime + difftime
            self.timings_logger.debug(f"After updating existing entry for {tagname}: {e_difftime} -> {difftime}")

        self.timingshash[hsh] = (tagname, difftime, plugin, prepender, appender, mplugin)

    def _gettime(self, plugins=None, prependers=None, appenders=None, mplugins=None):
        """
        Get a list of timings stored (all/only plugins/exclude plugins)

        Keyword Args:
            plugins (bool or None): 'None': ignore this restriction, True: timing must have 'plugin' tag, False: timing must not have plugin tag
            prependers (bool or None): 'None': ignore this restriction, True: timing must have 'prepender' tag, False: timing must not have plugin tag
            appenders (bool or None): 'None': ignore this restriction, True: timing must have 'appender' tag, False: timing must not have plugin tag
            mplugins (bool or None): 'None': ignore this restriction, True: timing must have 'mplugin' tag, False: timing must not have plugin tag

        Returns:
            list of tuples (name, time)

        """
        timing_list = []
        for timeitem in self.timingshash.values():
            if plugins is not None and timeitem[2] != plugins:
                continue
            if prependers is not None and timeitem[3] != prependers:
                continue
            if appenders is not None and timeitem[4] != appenders:
                continue
            if mplugins is not None and timeitem[5] != mplugins:
                continue
            timing_list.append(timeitem[:2])
        return timing_list

    def _sumtime(self, plugins=None, prependers=None, appenders=None, mplugins=None):
        """
        Get total time spent.

        Keyword Args:
            plugins (bool or None): For 'None' return total time, True: time spent in plugins, False: time spent outside plugins
            appenders (bool or None): For 'None' return total time, True: time spent in appenders, False: time spent outside appenders
            prependers (bool or None): For 'None' return total time, True: time spent in prependers, False: time spent outside prependers
            mplugins (bool or None): For 'None' return total time, True: time spent in milter plugins, False: time spent outside milter plugins

        Returns:
            float: total time spent, given restriction

        """
        puretimings = [a[1] for a in self.gettime(plugins=plugins, prependers=prependers, appenders=appenders, mplugins=mplugins)]
        if len(puretimings) == 0:
            return 0.0
        else:
            return functools.reduce(lambda x, y: (x + y), puretimings)

    def _report_timings(self, suspectid, withrealtime=False, end=True):
        """
        Report all the timings collected
        Args:
            suspectid (id):  the suspect id
            withrealtime(bool): The real time from start to end, which might differ from total time in case of async

        """
        if not self.timingshash:
            self.timings_logger.debug(f'{suspectid} no timings to report')
            return

        if end:
            self.tracktime('end')

        total_asynctime = 0.0
        if withrealtime:
            self.timings_logger.info(f'port: {self.port}, id: {suspectid}, real: {self.realtime:.6f}')
            for k, val in self.asynctime.items():
                self.timings_logger.info(f'port: {self.port}, id: {suspectid}, async{"("+k+")" if k else ""}: {val:.6f}')
                total_asynctime += val
            self.timings_logger.info(f'port: {self.port}, id: {suspectid}, total(async): {total_asynctime:.3f}')

        self.timings_logger.info(f'port: {self.port}, id: {suspectid}, total: {self.sumtime()-total_asynctime:.6f}')
        sumtime = self.sumtime(plugins=False, prependers=False, appenders=False, mplugins=False)
        self.timings_logger.info(f'port: {self.port}, id: {suspectid}, overhead: {sumtime:.3f}')
        
        all_milterplugs = self.gettime(mplugins=True)
        for mplugintime in all_milterplugs:
            self.timings_logger.info(f'port: {self.port}, id: {suspectid}, (MPL) {mplugintime[0]}: {mplugintime[1]:.3f}')
        all_prependertimes = self.gettime(prependers=True)
        for prependertime in all_prependertimes:
            self.timings_logger.info(f'port: {self.port}, id: {suspectid}, (PRE) {prependertime[0]}: {prependertime[1]:.3f}')
        all_plugintimes = self.gettime(plugins=True)
        for plugintime in all_plugintimes:
            self.timings_logger.info(f'port: {self.port}, id: {suspectid}, (PLG) {plugintime[0]}: {plugintime[1]:.3f}')
        all_appendertimes = self.gettime(appenders=True)
        for appendertime in all_appendertimes:
            self.timings_logger.info(f'port: {self.port}, id: {suspectid}, (APP) {appendertime[0]}: {appendertime[1]:.3f}')
        all_overheadtimes = self.gettime(plugins=False, prependers=False, appenders=False)
        for overheadtime in all_overheadtimes:
            self.timings_logger.debug(f'port: {self.port}, id: {suspectid}, {overheadtime[0]}: {overheadtime[1]:.3f}')

    def _report_plugintime(self, suspectid, pluginname, end=True):
        """
        Report timings inside plugin

        Args:
            suspectid (str): the id of the suspect
            pluginname (str): plugin name

        Keyword Args:
            end (bool): if true another timing called 'end' will be created before the report
        """
        if end:
            self.tracktime('end')
        all_timings = self.gettime()
        for itime in all_timings:
            self.timings_logger.debug(f'port: {self.port}, id: {suspectid}, [{pluginname}] {itime[0]}: {itime[1]:.3f}')


class SessionHandler(TrackTimings):

    """thread handling one message"""

    def __init__(self, protohandler, config, prependers, plugins, appenders, port, milterplugins):
        super().__init__(port=port)
        self.logger = logging.getLogger("fuglu.SessionHandler")
        self.prependers = prependers
        self.plugins = plugins
        self.appenders = appenders
        self.stats = Statskeeper()
        self.worker = None
        self.protohandler = protohandler
        self.config = config
        self.milterplugins = milterplugins

        # IMPORTANT: Initialise per message variables in resetvars
        #            to make sure these variables are re-initialised if connection is re-used
        #            for several messages
        self.action = None
        self.message = None
        self.enabletimetracker = config.getboolean('main', 'scantimelogger', fallback=False)
        self.logger.debug(f"enabletimetracker={self.enabletimetracker}")

    def resetvars(self):
        """Reset and initialise variables that are valid per message"""
        self.action = DUNNO
        self.message = None

        # reset timer for time tracking
        self.resettimer()

    def set_workerstate(self, status):
        if self.worker is not None:
            self.worker.workerstate = status

    def _gen_retmessage(self, suspect, msg):
        if self.config.getboolean('main', 'suspectidreturn') and suspect.id not in msg:
            msg = f'{msg} ({suspect.id})'
        return msg

    async def handlesession(self, worker=None):

        self.worker = worker
        prependheader = self.config.get('main', 'prependaddedheaders')

        keep_connection = True
        isuspect = 0  # in case connection is reused (milter) keep track of suspect for workerstate
        message_prefix = 'undef'

        while keep_connection:
            suspect = None
            try:
                isuspect += 1
                # reset variables to make sure per-message variables are re-initialised in case of handling
                # multiple messages in one session
                self.resetvars()

                message_prefix = f"(#{isuspect})"  # identifier (receiving multiple suspects in one session)

                self.set_workerstate(f'{message_prefix}receiving message')
                self.tracktime("SessionHandler-Setup")
                suspect = self.protohandler.get_suspect(milterplugins=self.milterplugins)
                if suspect is None:
                    self.logger.debug(f'{message_prefix}No Suspect retrieved, ending session')
                    try:
                        self.protohandler.endsession()
                        if isuspect > 2:
                            self.logger.info(f'Session finished handling multiple '
                                             f'suspects ({isuspect-1}) in same connection')
                    except Exception:
                        pass
                    return
                elif isinstance(suspect, HealthCheckSuspect):
                    self.logger.debug(f'{message_prefix}Health Check Suspect retrieved')
                    self.protohandler.healthcheck_reply()
                    self.resetvars()
                    return

                # register session to suspect in timetracker
                suspect.timetracker = self

                self.tracktime("Message-Receive-Suspect")
                self.stats.increase_counter_values(StatDelta(in_=1))

                if len(suspect.recipients) != 1:
                    self.logger.warning(
                        f'{message_prefix}Notice: Message from {suspect.from_address} has {len(suspect.recipients)} recipients. Plugins supporting only one recipient will see: {suspect.to_address}')
                self.logger.debug(f'{message_prefix}Message from {suspect.from_address} to {suspect.to_address}: {suspect.size} bytes stored to {suspect.tempfile}')
                self.set_workerstate(f'{message_prefix}Handling message {suspect}')
                # store incoming port to tag, could be used to disable plugins
                # based on port
                try:
                    port = self.protohandler.socket.getsockname()[1]
                    if port is not None:
                        suspect.tags['incomingport'] = port
                except Exception as e:
                    self.logger.warning(f'{message_prefix}Could not get incoming port: {e.__class__.__name__}: {str(e)}')

                pluglist, applist = await self.run_prependers(suspect)

                starttime = time.time()
                await self.run_plugins(suspect, pluglist)

                # Set fuglu spam status if wanted
                if self.config.getboolean('main', 'spamstatusheader'):
                    if suspect.is_spam():
                        suspect.add_header(f'{prependheader}Spamstatus', 'YES')
                    else:
                        suspect.add_header(f'{prependheader}Spamstatus', 'NO')

                # how long did it all take?
                difftime = time.time() - starttime
                suspect.tags['fuglu.scantime'] = "%.4f" % difftime

                # Debug info to mail
                if self.config.getboolean('main', 'debuginfoheader'):
                    debuginfo = str(suspect)
                    suspect.add_header(f"{prependheader}Debuginfo", debuginfo)

                # add suspect id for tracking
                if self.config.getboolean('main', 'suspectidheader'):
                    suspect.add_header(f'{prependheader}Suspect', suspect.id)
                self.tracktime("Adding-Headers")

                # checks done... print out suspect status
                logformat = self.config.get('main', 'logtemplate')
                if logformat.strip() != '':
                    self.logger.info(suspect.log_format(logformat))
                suspect.debug(suspect)
                self.tracktime("Debug-Suspect")

                # check if one of the plugins made a decision
                result = self.action

                self.set_workerstate(f"{message_prefix}Finishing message {suspect.id}")

                message_is_deferred = False
                if result == ACCEPT or result == DUNNO:
                    try:
                        self.protohandler.commitback(suspect)
                        self.tracktime("Commitback")
                        self.stats.increase_counter_values(StatDelta(out=1))
                        self.tracktime("Increase-Stats")

                    except KeyboardInterrupt:
                        sys.exit()
                    except Exception as e:
                        message_is_deferred = True
                        trb = traceback.format_exc()
                        self.logger.error(f'{suspect.id} Could not commit message. Error: {trb}')
                        #self.logger.exception(e)
                        self._defer()

                elif result == DELETE:
                    self.logger.info(f'MESSAGE DELETED: {suspect.id}')
                    retmesg = self.message or 'OK'
                    retmesg = self._gen_retmessage(suspect, retmesg)
                    self.protohandler.discard(retmesg)
                elif result == REJECT:
                    retmesg = self.message or 'Rejected by content scanner'
                    retmesg = self._gen_retmessage(suspect, retmesg)
                    self.protohandler.reject(retmesg)
                elif result == DEFER:
                    message_is_deferred = True
                    retmesg = self.message or 'Try again later'
                    retmesg = self._gen_retmessage(suspect, retmesg)
                    self._defer(retmesg)
                else:
                    self.logger.error(f'{suspect.id} Invalid Message action Code: {result}. Using DEFER')
                    message_is_deferred = True
                    self._defer()

                # run appenders (stats plugin etc) unless msg is deferred
                if not message_is_deferred:
                    self.stats.increasecounters(suspect)
                    self.tracktime("Increase-Counters")
                    await self.run_appenders(suspect, result, applist)
                else:
                    self.logger.warning(f'DEFERRED {suspect.id}')

                # clean up
                if suspect.tempfilename() != "(buffer-only)":
                    try:
                        os.remove(suspect.tempfile)
                        self.logger.debug(f'{message_prefix}Removed tempfile {suspect.tempfile if suspect.tempfile else "(not available)"}')
                        suspect.tempfile = None
                        self.tracktime("Remove-tempfile")
                    except OSError:
                        self.logger.warning(f'{message_prefix}Could not remove tempfile {suspect.tempfile}')
            except KeyboardInterrupt:
                sys.exit(0)
            except ValueError as e:
                # Error in envelope send/receive address
                try:
                    self.logger.warning(f'{message_prefix}Invalid send/receive address -> {str(e)}')
                except Exception:
                    pass

                address_compliance_fail_action = self.config.get('main', 'address_compliance_fail_action', fallback='defer').lower()
                message = self.config.get('main', 'address_compliance_fail_message', fallback='invalid sender or recipient address')

                if address_compliance_fail_action == "defer":
                    self._defer(message)
                elif address_compliance_fail_action == "reject":
                    self._reject(message)
                elif address_compliance_fail_action == "discard":
                    self._discard(message)
                elif address_compliance_fail_action == "dunno":
                    self.logger.warning(f'{message_prefix} accepting invalid sender or recipient')
                else:
                    self._defer(message)

            except Exception as e:
                exc = traceback.format_exc()
                self.logger.error(f'{suspect.id if suspect else "<>"} Exception {e}: {exc}')
                self._defer()
                # don't continue, might end in an infinite loop
                keep_connection = False

            finally:
                # finally is also executed if there's a return statement somewhere in try-except

                remove_tmpfiles_on_error = self.config.getboolean('main', 'remove_tmpfiles_on_error', fallback=True)
                if suspect is None:
                    # if there was an error creating the suspect, check if the filename can be
                    # extracted from the protohandler
                    tmpfilename = self.protohandler.get_tmpfile()
                    if tmpfilename is None:
                        tmpfilename = ""

                    if remove_tmpfiles_on_error:
                        if tmpfilename:
                            self.logger.debug(f'{message_prefix}Remove tmpfile: {tmpfilename} for failed message')
                        self.protohandler.remove_tmpfile()
                    else:
                        if tmpfilename:
                            self.logger.warning(f'{message_prefix}Keep tmpfile: {tmpfilename} for failed message')
                        else:
                            self.logger.warning(f'{message_prefix}No tmpfile to keep for failed message')

                elif suspect.tempfilename() != "(buffer-only)":
                    # suspect was created but not stopped cleanly
                    if remove_tmpfiles_on_error:
                        try:
                            os.remove(suspect.tempfilename())
                            self.logger.debug(f'{message_prefix}Removed tempfile {suspect.tempfilename()}')
                        except OSError:
                            self.logger.warning(f'{message_prefix}Could not remove tempfile {suspect.tempfilename()}')
                    else:
                        self.logger.warning(f'{message_prefix}Keep tempfile {suspect.tempfilename()} for failed message')

                # try to remove the suspect
                try:
                    self.logger.debug(f'{message_prefix}Remove suspect (current refs): {sys.getrefcount(suspect)}')
                    suspectid = suspect.id
                    del suspect
                except Exception:
                    suspectid = "unknown"

                # ---------------#
                # report timings #
                # ---------------#
                if not suspectid == "unknown":
                    self.report_timings(suspectid)

                if keep_connection:
                    try:
                        keep_connection = self.protohandler.keep_connection
                    except AttributeError:
                        keep_connection = False

                self.logger.debug(message_prefix+'Session finished')

        if isuspect > 2:
            self.logger.info(f'{message_prefix}Session finished for {isuspect-1} sessions in same connection')

    def _discard(self, message=None):
        if message is None:
            message = "internal problem - discard"

        # try to end the session gracefully, but this might cause the same exception again,
        # in case of a broken pipe for example
        try:
            self.protohandler.discard(message)
        except Exception:
            pass

    def _reject(self, message=None):
        if message is None:
            message = "internal problem - reject"

        # try to end the session gracefully, but this might cause the same exception again,
        # in case of a broken pipe for example
        try:
            self.protohandler.reject(message)
        except Exception:
            pass

    def _defer(self, message=None):
        if message is None:
            message = "internal problem - message deferred"

        # try to end the session gracefully, but this might cause the same exception again,
        # in case of a broken pipe for example
        try:
            self.protohandler.defer(message)
        except Exception:
            pass

    def trash(self, suspect, killerplugin=None):
        """copy suspect to trash if this is enabled"""
        trashdir = self.config.get('main', 'trashdir').strip()
        if trashdir == "":
            return

        if not os.path.isdir(trashdir):
            try:
                os.makedirs(trashdir)
            except OSError:
                self.logger.error(f"{suspect.id } Trashdir {trashdir} does not exist and could not be created")
                return
            self.logger.info(f'{suspect.id }Created trashdir {trashdir}')

        trashdir = self.config.get('main', 'trashdir')
        trashfilename = ''
        try:
            handle, trashfilename = tempfile.mkstemp(prefix=suspect.id, dir=trashdir)
            with os.fdopen(handle, 'w+b') as trashfile:
                trashfile.write(suspect.get_source())
            self.logger.debug(f'{suspect.id} Message stored to trash: {trashfilename}')
        except Exception as e:
            self.logger.error(f"{suspect.id} could not create file {trashfilename}: {e.__class__.__name__}: {str(e)}")

        # TODO: document main.trashlog
        if self.config.getboolean('main', 'trashlog', fallback=False):
            try:
                trashlogpath = os.path.join(trashdir, '00-fuglutrash.log')
                with open(trashlogpath, 'a') as handle:
                    # <date> <time> <from address> <to address> <plugin that said "DELETE"> <filename>
                    now = utcnow().isoformat()
                    handle.write(f'{now} {suspect.from_address} {suspect.to_address} {killerplugin} {trashfilename}')
                    handle.write("\n")
            except Exception as e:
                self.logger.error(f'{suspect.id} Could not update trash log: {e.__class__.__name__}: {str(e)}')

    async def run_plugins(self, suspect, pluglist):
        """Run scannerplugins on suspect"""
        suspect.debug(f'{suspect.id} Will run plugins: {", ".join([p.__class__.__name__ for p in pluglist])}')
        self.tracktime("Before-Plugins")
        for plugin in pluglist:
            try:
                iscoroutine = asyncio.iscoroutinefunction(plugin.examine)
                msg = f'{suspect.id} Running(async={iscoroutine}) Plugin {str(plugin)}'
                self.logger.debug(msg)
                self.set_workerstate(msg)
                suspect.debug(f'Running(async={iscoroutine}) Plugin {str(plugin)}')
                starttime = time.time()
                
                if iscoroutine:
                    ans = await plugin.run_examine(suspect)
                else:
                    ans = plugin.run_examine(suspect)
                plugintime = time.time() - starttime
                suspect.tags['scantimes'].append((plugin.section, plugintime))
                message = None
                if type(ans) is tuple:
                    result, message = ans
                else:
                    result = ans

                if result is None:
                    result = DUNNO

                suspect.tags['decisions'].append((plugin.section, result))

                if result == DUNNO:
                    suspect.debug(f'Plugin {str(plugin)} makes no final decision')
                elif result == ACCEPT:
                    suspect.debug(f'Plugin {str(plugin)} accepts the message - skipping all further tests')
                    self.logger.debug(f'{suspect.id} Plugin {str(plugin)} says: ACCEPT. Skipping all other tests')
                    self.action = ACCEPT
                    break
                elif result == DELETE:
                    suspect.debug(f'Plugin {str(plugin)} DELETES this message - no further tests')
                    self.logger.debug(f'{suspect.id} Plugin {str(plugin)} says: DELETE. Skipping all other tests')
                    self.action = DELETE
                    self.message = message
                    self.trash(suspect, str(plugin))
                    break
                elif result == REJECT:
                    suspect.debug(f'Plugin {str(plugin)} REJECTS this message - no further tests')
                    self.logger.debug(f'{suspect.id} Plugin {str(plugin)} says: REJECT. Skipping all other tests')
                    self.action = REJECT
                    self.message = message
                    break
                elif result == DEFER:
                    suspect.debug(f'Plugin {str(plugin)} DEFERS this message - no further tests')
                    self.logger.debug(f'{suspect.id} Plugin {str(plugin)} says: DEFER. Skipping all other tests')
                    self.action = DEFER
                    self.message = message
                    break
                else:
                    self.logger.error(f'{suspect.id} Plugin {str(plugin)} says invalid message action code: {result}. Using DUNNO')

            except Exception as e:
                CrashStore.store_exception()
                exc = traceback.format_exc()
                self.logger.error(f'{suspect.id} Plugin {str(plugin)} failed: {str(exc)}')
                suspect.debug(f'Plugin failed : {e} . Please check fuglu log for more details')
                ptag = suspect.get_tag("processingerrors", defaultvalue=[])
                ptag.append(f"Plugin {str(plugin)} failed: {e.__class__.__name__}: {str(e)}")
                suspect.set_tag("processingerrors", ptag)
            finally:
                self.tracktime(str(plugin), plugin=True)

    async def run_prependers(self, suspect):
        """Run prependers on suspect"""
        plugcopy = self.plugins[:]
        appcopy = self.appenders[:]

        self.tracktime("Before-Prependers")
        for plugin in self.prependers:
            try:
                iscoroutine = asyncio.iscoroutinefunction(plugin.pluginlist)
                msg = f'{suspect.id} Running(async={iscoroutine}) Prepender pluginlist {str(plugin)}'
                self.logger.debug(msg)
                self.set_workerstate(msg)
                suspect.debug(f'Running(async={iscoroutine}) Prepender pluginlist {str(plugin)}')
                starttime = time.time()
                
                if iscoroutine:
                    out_plugins = await plugin.pluginlist(suspect, plugcopy)
                else:
                    out_plugins = plugin.pluginlist(suspect, plugcopy)
                
                iscoroutine = asyncio.iscoroutinefunction(plugin.appenderlist)
                msg = f'{suspect.id} Running(async={iscoroutine}) Prepender appenderlist {str(plugin)}'
                self.logger.debug(msg)
                self.set_workerstate(msg)
                suspect.debug(f'Running(async={iscoroutine}) Prepender appenderlist {str(plugin)}')
                
                if iscoroutine:
                    out_appenders = await plugin.appenderlist(suspect, appcopy)
                else:
                    out_appenders = plugin.appenderlist(suspect, appcopy)

                plugintime = time.time() - starttime
                suspect.tags['scantimes'].append((plugin.section, plugintime))

                # Plugins
                if out_plugins is not None:
                    plugcopyset = set(plugcopy)
                    resultset = set(out_plugins)
                    removed = list(plugcopyset - resultset)
                    added = list(resultset - plugcopyset)
                    if len(removed) > 0:
                        self.logger.debug(f'{suspect.id} Prepender {str(plugin)} removed plugins: {", ".join(list(map(str, removed)))}')
                    if len(added) > 0:
                        self.logger.debug(f'{suspect.id} Prepender {str(plugin)} added plugins: {", ".join(list(map(str, added)))}')
                    plugcopy = out_plugins

                # Appenders
                if out_appenders is not None:
                    appcopyset = set(appcopy)
                    resultset = set(out_appenders)
                    removed = list(appcopyset - resultset)
                    added = list(resultset - appcopyset)
                    if len(removed) > 0:
                        self.logger.debug(f'{suspect.id} Prepender {str(plugin)} removed appender: {", ".join(list(map(str, removed)))}')
                    if len(added) > 0:
                        self.logger.debug(f'{suspect.id} Prepender {str(plugin)} added appender: {", ".join(list(map(str, added)))}')
                    appcopy = out_appenders

            except Exception as e:
                CrashStore.store_exception()
                exc = traceback.format_exc()
                self.logger.error(f'{suspect.id} Prepender plugin {str(plugin)} failed: {str(exc)}')
                ptag = suspect.get_tag("processingerrors", defaultvalue=[])
                ptag.append(f"Prepender {str(plugin)} failed: {e.__class__.__name__}: {str(e)}")
                suspect.set_tag("processingerrors", ptag)
            finally:
                self.tracktime(str(plugin), prepender=True)
            if suspect.get_tag('skip_prependers'):
                self.logger.debug(f'{suspect.id} Prepender {str(plugin)} skips all remaining prependers')
                break
        return plugcopy, appcopy

    async def run_appenders(self, suspect, finaldecision, applist):
        """Run appenders on suspect"""
        if suspect.get_tag('noappenders'):
            return

        self.tracktime("Before-Appenders")
        for plugin in applist:
            try:
                iscoroutine = asyncio.iscoroutinefunction(plugin.process)
                msg = f'{suspect.id} Running(async={iscoroutine}) Appender {str(plugin)}'
                self.logger.debug(msg)
                self.set_workerstate(msg)
                suspect.debug(f'Running(async={iscoroutine}) Appender {str(plugin)}')
                starttime = time.time()
                
                if iscoroutine:
                    await plugin.process(suspect, finaldecision)
                else:
                    plugin.process(suspect, finaldecision)
                plugintime = time.time() - starttime
                suspect.tags['scantimes'].append((plugin.section, plugintime))
            except Exception as e:
                CrashStore.store_exception()
                exc = traceback.format_exc()
                self.logger.error(f'{suspect.id} Appender plugin {str(plugin)} failed: {str(exc)}')
                ptag = suspect.get_tag("processingerrors", defaultvalue=[])
                ptag.append(f"Appender {str(plugin)} failed: {e.__class__.__name__}: {str(e)}")
                suspect.set_tag("processingerrors", ptag)
            finally:
                self.tracktime(str(plugin), appender=True)
