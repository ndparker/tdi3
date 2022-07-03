# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2022
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

==================================
 Tests for tdi.markup.text.parser
==================================

Tests for tdi.markup.text.parser.
"""
__author__ = u"Andr\xe9 Malo"

from pytest import raises

from tdi.markup.text import parser as _parser
from tdi import abstract as _abstract

from .... import _util as _test

# pylint: disable = invalid-name, protected-access, missing-docstring


def test_Lexer_init():
    """ TextLexer() inits properly """
    listener = _test.mock.MagicMock()
    inst = _parser.TextLexer(listener)

    assert isinstance(inst, _abstract.Parser)
    assert inst._listener is listener
    assert inst._state == inst._lex_text  # pylint: disable = comparison-with-callable
    assert inst.state == 'TEXT'
    assert inst._buffer == b''
    assert inst.encoding == 'utf-8'

    assert _test.calls(listener) == []  # pylint: disable = use-implicit-booleaness-not-comparison


def test_Lexer_feed():
    """ TextLexer().feed() works as expected """
    mock = _test.mock.MagicMock()

    class Foo(_parser.TextLexer):
        def _lex(self):
            mock._lex(with_buffer=self._buffer)
            self._buffer = self._buffer[4:]
            return True

    inst = Foo(mock.listener)
    inst.feed(b'hallo')
    inst.feed(u'Andr\xe9')

    assert _test.calls(mock) == [
        ('_lex', (), {'with_buffer': b'hallo'}),
        ('_lex', (), {'with_buffer': b'oAndr\xc3\xa9'}),
    ]


def test_Lexer_finalize():
    """ TextLexer().finalize() works as expected """
    mock = _test.mock.MagicMock()

    class Foo(_parser.TextLexer):
        def _lex(self):
            mock._lex(self._buffer, self.state)
            self._buffer = self._buffer[4:]
            return True

    inst = Foo(mock.listener)
    inst.feed(b'hallo1234')

    with raises(_parser.LexerEOFError) as e:
        inst.finalize()
    assert e.value.args == ("Unfinished parser state 'TEXT'",)

    inst.feed(b'123b')
    inst.finalize()
    assert inst.state == 'FINAL'

    assert _test.calls(mock) == [
        ('_lex', (b'hallo1234', 'TEXT'), {}),
        ('_lex', (b'o1234', 'TEXT'), {}),
        ('_lex', (b'4123b', 'TEXT'), {}),
        ('_lex', (b'b', 'TEXT'), {}),
    ]


def test_Lexer_lex():
    """ TextLexer()._lex() works as expected """
    mock = _test.mock.MagicMock()

    class Foo(_parser.TextLexer):
        def _lex_text(self):
            mock._text(self._buffer, self.state)
            self._buffer = self._buffer[4:]
            self.state, self._state = 'HAH', self._lex_hah
            return False

        def _lex_hah(self):
            mock._hah(self._buffer, self.state)
            self._buffer = self._buffer[4:]
            self.state, self._state = 'TEXT', self._lex_text
            return True

    inst = Foo(mock.listener)
    inst.feed(b'hallo1234')
    assert _test.calls(mock) == [
        ('_text', (b'hallo1234', 'TEXT'), {}),
        ('_hah', (b'o1234', 'HAH'), {}),
    ]

    inst.feed(b'yikes')
    assert _test.calls(mock) == [
        ('_text', (b'hallo1234', 'TEXT'), {}),
        ('_hah', (b'o1234', 'HAH'), {}),
        ('_text', (b'4yikes', 'TEXT'), {}),
        ('_hah', (b'es', 'HAH'), {}),
    ]

    inst.feed(b'dd')
    assert _test.calls(mock) == [
        ('_text', (b'hallo1234', 'TEXT'), {}),
        ('_hah', (b'o1234', 'HAH'), {}),
        ('_text', (b'4yikes', 'TEXT'), {}),
        ('_hah', (b'es', 'HAH'), {}),
        ('_text', (b'dd', 'TEXT'), {}),
    ]


def test_Lexer_lex_final():
    """ TextLexer()._lex_final() works as expected """
    mock = _test.mock.MagicMock()
    inst = _parser.TextLexer(mock.listener)

    with raises(_parser.LexerFinalizedError) as e:
        inst._lex_final()
    assert e.value.args == ('The lexer was already finalized',)

    assert _test.calls(mock) == []  # pylint: disable = use-implicit-booleaness-not-comparison


def test_Lexer_lex_text():
    """ TextLexer()._lex_text() works as expected """
    mock = _test.mock.MagicMock()

    class Foo(_parser.TextLexer):
        def _lex_text(self):
            mock._lex_text(self._buffer, self.state)
            return super(Foo, self)._lex_text()

        def _lex_markup(self):
            mock._lex_markup(self._buffer, self.state)
            self._buffer = self._buffer[1:]
            self.state, self._state = 'TEXT', self._lex_text
            return True

    inst = Foo(mock.listener)

    inst.feed(b'lalala')
    assert _test.calls(mock) == [
        ('_lex_text', (b'lalala', 'TEXT'), {}),
        ('listener.handle_text', (b'lalala',), {}),
    ]

    inst.feed(b'[lalala')
    assert _test.calls(mock) == [
        ('_lex_text', (b'lalala', 'TEXT'), {}),
        ('listener.handle_text', (b'lalala',), {}),

        ('_lex_text', (b'[lalala', 'TEXT'), {}),
        ('_lex_markup', (b'[lalala', 'MARKUP'), {}),
    ]

    inst.feed(b'lal[ala')
    assert _test.calls(mock) == [
        ('_lex_text', (b'lalala', 'TEXT'), {}),
        ('listener.handle_text', (b'lalala',), {}),

        ('_lex_text', (b'[lalala', 'TEXT'), {}),
        ('_lex_markup', (b'[lalala', 'MARKUP'), {}),

        ('_lex_text', (b'lalalalal[ala', 'TEXT'), {}),
        ('listener.handle_text', (b'lalalalal',), {}),
        ('_lex_markup', (b'[ala', 'MARKUP'), {}),
    ]


def test_Lexer_lex_markup():
    """ TextLexer()._lex_markup() works as expected """
    mock = _test.mock.MagicMock()

    class Foo(_parser.TextLexer):
        def _lex_text(self):
            mock._lex_text(self._buffer, self.state)
            return super(Foo, self)._lex_text()

        def _lex_markup(self):
            mock._lex_markup(self._buffer, self.state)
            return super(Foo, self)._lex_markup()

        def _lex_endtag(self):
            mock._lex_endtag(self._buffer, self.state)
            self._buffer = b''
            self.state, self._state = 'TEXT', self._lex_text
            return True

        def _lex_comment(self):
            mock._lex_comment(self._buffer, self.state)
            self._buffer = b''
            self.state, self._state = 'TEXT', self._lex_text
            return True

        def _lex_pi(self):
            mock._lex_pi(self._buffer, self.state)
            self._buffer = b''
            self.state, self._state = 'TEXT', self._lex_text
            return True

        def _lex_starttag(self):
            mock._lex_starttag(self._buffer, self.state)
            self._buffer = b''
            self.state, self._state = 'TEXT', self._lex_text
            return True

    inst = Foo(mock.listener)

    inst.feed(b'[')
    inst.feed('/')
    assert _test.calls(mock) == [
        ('_lex_text', (b'[', 'TEXT'), {}),
        ('_lex_markup', (b'[', 'MARKUP'), {}),
        ('_lex_markup', (b'[/', 'MARKUP'), {}),
        ('_lex_endtag', (b'[/', 'ENDTAG'), {}),
    ]

    inst.feed(b'[#')
    assert _test.calls(mock) == [
        ('_lex_text', (b'[', 'TEXT'), {}),
        ('_lex_markup', (b'[', 'MARKUP'), {}),
        ('_lex_markup', (b'[/', 'MARKUP'), {}),
        ('_lex_endtag', (b'[/', 'ENDTAG'), {}),

        ('_lex_text', (b'[#', 'TEXT'), {}),
        ('_lex_markup', (b'[#', 'MARKUP'), {}),
        ('_lex_comment', (b'[#', 'COMMENT'), {}),
    ]

    inst.feed(b'[?')
    assert _test.calls(mock) == [
        ('_lex_text', (b'[', 'TEXT'), {}),
        ('_lex_markup', (b'[', 'MARKUP'), {}),
        ('_lex_markup', (b'[/', 'MARKUP'), {}),
        ('_lex_endtag', (b'[/', 'ENDTAG'), {}),

        ('_lex_text', (b'[#', 'TEXT'), {}),
        ('_lex_markup', (b'[#', 'MARKUP'), {}),
        ('_lex_comment', (b'[#', 'COMMENT'), {}),

        ('_lex_text', (b'[?', 'TEXT'), {}),
        ('_lex_markup', (b'[?', 'MARKUP'), {}),
        ('_lex_pi', (b'[?', 'PI'), {}),
    ]

    inst.feed(b'xx[]yy')
    assert _test.calls(mock) == [
        ('_lex_text', (b'[', 'TEXT'), {}),
        ('_lex_markup', (b'[', 'MARKUP'), {}),
        ('_lex_markup', (b'[/', 'MARKUP'), {}),
        ('_lex_endtag', (b'[/', 'ENDTAG'), {}),

        ('_lex_text', (b'[#', 'TEXT'), {}),
        ('_lex_markup', (b'[#', 'MARKUP'), {}),
        ('_lex_comment', (b'[#', 'COMMENT'), {}),

        ('_lex_text', (b'[?', 'TEXT'), {}),
        ('_lex_markup', (b'[?', 'MARKUP'), {}),
        ('_lex_pi', (b'[?', 'PI'), {}),

        ('_lex_text', (b'xx[]yy', 'TEXT'), {}),
        ('listener.handle_text', (b'xx',), {}),
        ('_lex_markup', (b'[]yy', 'MARKUP'), {}),
        ('listener.handle_escape', (b'[', b'[]'), {}),
        ('_lex_text', (b'yy', 'TEXT'), {}),
        ('listener.handle_text', (b'yy',), {}),
    ]

    inst.feed(b'[yy')
    assert _test.calls(mock) == [
        ('_lex_text', (b'[', 'TEXT'), {}),
        ('_lex_markup', (b'[', 'MARKUP'), {}),
        ('_lex_markup', (b'[/', 'MARKUP'), {}),
        ('_lex_endtag', (b'[/', 'ENDTAG'), {}),

        ('_lex_text', (b'[#', 'TEXT'), {}),
        ('_lex_markup', (b'[#', 'MARKUP'), {}),
        ('_lex_comment', (b'[#', 'COMMENT'), {}),

        ('_lex_text', (b'[?', 'TEXT'), {}),
        ('_lex_markup', (b'[?', 'MARKUP'), {}),
        ('_lex_pi', (b'[?', 'PI'), {}),

        ('_lex_text', (b'xx[]yy', 'TEXT'), {}),
        ('listener.handle_text', (b'xx',), {}),
        ('_lex_markup', (b'[]yy', 'MARKUP'), {}),
        ('listener.handle_escape', (b'[', b'[]'), {}),
        ('_lex_text', (b'yy', 'TEXT'), {}),
        ('listener.handle_text', (b'yy',), {}),

        ('_lex_text', (b'[yy', 'TEXT'), {}),
        ('_lex_markup', (b'[yy', 'MARKUP'), {}),
        ('_lex_starttag', (b'[yy', 'STARTTAG'), {}),
    ]
