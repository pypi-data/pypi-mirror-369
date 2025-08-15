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

import mimetypes
import email
import logging
import weakref
import hashlib
import base64
import re
import string
import random
import typing as tp
from fuglu.extensions.filearchives import Archivehandle
from fuglu.extensions.filetype import filetype_handler
from fuglu.extensions import fuzzyhashlib
from fuglu.caching import smart_cached_property, smart_cached_memberfunc, Cachelimits
from fuglu.stringencode import force_uString, force_bString
from fuglu.lib.patchedemail import PatchedMessage
from fuglu.mixins import SimpleTimeoutMixin
from io import BytesIO

# workarounds for mimetypes
# - always takes .ksh for text/plain
# - python3 takes .exe for application/octet-stream which is often used for content types
#   unknwon to the creating MUA (e.g. pdf files are often octet-stream)
MIMETYPE_EXT_OVERRIDES = {
    'text/plain': 'txt',
    'application/octet-stream': None,
}


# defect added to Mailattachment.defects if anything to defect list
# if attachment decoding error raises exception or defect is in
# list BAD_DEFECTS
# If DEFECT_ATTPARSEERROR is in Mailattachment.defects,
# Mailattachment.parsed becomes false
DEFECT_ATTPARSEERROR = "<<ATTPARSEERROR>>"
# tuple containing errors preventing correct decoding of buffer
BAD_DEFECTS = (email.errors.InvalidBase64LengthDefect,)
# The contenttype returned for an attachment with parsing error
ATTPARSEERROR_CONTENTTYPE = "application/unknown"


class NoExtractInfo(object):
    """Store info about files """

    valid_causes = ["level", "archivehandle", "toolarge", "extractsize", 'numfiles']

    def __init__(self):
        """Constructor"""

        self.infolists = {}
        for cause in NoExtractInfo.valid_causes:
            self.infolists[cause] = []

    def append(self, filename, cause, message):
        """
        Append a new info about noExtraction

        Args:
            filename (str, unicode): filename causing the issue
            cause (str, unicode): reason for being added, must be in valid_causes
            message (str, unicode): an additional message
        """

        assert cause in NoExtractInfo.valid_causes

        self.infolists[cause].append((force_uString(filename), force_uString(message)))

    def get_filtered(self, plus_filters=None, minus_filters=None):
        """
        Get filtered result

        Args:
            plus_filters (list): list with valid causes (all causes if not defined)
            minus_filters (list): list with causes not to show (empty if not defined)

        Returns:
            list(tuples): (filename, message)

        """
        if plus_filters is None:
            plus_filters = NoExtractInfo.valid_causes
        if minus_filters is None:
            minus_filters = []

        output = []
        for fltr in plus_filters:
            assert fltr in NoExtractInfo.valid_causes
        for fltr in minus_filters:
            assert fltr in NoExtractInfo.valid_causes

        for fltr in plus_filters:
            if fltr not in minus_filters:
                output.extend(self.infolists[fltr])
        return output


class Mailattachment(Cachelimits, SimpleTimeoutMixin):
    """
    Mail attachment object or a file contained in the attachment.
    """
    objectCounter = 0

    HASH_DEFAULTS = ['md5', 'sha1', 'sha256']
    HASHENC_HEX = 'hex'
    HASHENC_B64 = 'b64'
    HASHENC_B32 = 'b32'

    def __init__(self, buffer, filename, mgr, fugluid, filesize=None, in_obj=None, contenttype_mime=None,
                 maintype_mime=None, subtype_mime=None, ismultipart_mime=None, content_charset_mime=None,
                 is_attachment=False, is_inline=False, defects=None, filename_generated=False,
                 archive_passwords=None):
        """
        Constructor

        Args:
            fugluid (str): fuglu id
            buffer (bytes): buffer containing attachment source
            filename (str): filename of current attachment object
            filesize (int): file size in bytes
            mgr (Mailattachment_mgr/None): Mail attachment manager
            in_obj (Mailattachment): "Father" Mailattachment object (if existing), the archive containing the current object
            contenttype_mime (str): The contenttype as defined in the mail attachment, only available for direct mail attachments
            maintype_mime (str): The main contenttype as defined in the mail attachment, only available for direct mail attachments
            subtype_mime (str): The sub-contenttype as defined in the mail attachment, only available for direct mail attachments
            ismultipart_mime (str): multipart as defined in the mail attachment, only available for direct mail attachments
            content_charset_mime (str): The characterset as defined in the mail attachment, only available for direct mail attachments
            is_attachment (bool): True for direct mail attachments with Content-disposition=attachment
            is_inline (bool): True for inline mail attachments with Content-disposition=inline
            defects (list): a list of strings describing problems during creation of the object (transfer-decode errors)
            filename_generated (bool): True if name was not available from mail (auto generated name)
        """
        super().__init__()
        self.filename = force_uString(filename)
        self.filesize = filesize or len(buffer) if buffer else filesize
        self.buffer = force_bString(buffer)
        self._buffer_archobj = {}
        self._buffer_noextractinfo = {}
        self.fugluid = fugluid
        self.defects = defects if defects else []  # make an empty list for None
        self.filename_generated = filename_generated
        self.archive_passwords = archive_passwords
        self.logger = logging.getLogger(f"fuglu.{self.__class__.__name__}")

        # use weak reference to avoid cyclic dependency
        self.in_obj = weakref.ref(in_obj) if in_obj is not None else None
        
        if not contenttype_mime and maintype_mime and subtype_mime:
            contenttype_mime = f'{maintype_mime}/{subtype_mime}'
        self.contenttype_mime = contenttype_mime
        if contenttype_mime and not maintype_mime:
            maintype_mime = contenttype_mime.split('/',1)[0]
        self.maintype_mime = maintype_mime
        if contenttype_mime and not subtype_mime:
            subtype_mime = contenttype_mime.rsplit('/',1)[-1]
        self.subtype_mime = subtype_mime
        
        self.ismultipart_mime = ismultipart_mime
        self.content_charset_mime = content_charset_mime
        self.is_attachment = is_attachment
        self.is_inline = is_inline

        # use weak reference to avoid cyclic dependency
        self._mgr = weakref.ref(mgr) if mgr is not None else None  # keep only weak reference

        # store exception creating archive handle (if any)
        self._archive_handle_exc = None
        
        # archive extension for internal use
        self._arext = None

        # try to increment object counter in manager for each object created.
        # this helps debugging and testing caching...
        try:
            self._mgr()._increment_ma_objects()
        except (AttributeError, TypeError):
            pass
        
    def __repr__(self):
        return f'<Mailattachment name={self.filename} mime={self.contenttype} size={self.filesize} inline={self.is_inline} att={self.is_attachment} arch={self.is_archive}>'

    def content_fname_check(self, maintype=None, ismultipart=None, subtype=None, contenttype=None, contenttype_start=None,
                            name_end=None, contenttype_contains=None, name_contains=None,
                            ctype=None, ctype_start=None, ctype_contains=None):
        """
        Test content or filename for options or a set of options. All inputs except 'ismultipart' allow
        simple strings, a list of strings or a tuple of strings as input.
        Note: contenttype* checks the mime contenttype whereas ctype* checks the type extracted from the buffer anaysis
        """
        try:
            if maintype is not None:
                if isinstance(maintype, (list, tuple)):
                    if not self.maintype_mime in maintype:
                        return False
                else:
                    if not self.maintype_mime == maintype:
                        return False

            if ismultipart is not None:
                if not self.ismultipart_mime == ismultipart:
                    return False

            if subtype is not None:
                if isinstance(subtype, (list, tuple)):
                    if not self.subtype_mime in subtype:
                        return False
                else:
                    if not self.subtype_mime == subtype:
                        return False

            if contenttype is not None:
                if isinstance(contenttype, (list, tuple)):
                    if not self.contenttype_mime in contenttype:
                        return False
                else:
                    if not self.contenttype_mime == contenttype:
                        return False

            if ctype is not None:
                if isinstance(ctype, (list, tuple)):
                    if not self.contenttype in ctype:
                        return False
                else:
                    if not self.contenttype == ctype:
                        return False

            if contenttype_start is not None:
                if isinstance(contenttype_start, list):
                    if not self.contenttype_mime.startswith(tuple(contenttype_start)):
                        return False
                else:
                    if not self.contenttype_mime.startswith(contenttype_start):
                        return False

            if ctype_start is not None:
                if isinstance(ctype_start, list):
                    if not self.contenttype.startswith(tuple(ctype_start)):
                        return False
                else:
                    if not self.contenttype.startswith(ctype_start):
                        return False

            if name_end is not None:
                if isinstance(name_end, list):
                    if not self.filename.endswith(tuple(name_end)):
                        return False
                else:
                    if not self.filename.endswith(name_end):
                        return False

            if contenttype_contains is not None:
                if isinstance(contenttype_contains, (list, tuple)):
                    if not any((a in self.contenttype_mime for a in contenttype_contains)):
                        return False
                else:
                    if not contenttype_contains in self.contenttype_mime:
                        return False

            if ctype_contains is not None:
                if isinstance(ctype_contains, (list, tuple)):
                    if not any((a in self.contenttype for a in ctype_contains)):
                        return False
                else:
                    if not ctype_contains in self.contenttype:
                        return False

            if name_contains is not None:
                if isinstance(name_contains, (list, tuple)):
                    if not any((a in self.filename for a in name_contains)):
                        return False
                else:
                    if not name_contains in self.filename:
                        return False
        except Exception:
            # for any exception happening return False
            return False

        return True

    @smart_cached_property(inputs=['buffer', 'in_obj', 'content_charset_mime'])
    def decoded_buffer_text(self):
        """
        (Cached Member Function)

        Try to decode the buffer.

        Internal member dependencies:
            - buffer (bytes): The buffer with the raw attachment content
            - in_obj (Mailattachment): Reference to parent if this object was extracted from an archive
            - content_charset_mime (string): charset if available or None

        Returns:
            unicode : the unicode string representing the buffer or an empty string on any error

        """

        # only for first level attachments
        decoded_buffer = ""
        if self.in_obj is None:
            charset = self.content_charset_mime if self.content_charset_mime else "utf-8"
            decoded_buffer = force_uString(self.buffer, encodingGuess=charset, errors='strict+ignore')

        return decoded_buffer

    def _mkchecksum(self, value, method, encoding=None, strip=False):
        """
        generate checksum of value using given method and encoding
        :param value: the value to be encoded
        :param method: any hash algorithm supported by hashlib (see hashlib.algorithms_guaranteed for a list)
        :param encoding: returned encoding: hex (default), b64, b32
        :param strip: boolean: strip trailing '=' from b64, b32 hash
        :return: string containing checksum
        """
        if not encoding in [None, self.HASHENC_HEX, self.HASHENC_B64, self.HASHENC_B32]:
            raise KeyError(f'unsupported hash encoding: {encoding}')
        if method in hashlib.algorithms_guaranteed:
            use_hashlib = True
            if encoding is None:
                encoding = self.HASHENC_HEX
        elif method in fuzzyhashlib.hashers_available:
            use_hashlib = False
        else:
            raise KeyError(f'unsupported hash algorithm: {method}')
        
        if not use_hashlib:
            myhash = fuzzyhashlib.digest(method, value)
        else:
            hasher = hashlib.new(method, force_bString(value))
            if encoding == self.HASHENC_HEX:
                myhash = hasher.hexdigest()
            elif encoding == self.HASHENC_B64:
                myhash = base64.b64encode(hasher.digest()).decode()
            elif encoding == self.HASHENC_B32:
                myhash = base64.b32encode(hasher.digest()).decode()
            else:
                myhash = ''
    
            if strip:
                myhash = myhash.rstrip('=')

        return myhash

    @smart_cached_memberfunc(inputs=['buffer'])
    def get_checksum(self, method, encoding=None, strip=False):
        """
        Calculate attachment checksum.

        Args:
            method (string): Checksum method.
            encoding (string): encoding to be used
            strip (boolean): strip trailing = from checksum

        Returns:
            str: checksum
        """
        csum = ""
        if self.buffer is not None:
            try:
                csum = self._mkchecksum(self.buffer, method, encoding, strip)
            except KeyError:
                self.logger.error(f"{self.fugluid} checksum method {method} not valid! Options are [{','.join(list(hashlib.algorithms_guaranteed))}]")
        return csum

    @smart_cached_memberfunc(inputs=['buffer'])
    def get_checksumdict(self, methods=(), encoding=HASHENC_HEX, strip=False):
        """Create a dict for all checksum methods given (or sane default if none)"""

        # select methods, all if none is given
        if not methods:
            mlist = Mailattachment.HASH_DEFAULTS
        else:
            mlist = list(methods)

        # create checksums
        checksumdict = {}
        for m in mlist:
            checksumdict[m] = self.get_checksum(m, encoding, strip)
        return checksumdict

    @smart_cached_property(inputs=['buffer'])
    def parsed(self) -> bool:
        """
        (Cached Property-Getter)

        Returns:
            (bool): true if attachment was parsed, so no decoding error
        """
        return DEFECT_ATTPARSEERROR not in self.defects

    @smart_cached_property(inputs=['buffer'])
    def contenttype(self) -> str:
        """
        (Cached Property-Getter)

        Stores the content type of the file buffer using filetype_handler.

        Internal member dependencies:
            - buffer (bytes): File buffer
        Returns:
            (str): contenttype of file buffer
        """
        contenttype_magic = None
        if self.buffer is not None and filetype_handler.available():
            if DEFECT_ATTPARSEERROR in self.defects:
                # if there are defects then the buffer was not decoded, and it doesn't
                # make sense to return a type by filemagic. For example, if a base64
                # encoded content can not be decoded filemagic will detect it as text
                return ATTPARSEERROR_CONTENTTYPE
            else:
                contenttype_magic = filetype_handler.get_buffertype(self.buffer)
        return contenttype_magic

    @smart_cached_property(inputs=['contenttype', 'filename'])
    def archive_type(self) -> tp.Optional[str]:
        """
        (Cached Property-Getter)

        Stores the archive type stored in this object.

        Internal member dependencies:
            - contenttype: File content type
            - filename: Filename (Extension might be used to detect archive type)

        Returns:
            (str): Archive type if object is an archive, None otherwise
        """

        # try guessing the archive type based on magic content type first
        archive_type = Archivehandle.archive_type_from_content_type(str(self.contenttype))

        # if it didn't work, try to guess by the filename extension, if it is enabled
        if archive_type is None:
            # sort by length, so tar.gz is checked before .gz
            for arext in Archivehandle.avail_archive_extensions_list:
                if self.filename.lower().endswith(f'.{arext}'):
                    archive_type = Archivehandle.avail_archive_extensions[arext]
                    # store archive extension for internal use
                    self._arext = arext
                    break
        return archive_type

    @smart_cached_memberfunc(inputs=['archive_type'])
    def atype_fromext(self):
        """True if extension was used to determine archive type"""
        return self._arext

    @smart_cached_property(inputs=['archive_type'])
    def is_archive(self) -> bool:
        """
        (Cached Property-Getter)

        Define if this object is an extractable archive or an ordinary file.

        Internal:
            - archive_type: Depends on the member variable 'archive_type'

        Returns:
            (bool): True for an archive that can be extracted
        """
        return self.archive_type is not None

    @smart_cached_property(inputs=['is_archive'])
    def is_protected_archive(self) -> bool:
        """
        (Cached Property-Getter)

        Define if this object is an extractable archive or an ordinary file.

        Internal:
            - archive_type: Depends on the member variable 'archive_type'

        Returns:
            (bool): True for an archive that can be extracted
        """
        # try to extract a file
        if self.is_archive and self.fileslist_archive:
            fname = self.fileslist_archive[0]
            noextractinfo = NoExtractInfo()
            _ = self.get_archive_obj(fname, None, noextractinfo=noextractinfo)
            noextractlist = noextractinfo.get_filtered(plus_filters=["archivehandle"])
            return self.archive_handle.protected or self.archive_handle.protected_meta() or any(["password" in item[1].lower() for item in noextractlist])
        return False
    
    
    @smart_cached_property(inputs=['is_protected_archive'])
    def get_archive_password(self) -> tp.Optional[str]:
        if self.is_protected_archive:
            return self.archive_handle.matching_password
        return None
            

    def get_fileslist(self, levelin: tp.Optional[int] = None, levelmax: tp.Optional[int] = None,
                      maxsize_extract: tp.Optional[int] = None, maxfiles_extract: tp.Optional[int] = None):
        """
        Get a list of files contained in this archive (recursively extracting archives)
        or the current filename if this is not an archive.

        Don't cache here, "fileslist_archive" is only available for
        archives. If this is put as dependency then there will be an
        archive handler applied on a non-archive which throws an
        exception

        IMPORTANT: If this is the maximal recursive level to check then only the filelist is
                   extracted from the archive but the actual archive files are NOT extracted.

        Args:
            levelin  (in): Current recursive level
            levelmax (in): Max recursive archive level up to which archives are extracted
            maxsize_extract (int): Maximum size that will be extracted to further go into archive
            maxfiles_extract (int): Maximum number of files that will be extracted from one archive

        Returns:
            (list[str]): List with filenames contained in this object or this object filename itself

        """
        filelist = []
        if levelmax is None or levelin < levelmax:
            if self.is_archive:
                if levelmax is None or levelin + 1 < levelmax:
                    filelist = self.get_fileslist_arch(levelin, levelmax, maxsize_extract, maxfiles_extract)
                else:
                    maxlen = len(self.fileslist_archive)
                    if maxfiles_extract is not None:
                        maxlen = min(maxlen, maxfiles_extract)
                    filelist = self.fileslist_archive[:maxlen]

        if not filelist:
            filelist = [self.filename]

        return filelist

    def get_objectlist(self, levelin:int=0, levelmax:int=None, maxsize_extract: tp.Optional[int]=None,
                       maxfiles_extract: tp.Optional[int]=None, noextractinfo:NoExtractInfo=None,
                       include_parents:bool=False, extraction_timeout:float=10):
        """
        Get a list of file objects contained in this archive (recursively extracting archives)
        or the current object if this is not an archive.

        Don't cache here, "fileslist_archive" is only available for
        archives. If this is put as dependency then there will be an
        archive handler applied on a non-archive which throws an
        exception

        IMPORTANT: This will extract the objects of (at least) the current recursive level.
                   Further extraction depends on the input recursion level.

        Args:
            levelin  (int): Current recursive level
            levelmax (int): Max recursive archive level up to which archives are extracted
            maxsize_extract (int, None): Maximum size that will be extracted to further go into archive
            maxfiles_extract (int, None): Maximum number of files that will be extracted
            noextractinfo (NoExtractInfo): stores info why object was not extracted
            include_parents (bool): True means extract the archives (depending on level) but return archive as well,
                                    not only the extracted files
            extraction_timeout (float): stop extraction after given number of seconds

        Returns:
            (list[Mailattachment]): List with Mailattachment objects contained in this object of this object itself
        """

        if include_parents:
            # if include_parents is true then the current object has to be part of the list whatever...
            newlist = [self]
        else:
            newlist = []
        
        stimeout_key = f'mailattach-{self.filename}'
        self.stimeout_set_timer(stimeout_key, extraction_timeout)
        if levelmax is None or levelin < levelmax:
            if self.is_archive:
                # if an archive and its metadata is encrypted we can't extract
                # the filelist in which case a message in noextractinfo should be added
                if self.fileslist_archive:
                    maxlen = len(self.fileslist_archive)
                    if maxfiles_extract is not None:
                        maxlen = min(maxlen, maxfiles_extract)

                    if levelmax is None or levelin + 1 < levelmax:
                        for fname in self.fileslist_archive[:maxlen]:
                            if not self.stimeout_continue(stimeout_key):
                                break
                            attachObj = self.get_archive_obj(fname, maxsize_extract, noextractinfo)
                            if attachObj is not None:
                                newlist.extend(attachObj.get_objectlist(levelin+1, levelmax, maxsize_extract, maxfiles_extract, noextractinfo=noextractinfo))
                    else:
                        for fname in self.fileslist_archive[:maxlen]:
                            if not self.stimeout_continue(stimeout_key):
                                break
                            attachObj = self.get_archive_obj(fname, maxsize_extract, noextractinfo)
                            if attachObj is not None:
                                newlist.append(attachObj)
                    if noextractinfo and self.fileslist_archive[maxlen:]:
                        for fname in self.fileslist_archive[maxlen:]:
                            if not self.stimeout_continue(stimeout_key):
                                break
                            noextractinfo.append(fname, "numfiles", f"num files (current/allowed) {len(self.fileslist_archive)}/{maxlen}")

                elif self.archive_handle is None:
                    if noextractinfo is not None:
                        errorstring = self._archive_handle_exc if self._archive_handle_exc else '<generic>'
                        noextractinfo.append(self.filename, "archivehandle", f"No archive handler: {errorstring}")
                elif self.archive_handle.protected_meta():
                    if noextractinfo is not None:
                        noextractinfo.append(self.filename, "archivehandle", "Password protected archive (data + meta)")
        elif self.is_archive and noextractinfo is not None:
            for fname in self.fileslist_archive:
                noextractinfo.append(fname, "level", f"level (current/max) {levelin}/{levelmax}")

        if not newlist:
            newlist = [self]

        return newlist

    @smart_cached_memberfunc(inputs=['fileslist_archive', 'archive_handle', 'is_archive'])
    def get_archive_flist(self, maxsize_extract: tp.Optional[int]=None, inverse:bool=False):
        """
        Get list of all filenames for objects in archive if within size limits. The list
        is consistent with the object list that would be returned by 'get_archive_objlist' or
        the inverse of it.
        Note: This will extract objects withing the limit if not already extracted!

        Here caching is allowed. Even if the attachment Object is destroyed, the filename
        remains valid (unlike the object reference returned by get_archive_objlist for uncached objects)

        Keyword Args:
            maxsize_extract (int): Maximum size that will be extracted
            inverse (bool): invert list

        Returns:

        """
        matchlist = []
        inverselist = []
        if self.is_archive:
            for fname in self.fileslist_archive:
                attachObj = self.get_archive_obj(fname, maxsize_extract)
                if attachObj is not None:
                    matchlist.append(fname)
                else:
                    inverselist.append(fname)
        return inverselist if inverse else matchlist

    def get_archive_objlist(self, maxsize_extract: tp.Optional[int]=None, noextractinfo:NoExtractInfo=None):
        """
        Get list of all object in archive (extracts the archive) if within size limits.
        If the file is already extracted the file will be returned even if the size is
        larger than 'maxsize_extract'.

        No caching of the lists here because get_archive_obj might return an
        uncached object. The list returned here contains only references and therefore
        the caching of the list would make the uncached object permanent because the
        garbage collector can not remove it because of the reference count.

        Args:
            maxsize_extract (int): Maximum size that will be extracted
            noextractinfo (NoExtractInfo): stores info why object was not extracted

        Returns:
            list containing objects contained in archive

        """
        newlist = []
        if self.is_archive:
            for fname in self.fileslist_archive:
                attach_obj = self.get_archive_obj(fname, maxsize_extract, noextractinfo)
                if attach_obj is not None:
                    newlist.append(attach_obj)
        return newlist

    def get_archive_obj(self, fname:str, maxsize_extract: tp.Optional[int]=None, noextractinfo:NoExtractInfo=None):
        """
        Get cached archive object or create a new one.

        Args:
            fname (str): filename of file object
            maxsize_extract (int): Maximum size that will be extracted
            noextractinfo (NoExtractInfo): stores info why object was not extracted

        Returns:
            (Mailattachment): Requested object from archive

        """
        if not self.is_archive:
            return None
        else:
            try:
                obj = self._buffer_archobj[fname]
                einfo = self._buffer_noextractinfo.get(fname)
                if einfo:
                    if noextractinfo:
                        noextractinfo.append(*einfo)
            except KeyError:
                try:
                    filesize = self.archive_handle.filesize(fname)
                except Exception as e:
                    if noextractinfo is not None:
                        noextractinfo.append(fname, "archivehandle", f"exception: {e.__class__.__name__}: {str(e)}")
                    # cache answer despite problem
                    if self._mgr:
                        self._buffer_archobj[fname] = None
                        self._buffer_noextractinfo[fname] = fname, "archivehandle", f"exception: {force_uString(e)}"
                    return None

                try:
                    buffer = self.archive_handle.extract(fname, maxsize_extract)
                except Exception as e:
                    if noextractinfo is not None:
                        noextractinfo.append(fname, "archivehandle", f"exception: {e.__class__.__name__}: {str(e)}")
                    # cache answer despite problem
                    if self._mgr:
                        self._buffer_archobj[fname] = None
                        self._buffer_noextractinfo[fname] = fname, "archivehandle", f"exception: {e.__class__.__name__}: {str(e)}"
                    return None

                if buffer is None:
                    if noextractinfo is not None:
                        if maxsize_extract is not None \
                                and filesize is not None \
                                and filesize > maxsize_extract:
                            noextractinfo.append(fname, "extractsize", "not extracted: %u > %u" % (filesize, maxsize_extract))
                            if self._mgr:
                                self._buffer_noextractinfo[fname] = fname, "extractsize", "not extracted: %u > %u" % (filesize, maxsize_extract)
                        else:
                            noextractinfo.append(fname, "archivehandle", "(no info)")
                        if self._mgr:
                            self._buffer_noextractinfo[fname] = fname, "archivehandle", "(no info)"
                    # cache answer despite problem
                    if self._mgr:
                        self._buffer_archobj[fname] = None
                    return None
                obj = Mailattachment(buffer, fname, self._mgr() if self._mgr else None, self.fugluid, filesize=filesize, in_obj=self,
                                     is_attachment=self.is_attachment, is_inline=self.is_inline)

                # This object caching is outside the caching decorator used in other parts of this
                # file (not for this function anyway...).
                if self._mgr and self._mgr().use_caching(filesize):
                    self._buffer_archobj[fname] = obj
            return obj

    @smart_cached_memberfunc(inputs=['fileslist_archive', 'archive_handle'])
    def get_fileslist_arch(self, levelin: int, levelmax: tp.Optional[int],
                           maxsize_extract: tp.Optional[int] = None,
                           maxfiles_extract: tp.Optional[int] = None):
        """
        Get a list of filenames contained in this archive (recursively extracting archives)
        or the current object filename if this is not an archive.

        Internal:
            - fileslist_archive: The list of archive filenames
            - archive_handle: The archive handle to work with the archvie

        Args:
            levelin  (int): Current recursive level
            levelmax (int, None): Max recursive archive level up to which archives are extracted
            maxsize_extract (int, None): Maximum size that will be extracted to further go into archive
            maxfiles_extract (int, None): Maximum number of files that will be extracted from one archive

        Returns:
            (list[str]): List with filenames contained in this object or this object filename itself
        """
        newlist = []
        if self.fileslist_archive is not None:
            maxlen = len(self.fileslist_archive)
            if maxfiles_extract is not None:
                maxlen = min(maxlen, maxfiles_extract)

            for fname in self.fileslist_archive[:maxlen]:
                attach_obj = self.get_archive_obj(fname, maxsize_extract)
                if attach_obj is not None:
                    newlist.extend(attach_obj.get_fileslist(levelin+1, levelmax, maxsize_extract, maxfiles_extract))
                else:
                    # if the object can't be extracted (because for example archive is password protected)
                    # then return filename directly
                    newlist.append(fname)
        return newlist

    @smart_cached_property(inputs=['archive_type', 'buffer'])
    def archive_handle(self):
        """
        (Cached Property-Getter)

        Create an archive handle to check, extract, ... files in the buffered archive.

        Internal:
            - archive_type: The archive type (already detected)
            - buffer: The file buffer containing the archive

        Returns:
           (Archivehandle) : The handle to work with the archive

        """
        # make sure there's no buffered archive object when
        # the archive handle is created (or overwritten)
        self._buffer_archobj = {}
        self._buffer_noextractinfo = {}
        handle = None
        if self.buffer is not None and self.archive_type is not None:
            try:
                handle = Archivehandle(str(self.archive_type), BytesIO(self.buffer), archivename=self.filename, pwd=self.archive_passwords)
            except Exception as e:
                self.logger.warning(f"{self.fugluid} Problem creating Archivehandle for file: "
                                    f"{self.filename} using archive handler {str(self.archive_type)} "
                                    f"({e.__class__.__name__}: {str(e)}) -> ignore")
                if force_uString(e).strip() == "":
                    # store class name if no string
                    self._archive_handle_exc = e.__class__.__name__
                else:
                    # store string
                    self._archive_handle_exc = force_uString(e)
        elif self.buffer is not None and self.archive_type is None:
            self.logger.debug(f"{self.fugluid} {self.filename} is not a (supported) archive, not creating archive handle")

        return handle

    @smart_cached_property(inputs=['archive_handle'])
    def fileslist_archive(self):
        """
        (Cached Property-Getter)

        Internal:
            - archive_type: The archive type (already detected)
            - buffer: The file buffer containing the archive

        Returns:
           list : List containing filenames

        """
        if self.archive_handle is None:
            return []
        else:
            return self.archive_handle.namelist()

    @smart_cached_property(inputs=["in_obj"])
    def in_archive(self):
        """Return if this object is in an archive"""
        return True if self.parent_archives else False

    @smart_cached_property(inputs=["in_obj"])
    def parent_archives(self):
        """
        (Cached Property-Getter)

        The ordered list of parent objects this file was extracted from.
        First element is the direct parent (if existing).

        Returns:
           (list[Mailattachment]) : list of parents

        """
        parentsList = []
        upstream_obj = weakref.ref(self)
        while upstream_obj() is not None and upstream_obj().in_obj is not None:
            parentsList.append(upstream_obj().in_obj)
            upstream_obj = upstream_obj().in_obj
        return parentsList

    def location(self):
        """Print the location of the file in the archive tree"""
        element_of = " \u2208 "
        location = self.filename
        if self.parent_archives:
            location += element_of + element_of.join(["{" + obj().filename + "}" for obj in self.parent_archives])
        return location
    
    _re_ws = re.compile(r'\s')
    @classmethod
    def mangle_filename(cls, value: str, maxchars: int = 15, keepending: bool = False, replace_ws: bool = False):
        allowed_chars = string.ascii_letters + string.digits
        first = value.split('.')[0]
        if replace_ws:
            # replace spaces with underscore
            first = cls._re_ws.sub('_', first)
            allowed_chars += '_'
        # remove all non alnum chars
        first = ''.join([x for x in first if x in allowed_chars])
        if first.strip() == '' or first.strip() == 'filename':  # renattach renames to 'filename'
            first = f'upn-{random.randint(1000, 9999)}'
        elif len(first) < 4:
            first = f'sh-{random.randint(1000, 9999)}-{first}'
        # strip to a maximum of maxchars characters
        newfilename = first[:maxchars]
        if keepending and "." in value:
            ending = value.rsplit(".", 1)[1]
            if ending:
                # if filename ends with a "." ending is empty
                newfilename = f'{newfilename}.{ending}'
        return newfilename

    @smart_cached_memberfunc(inputs=["filename"])
    def get_mangled_filename(self, prefix: str = '', maxchars: int = 15, keepending: bool = False, replace_ws: bool = False):
        newfilename = self.mangle_filename(self.filename, maxchars, keepending, replace_ws)
        if prefix:
            newfilename = f'{prefix}.{newfilename}'
        return newfilename

    def __str__(self):
        """
        String conversion function for object. Creates
        a string with some basic information
        Returns:
            (str): string with object information

        """
        element_of = " \u2208 "
        return f"""
Filename     : {self.filename}
Size (bytes) : {'(unknown)' if self.filesize is None else str(self.filesize)}
Location     : {self.filename}{element_of}{element_of.join(["{" + obj().filename + "}" for obj in self.parent_archives])}
Archive type : {self.archive_type}
Content type : {self.contenttype}"""


class Mailattachment_mgr(object):
    """Mail attachment manager"""

    def __init__(self,
                 msgrep: PatchedMessage,
                 fugluid: str, section: tp.Optional[str] = None,
                 cachelimit: tp.Optional[int] = None,
                 default_filelimit: tp.Optional[int] = None,
                 max_filelimit: tp.Optional[int] = None,
                 default_numfilelimit: tp.Optional[int] = None,
                 max_numfilelimit: tp.Optional[int] = None,
                 archive_passwords: tp.Optional[tp.List[str]] = None,
                 ):
        """
        Constructor, initialised by message.

        Args:
            msgrep (email.message.Message): Message to work with
            fugluid (string): fugluid for logging
            cachelimit (int): cachelimit for keeping attachments during Suspect lifetime
            default_filelimit (int): default maximum filelimit to extract files if not defined otherwise
            max_filelimit (int): maximum filelimit to extract files, limiting all other limits
            default_numfilelimit (int): default maximum number of files extracted from a single archive
            max_numfilelimit (int): maximum number of files extracted from a single archive, limiting all other limits
            archive_passwords (List of str): possible passwords to decrypt encrypted archive attachments
        """
        self._msgrep = msgrep
        self._manually_added = []  # List of manually added Mailattachments
        self.fugluid = fugluid
        if section is None:
            self.section = self.__class__.__name__
        else:
            self.section = section
        self.logger = logging.getLogger(f"fuglu.{self.__class__.__name__}")

        # to limit the size of the attachment cache
        self._current_att_cache = 0
        self._new_att_cache = 0
        self._cache_limit = cachelimit
        self._default_filelimit = default_filelimit

        # default limit should be bound by max
        if max_filelimit is not None and default_filelimit is not None:
            self._default_filelimit = min(default_filelimit, max_filelimit)

        self._max_filelimit = max_filelimit
        self._mailatt_obj_counter = 0
        self._att_file_dict = None

        # limit max number of files extracted from a single archive
        self._default_numfilelimit = default_numfilelimit
        if default_numfilelimit is not None and max_numfilelimit is not None:
            self._default_numfilelimit = min(max_numfilelimit, default_numfilelimit)

        self._max_numfilelimit = max_numfilelimit
        self._archive_passwords = archive_passwords

    def get_maxsize_extract(self, maxsize: tp.Optional[int]):
        """Get maximum size to extract file from archive applying the various limits."""
        if maxsize is not None:
            # input value given
            # (max_filelimit will still be applied)
            pass
        elif self._default_filelimit is not None:
            # default limit given
            maxsize = self._default_filelimit
        elif self._max_filelimit is not None:
            # default limit given
            maxsize = self._max_filelimit
        else:
            maxsize = None

        if maxsize is not None and self._max_filelimit is not None:
            maxsize = min(maxsize, self._max_filelimit)

        return maxsize

    def get_maxfilenum_extract(self, maxnum: tp.Optional[int]):
        """Get the maximum number of files to extract from a single archive, applying the various limits."""
        if maxnum is not None:
            # input value given
            # (max_filelimit will still be applied)
            pass
        elif self._default_numfilelimit is not None:
            # default limit given
            maxnum = self._default_numfilelimit
        elif self._max_numfilelimit is not None:
            # default limit given
            maxnum = self._max_numfilelimit
        else:
            maxnum = None

        if maxnum is not None and self._max_numfilelimit is not None:
            maxnum = min(maxnum, self._max_numfilelimit)

        return maxnum

    def _increment_ma_objects(self):
        """
        For caching testing and debugging purposes count the number
        of Mailattachment objects created
        """
        self._mailatt_obj_counter += 1

    def use_caching(self, used_size):
        """
        Used to decide if new attachment objects inside other attachments should be cached or noe

        Returns:
            bool : True to cache the object

        """
        self._new_att_cache = self._current_att_cache + (used_size if used_size else 0)

        if True if self._cache_limit is None else self._cache_limit >= self._new_att_cache:
            self._current_att_cache += (used_size if used_size else 0)
            return True
        else:
            return False

    def walk_all_parts(self, message):
        """
        Like email.message.Message's .walk() but also tries to find parts in the message's epilogue.

        Args:
            message (email.message.Message):

        Returns:
            (iterator): to iterate over message parts

        """
        for part in message.walk():
            yield part

        boundary = message.get_boundary()
        epilogue = message.epilogue
        if epilogue is None or boundary not in epilogue or not boundary:
            return

        candidate_parts = epilogue.split(boundary)
        for candidate in candidate_parts:
            try:
                part_content = candidate.strip()
                if part_content.lower().startswith('content'):
                    message = email.message_from_string(part_content)
                    yield message

            except Exception as e:
                self.logger.info(f"{self.fugluid} hidden part extraction failed: {e.__class__.__name__}: {str(e)}")

    @smart_cached_property(inputs=["_msgrep"])
    def att_file_dict(self, skip_named_multipart: bool = False):
        """
        (Cached Property-Getter)

        Dictionary storing attachments in mail. Key is filename, value is list of
        Mailattachment objects for given name.

        Internal member dependencies:
            - _msgrep (email.message.Message): Email message

        Returns:
            (dict): Dictionary storing attachments in list
        """
        newatt_file_dict = dict()

        # reset caching
        self._current_att_cache = 0
        self._new_att_cache = 0

        for part in self.walk_all_parts(self._msgrep):
            if part.is_multipart() and (part.get_filename() is None or skip_named_multipart):
                continue

            # process part, extract information needed to create Mailattachment
            (att_name, buffer, attsize,
             contenttype_mime, maintype_mime, subtype_mime,
             ismultipart_mime, content_charset_mime,
             isattachment, isinline, defects, att_name_generated) = self.process_msg_part(part)

            if self.use_caching(attsize):
                # cache the object if a cachelimit is defined
                # and if size could be extracted and is within the limit
                newatt_file_dict[id(part)] = Mailattachment(buffer, att_name, self, self.fugluid, filesize=attsize,
                                                           contenttype_mime=contenttype_mime,
                                                           maintype_mime=maintype_mime, subtype_mime=subtype_mime,
                                                           ismultipart_mime=ismultipart_mime,
                                                           content_charset_mime=content_charset_mime,
                                                           is_attachment=isattachment, is_inline=isinline,
                                                           defects=defects, filename_generated=att_name_generated)
            else:
                # No caching of the object
                newatt_file_dict[id(part)] = None
        return newatt_file_dict

    def get_mailatt_generator(self, archives_passwords: tp.Optional[tp.List[str]], skip_named_multipart: bool = False):
        """
        Dictionary storing attachments in mail. Key is filename, value is list of
        Mailattachment objects for given name.

        Internal member dependencies:
            - _msgrep (email.message.Message): Email message

        Returns:
            (dict): Dictionary storing attachments in list
        """

        if self._msgrep is None:
            return
        for part in self.walk_all_parts(self._msgrep):
            if part.is_multipart() and (part.get_filename() is None or skip_named_multipart):
                continue

            # use cached object if available
            cached_obj = self.att_file_dict.get(id(part))
            if cached_obj is not None:
                #---------------#
                # Cached object #
                #---------------#
                yield cached_obj
            else:
                #-----------------#
                # UNCached object #
                #-----------------#

                # process part, extract information needed to create Mailattachment
                (att_name, buffer, attsize, contenttype_mime,
                 maintype_mime, subtype_mime, ismultipart_mime,
                 content_charset_mime, isattachment, isinline,
                 defects, att_name_generated) = self.process_msg_part(part)
                att = Mailattachment(buffer, att_name, self, self.fugluid, filesize=attsize,
                                     contenttype_mime=contenttype_mime, maintype_mime=maintype_mime,
                                     subtype_mime=subtype_mime, ismultipart_mime=ismultipart_mime,
                                     content_charset_mime=content_charset_mime, is_attachment=isattachment,
                                     is_inline=isinline, defects=defects, filename_generated=att_name_generated,
                                     archive_passwords=archives_passwords or self._archive_passwords)
                yield att
        
    
    def process_msg_part(self, part):
        """
        Process message part, return tuple containing all information to create Mailattachment object

        Args:
            part (message part):

        Returns:
            tuple : tuple containing

        -   att_name             (string) : attachment filename
        -   buffer               (bytes)  : attachment buffer (must be type bytes)
        -   attsize              (int)    : attachment size in bytes
        -   contenttype_mime     (string) : content type
        -   maintype_mime        (string) : main content type
        -   subtype_mime         (string) : content subtype
        -   ismultipart_mime     (bool)   : multipart
        -   content_charset_mime (string) : charset for content
        -   isattachment         (bool)   : True if this is a direct mail attachment,
                                            not inline (Content-Disposition=inline)
        -   isinline             (bool)   : True if this is an inline mail attachment,
                                               not attachment (Content-Disposition=attachment)
        -   defects              (list)   : A list of strings containing errors during decoding
        -   att_name_generated   (bool)   : True if name has been generated (not in mail)

        """
        contenttype_mime = part.get_content_type()
        maintype_mime = part.get_content_maintype()
        subtype_mime = part.get_content_subtype()
        ismultipart_mime = part.is_multipart()
        content_charset_mime = part.get_content_charset()
        att_name = part.get_filename(None)
        defects = []
        att_name_generated = False

        # any error all parts are marked as attachment
        isattachment = True
        isinline = False
        
        try:
            content_disposition = part.get_content_disposition()
        except AttributeError:
            content_disposition = part.get("Content-Disposition", None)
            # here it is possible we get a Header object back

            if content_disposition is not None:
                try:
                    # include here to prevent cyclic import
                    from fuglu.shared import Suspect
                    content_disposition = Suspect.decode_msg_header(content_disposition, logid=self.fugluid)
                except Exception as e:
                    self.logger.error(f"{self.fugluid} error extracting attachment info using "
                                      f"Content-Disposition header : {force_uString(e, errors='ignore')}")
                    content_disposition = "attachment"

                try:
                    content_disposition = content_disposition.lower()
                except Exception as e:
                    self.logger.error(f"{self.fugluid} error extracting attachment info using "
                                      f"Content-Disposition header : {force_uString(e, errors='ignore')}")
                    content_disposition = "attachment"

        if content_disposition is None:
            isattachment = False
            isinline = False
        else:
            try:
                if "attachment" in content_disposition:
                    isattachment = True
                    isinline = False
                elif "inline" in content_disposition:
                    isattachment = False
                    isinline = True
            except AttributeError as e:
                self.logger.error(f"{self.fugluid} error extracting attachment info using "
                                  f"Content-Disposition header as string: {force_uString(e, errors='ignore')}")

        if att_name:
            # some filenames are encoded, try to decode
            try:
                # include here to prevent cyclic import
                from fuglu.shared import Suspect
                att_name = Suspect.decode_msg_header(att_name, logid=self.fugluid)
            except Exception:
                pass
            # for long filenames (<78 chars) not properly implementing
            # continuation according to RFC2231 we might end up with
            # line break in the filename. Even tough some operating systems
            # allow line breaks in filenames, better to remove them...
            att_name = att_name.replace('\r', '').replace('\n', '')
        else:
            #  --
            #  generate a filename
            #  --
            att_name_generated = True
            ct = part.get_content_type()
            if ct in MIMETYPE_EXT_OVERRIDES:
                ext = MIMETYPE_EXT_OVERRIDES[ct]
            else:
                exts = mimetypes.guess_all_extensions(ct)
                # reply is randomly sorted list, get consistent result
                if len(exts) > 0:
                    exts.sort()
                    ext = exts[0]
                else:
                    ext = None

            if ext is None:
                ext = ''

            if ext.strip() == '':
                att_name = "unnamed"
            else:
                if ext.startswith("."):
                    att_name = f'unnamed{ext}'
                else:
                    att_name = f'unnamed.{ext}'

        try:
            buffer = part.get_payload(decode=True)  # Py2: string, Py3: bytes
            if part.defects:
                newdefectstring = ",".join(defect.__doc__ for defect in part.defects)
                if any(isinstance(defect, BAD_DEFECTS) for defect in part.defects):
                    # try to correct
                    if any(isinstance(defect, email.errors.InvalidBase64LengthDefect) for defect in part.defects):
                        try:
                            # now split into lines
                            rawbufferlines = part.get_payload(decode=False).split()
                            rawbufferlinescorrected = []
                            for line in rawbufferlines:
                                # make sure line length is not larger than 76
                                linelimited = line[:76]
                                # make sure line length is a multiple of 4
                                if len(linelimited) % 4:
                                    linelimited = linelimited + (4-len(linelimited) % 4)*'0'
                                rawbufferlinescorrected.append(linelimited)
                            rawbuffer = '\r\n'.join(rawbufferlinescorrected)
                            import base64
                            buffer = base64.b64decode(rawbuffer)
                            self.logger.warning(f"{self.fugluid} Repaired payload for {att_name}, "
                                                f"Defects: {newdefectstring}")
                        except Exception as e:
                            defects.append(DEFECT_ATTPARSEERROR)
                            self.logger.warning(f"{self.fugluid} Could not get payload (repair failed: {e}) for {att_name}, "
                                                f"Defects: {newdefectstring}, "
                                                f"continue without decoding!")
                    else:
                        # add out own parsing error keyword
                        defects.append(DEFECT_ATTPARSEERROR)
                        self.logger.warning(f"{self.fugluid} Could not get payload for {att_name}, "
                                            f"Defects: {newdefectstring}, "
                                            f"continue without decoding!")

                else:
                    self.logger.warning(f"{self.fugluid} Problems getting payload for {att_name}, "
                                        f"Defect(s): {newdefectstring}, "
                                        "(but payload extraction should be successful)"
                                        )
                defects.extend([defect.__doc__ for defect in part.defects])
        except Exception as e:
            newdefectstring = force_uString(e, errors="ignore")
            self.logger.error(f"{self.fugluid} Could not get payload for {att_name}, "
                              f"Reason: {newdefectstring}, "
                              f"continue without decoding!")
            buffer = part.get_payload(decode=False)
            defects.append(newdefectstring)
            # add out own parsing error keyword
            defects.append(DEFECT_ATTPARSEERROR)

        # try to get size from buffer length
        try:
            attsize = len(buffer)
        except Exception:
            attsize = None

        return (att_name, buffer, attsize,
                contenttype_mime, maintype_mime,
                subtype_mime, ismultipart_mime,
                content_charset_mime, isattachment,
                isinline, defects, att_name_generated)

    @smart_cached_memberfunc(inputs=['att_file_dict', '_manually_added'])
    def get_fileslist(self, level: tp.Union[int, None] = 0,
                      maxsize_extract: tp.Optional[int] = None,
                      maxfiles_extract: tp.Optional[int] = None,
                      archives_passwords: tp.Optional[tp.List[str]] = None,
                      skip_named_multipart: bool = False,
                      ):
        """
        (Cached Member Function)

        Get list of all filenames attached to message. For given recursion level attached
        archives are extracted to get filenames.

        Internal member dependencies:
            - att_file_dict (dict): The internal dictionary storing attached files as Mailattachment objects.

        Keyword Args:
            level (in): Level up to which archives are opened to get file list (default: 0 -> only filenames directly attached)
            - maxsize_extract (int): maximum file size to extract if asked for the file object
            - maxfiles_extract (int): maximum number of files to extract from a single archive
            - archives_passwords (List of str): list of possible archive passwords
            - skip_named_multipart (bool): skip multipart attachments even when they're named (e.g. attached .eml)

        Returns:
            list[str]: list containing attached files with archives extracted to given level
        """
        file_list = []
        for att_obj in self.get_mailatt_generator(archives_passwords, skip_named_multipart):
            file_list.extend(att_obj.get_fileslist(0, level,
                                                   self.get_maxsize_extract(maxsize_extract),
                                                   self.get_maxfilenum_extract(maxfiles_extract)
                                                   )
                             )

        # add manually added attachment filenames
        file_list.extend(obj.filename for obj in self._manually_added)

        return file_list

    def get_objectlist(self, level: int = 0,
                       maxsize_extract: tp.Optional[int] = None,
                       noextractinfo: tp.Optional[NoExtractInfo] = None,
                       include_parents: bool = False,
                       maxfiles_extract: tp.Optional[int] = None,
                       archives_passwords: tp.Optional[tp.List[str]] = None,
                       skip_named_multipart: bool = False,
                       ):
        """
        Get list of all Mailattachment objects attached to message. For given recursion level attached
        archives are extracted.

        No caching allowed since objects might not be cached...

        Keyword Args:
            level (in): Level up to which archives are opened to get file list (default: 0 -> direct mail attachments)
            maxsize_extract (int, None): The maximum size for files to be extracted from archives
            noextractinfo (NoExtractInfo): stores info why object was not extracted
            include_parents (bool): True means extract the archives (depending on level) but return archive as well,
                                    not only the extracted files
            maxfiles_extract (in): The maximun number of files to extract in a single archive
            archives_passwords (List of str): list of possible archive passwords
            skip_named_multipart (bool): skip multipart attachments even when they're named (e.g. attached .eml)

        Returns:
            list[Mailattachment]: list containing attached files with archives extracted to given level
        """
        obj_list = []
        g = self.get_mailatt_generator(archives_passwords, skip_named_multipart)

        for att_obj in g:
            obj_list.extend(att_obj.get_objectlist(0, level,
                                                   self.get_maxsize_extract(maxsize_extract),
                                                   self.get_maxfilenum_extract(maxfiles_extract),
                                                   noextractinfo=noextractinfo, include_parents=include_parents))
        # add manually added mailattachments
        obj_list.extend(self._manually_added)

        return obj_list

    def get_fileslist_checksum(self, level: int = 0,
                               maxsize_extract: tp.Optional[int] = None,
                               methods: tp.Tuple = (),
                               noextractinfo: tp.Optional[NoExtractInfo] = None,
                               maxfiles_extract: tp.Optional[int] = None,
                               archives_passwords: tp.Optional[tp.List[str]] = None,
                               skip_named_multipart: bool = False,
                               ):
        """
        Get a list containg tuples (filanem, checksumdict) for all the extracted files up to a given extraction level

        Keyword Args:
            level (in): Level up to which archives are opened to get file list (default: 0 -> direct mail attachments)
            methods (set): set containing the checksum methods requested
            noextractinfo (NoExtractInfo): stores info why object was not extracted
            maxfiles_extract (int): maximum number of files to extract from a single archive
            archives_passwords (List of str): list of possible archive passwords
            skip_named_multipart (bool): skip multipart attachments even when they're named (e.g. attached .eml)

        Returns:
            list[(string, dict)]: list containing tuples (filename, checksumdict)
        """
        obj_list = []
        for att_obj in self.get_mailatt_generator(archives_passwords, skip_named_multipart):
            obj_list.extend(att_obj.get_objectlist(0, level,
                                                   self.get_maxsize_extract(maxsize_extract),
                                                   self.get_maxfilenum_extract(maxfiles_extract),
                                                   noextractinfo=noextractinfo))

        # add manually added mailattachments
        obj_list.extend(self._manually_added)

        checksumlist = []
        for obj in obj_list:
            checksumlist.append((obj.filename, obj.get_checksumdict(methods=methods)))
        return checksumlist

    def manual_add(self, buffer: bytes, filename: str, filesize: tp.Union[int, None] = None, contenttype_mime=None,
                   maintype_mime=None, subtype_mime=None, ismultipart_mime=None, content_charset_mime=None):
        """Manually add mailattachment to list independent of python message object linked...

        Args:
            buffer (bytes): buffer containing attachment source
            filename (str): filename of current attachment object
            filesize (int): file size in bytes (set to length of buffer if unset)
            contenttype_mime (str): The contenttype as defined in the mail attachment, only available for direct mail attachments
            maintype_mime (str): The main contenttype as defined in the mail attachment, only available for direct mail attachments
            subtype_mime (str): The sub-contenttype as defined in the mail attachment, only available for direct mail attachments
            ismultipart_mime (str): multipart as defined in the mail attachment, only available for direct mail attachments
            content_charset_mime (str): The characterset as defined in the mail attachment, only available for direct mail attachments
        """

        m = Mailattachment(buffer, filename if filename else "unknown", self, fugluid=self.fugluid, filesize=filesize if isinstance(filesize, int) else len(buffer), contenttype_mime=contenttype_mime,
                           maintype_mime=maintype_mime, subtype_mime=subtype_mime, ismultipart_mime=ismultipart_mime, content_charset_mime=content_charset_mime,
                           is_attachment=True, is_inline=False, filename_generated=bool(filename))
        self._manually_added.append(m)
