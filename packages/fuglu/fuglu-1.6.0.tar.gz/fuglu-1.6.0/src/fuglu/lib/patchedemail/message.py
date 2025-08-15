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
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.generator import Generator
from copy import deepcopy
from io import StringIO

# ----------------------------------------------------------------- #
# ----------------------------------------------------------------- #
# Until https://bugs.python.org/issue27321 is merged we need        #
# a patched version already implementing this fix                   #
# ----------------------------------------------------------------- #
# ----------------------------------------------------------------- #


class PatchedGenerator(Generator):
    def __init__(self, *args, **kwargs):
        super(PatchedGenerator, self).__init__(*args, **kwargs)

    def _write(self, msg):
        # We can't write the headers yet because of the following scenario:
        # say a multipart message includes the boundary string somewhere in
        # its body.  We'd have to calculate the new boundary /before/ we write
        # the headers so that we can write the correct Content-Type:
        # parameter.
        #
        # The way we do this, to make the _handle_*() methods simpler,
        # is to cache any subpart writes into a buffer.  We write the
        # headers and the buffer contents.  That way, subpart handlers can
        # Do The Right Thing, and can still modify the Content-Type: header if
        # necessary.
        oldfp = self._fp
        try:
            self._munge_cte = None
            self._fp = sfp = self._new_buffer()
            self._dispatch(msg)
        finally:
            self._fp = oldfp
            munge_cte = self._munge_cte
            del self._munge_cte
        # If we munged the cte, copy the message again and re-fix the CTE.
        if munge_cte:
            msg = deepcopy(msg)
            # ----
            # -- Fix is here -> check if these headers exist, since
            # -- replace_header will create a KeyError otherwise
            # ----
            if msg.get('content-transfer-encoding') is not None:
                msg.replace_header('content-transfer-encoding', munge_cte[0])
            if msg.get('content-type', munge_cte[1]) is not None:
                msg.replace_header('content-type', munge_cte[1])
        # Write the headers.  First we see if the message object wants to
        # handle that itself.  If not, we'll do it generically.
        meth = getattr(msg, '_write_headers', None)
        if meth is None:
            self._write_headers(msg)
        else:
            meth(self)
        self._fp.write(sfp.getvalue())


class PatchedMessage(EmailMessage):
    def __init__(self, *args, **kwargs):
        super(PatchedMessage, self).__init__(*args, **kwargs)

    def as_string(self, unixfrom=False, maxheaderlen=0, policy=None):
        """
        Return the entire formatted message as a string.

        Overwrites the original method to use patched version of generator
        """
        policy = self.policy if policy is None else policy
        fp = StringIO()
        g = PatchedGenerator(fp, mangle_from_=False,
                             maxheaderlen=maxheaderlen,
                             policy=policy)
        g.flatten(self, unixfrom=unixfrom)
        return fp.getvalue()


class PatchedMIMEMultipart(MIMEMultipart):
    """Same problem as above. Appeared in sa - plugin"""

    def __init__(self, *args, **kwargs):
        super(PatchedMIMEMultipart, self).__init__(*args, **kwargs)
    
    def as_string(self, unixfrom=False, maxheaderlen=0, policy=None):
        """
        Return the entire formatted message as a string.

        Overwrites the original method to use patched version of generator
        """
        policy = self.policy if policy is None else policy
        fp = StringIO()
        g = PatchedGenerator(fp, mangle_from_=False,
                             maxheaderlen=maxheaderlen,
                             policy=policy)
        g.flatten(self, unixfrom=unixfrom)
        return fp.getvalue()