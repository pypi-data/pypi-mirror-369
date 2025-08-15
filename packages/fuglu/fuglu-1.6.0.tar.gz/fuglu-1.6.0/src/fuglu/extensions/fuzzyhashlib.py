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

"""
Abstraction layer for fuzzy hashing libraries.
"""

__all__ = ['hashers_available', 'digest']
hashers = {}

import typing as tp

try:
    import ssdeep
    hashers['ssdeep'] = (ssdeep.hash, None, None)
except ImportError:
    pass

try:
    import imagehash
    from PIL import Image
    from io import BytesIO
    def _infilter_imagehash(value):
        return Image.open(BytesIO(value))
    hashers['imagehash_average'] = (imagehash.average_hash, _infilter_imagehash, str)
    hashers['imagehash_color'] = (imagehash.colorhash, _infilter_imagehash, str)
    hashers['imagehash_cropresistant'] = (imagehash.crop_resistant_hash, _infilter_imagehash, str)
    hashers['imagehash_dhash'] = (imagehash.dhash, _infilter_imagehash, str)
    hashers['imagehash_phash'] = (imagehash.phash, _infilter_imagehash, str)
    hashers['imagehash_phashsimple'] = (imagehash.phash_simple, _infilter_imagehash, str)
    hashers['imagehash_whash'] = (imagehash.whash, _infilter_imagehash, str)
except ImportError:
    pass

try:
    import numpy
    import cv2
    def _infilter_cv2hash(value):
        nimg = numpy.frombuffer(value, dtype=numpy.uint8)
        cimg = cv2.imdecode(nimg, cv2.IMREAD_COLOR)
        return cimg
    def _outfilter_cv2hash(imghash):
        return imghash.tobytes().hex()
    hashers['opencvhash_average'] = (cv2.img_hash.averageHash, _infilter_cv2hash, _outfilter_cv2hash)
    hashers['opencvhash_blockmean'] = (cv2.img_hash.blockMeanHash, _infilter_cv2hash, _outfilter_cv2hash)
    hashers['opencvhash_colormoment'] = (cv2.img_hash.colorMomentHash, _infilter_cv2hash, _outfilter_cv2hash)
    hashers['opencvhash_marhildreth'] = (cv2.img_hash.marrHildrethHash, _infilter_cv2hash, _outfilter_cv2hash)
    hashers['opencvhash_phash'] = (cv2.img_hash.pHash, _infilter_cv2hash, _outfilter_cv2hash)
    hashers['opencvhash_radialvariance'] = (cv2.img_hash.radialVarianceHash, _infilter_cv2hash, _outfilter_cv2hash)
except ImportError:
    pass
    
    
hashers_available = list(hashers.keys())
STATUS = ','.join(hashers_available)
ENABLED = len(hashers_available)>0

def digest(method: str, buffer: tp.Union[str, bytes]) -> str:
    """
    get fuzzy digest of value
    :param method: fuzzy hashing method to be used. see hashers_available for a list of enabled and available hash methods
    :param buffer: the input to be fuzzy hashed. most hashers will expect bytes, some may accept str input
    :return: the fuzzy hash representation
    """
    if not method in hashers_available:
        raise KeyError(f'unsupported hash algorithm: {method}')
    hasher, infilter, outfilter = hashers[method]
    if infilter is not None:
        buffer = infilter(buffer)
    hashvalue = hasher(buffer)
    if outfilter is not None:
        hashvalue = outfilter(hashvalue)
    return hashvalue


