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

from collections import defaultdict
from .backendint import BackendInterface

STRATEGY = 'always-hit'
BACKENDS = defaultdict(dict)

__all__ = ['STRATEGY', 'BACKENDS']


class GeneralBackend(BackendInterface):
    def __init__(self, backendconfig: str):
        super().__init__(backendconfig=backendconfig)

    def check_allowed(self, eventname, limit, timespan, increment):
        return False, 0


BACKENDS[STRATEGY]['memory'] = GeneralBackend
BACKENDS[STRATEGY]['redis'] = GeneralBackend
BACKENDS[STRATEGY]['aioredis'] = GeneralBackend
BACKENDS[STRATEGY]['sqlalchemy'] = GeneralBackend
