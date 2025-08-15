# -*- coding: UTF-8 -*- #
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
# This content has been extracted from attachment.py and refactored
#
# How to use this file:
# For normal use, just import the class "Archivehandle". Check class description
# for more information how to use the class.

import logging
import zipfile
import tarfile
import gzip
import struct
import re
import os
import resource
import typing as tp
from unittest.mock import MagicMock
from fuglu.stringencode import force_uString

STATUS = "unknown"
ENABLED = True
MISSING = []
try:
    import rarfile
    RARFILE_AVAILABLE = True
    STATUS += ", rar"
except (ImportError, OSError):
    RARFILE_AVAILABLE = False
    MISSING.append('rar')

try:
    fitz = MagicMock()
    FITZ_AVAILABLE = False
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    pypdf = MagicMock()
    PYPDF_AVAILABLE = False
    try:
        import fitz
        FITZ_AVAILABLE = True
    except ImportError:
        MISSING.append('pdf')


# let's try to import both 7z libraries (easier for debugging)
# and prefer py7zr as it is easier to install and works on more platforms
SEVENZIP_AVAILABLE = False
SEVENZIP_PACKAGE = None
try:
    #raise ImportError()
    import py7zlib  # installed via pylzma library
    SEVENZIP_AVAILABLE = True
    SEVENZIP_PACKAGE = "py7zlib"
    py7zr = MagicMock()
except (ImportError, OSError):
    py7zlib = MagicMock()
    
try:
    import py7zr
    from _lzma import LZMAError
    SEVENZIP_AVAILABLE = True
    SEVENZIP_PACKAGE = "py7zr"
except (ImportError, OSError):
    py7zr = MagicMock
    class LZMAError(Exception):
        pass

if not SEVENZIP_AVAILABLE:
    MISSING.append('7z')


try:
    import psutil # external dependency
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

_CPUCOUNT = os.cpu_count() # cpu count shouldn't change during runtime, thus read only once

#-------------#
#- Interface -#
#-------------#
class Archive_int(object):
    """
    Archive_int is the interface for the archive handle implementations
    """

    def __init__(self, filedescriptor, archivename:tp.Optional[str]=None, pwd:tp.Optional[tp.List[str]]=None):
        self.logger = logging.getLogger(f'fuglu.extensions.filearchives.{self.__class__.__name__}')
        self._handle = None
        self._archivename = archivename
        if archivename is not None:
            try:
                self._archivename = os.path.basename(str(archivename))
            except Exception:
                pass
        if pwd is None:
            pwd = []
        elif pwd is not None and not isinstance(pwd, list):
            pwd = [pwd]
        self._passwords = pwd
        self.protected = False
        self.matching_password = None
        self._filesizes = {}

    def close(self) -> None:
        try:
            self._handle.close()
        except AttributeError:
            pass

    def namelist(self) -> tp.List[str]:
        """ Get archive file list

        Returns:
            (list) Returns a list of file paths within the archive
        """
        return []

    def filesize(self, path:str) -> int:
        """get extracted file size

        Args:
            path (str): is the filename in the archive as returned by namelist
        Raises:
            NotImplementedError because this routine has to be implemented by classes deriving
        """
        raise NotImplementedError()

    def extract(self, path:str, archivecontentmaxsize:int) -> tp.Optional[bytes]:
        """extract a file from the archive into memory

        Args:
            path (str): is the filename in the archive as returned by namelist
            archivecontentmaxsize (int): maximum file size allowed to be extracted from archive
        Returns:
            (bytes or None) returns the file content or None if the file would be larger than the setting archivecontentmaxsize

        """
        return None

    def protected_meta(self) -> bool:
        """Return true if metadata like file list is password protected"""
        return False
    
    def _parse_meminfo(self) -> int:
        if os.path.exists('/proc/meminfo'): # linux only
            with open('/proc/meminfo', 'r') as f:
                try:
                    for line in f.readlines():
                        if line.startswith('MemFree:'):
                            memkb = line.split()[1]
                            return int(memkb) * 1024
                except Exception as e:
                    self.logger.error(f'failed to parse /proc/meminfo due to {e.__class__.__name__}: {str(e)}')
        return 0
    
    def _get_free_memory(self) -> int:
        if PSUTIL_AVAILABLE:
            vmem = psutil.virtual_memory()
            maxavail = vmem.available
            del vmem # seems to be necessary to prevent random freezes a few mins later
            return int(maxavail)
        else:
            meminfo = self._parse_meminfo()
            if meminfo > 0:
                return meminfo
            else:
                memlock, _ = resource.getrlimit(resource.RLIMIT_MEMLOCK) # is this reasonable?
                memdata, _ = resource.getrlimit(resource.RLIMIT_DATA)
                return min(memlock, memdata)
    
    def max_extractsize(self, archivecontentmaxsize:tp.Optional[int]=None) -> int:
        free_memory = self._get_free_memory()
        free_memory = free_memory//(_CPUCOUNT*2+2) # use only as much as all fuglu procs could use, just to be sure!
        if archivecontentmaxsize is not None:
            maxsize = min(archivecontentmaxsize, free_memory)
        else:
            maxsize = free_memory
        #self.logger.debug(f'max extraction size {maxsize}b user defined {archivecontentmaxsize if archivecontentmaxsize else 0}b free memory {free_memory}b')
        return maxsize
    

# --------------------------- #
# - Archive implementations - #
# --------------------------- #
# Don't forget to add new implementations to the dict "archive_impl" and "archive_avail"
# below the implementations in class Archivehandle


class Archive_zip(Archive_int):
    def __init__(self, filedescriptor, archivename=None, pwd=None):
        super(Archive_zip, self).__init__(filedescriptor, archivename, pwd)
        self._handle = zipfile.ZipFile(filedescriptor)
        if self._archivename is None:
            try:
                self._archivename = os.path.basename(str(filedescriptor))
            except Exception:
                self._archivename = "generic.zip"

    def namelist(self):
        """ Get archive file list

        Returns:
            (list) Returns a list of file paths within the archive
        """
        return self._handle.namelist()

    def extract(self, path, archivecontentmaxsize):
        """extract a file from the archive into memory

        Args:
            path (str): is the filename in the archive as returned by namelist
            archivecontentmaxsize (int): maximum file size allowed to be extracted from archive
        Returns:
            (bytes or None) returns the file content or None if the file would be larger than the setting archivecontentmaxsize

        """
        maxsize = self.max_extractsize(archivecontentmaxsize)
        self.logger.debug(f'extracting {path} to size {maxsize} user defined {archivecontentmaxsize}')
        if self.filesize(path) > maxsize:
            return None
        
        ex = None
        data = None
        try:
            data = self._handle.read(path)
        except RuntimeError as e:
            ex = e
            if 'encrypted' in str(e):
                self.protected = True
                for pwd in self._passwords:
                    try:
                        pwd: str
                        data = self._handle.read(path, pwd.encode())
                        self.matching_password = pwd
                        break
                    except RuntimeError as e:
                        ex = e
        if data is None and ex is not None:
            raise ex
        return data

    def filesize(self, path):
        """get extracted file size

        Args:
            path (str): is the filename in the archive as returned by namelist
        Returns:
            (int) file size in bytes
        """
        if path in self._filesizes:
            return self._filesizes[path]
        filesize = self._handle.getinfo(path).file_size
        self._filesizes[path] = filesize
        return filesize


class Archive_rar(Archive_int):
    def __init__(self, filedescriptor, archivename=None, pwd=None):
        super(Archive_rar, self).__init__(filedescriptor, archivename, pwd)
        self._handle = rarfile.RarFile(filedescriptor)
        if self._archivename is None:
            try:
                self._archivename = os.path.basename(str(filedescriptor))
            except Exception:
                self._archivename = "generic.rar"

    def namelist(self):
        """ Get archive file list

        Returns:
            (list) Returns a list of file paths within the archive
        """
        return self._handle.namelist()

    def protected_meta(self):
        return (not self.namelist()) and self._handle.needs_password()

    def extract(self, path, archivecontentmaxsize):
        """extract a file from the archive into memory

        Args:
            path (str): is the filename in the archive as returned by namelist
            archivecontentmaxsize (int): maximum file size allowed to be extracted from archive
        Returns:
            (bytes or None) returns the file content or None if the file would be larger than the setting archivecontentmaxsize

        """
        maxsize = self.max_extractsize(archivecontentmaxsize)
        self.logger.debug(f'extracting {path} to size {maxsize} user defined {archivecontentmaxsize}')
        if self.filesize(path) > maxsize:
            return None
        
        ex = None
        data = None
        try:
            data = self._handle.read(path)
        except rarfile.PasswordRequired as e:
            self.protected = True
            ex = e
            for pwd in self._passwords:
                try:
                    data = self._handle.read(path, pwd)
                    self.matching_password = pwd
                    break
                except rarfile.BadRarFile as e:
                    ex = e
        if data is None and ex is not None:
            raise ex
        return data

    def filesize(self, path):
        """get extracted file size

        Args:
            path (str): is the filename in the archive as returned by namelist
        Returns:
            (int) file size in bytes
        """
        if path in self._filesizes:
            return self._filesizes[path]
        filesize = self._handle.getinfo(path).file_size
        self._filesizes[path] = filesize
        return filesize


class Archive_tar(Archive_int):
    def __init__(self, filedescriptor, archivename=None, pwd=None):
        super(Archive_tar, self).__init__(filedescriptor, archivename, pwd)
        try:
            self._handle = tarfile.open(fileobj=filedescriptor)
            if self._archivename is None:
                self._archivename = "generic.tar"
        except AttributeError:
            self._handle = tarfile.open(filedescriptor)
            if self._archivename is None:
                try:
                    self._archivename = os.path.basename(str(filedescriptor))
                except Exception:
                    self._archivename = "generic.tar"

    def namelist(self):
        """ Get archive file list

        Returns:
            (list) Returns a list of file paths within the archive
        """
        return self._handle.getnames() if self._handle else []

    def extract(self, path, archivecontentmaxsize):
        """extract a file from the archive into memory

        Args:
            path (str): is the filename in the archive as returned by namelist
            archivecontentmaxsize (int): maximum file size allowed to be extracted from archive
        Returns:
            (bytes or None) returns the file content or None if the file would be larger than the setting archivecontentmaxsize

        """
        maxsize = self.max_extractsize(archivecontentmaxsize)
        self.logger.debug(f'extracting {path} to size {maxsize} user defined {archivecontentmaxsize}')
        if self.filesize(path) > maxsize:
            return None

        arinfo = self._handle.getmember(path)
        if not arinfo.isfile():
            return None
        x = self._handle.extractfile(path)
        extracted = x.read()
        x.close()
        return extracted

    def filesize(self, path):
        """get extracted file size

        Args:
            path (str): is the filename in the archive as returned by namelist
        Returns:
            (int) file size in bytes
        """
        if path in self._filesizes:
            return self._filesizes[path]
        arinfo = self._handle.getmember(path)
        self._filesizes[path] = arinfo.size
        return arinfo.size


class Archive_7z(Archive_int):
    def __init__(self, filedescriptor, archivename=None, pwd=None):
        super(Archive_7z, self).__init__(filedescriptor, archivename, pwd)
        self._fdescriptor = None
        self._meta_protected = False
        try:
            self._handle = py7zlib.Archive7z(filedescriptor)
        except AttributeError:
            self._fdescriptor = open(filedescriptor, 'rb')
            self._handle = py7zlib.Archive7z(self._fdescriptor)
        except py7zlib.NoPasswordGivenError:
            self._meta_protected = True
        except Exception as e:
            # store setup exceptions like NoPasswordGivenError
            raise Exception(str(e) if str(e).strip() else e.__class__.__name__)

        if self._handle and self._archivename is None:
            try:
                self._archivename = os.path.basename(str(filedescriptor))
            except Exception:
                self._archivename = "generic.7z"

    def protected_meta(self):
        return self._meta_protected

    def namelist(self):
        """ Get archive file list

        Returns:
            (list) Returns a list of file paths within the archive
        """

        return self._handle.getnames() if self._handle else []

    def extract(self, path, archivecontentmaxsize):
        
        maxsize = self.max_extractsize(archivecontentmaxsize)
        self.logger.debug(f'extracting {path} to size {maxsize} user defined {archivecontentmaxsize}')
        if self.filesize(path) > maxsize:
            return None

        data = None
        try:
            data = self._handle.getmember(path).read()
        except py7zlib.NoPasswordGivenError:
            self.protected = True
            for pwd in self._passwords:
                try:
                    self._handle.password = pwd
                    data = self._handle.getmember(path).read()
                    self._handle.password = None
                    self.matching_password = pwd
                    break
                except py7zlib.WrongPasswordError:
                    pass
        except Exception as e:
            """
            py7zlib Exception doesn't contain a string, so convert name to have useful
            noExtractionInfo
            """
            if str(e).strip() == "":
                raise Exception(str(e.__class__.__name__))
            else:
                raise Exception(f"Reraising exception: {e}").with_traceback(e.__traceback__)

        if data is None:
            raise Exception('no data to unpack')
        return data

    def filesize(self, path):
        """get extracted file size

        Args:
            path (str): is the filename in the archive as returned by namelist
        Returns:
            (int) file size in bytes
        """
        
        if path in self._filesizes:
            return self._filesizes[path]
        arinfo = self._handle.getmember(path)
        self._filesizes[path] = arinfo.size
        return arinfo.size

    def close(self):
        """
        Close handle
        """
        super(Archive_7z, self).close()
        if self._fdescriptor is not None:
            try:
                self._fdescriptor.close()
            except Exception:
                pass
        self._fdescriptor = None


class Archive_7zr(Archive_int):
    def __init__(self, filedescriptor, archivename=None, pwd=None):
        super(Archive_7zr, self).__init__(filedescriptor, archivename, pwd)
        self._fdescriptor = filedescriptor
        self._meta_protected = False
        try:
            self._handle = py7zr.SevenZipFile(filedescriptor)
        except AttributeError:
            self.logger.debug(f'file descriptor {filedescriptor} seems to be a file')
            self._fdescriptor = open(filedescriptor, 'rb')
            self._handle = py7zr.SevenZipFile(self._fdescriptor)
        except py7zr.exceptions.PasswordRequired:
            self._meta_protected = True
        except Exception as e:
            # store setup exceptions like NoPasswordGivenError
            raise Exception(str(e) if str(e).strip() else e.__class__.__name__)

        if self._handle and self._archivename is None:
            try:
                self._archivename = os.path.basename(str(filedescriptor))
            except Exception:
                self._archivename = "generic.7z"

    def protected_meta(self):
        return self._meta_protected

    def namelist(self):
        """ Get archive file list

        Returns:
            (list) Returns a list of file paths within the archive
        """

        return self._handle.getnames() if self._handle else []

    def extract(self, path, archivecontentmaxsize):
        if not path.isascii():
            return None
        
        maxsize = self.max_extractsize(archivecontentmaxsize)
        filesize = self.filesize(path)
        self.logger.debug(f'extracting {path} to size {maxsize} user defined {archivecontentmaxsize} filesize {filesize}')
        if filesize > 0 and filesize > maxsize:
            return None
        
        ex = None
        output = None
        try:
            output = self._handle.read([path])
        except py7zr.exceptions.PasswordRequired as e:
            ex = e
            self.protected = True
            for pwd in self._passwords:
                try:
                    self._handle.close()
                    self._fdescriptor.seek(0)
                    self._handle = py7zr.SevenZipFile(self._fdescriptor, password=pwd)
                    output = self._handle.read(path)
                    self.matching_password = pwd
                except LZMAError as e:
                    ex = e
        finally:
            self._handle.reset()
            
        if output and path in output:
            filecontent = output[path].getvalue()
            return filecontent
        if output is None and ex is not None:
            raise ex
        return None

    def filesize(self, path):
        """
        get extracted file size

        Args:
            path (str): is the filename in the archive as returned by namelist
        Returns:
            (int) file size in bytes
        """
        filesize = 0
        if self._filesizes:
            return self._filesizes.get(path, filesize)
        
        for filecontent in self._handle.files:
            try:
                fs = filecontent.uncompressed
                self._filesizes[filecontent.filename] = fs
                if filecontent.filename == path:
                    filesize = fs
            except KeyError:
                pass
        return filesize

    def close(self):
        """
        Close handle
        """
        super(Archive_7zr, self).close()
        if self._fdescriptor is not None:
            try:
                self._fdescriptor.close()
            except Exception:
                pass
        self._fdescriptor = None


class Archive_gz(Archive_int):
    def __init__(self, filedescriptor, archivename=None, pwd=None):
        super(Archive_gz, self).__init__(filedescriptor, archivename, pwd)
        self._filesize = None
        # --
        # Python 3 gzip.open handles both filename and file object
        # --
        self._handle = gzip.open(filedescriptor)
        if isinstance(filedescriptor, (str, bytes)):
            try:
                self._archivename = os.path.basename(str(filedescriptor))
            except Exception:
                self._archivename = "generic.gz"
        else:
            if self._archivename is None:
                # if there is no archive name defined yet
                try:
                    # eventually it is possible to get the filename from
                    # the GzipFile object
                    self._archivename = os.path.basename(self._handle.name)
                    if not self._archivename:
                        # If input is io.BytesIO then the name attribute
                        # stores an empty string, set generic
                        self._archivename = "generic.gz"
                except Exception:
                    # any error, set generic
                    self._archivename = "generic.gz"
    
    def _read_gzip_info(self, gzipfile):
        # from https://stackoverflow.com/questions/15610587/how-to-read-filenames-included-into-a-gz-file/15610751#15610751
        if hasattr(gzipfile, 'fileobj'):
            gf = gzipfile.fileobj
        else:
            gf = gzipfile
        pos = gf.tell()
        # Read archive size
        gf.seek(-4, 2)
        size = struct.unpack('<I', gf.read())[0]
        gf.seek(0)
        magic = gf.read(2)
        if magic != b'\x1f\x8b':
            raise IOError(f'Not a gzipped file - got {magic}')
        method, flag, mtime = struct.unpack("<BBIxx", gf.read(8))
        if not flag & gzip.FNAME and hasattr(gzipfile, 'name'):
            # Not stored in the header, use the filename sans .gz
            gf.seek(pos)
            fname = gzipfile.name
            if fname.endswith('.gz'):
                fname = fname[:-3]
            return fname, size
        elif not flag & gzip.FNAME:
            # Not stored in the header, filename not available
            return None, size
        if flag & gzip.FEXTRA:
            # Read & discard the extra field, if present
            gf.read(struct.unpack("<H", gf.read(2)))
        # Read a null-terminated string containing the filename
        fname = []
        while True:
            s = gf.read(1)
            if not s or s==b'\000':
                break
            fname.append(s)
        gf.seek(pos)
        filename = b''.join(fname)
        return force_uString(filename), size

    
    def namelist(self):
        """ Get archive file list

        Returns:
            (list) Returns a list of file paths within the archive
        """
        try:
            # extract filename from archive header if present:
            genericfilename, size = self._read_gzip_info(self._handle)
        except Exception as e:
            self.logger.warning(f'failed to extract gz filename and size from file header due to {e.__class__.__name__}: {str(e)}')
            genericfilename = ''

        # try to create a name from the archive name
        # gzipping a file creates the archive name by appending ".gz"
        if not genericfilename:
            genericfilename = self._archivename

        if not genericfilename:
            genericfilename = "generic.unknown.gz"

        try:
            # get list of file extensions
            fileendinglist = Archivehandle.avail_archive_extensionlist4type['gz']
            replacedict = {"wmz": "wmf",
                           "emz": "emf"}
            for ending in fileendinglist:
                endingwithdot = "."+ending
                if genericfilename.endswith(endingwithdot):
                    if ending in replacedict:
                        genericfilename = genericfilename[:-len(ending)]+replacedict[ending]
                    else:
                        genericfilename = genericfilename[:-len(endingwithdot)]
                    break

        except Exception as e:
            self.logger.warning(f'failed to convert gz filename due to {e.__class__.__name__}: {str(e)}')
        return [genericfilename]

    def extract(self, path, archivecontentmaxsize):
        """extract a file from the archive into memory

        Args:
            path (str): is the filename in the archive as returned by namelist
            archivecontentmaxsize (int,None): maximum file size allowed to be extracted from archive
        Returns:
            (bytes or None) returns the file content or None if the file would be larger than the setting archivecontentmaxsize

        """
        
        maxsize = self.max_extractsize(archivecontentmaxsize)
        self.logger.debug(f'extracting {path} to size {maxsize} user defined {archivecontentmaxsize}')
        if self.filesize(path) > maxsize:
            return None

        initial_position = self._handle.tell()
        filecontent = self._handle.read()
        self._handle.seek(initial_position)
        return filecontent

    def filesize(self, path):
        """get extracted file size

        Args:
            path (str): is the filename in the archive as returned by namelist
        Returns:
            (int) file size in bytes
        """
        if path in self._filesizes:
            return self._filesizes[path]
        try:
            initial_position = self._handle.tell()
            self._handle.seek(0, os.SEEK_END)
            filesize = self._handle.tell()
            self._handle.seek(initial_position)
            self._filesizes[path] = filesize
            return filesize
        except Exception:
            return 0


class Archive_tgz(object):
    r"""
    Archive combining tar and gzip extractor

    This archive combining gzip/tar extractor arises from a problem created when
    Archive_gz was introduced:  Reason are files with content "application/(x-)gzip".

    implemented_archive_ctypes = {
        ...
        '^application\/gzip': 'gz'
        '^application\/x-gzip': 'gz'
        ...}

    Ctype is checked before file ending, so a file [*].tar.gz is detected as gzip, extracted to
    [*].tar and then needs a second extraction to [*] using tar archive extractor.
    This is inconsistent with previous behavior. A solution currently passing the tests is to
    remove "^application\/gzip","^application\/x-gzip" from the implemented_archive_ctypes dict.
    Like this, the archive extractor is selected based on the file ending which detects "tar.gz"
    as tar before ".gz" (as gzip)

    A second solution is the creation of Archive_tgz which allows to keep the content type detection.
    This extractor will first try tar extractor and if this fails the gz extractor. This has the advantage
    we can keep content detection for gzip and be backward compatible.
    """

    def __init__(self, filedescriptor, archivename=None, pwd=None):
        # first try extract using tar
        # check if it is possible to extract filenames
        try:
            self._archive_impl = Archive_tar(filedescriptor, archivename, pwd)
            filenamelist = self._archive_impl.namelist()
        except Exception as e:
            self._archive_impl = Archive_gz(filedescriptor, archivename, pwd)

    def __getattr__(self, name):
        """
        Delegate to implementation stored in self._archive_impl

        Args:
            name (str): name of attribute/method

        Returns:
            delegated result

        """
        return getattr(self._archive_impl, name)


class Archive_pdf(Archive_int):
    def __init__(self, filedescriptor, archivename=None, pwd=None):
        super(Archive_pdf, self).__init__(filedescriptor, archivename, pwd)
        filedescriptor.seek(0)
        self._rawdata = filedescriptor.read()
        filedescriptor.seek(0)
        if PYPDF_AVAILABLE:
            self._archive = pypdf.PdfReader(filedescriptor)
            self.protected = self._archive.is_encrypted
            if self.protected and pwd:
                for pw in self._passwords:
                    try:
                        self._archive.decrypt(pw)
                        break
                    except Exception:
                        pass
        elif FITZ_AVAILABLE:
            self._archive = fitz.open(None, filedescriptor.read(), 'pdf')
            self.protected = self._archive.is_encrypted or self._archive.needs_pass
            if self.protected and pwd:
                for pw in self._passwords:
                    try:
                        self._archive.authenticate(pw)
                        break
                    except Exception:
                        pass
        
        if self._archivename is None:
            try:
                self._archivename = os.path.basename(str(filedescriptor))
            except Exception:
                self._archivename = "generic.pdf"
        filedescriptor.seek(0)
        self._filenames = None
        self._filecontent = {}
    
    def close(self):
        if hasattr(self._archive, 'close'): # pypdf api doc sez has close, reality sez no / fitz has close
            self._archive.close()
        del self._archive

    def protected_meta(self):
        return self.protected
    
    def namelist(self):
        """ Get archive file list

        Returns:
            (list) Returns a list of file paths within the archive.
            as we do not have the actual filenames of text body and images,
            we autogenrate them based on their page number or content id
        """
        if self._filenames is not None:
            return self._filenames
        
        files = []
        if self.protected:
            return files
        
        if PYPDF_AVAILABLE:
            self._archive: pypdf.PdfReader
            catalog = self._archive.trailer["/Root"]
            if "/Names" in catalog and "/EmbeddedFiles" in catalog["/Names"]:
                filenames = catalog['/Names']['/EmbeddedFiles']['/Names']
                for filename in filenames:
                    i = filenames.index(filename) + 1
                    fileobj = filenames[i].get_object()
                    content = fileobj['/EF']['/F'].get_data()
                    self._filecontent[f'att_{force_uString(filename)}'] = content
            if "/JavaScript" in catalog:
                content = catalog['/JavaScript']
                self._filecontent[f'script_{self._archivename[:-4]}.js'] = content
            for pageno in range(len(self._archive.pages)):
                page = self._archive.pages[pageno]
                textpart = page.extract_text()
                if textpart:
                    filename = f'page_{pageno}.txt'
                    self._filecontent[filename] = textpart
                for count, image_file_object in enumerate(page.images):
                    try:
                        filename = f"image{count}_{image_file_object.name}"
                        self._filecontent[filename] = image_file_object.data
                    except NotImplementedError:
                        # ignore unsupported image formats, e.g. JBIG2Decode
                        pass
            files = list(self._filecontent.keys())
        elif FITZ_AVAILABLE:
            self._archive: fitz.Document
            try:
                files = list(self._archive.embfile_names())
            except Exception as e:
                with open(f'/tmp/{self._archivename}', 'wb') as f:
                    f.write(self._rawdata)
                self.logger.error(f'failed to open pdf file: {e.__class__.__name__}: {str(e)} - saved to /tmp/{self._archivename}')
                return []
            pageno = 1
            try:
                for page in self._archive:
                    textpart = page.get_text(sort=False)
                    if textpart:
                        filename = f'page_{pageno}.txt'
                        self._filecontent[filename] = textpart
                    for image in page.get_images():
                        imgdata = self._archive.extract_image(image[0])
                        filename = f'image_{image[0]}.{imgdata["ext"]}'
                        self._filecontent[filename] = imgdata['image']
                    pageno += 1
                    if pageno>2:
                        break
            except ValueError as e:
                with open(f'/tmp/{self._archivename}', 'wb') as f:
                    f.write(self._rawdata)
                self.logger.error(f'failed to open pdf file: {str(e)} - saved to /tmp/{self._archivename}')
                self.protected = True
            files.extend(list(self._filecontent.keys()))
        self._filenames = sorted(files)
        return files
    
    def extract(self, path, archivecontentmaxsize):
        """extract a file from the archive into memory

        Args:
            path (str): is the filename in the archive as returned by namelist
            archivecontentmaxsize (int): maximum file size allowed to be extracted from archive
        Returns:
            (bytes or None) returns the file content or None if the file would be larger than the setting archivecontentmaxsize

        """
        maxsize = self.max_extractsize(archivecontentmaxsize)
        filesize = self.filesize(path)
        self.logger.debug(f'extracting {path} to size {maxsize} user defined {archivecontentmaxsize} filesize {filesize}')
        if filesize > 0 and filesize > maxsize:
            return None
        
        if FITZ_AVAILABLE:
            for item in range(self._archive.embfile_count()):
                info = self._archive.embfile_info(item)
                if info.get('ufilename') == path:
                    return self._archive.embfile_get(item)
        if not self._filecontent:
            self.namelist()
        return self._filecontent.get(path)
        
    def filesize(self, path):
        """get extracted file size

        Args:
            path (str): is the filename in the archive as returned by namelist
        Returns:
            (int) file size in bytes
        """
        filedata = self._filecontent.get(path)
        if filedata:
            return len(filedata)


#--                  --#
#- use class property -#
#--                  --#
# inspired by:
# https://stackoverflow.com/questions/128573/using-property-on-classmethods
# Working for static getter implementation in Py2 and Py3


class classproperty(property):
    def __get__(self, obj, objtype=None):
        return super(classproperty, self).__get__(objtype)

#--------------------------------------------------------------------------#
#- The pubic available factory class to produce the archive handler class -#
#--------------------------------------------------------------------------#


class Archivehandle(object):
    """
    Archivehandle is actually the factory for the archive handle implementations.
    Besides being the factory, Archivehandle provides also dicts and lists of implemented
    and available archives based on different keys (for example file extension).

    (1) Using Archivehandle go get information about available archive handles:

    Examples:
        Archivehandle.avail('tar') # check if tar archives can be handled
        Archivehandle.avail('zip') # check if zip archives can be handled
        Archivehandle.avail_archives_list # returns a list of archives that can be handled, for example
                                          # [ "rar", "zip" ]
        Archivehandle.avail_archive_extensions_list # returns a list of archive extensions (sorted by extension length)
                                                    # for example ['tar.bz2', 'tar.gz', 'tar.xz', 'tar', 'zip', 'tgz']
        Archivehandle.avail_archive_ctypes_list # returns a list of mail content type regex expressions,
                                                # for example ['^application\\/x-tar', '^application\\/zip',
                                                               '^application\\/x-bzip2', '^application\\/x-gzip']

    (2) Use Archivehandle to create a handle to work with an archive:

    Example:
        handle = Archivehandle('zip','test.zip') # get a handle
        files = handle.namelist()        # get a list of files contained in archive
        firstfileContent = handle.extract(files[0],500000) # extract first file if smaller than 0.5 MB
        print(firstfileContent)          # print content of first file extracted
    """

    # Dict mapping implementations to archive type string
    archive_impl = {
        "zip": Archive_zip,
        "rar": Archive_rar,
        "tar": Archive_tar,
        "7z": Archive_7z if SEVENZIP_PACKAGE == "py7zlib" else Archive_7zr,
        "tgz": Archive_tgz,
        "gz": Archive_gz,
        "pdf": Archive_pdf,
    }

    # Dict storing if archive type is available
    archive_avail = {
        "zip": True,
        "rar": RARFILE_AVAILABLE,
        "tar": True,
        "7z": SEVENZIP_AVAILABLE,
        "gz": True,
        "tgz": True,
        "pdf": PYPDF_AVAILABLE or FITZ_AVAILABLE
        }

    # key: regex matching content type as returned by file magic, value: archive type
    implemented_archive_ctypes = {
        r'^application\/zip': 'zip',
        r'^application\/x-tar': 'tar',
        r'^application\/x-gzip': 'tgz',
        r'^application\/x-bzip2': 'tar',
        r'^application\/x-xz': 'tar',
        r'^application\/gzip': 'tgz',
        r'^application\/x-rar': 'rar',           # available only if RARFILE_AVAILABLE
        r'^application\/x-7z-compressed': '7z',  # available only if SEVENZIP_AVAILABLE
        r'^application\/pdf': 'pdf',             # available only if PYPDF_AVAILABLE or FITZ_AVAILABLE
    }

    # key: file ending, value: archive type
    implemented_archive_extensions = {
        'zip': 'zip',
        'z': 'zip',
        'tar': 'tar',
        'tar.gz': 'tar',
        'tgz': 'tar',
        'tar.bz2': 'tar',
        'tar.xz': 'tar',
        'gz': 'gz',
        'emz': 'gz',
        'wmz': 'gz',
        'rar': 'rar',  # available only if RARFILE_AVAILABLE
        '7z': '7z',    # available only if SEVENZIP_AVAILABLE
        'pdf': 'pdf',  # available only if PYPDF_AVAILABLE or FITZ_AVAILABLE
    }

    # --
    # dicts and lists containing information about available
    # archives are set up automatically (see below in metaclass)
    # --

    # "avail_archives_list" is a list of available archives based on available implementations
    _avail_archives_list = None

    # avail_archive_ctypes_list is a list of available ctypes based on available implementations
    _avail_archive_ctypes_list = None

    # avail_archive_ctypes is a dict, set automatically based on available implementations
    # key:   regex matching content type as returned by file magic (see filetype.py)
    # value: archive type
    _avail_archive_ctypes = None

    # "avail_archive_extensions_list" is a list of available filetype extensions.
    # sorted by length, so tar.gz is checked before .gz
    _avail_archive_extensions_list = None

    # "avail_archive_extensions" dict with available archive types for file extensions
    # key: file ending
    # value: archive type
    _avail_archive_extensions = None

    # "avail_archive_extensionlist" dict with list of file extensions for given archive type
    # key: archive type
    # value: list with file endings
    _avail_archive_extensionlist4type = None

    @classproperty
    def avail_archive_extensions_list(cls):
        # first time this list has to be created based on what's available
        if cls._avail_archive_extensions_list is None:
            # sort by length, so tar.gz is checked before .gz
            newList = sorted(cls.avail_archive_extensions.keys(), key=lambda x: len(x), reverse=True)
            cls._avail_archive_extensions_list = newList
        return cls._avail_archive_extensions_list

    @classproperty
    def avail_archives_list(cls):
        # first time this list has to be created based on what's available
        if cls._avail_archives_list is None:
            tlist = []
            for atype, available in iter(Archivehandle.archive_avail.items()):
                if available:
                    tlist.append(atype)
            cls._avail_archives_list = tlist
        return cls._avail_archives_list

    @classproperty
    def avail_archive_ctypes(cls):
        # first time this dict has to be created based on what's available
        if cls._avail_archive_ctypes is None:
            newDict = {}
            for regex, atype in iter(Archivehandle.implemented_archive_ctypes.items()):
                if Archivehandle.avail(atype):
                    newDict[regex] = atype
            cls._avail_archive_ctypes = newDict

        return cls._avail_archive_ctypes

    @classproperty
    def avail_archive_ctypes_list(cls):
        # first time this list has to be created based on what's available
        if cls._avail_archive_ctypes_list is None:
            tlist = []
            for ctype, atype in iter(Archivehandle.avail_archive_ctypes.items()):
                if Archivehandle.avail(atype):
                    tlist.append(ctype)
            cls._avail_archive_ctypes_list = tlist
        return cls._avail_archive_ctypes_list

    @classproperty
    def avail_archive_extensions(cls):
        # first time this dict has to be created based on what's available
        if cls._avail_archive_extensions is None:
            newDict = {}
            for regex, atype in iter(Archivehandle.implemented_archive_extensions.items()):
                if Archivehandle.avail(atype):
                    newDict[regex] = atype
            cls._avail_archive_extensions = newDict

        return cls._avail_archive_extensions

    @classproperty
    def avail_archive_extensionlist4type(cls):
        # first time this dict has to be created based on what's available
        if cls._avail_archive_extensionlist4type is None:
            newDict = {}
            for regex, atype in iter(Archivehandle.implemented_archive_extensions.items()):
                # regex is the file extension
                # atype is the archive type
                if Archivehandle.avail(atype):
                    try:
                        # append ending to list of endings for given archive type
                        newDict[atype].append(regex)
                    except KeyError:
                        # create a new list for given archive type containg current file ending
                        newDict[atype] = [regex]
            cls._avail_archive_extensionlist4type = newDict
        return cls._avail_archive_extensionlist4type

    @classmethod
    def register(cls,
                 archivemanager: Archive_int,
                 archive_type: str,
                 archive_ctypes: tp.Union[tp.List[str], str] = (),
                 archive_extensions: [tp.List[str], str] = (),
                 ):
        """Method to add custom archive managers"""
        archive_type = archive_type.lower().strip()
        archive_ctypes = [archive_ctypes] if isinstance(archive_ctypes, str) else archive_ctypes
        archive_extensions = [archive_extensions] if isinstance(archive_extensions, str) else archive_extensions

        if not cls.archive_avail.get(archive_type, False):
            cls.archive_avail[archive_type] = True
            cls.archive_impl[archive_type] = archivemanager
            for ctype in archive_ctypes:
                cls.implemented_archive_ctypes[archive_type] = ctype
            for ext in archive_extensions:
                cls.implemented_archive_extensions[archive_type] = ext

            # reset calculated class properties
            cls._avail_archives_list = None
            cls._avail_archive_ctypes_list = None
            cls._avail_archive_ctypes = None
            cls._avail_archive_extensions_list = None
            cls._avail_archive_extensions = None
            cls._avail_archive_extensionlist4type = None

    @staticmethod
    def impl(archive_type):
        """
        Checks if archive type is implemented
        Args:
            archive_type (Str): Archive type to be checked, for example ('zip','rar','tar','7z')

        Returns:
            True if there is an implementation

        """
        return archive_type in Archivehandle.archive_impl

    @staticmethod
    def avail(archive_type):
        """
        Checks if archive type is available
        Args:
            archive_type (Str): Archive type to be checked, for example ('zip','rar','tar','7z')

        Returns:
            True if archive type is available

        """
        if not Archivehandle.impl(archive_type):
            return False
        return Archivehandle.archive_avail[archive_type]

    @staticmethod
    def archive_type_from_content_type(content_type, all_impl=False, custom_ctypes_dict=None):
        """
        Return the corresponding archive type if the content type matches a regex , None otherwise

        Args:
            content_type (str): content type string
            all_impl (bool): check all implementations, not only the ones available
            custom_ctypes_dict (dict): dict with custom mapping (key: regex matching content type as returned by file magic, value: archive type)

        Returns:
            (str or None) archive type

        """

        if content_type is None:
            return None

        archive_type = None
        if all_impl:
            ctypes2check = Archivehandle.implemented_archive_ctypes
        elif custom_ctypes_dict is not None:
            ctypes2check = custom_ctypes_dict
        else:
            ctypes2check = Archivehandle.avail_archive_ctypes

        for regex, atype in iter(ctypes2check.items()):
            if re.match(regex, content_type, re.I):
                archive_type = atype
                break

        return archive_type

    @staticmethod
    def archive_type_from_extension(att_name, all_impl=False, custom_extensions_dict=None):
        """
        Return the corresponding archive type if the extension matches regex , None otherwise

        Args:
            att_name (str): filename
            all_impl (bool): check all implementations, not only the ones available
            custom_extensions_dict (dict): dict with custom mapping (key: regex matching content type as returned by file magic, value: archive type)

        Returns:
            (str or None) archive type

        """
        if att_name is None:
            return None

        if all_impl:
            sorted_ext_dict = Archivehandle.implemented_archive_extensions
            # sort by length, so tar.gz is checked before .gz
            sorted_ext_list = sorted(sorted_ext_dict.keys(), key=lambda x: len(x), reverse=True)
        elif custom_extensions_dict is not None:
            sorted_ext_dict = custom_extensions_dict
            # sort by length, so tar.gz is checked before .gz
            sorted_ext_list = sorted(sorted_ext_dict.keys(), key=lambda x: len(x), reverse=True)
        else:
            sorted_ext_dict = Archivehandle.avail_archive_extensions
            # this list is already sorted
            sorted_ext_list = Archivehandle.avail_archive_extensions_list

        archive_type = None
        for arext in sorted_ext_list:
            if att_name.lower().endswith(f'.{arext}'):
                archive_type = sorted_ext_dict[arext]
                break
        return archive_type

    def __new__(cls, archive_type, filedescriptor, archivename=None, pwd=None):
        """
        Factory method that will produce and return the correct implementation depending
        on the archive type

        Args:
            archive_type (str): archive type ('zip','rar','tar','7z')
            filedescriptor (): file-like object (io.BytesIO) or path-like object (str or bytes with filename including path)
        """

        assert Archivehandle.impl(archive_type), f'Archive type {archive_type} not in list of supported types: {",".join(Archivehandle.archive_impl.keys())}'
        assert Archivehandle.avail(archive_type), f'Archive type {archive_type} not in list of available types: {",".join(Archivehandle.avail_archives_list)}'
        return Archivehandle.archive_impl[archive_type](filedescriptor, archivename, pwd)


def _gen_status() -> str:
    status = f'available: {", ".join(dict(Archivehandle.avail_archive_extensions).keys())}'
    if MISSING:
        status += "; not available: "+", ".join(MISSING)
    return status
STATUS = _gen_status()