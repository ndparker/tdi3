# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2017 - 2022
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

from .. import _abstract

impl = _abstract.make_impl(globals())


class Decoder(_abstract.base):
    """
    Decoder ABC

    Attributes:
      encoding (str):
        The source encoding
    """

    @_abstract.method
    def normalize(self, name):
        """
        Normalize a name

        Parameters:
          name (str):
            The name to normalize

        Returns:
          str: The normalized name
        """

    @_abstract.method
    def decode(self, value, errors='strict'):
        """
        Decode an arbitrary value

        Parameters:
          value (bytes):
            attribute value

          errors (str):
            Error handler description

        Returns:
          text: The decoded value
        """

    @_abstract.method
    def attribute(self, value, errors='strict'):
        """
        Decode a raw attribute value

        Parameters:
          value (bytes):
            Raw attribute value

          errors (str):
            Error handler description

        Returns:
          text: The decoded attribute
        """


class Encoder(_abstract.base):
    """
    Encoder Interface

    Attributes:
      encoding (str):
        The target encoding
    """

    @_abstract.method
    def starttag(self, name, attr, closed):
        """
        Build a starttag

        Parameters:
          name (bytes):
            The tag name (already encoded)

          attr (iterable):
            The tag attributes (``((name, value), ...)``), aleady quoted,
            escaped and encoded

          closed (bool):
            Closed tag?

        Returns:
          bytes: The starttag
        """

    @_abstract.method
    def endtag(self, name):
        """
        Build an endtag

        Parameters:
          name (bytes):
            Tag name (already encoded)

        Returns:
          bytes: The endtag
        """

    @_abstract.method
    def name(self, name):
        """
        Encode a name (tag or attribute name)

        Parameters:
          name (str or bytes):
            Name

        Returns:
          bytes: The encoded name
        """

    @_abstract.method
    def attribute(self, value):
        """
        Attribute encoder

        Note that this method also needs to put quotes around the attribute
        (if applicable).

        Parameters:
          value (str or bytes):
            The value to encode

        Returns:
          bytes: The encoded attribute value
        """

    @_abstract.method
    def content(self, value):
        """
        Regular text content encoder

        Parameters:
          value (str or bytes):
            The value to encode

        Returns:
          bytes: The encoded text
        """

    @_abstract.method
    def encode(self, value):
        """
        Character-encode a unicode string to :attr:`encoding`

        Parameters:
          value (text):
            The value to encode

        Returns:
          bytes: The encoded value
        """

    @_abstract.method
    def escape(self, value):
        """
        Escape text (scan for sequences needing escaping and escape them)

        Parameters:
          value (str or bytes):
            The value to escape

        Returns:
          str or bytes: The escaped value
        """
