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
import typing as tp
from hashlib import md5
import asyncio


class BackendInterface:
    """Abstract base class for backends"""

    def __init__(self, backendconfig: str):
        self.logger = logging.getLogger(f"fuglu.plugins.{self.__class__.__name__}")

    def _fix_eventname(self, eventname) -> str:
        if not isinstance(eventname, str):
            eventname = str(eventname)
        if len(eventname) > 255:
            eventname = md5(eventname.encode()).hexdigest() # nosemgrep CWE-327
        return eventname

    def check_allowed(self,
                      eventname: str,
                      limit: tp.Union[int, float],
                      timespan: tp.Union[int, float],
                      increment: int,
                      ) -> tp.Union[asyncio.Future, tp.Tuple[bool, tp.Union[int, float]]]:
        raise NotImplementedError()
