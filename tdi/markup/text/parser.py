# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2012 - 2022
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

===================
 Text Parser Logic
===================

Text Parser.
"""
__author__ = u"Andr\xe9 Malo"

import re as _re

from ...exceptions import LexerEOFError, LexerFinalizedError
from ... import abstract as _abstract

#: Unicode type
#:
#: :Type: type
_UNI = type(u'')

#: Regex matcher for a start tag
#:
#: :Type: ``callable``
_START_MATCH = _re.compile(br'''
    \[
        (
            [^\\"'\[\]]*
            (?:
                (?:
                    "[^\\"]*(?:\\.[^\\"]*)*"
                  | '[^\\']*(?:\\.[^\\']*)*'
                )
                [^\\"'\[\]]*
            )*
        )
    \]
''', _re.X | _re.S).match

#: Regex matcher for an self-closed start tag
#:
#: :Type: callable
_CLOSED_START_MATCH = _re.compile(br'''
    \[
        (
            \[
            [^\\"'\[\]]*
            (?:
                (?:
                    "[^\\"]*(?:\\.[^\\"]*)*"
                  | '[^\\']*(?:\\.[^\\']*)*'
                )
                [^\\"'\[\]]*
            )*
            \]
        )
    \]
''', _re.X | _re.S).match

#: Regex iterator for extracting start tag attributes
#:
#: :Type: callable
_ATT_ITER = _re.compile(r'''
    \s*
    (?P<name>[^\s=\]]*)           # attribute name
    \s*
    (?:
        =
        (?P<value>                # optional value
            \s* "[^\\"]*(?:\\.[^\\"]*)*"
          | \s* '[^\\']*(?:\\.[^\\']*)*'
          | [^\\\s\]]*
        )
    )?
''', _re.X | _re.S).finditer


@_abstract.impl('Parser')
class TextLexer(object):
    """
    Text lexer - identify units to deal with in the parser

    Attributes:
      encoding (str):
        Encoding to apply when converting text input to bytes

      state (str):
        Current state's name
    """

    def __init__(self, listener, encoding='utf-8'):
        """
        Initialization

        Parameters:
          lister (abstract.Listener):
            The event listener

          encoding (str):
            Encoding to apply when converting text input to bytes
        """
        #: Listener for our events
        #:
        #: :Type: abstract.Listener
        self._listener = listener

        #: Current state
        #:
        #: :Type: callable
        self._state = self._lex_text
        self.state = 'TEXT'

        #: Current buffer
        #:
        #: :Type: str
        self._buffer = b''
        self.encoding = encoding

    def feed(self, food):
        """
        Feed the lexer new data

        Parameters:
          food (text or bytes):
            The data to process
        """
        if isinstance(food, _UNI):
            self._buffer += food.encode(self.encoding)
        else:
            self._buffer += bytes(food)
        self._lex()

    def finalize(self):
        """
        Finalize the lexer

        This processes the rest buffer (if any)

        Raises:
          LexerEOFError: The rest buffer could not be consumed
        """
        self._lex()
        if self._buffer:
            raise LexerEOFError("Unfinished parser state %r" % (self.state,))
        self.state, self._state = 'FINAL', self._lex_final

    def _lex(self):
        """ Analyze the current buffer """
        while self._buffer:
            if self._state():
                break

    def _lex_final(self):
        """
        Called after the lexer was finalized

        State: after all

        Raises:
          LexerFinalizedError: The lexer was already finalized (raised always)
        """
        raise LexerFinalizedError("The lexer was already finalized")

    def _lex_text(self):
        """
        Text lexer

        State: We are between tags or at the very beginning of the document
        and look for a ``[``.

        Returns:
          bool: Unfinished state?
        """
        data = self._buffer
        pos = data.find(b'[')
        if pos == 0:
            self.state, self._state = 'MARKUP', self._lex_markup
            return False
        elif pos == -1:
            self._buffer = b''
        else:
            self._buffer, data = data[pos:], data[:pos]
            self.state, self._state = 'MARKUP', self._lex_markup

        self._listener.handle_text(data)
        return False

    def _lex_markup(self):
        """
        Markup lexer

        State: We've hit a ``[`` character and now find out, what it's
        becoming

        Returns:
          bool: Unfinished state?
        """
        data = self._buffer
        if len(data) < 2:
            return True

        char = data[1:2]
        if char == b'/':
            self.state, self._state = 'ENDTAG', self._lex_endtag
        elif char == b'#':
            self.state, self._state = 'COMMENT', self._lex_comment
        elif char == b'?':
            self.state, self._state = 'PI', self._lex_pi
        elif char == b']':
            self.state, self._state = 'TEXT', self._lex_text
            self._listener.handle_escape(data[0:1], data[:2])
            self._buffer = data[2:]
        else:
            self.state, self._state = 'STARTTAG', self._lex_starttag

        return False

    def _lex_starttag(self):
        """
        Starttag lexer

        State: We've hit a ``[tag`` and now look for the ``]``

        Returns:
          bool: Unfinished State?
        """
        data = self._buffer
        match = _CLOSED_START_MATCH(data) or _START_MATCH(data)
        if match is None:
            return True

        pos = match.end()
        self._buffer, data = data[pos:], data[:pos]
        attrstring = match.group(1)

        # strip self-closing marker
        closed = attrstring.startswith(b'[')
        if closed:
            attrstring = attrstring[1:-1]

        # Doesn't make sense if there's nothing inside -> handle as text
        splitted = attrstring.split(None, 1)
        if not splitted:
            self._listener.handle_text(data)
            self.state, self._state = 'TEXT', self._lex_text
            return False

        name = splitted[0]
        if b'=' in name:
            name = b''
        elif len(splitted) == 1:
            attrstring = None
        else:
            attrstring = splitted[1]

        attr = []
        if attrstring:
            for match in _ATT_ITER(attrstring):
                key, value = match.group('name', 'value')
                if key or value is not None:
                    if value:
                        value = value.strip()
                    attr.append((key.strip(), value))
                else:  # bug in Python < 2.3.5 (fixed in rev 37262)
                    break

        self._listener.handle_starttag(name, attr, closed, data)
        self.state, self._state = 'TEXT', self._lex_text
        return False

    def _lex_endtag(self):
        """
        Endtag lexer

        State: We've hit ``[/``.

        Returns:
          bool: Unfinished state?
        """
        data = self._buffer
        pos = data.find(b']') + 1
        if pos == 0:
            return True

        self._buffer, data = data[pos:], data[:pos]
        name = data[2:-1].strip()

        self._listener.handle_endtag(name, data)
        self.state, self._state = 'TEXT', self._lex_text
        return False

    def _lex_comment(self):
        """
        Comment lexer

        State: We've hit ``[#``.

        Returns:
          bool: Unfinished state?
        """
        data = self._buffer
        if len(data) < 4:
            return True

        pos = data.find(b'#]', 2)
        if pos == -1:
            return True
        pos += 2
        self._buffer, data = data[pos:], data[:pos]

        self._listener.handle_comment(data)
        self.state, self._state = 'TEXT', self._lex_text
        return False

    def _lex_pi(self):
        """
        Processing instruction lexer

        State: We've hit a ``[?`` and now peek inside

        Returns:
          bool: Unfinished state?
        """
        data = self._buffer
        pos = data.find(b'?]', 2)
        if pos == -1:
            return True
        pos += 2

        self._buffer, data = data[pos:], data[:pos]

        self._listener.handle_pi(data)
        self.state, self._state = 'TEXT', self._lex_text
        return False


@_abstract.impl('Listener', 'Parser')
class TextParser(object):
    """ Text parser - semantically deal with units identified by the lexer """
