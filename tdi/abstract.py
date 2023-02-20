# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2017 - 2023
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

from . import _abstract

base, method = _abstract.base, _abstract.method
impl = _abstract.make_impl(globals())

# pylint: disable = too-many-ancestors


class Parser(_abstract.base):
    """ ABC for template parsers """

    def feed(self, food):
        """
        Take a chunk of data and generate parser events out of it

        Parameters:
          food (text or bytes):
            The data to process
        """

    def finalize(self):
        """
        Finish the parser

        Calling `finalize` indicates that `feed` is not called any more
        and advises the parser to flush all pending events.
        """


class Listener(_abstract.base):
    """ ABC for a parser/lexer event listener """

    @_abstract.method
    def handle_text(self, data):
        """
        Handle text data

        Parameters:
          data (str):
            The text data to handle
        """

    @_abstract.method
    def handle_escape(self, escaped, data):
        """
        Handle escaped data

        Parameters:
          escaped (str):
            The escaped string (unescaped, despite the name)

          data (str):
            The full escape sequence
        """

    @_abstract.method
    def handle_starttag(self, name, attrs, closed, data):
        """
        Handle start tag (``<foo ....>``)

        Parameters:
          name (str):
            The element name (``''`` for empty tag)

          attrs (list):
            The attributes (``[(name, value), ...]``), where ``value``
            may be ``None`` for short attributes.

          closed (bool):
            Is the start tag closed? In that case, no endtag will be needed.

          data (str):
            The raw tag string
        """

    @_abstract.method
    def handle_endtag(self, name, data):
        """
        Handle end tag (``</foo>``)

        Parameters:
          name (str):
            The element name (``''`` for empty tag)

          data (str):
            The raw tag string
        """

    @_abstract.method
    def handle_comment(self, data):
        """
        Handle comment (``<!-- ... -->``)

        Parameters:
          data (str):
            The comment block
        """

    @_abstract.method
    def handle_msection(self, name, value, data):
        """
        Handle marked section (``<![name[...]]>`` or ``<![name ...]>``)

        The ``<![name ... ]>`` sections are MS specific. ``markupbase``
        comments::

          # An analysis of the MS-Word extensions is available at
          # http://www.planetpublish.com/xmlarena/xap/Thursday/WordtoXML.pdf

        Parameters:
          name (str):
            The section name

          value (str):
            The section value

          data (str):
            The section block
        """

    @_abstract.method
    def handle_decl(self, name, value, data):
        """
        Handle declaration (``<!...>``)

        Parameters:
          name (str):
            The name of the declaration block

          value (str):
            The value of the declaration block

          data (str):
            The declaration block
        """

    @_abstract.method
    def handle_pi(self, data):
        """
        Handle Processing instruction (``<? ... ?>``)

        Parameters:
          data (str):
            The PI block
        """


class BuildingListener(Listener):
    """
    Extensions to the listener interface

    Attributes:
      encoder (abstract.Encoder):
        Encoder

      decoder (abstract.Decoder):
        Decoder

      encoding (str):
        Encoding of the template

      analyze (abstract.AttributeAnalyzer):
        Attribute analyzer
    """

    @_abstract.method
    def handle_encoding(self, encoding):
        """
        Handle an encoding declaration

        Parameters:
          encoding (str):
            The encoding to handle
        """
