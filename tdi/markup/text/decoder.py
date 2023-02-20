# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2013 - 2023
 Andr\xe9 Malo or his licensors, as applicable

:License:

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

====================
 Text Input Decoder
====================

Text Input Decoder.
"""
__author__ = u"Andr\xe9 Malo"

import functools as _ft
import re as _re

from ... import c as _c
from ... import _util
from .. import abstract as _abstract


#: Backslash-escape Substituter
#:
#: :Type: callable
_SLASHSUB = _ft.partial(
    _re.compile(_util.ur(r'\\(.)'), _re.S).sub, _util.ur(r'\1')
)


@_abstract.impl('Decoder')
@_c.impl
class TextDecoder(object):
    """
    Decoder for text input

    :See: :class:`abstract.Decoder`
    """

    def __init__(self, encoding):
        """:See: :class:`abstract.Decoder`"""
        self.encoding = encoding

    def normalize(self, name):
        """:See: `abstract.Decoder`"""
        return name

    def decode(self, value, errors='strict'):
        """:See: :class:`abstract.Decoder`"""
        return value.decode(self.encoding, errors)

    def attribute(self, value, errors='strict'):
        """:See: :class:`abstract.Decoder`"""
        value = value.decode(self.encoding, errors)
        if value.startswith(u'"') or value.startswith(u"'"):
            value = value[1:-1]
        return _SLASHSUB(value)
