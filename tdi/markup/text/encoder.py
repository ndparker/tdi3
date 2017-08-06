# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2006 - 2017
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

=====================
 Text Output Encoder
=====================

Text Output Encoder.
"""
__author__ = u"Andr\xe9 Malo"
__docformat__ = "restructuredtext en"

from ... import c as _c
from .. import abstract as _abstract


@_abstract.impl('Encoder')
@_c.impl
class TextEncoder(object):
    """
    Encoder for text output

    :IVariables:
      `encoding` : ``str``
        Character encoding
    """
    # pylint: disable = no-self-use

    def __init__(self, encoding):
        """
        Initialization

        :Parameters:
          `encoding` : ``str``
            The target encoding
        """
        self.encoding = encoding

    def starttag(self, name, attr, closed):
        """ :See: `abstract.Encoder` """
        if str is bytes and not isinstance(name, bytes):
            raise TypeError("expected bytes")
        result = [b'[[' if closed else b'[', name]
        push = result.append
        for key, value in attr:
            push(b' ')
            if str is bytes and not isinstance(key, bytes):
                raise TypeError("expected bytes")
            push(key)
            if value is not None:
                push(b'=')
                if str is bytes and not isinstance(value, bytes):
                    raise TypeError("expected bytes")
                push(value)
        push(b']]' if closed else b']')
        return b''.join(result)

    def endtag(self, name):
        """ :See: `abstract.Encoder` """
        if str is bytes and not isinstance(name, bytes):
            raise TypeError("expected bytes")
        return name.join([b'[/', b']'])

    if bytes is str:
        def name(self, name):
            """ :See: `abstract.Encoder` """
            if isinstance(name, unicode):
                return name.encode(self.encoding, 'strict')
            return str(name)
    else:
        def name(self, name):
            """ :See: `abstract.Encoder` """
            if isinstance(name, bytes):
                return name
            return str(name).encode(self.encoding, 'strict')

    if bytes is str:
        def attribute(self, value):
            """ :See: `abstract.Encoder` """
            if isinstance(value, unicode):
                return (
                    value
                    .replace(u'\\', u'\\\\')
                    .replace(u'"', u'\\"')
                ).join([u'"', u'"']).encode(self.encoding, 'strict')

            return (
                str(value)
                .replace('\\', '\\\\')
                .replace('"', '\\"')
            ).join(['"', '"'])
    else:
        def attribute(self, value):
            """ :See: `abstract.Encoder` """
            if isinstance(value, bytes):
                return (
                    value
                    .replace(b'\\', b'\\\\')
                    .replace(b'"', b'\\"')
                ).join([b'"', b'"'])

            return (
                str(value)
                .replace('\\', '\\\\')
                .replace('"', '\\"')
            ).join(['"', '"']).encode(self.encoding, 'strict')

    if bytes is str:
        def content(self, value):
            """ :See: `abstract.Encoder` """
            if isinstance(value, unicode):
                return value.encode(self.encoding, 'strict')
            return str(value)
    else:
        def content(self, value):
            """ :See: `abstract.Encoder` """
            if isinstance(value, bytes):
                return value
            return str(value).encode(self.encoding, 'strict')

    if bytes is str:
        def encode(self, value):
            """ :See: `abstract.Encoder` """
            if isinstance(value, unicode):
                return value.encode(self.encoding, 'strict')
            return str(value)
    else:
        def encode(self, value):
            """ :See: `abstract.Encoder` """
            if isinstance(value, bytes):
                return value
            return str(value).encode(self.encoding, 'strict')

    if bytes is str:
        def escape(self, value):
            """ :See: `abstract.Encoder` """
            if isinstance(value, unicode):
                return value.replace(u'[', u'[]')
            return str(value).replace('[', '[]')
    else:
        def escape(self, value):
            """ :See: `abstract.Encoder` """
            if isinstance(value, bytes):
                return value.replace(b'[', b'[]')
            return str(value).replace('[', '[]')
