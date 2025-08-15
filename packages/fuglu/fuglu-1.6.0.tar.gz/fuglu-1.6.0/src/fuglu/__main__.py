#!/usr/bin/env python3
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
# main startup file

from fuglu import __version__ as FUGLU_VERSION
from fuglu.daemon import DaemonStuff
from fuglu.logtools import createPIDinfo
import logging
import logging.config
import fuglu.funkyconsole
from fuglu.bounce import Bounce
from fuglu import loghandlers
import sys
from fuglu.core import MainController, EXIT_NOTSET, EXIT_EXCEPTION, EXIT_LOGTERMERROR, sigterm
from fuglu.shared import create_filehash, FuConfigParser
import signal
import os
import optparse
import fuglu.logtools
import multiprocessing
import grp

controller = None
foreground = False
base_loglevel = "DEBUG"

theconfigfile = '/etc/fuglu/fuglu.conf'
dconfdir = '/etc/fuglu/conf.d'
theloggingfile = '/etc/fuglu/logging.conf'
thepidfile = '/var/run/fuglu.pid'

# register custom log handlers
logging.custom_handlers = loghandlers


try:
    os.getcwd()
except PermissionError:
    print('ERROR: cannot access current working dir')
    sys.exit(1)


def reloadconfig():
    """reload configuration file"""

    logger = logging.getLogger('fuglu.main.reloadconfig')
    if controller:
        if controller.threadpool is None and controller.procpool is None and controller.asyncprocpool is None:
            logger.error(f"""No process/threadpool -> This is not the main process!
                          \nNo changes will be applied...!\nSend SIGHUP to the main process!
                          \nCurrent controller object : {id(controller)}, {controller.__repr__()}""")
            return
    else:
        logger.error("No controller -> This is not the main process!\n"
                     "No changes will be applied...!\nSend SIGHUP to the main process!")
        return

    if controller.logProcessFacQueue is None and not foreground:
        logger.error("No log process in controller -> This is not the main process!\n"
                     "No changes will be applied...!\nSend SIGHUP to the main process!")
        return

    assert controller.logConfigFileUpdates is not None
    assert controller.configFileUpdates is not None

    configFileUpdates = getConfigFileUpdatesDict(theconfigfile, dconfdir)
    logConfigFileUpdates = getLogConfigFileUpdatesDict(theloggingfile)

    logfilechanged = (logConfigFileUpdates != controller.logConfigFileUpdates)
    mainconfigchanged = (configFileUpdates != controller.configFileUpdates)

    logger.info(f'Log config has changes: {logfilechanged}')
    if logfilechanged and foreground:
        logger.warning("No log-config changes applied in foreground mode.")
        controller.logConfigFileUpdates = logConfigFileUpdates
        logfilechanged = False

    logger.info(f'Main config has changes: {mainconfigchanged}')

    logger.info(f'Number of messages in logging queue: {controller.logQueue.qsize() if controller.logQueue else "none"}')

    if logfilechanged:
        # save backlog config file dict for later use
        controller.logConfigFileUpdates = logConfigFileUpdates

        logger.info("Create new log process with new configuration")
        logProcessFacQueue = controller.logProcessFacQueue
        newLogConfigure = fuglu.logtools.logConfig(logConfigFile=theloggingfile)
        logProcessFacQueue.put(newLogConfigure)


    if mainconfigchanged or not logfilechanged:
        # if logfile has not changed, reload main configuration for sure
        logger.info('Reloading configuration')

        # save back config file dict for later use
        controller.configFileUpdates = configFileUpdates
        newconfig = FuConfigParser()
        with open(theconfigfile) as cfgfp:
            newconfig.read_file(cfgfp)

        controller.setup_global()

        # load conf.d (note dconfdir can be None)
        if dconfdir and os.path.isdir(dconfdir):
            cfgfilelist = os.listdir(dconfdir)
            cfgfiles = [dconfdir + '/' + c for c in cfgfilelist if c.endswith('.conf')]
            logger.debug(f'Conffiles in {dconfdir}: {", ".join(cfgfiles)}')
            readcfgfiles = newconfig.read(cfgfiles)
            logger.debug(f'Read additional files: {readcfgfiles}')
        
        identifier = newconfig.get('main', 'identifier', fallback='no identifier given')
        logger.info(f'Reload config complete. Current configuration: {identifier}')
        controller.config = newconfig
        controller.propagate_core_defaults()

        logger.info('Reloading plugins...')
        ok = controller.load_plugins()
        if ok:
            logger.info('Plugin reload completed')
        else:
            logger.error('Plugin reload failed')

        controller.reload()


def sighup(signum, frame):
    """handle sighup to reload config"""
    reloadconfig()

def getConfigFileUpdatesDict(configfilename,dconfigFileDir):
    cfgfiles = [configfilename]
    # load conf.d
    if dconfigFileDir and os.path.isdir(dconfigFileDir):
        cfgfilelist = os.listdir(dconfigFileDir)
        cfgfiles.extend([dconfigFileDir + '/' + c for c in cfgfilelist if c.endswith('.conf')])

    hashlist = create_filehash(cfgfiles, "md5")
    configFileUpdates = dict(zip(cfgfiles, hashlist))
    return configFileUpdates

def getLogConfigFileUpdatesDict(logConfFile):
    logConfigFileUpdates = {}
    logConfigFileUpdates[logConfFile] = create_filehash([logConfFile], "md5")[0]
    return logConfigFileUpdates


debugmsg = False
logtext = []

parser = optparse.OptionParser(version=FUGLU_VERSION)
parser.add_option("--lint", action="store_true", dest="lint",
                  default=False, help="Check configuration and exit")
parser.add_option("--copylintout", dest="copylintout",
                  default=None, help="Copy Lint output to this class")
parser.add_option("--console", action="store_true", dest="console",
                  default=False, help="start an interactive console after fuglu startup")
parser.add_option("-f", "--foreground", action="store_true", dest="foreground", default=False,
                  help="start fuglu in the foreground and log to stdout, even if daemonize is enabled in the config")
parser.add_option("--pidfile", action="store", dest="pidfile",
                  help="use a different pidfile than /var/run/fuglu.pid")
parser.add_option("-c", "--config", action="store", dest="configfile",
                  help="use a different config file and disable reading from /etc/fuglu/conf.d")
parser.add_option("--logconfig", action="store", dest="logconfigfile",
                  help="use a different logging config file")
parser.add_option("--configdir", action="store", dest="configdir",
                  help="use a folder different from conf.d, enable reading even if using -c/--config option")
parser.add_option("--baseloglevel", dest="baseloglevel", default="DEBUG", choices=["DEBUG", "INFO", "ERROR"],
                  help="log-level for foreground mode and base (MIN) for all logging")

(opts, args) = parser.parse_args()
if len(args) > 0:
    print(f"Unknown option(s): {args}")
    print("")
    parser.print_help()
    sys.exit(1)

lint = opts.lint
console = opts.console
copylintout = opts.copylintout if lint else None
if copylintout:
    try:
        # get function
        objname = copylintout.rsplit(".", 1)
        objname = [f for f in objname if f.strip()]

        obj = None
        if len(objname) > 1:
            modname, objname = objname
            try:
                module = __import__(modname, fromlist=[objname])
                obj = getattr(module, objname)
            except Exception:
                obj = None
        else:
            objname = objname[0]
            try:
                obj = locals()[objname]
            except KeyError:
                try:
                    obj = globals()[objname]
                except KeyError:
                    fun = None
        if obj is None:
            raise Exception(f"Couldn't find object {copylintout}")
        else:
            copylintout = obj
    except Exception as e:
        print(e)
        copylintout = None


if opts.pidfile:
    thepidfile = opts.pidfile
    logtext.append(f"Use pidfile \"{thepidfile}\" from options")

if opts.configfile:
    theconfigfile = opts.configfile
    logtext.append(f"Use config file \"{theconfigfile}\" from options")
    theloggingfile = os.path.join(
        os.path.split(theconfigfile)[0], os.path.split(theloggingfile)[1])
    logtext.append(f"Use logging file \"{theloggingfile}\" relative to config file from options")
    # set config dir option to None in case of a custom configfile, might be set again by
    # - option in config file
    # - command line option
    dconfdir = None

config = FuConfigParser()
if not os.path.exists(theconfigfile):
    print(f"Configfile {theconfigfile} not found. Please create it by renaming the .dist file and modifying it to your needs")
    sys.exit(1)

# set configfile path to FuConfigParser so string vars
# with ${confdir} markers will replace this with path
# to main config file
config.set_configpath_from_configfile(theconfigfile)
# read main config file
with open(theconfigfile) as fp:
    readconfig = config.read_file(fp)

# set config directory if given in config file
if config.has_option('main', 'configdir'):
    configdirinput = config.get('main', 'configdir')
    # set config to input from config file if not an empty string
    if configdirinput:
        dconfdir = configdirinput
        logtext.append(f"Got config dir 'conf.d' input \"{dconfdir}\" from config file")
        if lint:
            print(f"Setting configdir by config file option to {dconfdir}")

# overwrite config directory "conf.d" by command line option
if opts.configdir:
    dconfdir = opts.configdir
    logtext.append(f"Got config dir 'conf.d' input \"{dconfdir}\" from options")
    if lint:
        print(f"Setting configdir by command line option to {dconfdir}")

# load conf.d
if dconfdir and os.path.isdir(dconfdir):
    filelist = os.listdir(dconfdir)
    configfiles = [dconfdir + '/' + c for c in filelist if c.endswith('.conf')]
    readfiles = config.read(configfiles)

# store if run in foreground mode, so it can be used in reload
foreground = opts.foreground
base_loglevel = opts.baseloglevel
logconfigfile = opts.logconfigfile

backend = config.get('performance', 'backend', fallback="thread")

daemon = DaemonStuff(thepidfile)
# we could have an empty config file
# no daemon for lint&console mode
if not lint and not console and not foreground:
    logtext.append(f"Not lint/console/foreground -> daemonize")
    if config.has_option('main', 'daemonize'):
        if config.getboolean('main', 'daemonize'):
            daemon.createDaemon()
    else:  # option not specified -> default to run daemon
        daemon.createDaemon()


def pick_group(groups):
    for group in groups:
        try:
            grp.getgrnam(group)
            return group
        except KeyError:
            continue

# drop privileges
try:
    running_user = config.get('main', 'user')
    running_group = pick_group(config.getlist('main', 'group'))
    logtext.append(f"Drop privileges: user={running_user}, group={running_group}")
except Exception:
    running_user = 'nobody'
    running_group = pick_group(['nobody', 'nogroup'])
    logtext.append(f"Drop privileges: fallback to user={running_user}, group={running_group}")

priv_drop_ok = False
try:
    daemon.drop_privs(running_user, running_group)
    priv_drop_ok = True
    logtext.append(f"Successfully dropped privileges")
except Exception as e:
    logtext.append(f"Could not drop provileges: {str(e)}")
    err = sys.exc_info()[1]
    print(f"Could not drop privileges to {running_user}/{running_group} : {str(err)}")


# --
# set up logging
# --

# all threads/processes write to the logQueue which
# will be handled by a separate process
if backend not in ['thread', 'process', 'asyncprocess'] or foreground:
    # no need for an advanced multiprocessing logging structure
    logtext.append(f"Loggin setup - no workerpool or foreground mode and therefore no need for multiprocessing logging")
    logQueue = None
    logFactoryQueue = None
else:
    logtext.append(f"Loggin setup - multiprcessing setup with logging queue")
    logQueue = multiprocessing.Queue(-1)
    logFactoryQueue = multiprocessing.Queue(-1)

oldout = None
lintout = None
if copylintout:
    import io
    oldout = (sys.stdout, sys.stderr)
    lintout = io.StringIO()
    #sys.stdout = lintout
    #sys.stderr = lintout


    class Logger:
        def __init__(self, stdout_err, lout):
            self.terminal = sys.stdout
            self.log = lintout

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)


    sys.stdout = Logger(stdout_err=sys.stdout, lout=lintout)
    sys.stderr = Logger(stdout_err=sys.stderr, lout=lintout)

# set up a process which handles logging messages
fc = None
if lint:
    fc = fuglu.funkyconsole.FunkyConsole()
    print(fc.strcolor("Fuglu", "yellow"), end=' ')
    print(fc.strcolor(FUGLU_VERSION, "green"))
    print("----------", fc.strcolor("LINT MODE", (fc.MODE["blink"], fc.FG["magenta"])), "----------")

    logConfigure = fuglu.logtools.logConfig(lint=True)

elif logconfigfile:
    logConfigure = fuglu.logtools.logConfig(logConfigFile=logconfigfile)
    logtext.append(f"Load logging from config file \"{logconfigfile}\"")
elif foreground:
    logConfigure = fuglu.logtools.logConfig(foreground=True, level=base_loglevel)
    logtext.append(f"Setup foreground mode with base loglevel: {base_loglevel}")
else:
    logConfigure = fuglu.logtools.logConfig(logConfigFile=theloggingfile)
    logtext.append(f"Load logging from logging file \"{theloggingfile}\"")

logProcessFactory = None
if logFactoryQueue and logQueue:
    logtext.append(f"Setup logFactoryQueue and logQueue")
    # --
    # start process handling logging queue
    # --
    logProcessFactory = multiprocessing.Process(target=fuglu.logtools.logFactoryProcess,
                                                args=(logFactoryQueue, logQueue))
    logProcessFactory.start()

    # now create a log - listener process
    logFactoryQueue.put(logConfigure)

    # setup this main thread to send messages to the log queue
    # (which is handled by the logger process created by the logProcessFactory)
    fuglu.logtools.client_configurer(logQueue, level=base_loglevel)
else:
    logtext.append(f"configure logging")
    # no multiprocessing logging, just configure process
    logConfigure.configure()

# ===                      === #
# = Now logging is available = #
# ===                      === #
baselogger = logging.getLogger()
mainlogger = logging.getLogger('fuglu.main')
mainlogger.info(f"FuGLU Version {FUGLU_VERSION} starting up")
baselogger.debug(f"current working dir: {os.getcwd()}")
baselogger.debug(f"logProcessFactory: {logProcessFactory}")
baselogger.debug(f"logFactoryQueue: {logFactoryQueue}")
baselogger.debug(f"logQueue: {logQueue}")
baselogger.debug(f"Stored setup loglines (start)")
baselogger.debug(f"Main process info: {createPIDinfo()}")
for logline in logtext:
    baselogger.debug(logline)
baselogger.debug(f"Stored setup loglines (end)")

exitstatus = EXIT_NOTSET
try:
    # instantiate the MainController and load default configuration
    controller = MainController(config,logQueue,logFactoryQueue)
    controller.configFileUpdates = getConfigFileUpdatesDict(theconfigfile,dconfdir)
    controller.logConfigFileUpdates = getLogConfigFileUpdatesDict(theloggingfile)
    controller.propagate_core_defaults()
    controller.setup_global()

    if lint:
        exitstatus = controller.lint()
        # the controller doesn't know about the logging.conf, so we lint this here
        print("\nChecking Bounce configuration:")
        b = Bounce(config = config)
        if not b.lint():
            exitstatus = EXIT_EXCEPTION
        print("")
        if priv_drop_ok:
            if foreground and not logconfigfile:
                print("Not checking logging configuration in foreground mode with log configfile given...")
            else:
                print("Checking logging configuration....")
                try:
                    logging.config.fileConfig(logconfigfile if logconfigfile else theloggingfile)
                    logging.info("fuglu --lint log configuration test")
                    print(fc.strcolor("OK", "green"))
                except Exception as e:
                    print(f"Logging configuration check failed: {e.__class__.__name__}: {str(e)}")
                    print("This may prevent the daemon from starting up.")
                    print(f"Make sure the log directory exists and is writable by user '{running_user}' ")
                    print(fc.strcolor("NOT OK", "red"))
        else:
            print(fc.strcolor("WARNING:", "yellow"))
            print(f"Skipping logging configuration check because I could not switch to user '{running_user}' earlier.")
            print("please re-run fuglu --lint as privileged user")
            print("(problems in the logging configuration could prevent the fuglu daemon from starting up)")

    else:
        signal.signal(signal.SIGHUP, sighup)
        signal.signal(signal.SIGTERM, sigterm)
        if console:
            controller.debugconsole = True
        exitstatus = controller.startup()
except Exception as e:
    baselogger.exception(e)
    baselogger.error(f'Exception caught: {e.__class__.__name__}: {str(e)}')
    exitstatus = EXIT_EXCEPTION
finally:
    #---
    # stop logger factory & process
    #---
    if not lint and not copylintout:
        mainlogger.info(f"Shutdown complete (FuGLU Version {FUGLU_VERSION})")

    if logQueue and logFactoryQueue and logProcessFactory:
        baselogger.info("Stop logging framework -> Goodbye")
        try:
            baselogger.debug("Send Poison pill to logFactoryQueue")
            logFactoryQueue.put_nowait(None)
            logProcessFactory.join(120)
        except Exception as e:
            logProcessFactory.terminate()
            exitstatus = EXIT_LOGTERMERROR

    if oldout:
        sys.stdout, sys.stderr = oldout

    if copylintout:
        output = lintout.getvalue()
        try:
            copylintout(config=config).print(returncode=exitstatus, message=output)
        except Exception as e:
            print(str(e))

    if lint and fc:
        print("")
        if exitstatus:
            print(fc.strcolor("----------------------", "red"))
            print(fc.strcolor('-', 'red'), "Lint status: ", fc.strcolor("FAIL", "red"), fc.strcolor('-', 'red'))
            print(fc.strcolor("----------------------", "red"))
        else:
            print(fc.strcolor("----------------------", "green"))
            print(fc.strcolor('-', 'green'), "Lint status: ", fc.strcolor("OK  ", "green"), fc.strcolor('-', 'green'))
            print(fc.strcolor("----------------------", "green"))
    sys.exit(exitstatus)


