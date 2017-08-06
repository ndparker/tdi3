# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2017
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

=================
 ABC definitions
=================

ABCs used within this (sub)package.
"""
__author__ = u"Andr\xe9 Malo"
__docformat__ = "restructuredtext en"

from .. import _abstract

impl = _abstract.make_impl(globals())


class Decoder(_abstract.base):
    """
    Decoder ABC

    :IVariables:
      `encoding` : ``str``
        The source encoding
    """

    @_abstract.method
    def normalize(self, name):
        """
        Normalize a name

        :Parameters:
          `name` : ``str``
            The name to normalize

        :Return: The normalized name
        :Rtype: ``str``
        """

    @_abstract.method
    def decode(self, value, errors='strict'):
        """
        Decode an arbitrary value

        :Parameters:
          `value` : ``bytes``
            attribute value

          `errors` : ``str``
            Error handler description

        :Return: The decoded value
        :Rtype: text
        """

    @_abstract.method
    def attribute(self, value, errors='strict'):
        """
        Decode a raw attribute value

        :Parameters:
          `value` : ``bytes``
            Raw attribute value

          `errors` : ``str``
            Error handler description

        :Return: The decoded attribute
        :Rtype: text
        """


class Encoder(_abstract.base):
    """
    Encoder Interface

    :IVariables:
      `encoding` : ``str``
        The target encoding
    """

    @_abstract.method
    def starttag(self, name, attr, closed):
        """
        Build a starttag

        :Parameters:
          `name` : ``bytes``
            The tag name (already encoded)

          `attr` : iterable
            The tag attributes (``((name, value), ...)``), aleady quoted,
            escaped and encoded

          `closed` : ``bool``
            Closed tag?

        :Return: The starttag
        :Rtype: ``bytes``
        """

    @_abstract.method
    def endtag(self, name):
        """
        Build an endtag

        :Parameters:
          `name` : ``bytes``
            Tag name (already encoded)

        :Return: The endtag
        :Rtype: ``bytes``
        """

    @_abstract.method
    def name(self, name):
        """
        Encode a name (tag or attribute name)

        :Parameters:
          `name` : ``basestring``
            Name

        :Return: The encoded name
        :Rtype: ``bytes``
        """

    @_abstract.method
    def attribute(self, value):
        """
        Attribute encoder

        Note that this method also needs to put quotes around the attribute
        (if applicable).

        :Parameters:
          `value` : ``basestring``
            The value to encode

        :Return: The encoded attribute value
        :Rtype: ``bytes``
        """

    @_abstract.method
    def content(self, value):
        """
        Regular text content encoder

        :Parameters:
          `value` : ``basestring``
            The value to encode

        :Return: The encoded text
        :Rtype: ``bytes``
        """

    @_abstract.method
    def encode(self, value):
        """
        Character-encode a unicode string to `encoding`

        :Parameters:
          `value` : ``unicode``
            The value to encode

        :Return: The encoded value
        :Rtype: ``bytes``
        """

    @_abstract.method
    def escape(self, value):
        """
        Escape text (scan for sequences needing escaping and escape them)

        :Parameters:
          `value` : ``basestring``
            The value to escape

        :Return: The escaped value
        :Rtype: ``basestring``
        """
