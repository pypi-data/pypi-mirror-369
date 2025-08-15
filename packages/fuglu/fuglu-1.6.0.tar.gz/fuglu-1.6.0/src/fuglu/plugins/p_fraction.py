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

from fuglu.shared import PrependerPlugin, SuspectFilter
import os


class PluginFraction(PrependerPlugin):

    """Runs only a fraction of loaded scanner plugins based on standard filter file
Use this if you only want to run a fraction of the standard plugins on a specific port for example
e.g. put this in /etc/fuglu/pluginfraction.regex:

@incomingport    1100    SAPlugin,AttachmentPlugin
"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.filter = None
        self.requiredvars = {
            'filterfile': {
                'default': '${confdir}/pluginfraction.regex',
                'description': 'path to file containing scanner plugin fraction regex rules'
            },
            'skip_appenders': {
                'default': 'False',
                'desciption': 'also skip appender plugins'
            }
        }
        self.logger = self._logger()

    def __str__(self):
        return "Plugin Fraction"

    def _alter_list(self, suspect, pluginlist):
        if not self._init_filter():
            return pluginlist

        args = self.filter.get_args(suspect)
        # each arg should be a comma separated list of classnames to skip

        if len(args) == 0:
            return pluginlist
        includepluginlist = []

        for arg in args:
            includepluginlist.extend(arg.split(','))

        listcopy = pluginlist[:]
        for plug in pluginlist:
            name = plug.__class__.__name__
            if name not in includepluginlist:
                listcopy.remove(plug)
        return listcopy

    def pluginlist(self, suspect, pluginlist):
        """Removes scannerplugins based on filter file"""
        return self._alter_list(suspect, pluginlist)

    def appenderlist(self, suspect, appenderlist):
        """Removes appender plugins based on filter file"""

        if not self.config.getboolean(self.section, 'skip_appenders'):
            return appenderlist

        return self._alter_list(suspect, appenderlist)

    def _init_filter(self):
        if self.filter is not None:
            return True

        filename = self.config.get(self.section, 'filterfile')
        if filename is None or filename == "":
            return False

        if not os.path.exists(filename):
            self.logger.error('Filterfile not found for pluginfraction: %s' % filename)
            return False

        self.filter = SuspectFilter(filename)
        return True

    def lint(self):
        return self.check_config() and self.lint_filter()

    def lint_filter(self):
        filterfile = self.config.get(self.section, 'filterfile')
        sfilter = SuspectFilter(filterfile)
        return sfilter.lint()
