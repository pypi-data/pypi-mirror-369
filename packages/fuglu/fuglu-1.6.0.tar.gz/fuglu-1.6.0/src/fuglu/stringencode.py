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
import logging
from encodings.aliases import aliases

try:
    import chardet

    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False


class ForceUStringError(TypeError):
    pass


def try_encoding(u_inputstring, encoding="utf-8"):
    """Try to encode a unicode string

    Args:
        u_inputstring (unicode/str):
        encoding (str): target encoding type

    Returns:
        byte-string
    """
    if u_inputstring is None:
        return None

    # make sure encoding is not None or empty
    if not encoding:
        encoding = "utf-8"

    logger = logging.getLogger(f"{__package__ or 'fuglu'}.stringencode.try_encoding")
    try:
        return u_inputstring.encode(encoding, "strict")
    except UnicodeEncodeError as e:
        logger.error("Encoding error!")
        logger.exception(e)
        raise e


def try_decoding(b_inputstring, encodingGuess="utf-8", errors="strict"):
    """ Try to decode an encoded string

    This will raise exceptions if object can not be decoded. The calling
    routine has to handle the exception. For example, "force_uString" has
    to handle exceptions for sending non-encoded strings.

    Args:
        b_inputstring (str/bytes): input byte string
        encodingGuess (str): guess for encoding used, default assume unicode
        errors (str): error handling as in standard bytes.decode -> strict, ignore, replace
                        or strict+ignore, strict+replace (try strict first, on certain errors try ignore/replace)

    Returns:
        unicode string

    """
    if b_inputstring is None:
        return None

    # make sure encoding is not None or empty
    if not encodingGuess:
        encodingGuess = "utf-8"

    if '+' in errors:
        firsterrors, seconderrors = errors.split('+', 1)
    else:
        firsterrors = errors
        seconderrors = None

    logger = logging.getLogger(f"{__package__ or 'fuglu'}.stringencode.try_decoding")
    u_outputstring = None
    try:
        u_outputstring = b_inputstring.decode(encodingGuess, errors=firsterrors)
    except (UnicodeDecodeError, LookupError) as e:
        if seconderrors and str(e).endswith('invalid continuation byte'):
            try:
                u_outputstring = b_inputstring.decode(encodingGuess, errors=seconderrors)
            except (UnicodeDecodeError, LookupError) as f:
                e = f
        if not u_outputstring:
            # if we get here we will also print either the chardet or trial&error decoding message anyway
            logger.debug(f"found non {str(e)} encoding or encoding not found (msg: {encodingGuess}), try to detect encoding")

    if u_outputstring is None:
        if CHARDET_AVAILABLE:
            # limit to analyse max 10'000 characters because it might become very expensive
            encoding = chardet.detect(b_inputstring[:10000])['encoding']
            logger.info(f"chardet -> encoding estimated as {encoding}")
            try:
                u_outputstring = b_inputstring.decode(encoding, errors=firsterrors)
            except (UnicodeDecodeError, LookupError):
                logger.info(f"encoding found by chardet ({encoding}) does not work")
        else:
            logger.debug("module chardet not available -> skip autodetect")

    if u_outputstring is None:
        trialerrorencoding = EncodingTrialError.test_all(b_inputstring)
        logger.info(f"trial&error -> encoding estimated as one of (selecting first) {trialerrorencoding}")
        if trialerrorencoding:
            try:
                u_outputstring = b_inputstring.decode(trialerrorencoding[0], errors=firsterrors)
            except (UnicodeDecodeError, LookupError):
                logger.info(f"encoding found by trial & error ({trialerrorencoding}) does not work")

    if u_outputstring is None:
        raise UnicodeDecodeError

    return u_outputstring


def force_uString(inputstring, encodingGuess="utf-8", errors="strict", convert_none=False):
    """Try to enforce a unicode string

    Args:
        inputstring (str, unicode, list): input string or list of strings to be checked
        encodingGuess (str): guess for encoding used, default assume unicode
        errors (str): error handling as in standard bytes.decode -> strict, ignore, replace
                        or strict+ignore, strict+replace (try strict first, on certain errors try to ignore/replace)
        convert_none (bool): convert None to empty string if True

    Raises:
        ForceUStringError: if input is not string/unicode/bytes (or list containing such elements)

    Returns: unicode string (or list with unicode strings)

    """

    if isinstance(encodingGuess, str) and "unknown" in encodingGuess.lower():
        encodingGuess = "utf-8"

    if inputstring is None:
        return "" if convert_none else None
    elif isinstance(inputstring, list):
        return [force_uString(item, encodingGuess=encodingGuess, errors=errors) for item in inputstring]

    try:
        if isinstance(inputstring, str):
            return inputstring
        else:
            return try_decoding(inputstring, encodingGuess=encodingGuess, errors=errors)
    except (AttributeError, TypeError) as e:
        # Input might not be bytes but a number which is then
        # expected to be converted to unicode

        logger = logging.getLogger("fuglu.force_uString")
        if isinstance(inputstring, (int, float)):
            pass
        elif not isinstance(inputstring, (str, bytes)):
            logger.debug(f"object is not string/bytes/int/float but {str(type(inputstring))}")
        else:
            logger.debug(f"decoding failed using guess {encodingGuess} for object of type {str(type(inputstring))} with message {str(e)}")

        try:
            return str(inputstring)
        except (NameError, ValueError, TypeError, UnicodeEncodeError, UnicodeDecodeError) as e:
            logger.debug(f"Could not convert using 'str' -> error {e.__class__.__name__}: {str(e)}")
            pass
        except Exception as e:
            logger.debug(f"Could not convert using 'str' -> error {e.__class__.__name__}: {str(e)}")
            pass

        try:
            representation = str(repr(inputstring))
        except Exception as e:
            representation = f"({e.__class__.__name__}: {str(e)})"

        errormsg = f"Could not transform input object of type {str(type(inputstring))} with repr: {representation}"
        logger.error(errormsg)
        raise ForceUStringError(errormsg)


def force_bString(inputstring, encoding="utf-8", checkEncoding=False):
    """Try to enforce a string of bytes

    Args:
        inputstring (unicode, str, list): string or list of strings
        encoding (str): encoding type in case of encoding needed
        checkEncoding (bool): if input string is encoded, check type

    Returns: encoded byte string (or list with endcoded strings)

    """
    if inputstring is None:
        return None
    elif isinstance(inputstring, list):
        return [force_bString(item) for item in inputstring]

    try:
        if isinstance(inputstring, bytes):
            # string is already a byte string
            # since basic string type is unicode
            b_outString = inputstring
        else:
            # encode
            b_outString = try_encoding(inputstring, encoding)
    except (AttributeError, ValueError):
        # we end up here if the input is not a unicode/string
        # just try to first create a string and then encode it
        inputstring = force_uString(inputstring)
        b_outString = try_encoding(inputstring, encoding)

    if checkEncoding:
        # re-encode to make sure it matches input encoding
        return try_encoding(try_decoding(b_outString, encodingGuess=encoding), encoding=encoding)
    else:
        return b_outString


def force_bfromc(chars_iteratable):
    """Python 2 like bytes from char for Python 3

    Implemented to have the same char-byte conversion in Python 3 as in Python 2
    for special applications. In general, it is recommended to use the real
    str.encode() function for Python3

    Args:
        chars_iteratable (str or bytes): char-string to be byte-encoded

    Returns:
        bytes: a byte-string

    """
    if isinstance(chars_iteratable, bytes):
        return chars_iteratable
    elif isinstance(chars_iteratable, str):
        return bytes([ord(x) for x in chars_iteratable])
    else:
        raise AttributeError


def force_cfromb(bytes_iteratable):
    """Python 2 like chars from bytes for Python 3

    Implemented to have the same byte-char conversion in Python 3 as in Python 2
    for special applications. In general, it is recommended to use the real
    bytes.decode() function for Python3

    Args:
        bytes_iteratable (): byte-string

    Returns:
        str: chr - string

    """
    if isinstance(bytes_iteratable, str):
        return bytes_iteratable
    elif isinstance(bytes_iteratable, int):
        return chr(bytes_iteratable)
    elif isinstance(bytes_iteratable, bytes):
        return "".join([chr(x) for x in bytes_iteratable])
    elif isinstance(bytes_iteratable, list):
        return [force_cfromb(b) for b in bytes_iteratable]
    else:
        raise AttributeError(f"Type: {type(bytes_iteratable)} is not str and not bytes")


def _gen_all_encodings():
    """
    generate a sorted list of all encodings supported by current python version that are suitable for mail content encoding
    :return: list(str) list containing all encodings we want to test
    """
    enclist = ['utf_8', 'iso8859_15'] # encodings we want to test first
    excludes = {'rot_13', 'base64_codec', 'hex_codec', 'quopri_codec', 'bz2_codec', 'zlib_codec', 'uu_codec'} # encodings we don't want to test
    alias = set(aliases.values())
    alias = alias - set(enclist) - excludes
    alias = sorted(list(alias))
    enclist.extend(alias)
    return enclist
ALL_ENCODINGS = _gen_all_encodings()


class EncodingTrialError(object):
    
    @staticmethod
    def get_encodings_list():
        return ALL_ENCODINGS
    

    @staticmethod
    def test_all(bytestring, returnimmediately=False):
        """
        Test all known codecs if they can be used to decode an encoded string.
        A codec can be used if it is possible to decode the string without exception.
        Then after reencoding the string it should be the same as the original string.

        Args:
            bytestring (str, bytes): the encoded string
            returnimmediately (bool): if true function returns after the first working encoding found

        Returns:
            list(str) : list containing all encodings which passed the test

        """
        assert isinstance(bytestring, bytes)

        positive = []
        for enc in ALL_ENCODINGS:
            try:
                # encode and decode
                test_decoded = bytestring.decode(enc, "strict")
                test_reencoded = test_decoded.encode(enc, "strict")

                if not (isinstance(test_decoded, str) and isinstance(test_reencoded, bytes)):
                    raise TypeError()

                if bytestring == test_reencoded:
                    positive.append(enc)
                    if returnimmediately:
                        break
            except Exception:
                pass

        return positive
