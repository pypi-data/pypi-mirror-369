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
#
from queue import Empty as EmptyQueue
import multiprocessing
import multiprocessing.queues
import signal
import time
import logging
import traceback
import threading
import sys
import os
import asyncio
import typing as tp
import functools
try:
    import aioprocessing
except ImportError:
    from unittest.mock import MagicMock
    aioprocessing = MagicMock()


from concurrent.futures import ThreadPoolExecutor

try:
    import uvloop
except ImportError:
    uvloop = None

import importlib
try:
    import objgraph
    OBJGRAPH_EXTENSION_ENABLED = True
except ImportError:
    OBJGRAPH_EXTENSION_ENABLED = False

import fuglu.core
import fuglu.logtools as logtools
from fuglu.protocolbase import compress_task, uncompress_task
from fuglu.stats import Statskeeper, StatDelta
from fuglu.addrcheck import Addrcheck
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from fuglu.debug import ControlServer


class ProcManager(object):
    def __init__(self, logQueue, numprocs=None, queuesize=100, config=None):
        self._child_id_counter = 0
        self._logQueue = logQueue
        self.manager = multiprocessing.Manager()
        self.shared_state = self._init_shared_state()
        self.config = config
        self.numprocs = numprocs
        self.workers = []
        self.queuesize = queuesize

        # This can only work if aioprocessing module is installed
        assert aioprocessing is not None

        self.tasks = aioprocessing.AioQueue(queuesize)
        self.child_to_server_messages = multiprocessing.Queue()

        self.logger = logging.getLogger('%s.procpool' % __package__)
        self._stayalive = True
        self.name = 'ProcessPool'
        self.message_listener = MessageListener(self.child_to_server_messages)
        self.start()

    def _init_shared_state(self):
        shared_state = self.manager.dict()
        return shared_state

    @property
    def stayalive(self):
        return self._stayalive

    @stayalive.setter
    def stayalive(self, value):
        # procpool is shut down -> send poison pill to workers
        if self._stayalive and not value:
            self._stayalive = False
            self._send_poison_pills()
        self._stayalive = value

    def _send_poison_pills(self):
        """flood the queue with poison pills to tell all workers to shut down"""
        async_coroutines = self.config.getint('performance', 'async_coroutines', fallback=1)
        try:
            for _ in range(min(len(self.workers)*async_coroutines, self.queuesize)):
                # tasks queue is FIFO queue. As long as nothing is added to the queue
                # anymore the poison pills will be the last elements taken from the queue
                self.tasks.put_nowait(None)
        except Exception:
            pass

    def add_task(self, session):
        if self._stayalive:
            self.tasks.put(session)

    def add_task_from_socket(self, sock, handler_modulename, handler_classname, port):
        """
        Consistent interface with procpool. Add a new task to the queu
        given the socket to receive the message.

        Args:
            sock (socket): socket to receive the message
            handler_modulename (str): module name of handler
            handler_classname (str): class name of handler
            port (int): original incoming port
        """
        try:
            task = compress_task(sock, handler_modulename, handler_classname, port)
            self.add_task(task)
        except Exception as e:
            self.logger.error(f"Exception happened trying to add task to queue: {e.__class__.__name__}: {str(e)}")
            self.logger.exception(e)

    def _create_worker(self):
        self._child_id_counter += 1
        worker_name = "Worker-%s" % self._child_id_counter
        worker = aioprocessing.AioProcess(target=fuglu_async_process_worker, name=worker_name,
                                          args=(self.tasks, self.config, self.shared_state,
                                                self.child_to_server_messages, self._logQueue)
                                          )
        return worker

    def start(self):
        for i in range(self.numprocs):
            worker = self._create_worker()
            worker.start()
            self.workers.append(worker)

        # Start the child-to-parent message listener
        self.message_listener.start()

    def shutdown(self, newmanager=None):
        # setting stayalive equal to False
        # will send poison pills to all processors
        self.logger.debug("Shutdown procpool -> send poison pills")
        self.stayalive = False

        # add another poison pill for the ProcManager itself removing tasks...
        self.logger.debug("Another poison pill for the ProcManager itself")
        try:
            self.tasks.put_nowait(None)
        except Exception:
            pass

        if newmanager:
            # new manager available. Transfer tasks
            # to new manager
            self.logger.debug("Pass queue items to new manager")
            countmessages = 0
            while True:
                task = self.tasks.get()
                if task is None:  # poison pill
                    break
                newmanager.add_task(task)
                countmessages += 1
            self.logger.info("Moved %u messages to queue of new manager" % countmessages)
        else:
            self.logger.debug("Get rid of items in queue")
            return_message = "Temporarily unavailable... Please try again later."
            mark_defer_counter = 0
            while True:
                # Don't wait
                try:
                    task = self.tasks.get(False)
                except EmptyQueue:
                    self.logger.warning("Queue is empty! Take a poison pill!")
                    task = None
                if task is None:  # poison pill
                    self.logger.debug("Got poison pill")
                    break
                self.logger.debug("Got task, mark as defer")
                mark_defer_counter += 1
                sock, handler_modulename, handler_classname, port = uncompress_task(task)
                handler_class = getattr(importlib.import_module(handler_modulename), handler_classname)
                handler_instance = handler_class(sock, self.config)
                handler_instance.defer(return_message)
            if mark_defer_counter > 0:
                self.logger.info("Marked %s messages as '%s' to close queue" % (mark_defer_counter, return_message))

        # join the workers
        try:
            join_timeout = self.config.getfloat('performance', 'join_timeout')
        except Exception:
            if newmanager:
                join_timeout = 120.0
            else:
                # if there's no new manager then
                # we don't wait, just kill
                join_timeout = 1

        self.logger.debug("Join workers")
        tstart = time.time()
        for worker in self.workers:
            tpassed = time.time()-tstart
            remaining_timeout = max(join_timeout - tpassed, 0.05)
            worker.join(int(remaining_timeout))
            if worker.is_alive():
                self.logger.warning("Could not stop worker %s (pid: %u) with given timeout of %f (%f)"
                                    % (worker, worker.pid, join_timeout, remaining_timeout))
                worker.terminate()
                time.sleep(0.1)
                if worker.is_alive():
                    self.logger.warning("Could not stop worker %s (pid: %u) with SIGTERM, use SIGKILL"
                                        % (worker, worker.pid))
                    try:
                        worker.kill()
                    except AttributeError:
                        os.kill(worker.pid, signal.SIGKILL)

        self.logger.debug("Join message listener")
        self.message_listener.stayalive = False
        # put poison pill into queue otherwise the process will not stop
        # since "stayalive" is only checked after receiving a message from the queue
        self.child_to_server_messages.put_nowait(None)
        self.message_listener.join(join_timeout)
        if self.message_listener.is_alive():
            self.logger.error("Could not stop message_listener %s with given timeout of %f, just go ahead..."
                              % (self.message_listener.name, join_timeout))

        self.logger.debug("Close tasks queue")
        self.tasks.close()

        self.child_to_server_messages.close()
        self.logger.debug("Shutdown multiprocessing manager")
        self.manager.shutdown()
        self.logger.debug("done...")


class MessageListener(threading.Thread):
    def __init__(self, message_queue):
        super().__init__()
        self.name = "Process Message Listener"
        self.message_queue = message_queue
        self.stayalive = True
        self.statskeeper = Statskeeper()
        self.daemon = True

    def run(self):
        while self.stayalive:
            message = self.message_queue.get()
            if message is None:
                break
            event_type = message['event_type']
            if event_type == 'statsdelta':  # increase statistics counters
                try:
                    delta = StatDelta(**message)
                    self.statskeeper.increase_counter_values(delta)
                except Exception:
                    print(traceback.format_exc())


lock_get_event_loop = threading.Lock()
def get_event_loop(logid: str = None) -> asyncio.AbstractEventLoop:
    """
    Central method for retrieving current event loop.
    If no event loop is running, a fresh one will be initialised.
    If uvloop is available it will be preferred over native asyncio
    """
    def _logid(msg:str) -> str:
        if logid is not None:
            msg = f'{logid} {msg}'
        return msg

    pidinfo = logtools.createPIDinfo()
    logger = logging.getLogger()

    with lock_get_event_loop:
        policy = asyncio.get_event_loop_policy()
        if uvloop and not isinstance(policy, uvloop.EventLoopPolicy):
            logger.debug(_logid(f"{pidinfo}: Set uvloop as event loop!"))
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            policy = asyncio.get_event_loop_policy()
        elif not uvloop:
            logger.debug(_logid(f"{pidinfo}: use asyncio as event loop!"))
        try:
            loop = policy.get_event_loop()
            if loop.is_closed():
                logger.debug(_logid(f"{pidinfo}: event loop is closed!"))
                raise RuntimeError('existing event loop is closed')
        except RuntimeError as e:
            logger.debug(_logid(f"{pidinfo}: create new event loop due to {str(e)}"))
            loop = policy.new_event_loop()
            asyncio.set_event_loop(loop)
    return loop


async def mp_queue_wait(mp_q: multiprocessing.Queue, executor=None):
    """Helper routine to combine waiting for element in multiprocessing queue with asyncio"""
    try:
        loop = get_event_loop()
        if executor:
            result = await loop.run_in_executor(executor, mp_q.get)
        else:
            with ThreadPoolExecutor(max_workers=1) as pool:
                result = await loop.run_in_executor(pool, mp_q.get)
    except Exception as ex:
        result = ex
    return result


def raise_keyboardinterrupt(*args, **kwargs):
    logging.getLogger().debug(f"{logtools.createPIDinfo()}: raise KeyboardInterrupt")
    raise KeyboardInterrupt("SIGALRM received!")


def fuglu_async_process_worker(queue, config, shared_state, child_to_server_messages, logQueue):
    """Multiprocessing worker handling requests async"""

    signal.signal(signal.SIGHUP, signal.SIG_IGN)

    logtools.client_configurer(logQueue)
    logging.basicConfig(level=logging.DEBUG)
    pidinfo = logtools.createPIDinfo()
    async_coroutines = config.getint('performance', 'async_coroutines', fallback=1)

    async_threadpoolworkers = config.getint('performance', 'async_threadpool', fallback=None)
    if not async_threadpoolworkers:
        async_threadpoolworkers = max(1, int(async_coroutines/2))
    async_prepare_timeout = config.getfloat('performance', 'async_prepare_timeout', fallback=None)

    workerstate = WorkerStateWrapper(shared_state, 'loading configuration', async_coroutines=async_coroutines)
    logger = logging.getLogger('fuglu.process.%s(%u)' % (workerstate.process.name, workerstate.process.pid))
    logger.debug(f"{pidinfo}: New worker, coroutines={async_coroutines} with threadpool{async_threadpoolworkers}")
    logger.debug(f"{pidinfo}: async timeouts: "
                 f"coroutines={async_coroutines}, "
                 f"threadworkers={async_threadpoolworkers}, "
                 f"preparetimeout={async_prepare_timeout}")

    try:
        logtimings = config.getboolean('main', 'scantimelogger', False)
    except Exception:
        logtimings = False

    # load config and plugins
    logger.debug(f"{pidinfo}: Create MainController")
    controller = fuglu.core.MainController(config, logQueue=logQueue, nolog=True)
    controller.setup_global()
    controller.load_extensions()
    controller.load_plugins()

    # control server
    # if it's a socket, add id
    cport = config.get('main', 'controlport')
    if cport is None:
        cport = "/tmp/fuglu_control.sock"
    if not isinstance(cport, int):
        pid = os.getpid()
        if pid:
            cport = f"{cport}.{pid}"
            logger.info(f"{pidinfo}: Creating processor-local control server with socket: {cport}")
            control = ControlServer(controller, address=config.get('main', 'bindaddress'), port=cport)
            ctrl_server_thread = threading.Thread(name='Control server', target=control.serve, args=())
            ctrl_server_thread.daemon = True
            ctrl_server_thread.start()
            controller.controlserver = control
    else:
        logger.debug(f"{pidinfo}: Not creating processor-local control server because socket is int: {cport}")

    # forward statistics counters to parent process
    stats = Statskeeper()
    stats.stat_listener_callback.append(lambda event: child_to_server_messages.put(event.as_message()))

    logger.debug(f"{pidinfo}: Enter service loop...")

    loop = None
    try:
        loop = get_event_loop()
        if not uvloop and async_coroutines > 5:
            logger.warning(f"{pidinfo}: More than 5 coroutines only seems to have problems with aioredis.\n"
                           "-> reduced to 5\n"
                           "-> install module uvloop to use more coroutines per processor")

        loop.add_signal_handler(signal.SIGHUP, signal.SIG_IGN)
        loop.add_signal_handler(signal.SIGTERM, raise_keyboardinterrupt)

        # create pool here because we only want one tread waiting for the queue

        with ThreadPoolExecutor(max_workers=async_threadpoolworkers) as pool:
            # create worker coroutines for async loop
            asworkers = [fuglu_async_process_worker_main(queue, workerstate, logger, controller, i, logtimings, pool,
                                                         async_prepare_timeout) for i in range(1, 1+async_coroutines)]
            logger.debug(f"{pidinfo}: We put {len(asworkers)} into the loop...")
            if sys.version_info > (3, 10):
                # loop parameter has been removed for python-3.10
                loop.run_until_complete(asyncio.gather(*asworkers, return_exceptions=True))
            else:
                loop.run_until_complete(asyncio.gather(*asworkers, loop=loop))
            logger.debug(f"{pidinfo}: Gathered result...")
    except KeyboardInterrupt:
        workerstate.workerstate = 'ended (keyboard interrupt)'
        logger.debug(f"{pidinfo}: Keyboard interrupt")
    except Exception as e:
        logger.error(f"{pidinfo}: Exception in worker process: {str(e)}", exc_info=e)
        workerstate.workerstate = 'crashed'
    finally:
        # this process will not put any object in queue
        if loop:
            logger.debug(f"{pidinfo}: Stop async event loop: {loop.is_running()}")
            if loop.is_running():
                loop.stop()
                logger.debug("-> stopped")
            logger.debug(f"Close async event loop: {not loop.is_closed()}")
            if not loop.is_closed():
                loop.close()
                logger.debug("-> closed")
            logger.debug(f"{pidinfo}: Async event loop stopped & closed")
        logger.debug(f"{pidinfo}: Close multiprocessing queue")
        queue.close()
        try:
            logger.debug(f"{pidinfo}: Multiprocessing queue closed, shutdown processor-local controller")
        except BrokenPipeError:
            pass
        controller.shutdown()
        try:
            logger.debug(f"{pidinfo}: Processor-local controller closed")
        except BrokenPipeError:
            pass

        logger.debug(f"{pidinfo}: async proc worker finished & complete...")


def prepare_session_task_reader(asyncid: int, workerstate, logger, task, loop):
    """First part for preparing session: uncompress task & create async reader"""
    workerstate.set_workerstate('starting scan session', id=asyncid)
    logger.debug(f"{logtools.createPIDinfo()}({asyncid}): Child process starting scan session")

    sock, handler_modulename, handler_classname, port = uncompress_task(task)

    assert sm.MilterHandler.__name__ == handler_classname, \
        f"{sm.MilterHandler.__name__} != {handler_classname} => asyncprocpool only works for milter {sm.MilterHandler.__name__} != {handler_classname}!!!"

    reader = asyncio.StreamReader(loop=loop)
    protocol = asyncio.StreamReaderProtocol(reader, loop=loop)
    return sock, handler_modulename, handler_classname, port, reader, protocol


def prepare_session_writer_handler(asyncid: int, workerstate, logger, controller,
                                   logtimings: bool, pool, transport, protocol, reader, loop, port):
    """Second part for preparing session: create async writer and Milterhandler/-session"""

    writer = asyncio.StreamWriter(transport, protocol, reader, loop)

    logger.debug(
        f"{logtools.createPIDinfo()}({asyncid}): Extracted reader/writer -> create MilterHandler & MilterSession")
    # create milter handler
    mhand = asm.MilterHandler(controller.config,
                              controller.prependers,
                              controller.plugins,
                              controller.appenders,
                              port,
                              controller.milterdict,
                              workerstate=workerstate,
                              asyncid=asyncid,
                              enable=logtimings,
                              pool=pool)

    # create milter session, passing handler
    msess = asm.MilterSession(reader, writer, controller.config, options=mhand.sess_options, mhandler=mhand)
    return writer, mhand, msess


async def fuglu_async_process_worker_main(queue: aioprocessing.AioQueue, workerstate, logger, controller, asyncid, logtimings, pool, async_prepare_timeout):
    # define queue type here to prevent an error if aioprocessing module is not present
    logger.info(f"{logtools.createPIDinfo()}({asyncid}): Child asworker process ready")
    while True:
        try:
            workerstate.set_workerstate('waiting for task', id=asyncid)
            logger.debug(f"{logtools.createPIDinfo()}({asyncid}): Child process waiting for task")
            task = await queue.coro_get()

            if task is None:  # poison pill
                logger.debug(f"{logtools.createPIDinfo()}({asyncid}): Child process received poison pill - shut down")
                try:
                    # it might be possible it does not work to properly set the workerstate
                    # since this is a shared variable -> prevent exceptions
                    workerstate.set_workerstate('ended (poison pill)', id=asyncid)
                except Exception as e:
                    logger.debug(f"Exception setting workstate while getting poison pill due to {e.__class__.__name__}: {str(e)}")
                    logger.exception(e)
                return

            loop: asyncio.AbstractEventLoop = get_event_loop(f'asyncid={asyncid}')
            if pool:
                logger.debug(f"Prepare session (reader, timeout={async_prepare_timeout}) using executor from pool")
                future = loop.run_in_executor(pool,
                                              functools.partial(prepare_session_task_reader,
                                                                asyncid=asyncid,
                                                                workerstate=workerstate,
                                                                logger=logger,
                                                                task=task,
                                                                loop=loop
                                                                )
                                              )
                if async_prepare_timeout:
                    sock, handler_modulename, handler_classname, port, reader, protocol \
                        = await asyncio.wait_for(future, timeout=async_prepare_timeout)
                else:
                    sock, handler_modulename, handler_classname, port, reader, protocol \
                        = await future
            else:
                logger.debug("Prepare session (reader) directly")
                sock, handler_modulename, handler_classname, port, reader, protocol \
                    = prepare_session_task_reader(asyncid, workerstate, logger, task, loop)

            future = loop.create_connection(lambda p=protocol: protocol, sock=sock)

            logger.debug(f"Prepare session (connection, timeout={async_prepare_timeout})")
            if async_prepare_timeout:
                transport, _ = await asyncio.wait_for(future, timeout=async_prepare_timeout)
            else:
                transport, _ = await future

            logger.debug(f"{logtools.createPIDinfo()}({asyncid}): Extracted transport & protocol")

            if pool:
                logger.debug(f"Prepare session (objects, timeout={async_prepare_timeout}) using executor from pool")
                future = loop.run_in_executor(pool,
                                              functools.partial(prepare_session_writer_handler,
                                                                asyncid=asyncid,
                                                                workerstate=workerstate,
                                                                logger=logger,
                                                                controller=controller,
                                                                logtimings=logtimings,
                                                                pool=pool,
                                                                transport=transport,
                                                                protocol=protocol,
                                                                reader=reader,
                                                                loop=loop,
                                                                port=port
                                                                )
                                              )

                if async_prepare_timeout:
                    writer, mhand, msess = await asyncio.wait_for(future, timeout=async_prepare_timeout)
                else:
                    writer, mhand, msess = await future
            else:
                logger.debug("Prepare session (objects) directly")
                writer, mhand, msess = prepare_session_writer_handler(asyncid=asyncid, workerstate=workerstate,
                                                                      logger=logger, controller=controller,
                                                                      logtimings=logtimings, pool=pool,
                                                                      transport=transport, protocol=protocol,
                                                                      reader=reader, loop=loop, port=port)

            # handle session
            workerstate.set_workerstate(f'{msess.id} Handle scan session...', id=asyncid)
            logger.debug(f"{logtools.createPIDinfo()}({asyncid}): Handle scan session {msess.id}")
            await msess.handlesession()
            logger.debug(f"{logtools.createPIDinfo()}({asyncid}): Finished handling session {msess.id}...")

            del reader
            del protocol
            del transport
            del writer
            del sock
            del handler_modulename
            del handler_classname
            del port
            del mhand
            msess._MACMAP.clear()
            del msess
        except KeyboardInterrupt:
            logger.error(f"{logtools.createPIDinfo()}({asyncid}): Got Keyboard Interrupt -> leaving while - loop")
            return
        except OSError as e:
            logger.warning(f"{logtools.createPIDinfo()}({asyncid}): Got OSError {str(e)}, continue...")
            #
            # This error happens from time to time, not sure why, maybe if connection gets killed on the outside
            # by postfix. Traceback example:
            #
            # Traceback (most recent call last):
            #   File "/fuglu/fuglu/asyncprocpool.py", line 448, in fuglu_async_process_worker_main
            #     sock, handler_modulename, handler_classname, port = uncompress_task(task)
            #   File "/fuglu/fuglu/protocolbase.py", line 220, in uncompress_task
            #     sock = pickle.loads(pickled_socket)
            #   File "/usr/local/lib/python3.9/multiprocessing/reduction.py", line 246, in _rebuild_socket
            #     fd = df.detach()
            #   File "/usr/local/lib/python3.9/multiprocessing/resource_sharer.py", line 58, in detach
            #     return reduction.recv_handle(conn)
            #   File "/usr/local/lib/python3.9/multiprocessing/reduction.py", line 188, in recv_handle
            #     with socket.fromfd(conn.fileno(), socket.AF_UNIX, socket.SOCK_STREAM) as s:
            #   File "/usr/local/lib/python3.9/socket.py", line 545, in fromfd
            #     return socket(family, type, proto, nfd)
            #   File "/usr/local/lib/python3.9/socket.py", line 232, in __init__
            #     _socket.socket.__init__(self, family, type, proto, fileno)
            # OSError: [Errno 9] Bad file descriptor
        except asyncio.TimeoutError as e:
            logger.error(f"{logtools.createPIDinfo()}({asyncid}): Async-Timeout {str(e)}", exc_info=e)
        except Exception as e:
            logger.error(f"{logtools.createPIDinfo()}({asyncid}): Exception {str(e)}", exc_info=e)


def debug_procpoolworkermemory(logger, config):
    """
    Debug memory usage using the objgraph library, eventually
    write graphs to file in tmp directory

    Args:
        logger (logging.Logger): logger to log into
        config (RawConfigParser): configuration used for temporary file dir

    """
    # now check what remains

    # can be set to true for debugging
    # -> remaining objects will be written to the dot files in the tmp folder
    # -> use "xdot" to visualise the file which contains the objects referencing the corresponding
    #    object instance and preventing direct deallocation because of the reference count
    writedebuggraphs = False

    suspectobjects = objgraph.by_type('Suspect')
    if len(suspectobjects) > 0:
        if writedebuggraphs:
            objgraph.show_backrefs(suspectobjects[-1], max_depth=5, refcounts=True,
                                   filename=os.path.join(config.get('main', 'tempdir'), 'suspects.dot'))
        logger.info("Refcounts on last subject: %u" % sys.getrefcount(suspectobjects[-1]))
    mailattachmentobjects = objgraph.by_type('Mailattachment')
    if len(mailattachmentobjects) > 0:
        if writedebuggraphs:
            objgraph.show_backrefs(mailattachmentobjects[-1], max_depth=5, refcounts=True,
                                   filename=os.path.join(config.get('main', 'tempdir'),
                                                         'mailattachments.dot'))
        logger.info("Refcounts on last mailattachment: %u" % sys.getrefcount(mailattachmentobjects[-1]))
    mailattachmentmanagerobjects = objgraph.by_type('Mailattachment_mgr')
    if len(mailattachmentmanagerobjects) > 0:
        if writedebuggraphs:
            objgraph.show_backrefs(mailattachmentmanagerobjects[-1], max_depth=5, refcounts=True,
                                   filename=os.path.join(config.get('main', 'tempdir'),
                                                         'mailattachmentsmgr.dot'))
        logger.info("Refcounts on last mailattachmentmgr: %u"
                    % sys.getrefcount(mailattachmentmanagerobjects[-1]))
    allobjects = suspectobjects + mailattachmentobjects + mailattachmentmanagerobjects
    if len(allobjects) > 0:
        logger.error('objects in memory: Suspect: %u, MailAttachments: %u, MailAttachment_mgr: %u'
                     % (len(suspectobjects), len(mailattachmentobjects), len(mailattachmentmanagerobjects)))
    else:
        logger.debug('objects in memory: Suspect: %u, MailAttachments: %u, MailAttachment_mrt: %u'
                     % (len(suspectobjects), len(mailattachmentobjects), len(mailattachmentmanagerobjects)))
    del suspectobjects
    del mailattachmentobjects
    del mailattachmentmanagerobjects


class WorkerStateWrapper(object):
    def __init__(self, shared_state_dict, initial_state='created', process=None, async_coroutines: int = 0):
        self.shared_state_dict = shared_state_dict
        self.process = process
        self.async_coroutines = async_coroutines if async_coroutines else 1
        self._state = [initial_state] * self.async_coroutines

        if not process:
            self.process = multiprocessing.current_process()

        self._publish_state()

    def _publish_state(self, asyncid: int = 0):
        try:
            if self.process.name not in self.shared_state_dict:
                self.shared_state_dict[self.process.name] = list(self._state)
            if asyncid:
                ind = asyncid - 1
                self.shared_state_dict[self.process.name][ind] = self._state[ind]
            else:
                self.shared_state_dict[self.process.name] = list(self._state)
        except (EOFError, ConnectionResetError, BrokenPipeError): # also: OSError?
            pass

    @property
    def workerstate(self):
        return self._state[0]

    @workerstate.setter
    def workerstate(self, value):
        self._state = [value]*self.async_coroutines
        self._publish_state()

    def set_workerstate(self, value: str, id: tp.Optional[int] = None):
        if id:
            self._state[id-1] = value
            self._publish_state()
        else:
            self.workerstate = value

    def get_workerstates(self) -> tp.List[str]:
        return self._state
