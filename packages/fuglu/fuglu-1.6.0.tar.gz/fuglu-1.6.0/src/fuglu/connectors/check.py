# -*- coding: utf-8 -*-
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
import socket
import random
import logging
from fuglu.shared import Suspect, fold_header
from fuglu.stringencode import force_uString


class HealthCheckSuspect(Suspect):
    def __init__(self, *args, **kwargs):
        # try to initialise original suspect but don't fail on any error
        try:
            super().__init__(*args, **kwargs)
        except Exception as e:
            pass

    def _log_incoming_basics(self, *args, **kwargs):
        # disable basic logging line during healtchcheck checking suspect
        pass


def _connect(host, port, timeout):
    """Socket connect for healch checks"""

    logger = logging.getLogger("fuglu.check._connect")

    ipvers = socket.AF_INET
    if ':' in host:
        ipvers = socket.AF_INET6
    s = socket.socket(ipvers, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((host, port),)
    sockfile = s.makefile('rwb')
    banner = str(sockfile.readline())
    logger.debug(f"Banner: {banner}")
    return s, sockfile


def check_fuglu_netcat(host: str = '127.0.0.1', port: int = 10125, timeout: int = 5) -> int:
    """Connect to fuglu and run healthcheck on SMTP connector"""

    logger = logging.getLogger("fuglu.check.check_fuglu_netcat")

    try:
        logger.debug("Open connection")
        s, sockfile = _connect(host, port, timeout)

        # --                        -- #
        # - prepend header for FUGLU - #
        # --                        -- #

        # start marker
        prepend_identifier = str(random.randint(1, 999))
        add_headers = [("X-DATA-PREPEND-START", prepend_identifier)]
        add_headers.append(("X-HEALTHCHECK", "true"))
        add_headers.append(("X-DATA-PREPEND-END", prepend_identifier))

        headerlines = b""
        for key, value in add_headers:
            # convert inputs if needed
            u_key = str(key)
            u_value = str(value)
            hdr = fold_header(u_key, u_value)
            headerlines += hdr.encode()

        logger.debug("Send headerlines...")
        sockfile.write(headerlines)
        sockfile.flush()
        logger.debug("Sent, now disable writing to socket")
        try:
            s.shutdown(socket.SHUT_WR)
        except (OSError, socket.error):
            pass
        logger.debug("Wait for response and parse...")
        reply = force_uString(sockfile.read()).strip()
        logger.info(f"Got reply: {reply}")
        if reply == "DUNNO: healthcheck":
            return 0
    except Exception as e:
        logger.error(str(e))

    return 1


def check_fuglu_smtp(host: str = '127.0.0.1', port: int = 10125, timeout: int = 5) -> int:
    """Connect to fuglu and run healthcheck on SMTP connector"""

    logger = logging.getLogger("fuglu.check.check_fuglu_smtp")

    try:
        logger.debug("Open connection")
        s, sockfile = _connect(host, port, timeout)

        logger.debug("Send healthcheck...")
        sockfile.write(b"HCHK\r\n")
        sockfile.flush()

        logger.debug("Sent, now disable writing to socket")
        try:
            s.shutdown(socket.SHUT_WR)
        except (OSError, socket.error):
            pass

        logger.debug("Wait for response and parse...")
        reply = force_uString(sockfile.read()).strip()
        logger.debug(f"Got reply: {reply}")
        if reply == "250 healthcheck":
            return 0
    except Exception as e:
        logger.error(str(e))

    return 1


def check_fuglu_asmilter(host: str = '127.0.0.1', port: int = 10125, timeout: int = 5) -> int:
    """Connect to fuglu and run healthcheck on SMTP connector"""
    from libmilter import MILTER_CHUNK_SIZE, SMFIC_OPTNEG
    logger = logging.getLogger("fuglu.check.check_fuglu_asmilter")

    try:
        logger.debug("Open connection")

        ipvers = socket.AF_INET
        if ':' in host:
            ipvers = socket.AF_INET6
        s = socket.socket(ipvers, socket.SOCK_STREAM)
        s.settimeout(timeout)
        logger.debug(f"Socket.connect to {host}:{port}")
        s.connect((host, port), )

        logger.debug("Negotiate options...")
        logger.debug("Sent, now disable writing to socket")
        s.send(b'\x00\x00\x00\rO\x00\x00\x00\x06\x00\x00\x01\xff\x00\x1f\xff\xff')

        try:
            s.shutdown(socket.SHUT_WR)
        except (OSError, socket.error):
            pass

        logger.debug("Wait for response and parse...")
        line = s.recv(MILTER_CHUNK_SIZE)
        logger.debug(f"Got line: {line}")

        if line and SMFIC_OPTNEG in line:
            logger.debug(f"Success: found SMFIC_OPTNEG in line")
            return 0
        else:
            logger.debug(f"Fail: Didn't find SMFIC_OPTNEG in line")
    except Exception as e:
        logger.error(str(e))

    return 1
