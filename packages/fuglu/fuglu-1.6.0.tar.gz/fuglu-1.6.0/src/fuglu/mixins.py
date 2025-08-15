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

import time
import weakref
import typing as tp


class DefConfigMixin:
    """
    Mixin for FuConfigParser, watching requiredvarsdict,
    applying plugin defaults from requiredvars as config fallback
    """
    class RequiredvarDict(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._updated = False
            self.notice_on_update = []

        def register_update_listener(self, listener):
            self.notice_on_update.append(weakref.ref(listener))

        def notify_update_listener(self):
            for listenerwf in self.notice_on_update:
                listener = listenerwf()
                try:
                    listener.upd(self)
                except Exception:
                    pass

        def update(self, *args, **kwargs):
            out = super().update(*args, **kwargs)
            self.notify_update_listener()
            return out

        def __setitem__(self, *args, **kwargs):
            out = super().__setitem__(*args, **kwargs)
            self.notify_update_listener()
            return out

    def __init__(self, config, *args, **kwargs):
        self.config = config
        self._requiredvars = None
        section = kwargs.get("section") if kwargs else None
        if section is None:
            self.section = self.__class__.__name__
        else:
            self.section = section
        self.requiredvars = {}

    def upd(self, dictupdt):
        """Action to perform if notified by RequiredVarsDict update -> update default vars in FuConfigParser"""
        from .shared import FuConfigParser
        if self.config and isinstance(self.config, FuConfigParser) and self.section is not None:
            self.config.update_defaults(self.section, defaults=dictupdt)

    @property
    def requiredvars(self):
        return self._requiredvars

    @requiredvars.setter
    def requiredvars(self, requiredvarsdict: tp.Union[dict, RequiredvarDict]):
        if not isinstance(requiredvarsdict, DefConfigMixin.RequiredvarDict):
            rdict = DefConfigMixin.RequiredvarDict()
            try:
                for k, v in requiredvarsdict.items():
                    rdict[k] = v
            except Exception:
                pass
            requiredvarsdict = rdict
        self._requiredvars = requiredvarsdict
        self._requiredvars.register_update_listener(listener=self)
        self.upd(self._requiredvars)


class SimpleTimeoutMixin:
    """Simple timeout mixin for given tags"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stimedict = {}
        self._stimehit = {}

    def stimeout_set_timer(self, name: str, timeout: float):
        if timeout:
            now = time.time()
            self._stimedict[name] = (now + timeout, now, timeout)

    def stimeout_continue(self, name: str):
        timeout_end, timeout_start, timeout_duration = self._stimedict.get(name, (0, 0, 0))
        if timeout_end and time.time() > timeout_end:
            self._stimehit[name] = True
            return False
        else:
            return True

    def stimeout_string(self, name: str):
        timeout_end, timeout_start, timeout_duration = self._stimedict.get(name, (0, 0, 0))
        if timeout_duration:
            return f"timeout(real/limit) = {(time.time()-timeout_start):.1f}/{timeout_duration:.1f} [s]"
        else:
            return "no timeout"
    
    def stimeout_runtime(self, name: str):
        if name in self._stimedict:
            return time.time() - self._stimedict[name][1]
        else:
            return -1
    
    def stimeout_remaining(self, name: str):
        if name in self._stimedict:
            return max(0, self._stimedict[name][0] - time.time())
        else:
            return 0


class ReturnOverrideMixin(object):
    #config = None
    #section = None
    #_logger = None

    def __init__(self, config, section: tp.Optional[str] = None):
        super().__init__(config, section=section)
        self._overrideaction = -1
        self._milt_overrideaction = b"undefined"
        self._overridemessage = None

    @property
    def overrideaction(self):
        """get override-action which will be returned instead of 'real' plugin output"""
        if isinstance(self._overrideaction, int) and self._overrideaction < 0:
            # setup return code override if given in config
            self._overrideaction = None
            overrideaction = self.config.get(self.section, 'overrideaction', fallback=None)
            overridemessage = self.config.get(self.section, 'overridemessage', fallback='').strip()

            if overrideaction:
                from fuglu.shared import string_to_actioncode
                # import here to prevent circular dependency
                self._overrideaction = string_to_actioncode(overrideaction, self.config)
            if overridemessage:
                self._overridemessage = overridemessage
        return self._overrideaction

    @property
    def milter_overrideaction(self):
        if isinstance(self._milt_overrideaction, bytes) and self._milt_overrideaction == b"undefined":
            self._milt_overrideaction = None
            from fuglu.mshared import retcode2milter
            if self.overrideaction is not None:
                self._milt_overrideaction = retcode2milter.get(self.overrideaction)
        return self._milt_overrideaction

    def _check_apply_override(self,
                              out: tp.Optional[tp.Union[int, tp.Tuple[int, str]]] = None,
                              suspectid: str = "<>") -> tp.Optional[tp.Union[int, tp.Tuple[int, str]]]:
        """Run examine method of plugin + additional pre/post calculations"""

        from fuglu.shared import actioncode_to_string
        # import here to prevent circular dependency

        if isinstance(out, tuple):
            ret, msg = out
        else:
            ret = out
            msg = None

        if self.overrideaction is not None:
            if ret is not None and ret != self.overrideaction:
                plugin_return = actioncode_to_string(ret)
                plugin_msg = msg if msg else ""
                override_return = actioncode_to_string(self.overrideaction)
                override_msg = self._overridemessage if self._overridemessage else ""
                try:
                    self._logger().warning(f"{suspectid} overrideaction: "
                                           f"plugin={plugin_return}/msg={plugin_msg}, "
                                           f"override={override_return}/msg={override_msg}")
                except Exception:
                    pass
                ret = self.overrideaction
                msg = self._overridemessage

        if msg is not None:
            return ret, msg
        else:
            return ret

    def _check_apply_override_milter(self,
                                     out: tp.Optional[tp.Union[int, tp.Tuple[int, str]]] = None,
                                     suspectid: str = "<>") -> tp.Union[bytes, tp.Tuple[bytes, str]]:

        from fuglu.connectors.milterconnector import RETCODE2STR
        # import here to prevent circular dependency

        if isinstance(out, tuple):
            ret, msg = out
        else:
            ret = out
            msg = None

        if self.milter_overrideaction is not None:
            if ret is not None and ret != self.milter_overrideaction:
                plugin_return = RETCODE2STR.get(ret)
                plugin_msg = msg if msg else ""
                override_return = RETCODE2STR.get(self.milter_overrideaction)
                override_msg = self._overridemessage if self._overridemessage else ""
                self._logger().warning(f"{suspectid} overrideaction: "
                                       f"plugin={plugin_return}/msg={plugin_msg}, "
                                       f"override={override_return}/msg={override_msg}")
                ret = self.milter_overrideaction
                msg = self._overridemessage

        if msg is not None:
            return ret, msg
        else:
            return ret
