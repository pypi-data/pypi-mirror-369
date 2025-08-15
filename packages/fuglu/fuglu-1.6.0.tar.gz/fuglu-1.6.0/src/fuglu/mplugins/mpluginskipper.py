import typing

import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from fuglu.mshared import BMPConnectMixin, BasicMilterPlugin
from fuglu.shared import Suspect


class MilterPluginSkipper(BMPConnectMixin, BasicMilterPlugin):
    """
    Milter plugin skipper (based on config/env var)

    This should run as the first plugin to be able to skip any plugin later on
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars.update({
            'skiplist': {
                'default': '$MPLUGINSKIPLIST',
                'description': 'Comma-separated list of plugins to skip (allows env var)'
            },
            'state': {'default': f'{asm.CONNECT}'}
        })

    def _get_skiplist(self, raise_on_error: bool = False, loggerid: str = "") -> typing.List[str]:
        """Get list of plugins to skip, log with logggerid if defined, raise exceptions on request only"""
        skiplist = []
        skipstring = self.config.get(self.section, "skiplist", resolve_env=True)
        if skipstring:
            loggerid = loggerid.strip() if loggerid else ""
            if loggerid:
                loggerid += " "
            try:
                skiplist = Suspect.getlist_space_comma_separated(skipstring)
                self.logger.info(f"{loggerid}Setup plugin skiplist: {'j'.join(skiplist)}")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "") # create nice type string for logging
                self.logger.error(f"{loggerid}Could not convert skipstring '{skipstring}' to plugin list: ({typestring}) {e}")
                raise ValueError(f"Could not convert skipstring '{skipstring}' to plugin list: ({typestring}) {e}")
        return skiplist

    def examine_connect(self, sess: typing.Union[sm.MilterSession, asm.MilterSession], host: bytes, addr: bytes) -> typing.Union[bytes, typing.Tuple[bytes, str]]:
        """Skip plugins based on config/environment vars"""
        skiplist = self._get_skiplist(loggerid=sess.id)
        if skiplist:
            for pluginname in skiplist:
                sess.add_plugin_skip(pluginname)
                self.logger.debug(f'{sess.id} skipping plugin {pluginname}')
        return sm.CONTINUE

    def lint(self, **kwargs) -> bool:
        """Basic lint checks inherited and skiplist check"""
        from fuglu.funkyconsole import FunkyConsole
        if not super().lint():
            return False

        fc = FunkyConsole()
        try:
            skiplist = self._get_skiplist(raise_on_error=True)
            if skiplist:
                print(f"Skipping plugins: {','.join(skiplist)}")
            else:
                print("Not plugins to skip defined...")
        except ValueError as e:
            print(fc.strcolor("ERROR", "red"), str(e))
            return False
        except Exception as e:
            typestring = str(type(e)).replace("<", "").replace(">", "") # create nice type string for logging
            print(fc.strcolor("ERROR", "red"), f"Unhandled error: ({typestring}) {str(e)}")
            return False

        return True