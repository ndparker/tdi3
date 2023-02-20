# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2022 - 2023
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


def test_lexer():
    """TextLexer works as expected"""
    listener = _test.mock.MagicMock()

    lexer = _parser.TextLexer(listener)
    assert isinstance(lexer, _abstract.Parser)

    tpl = _test.dedent(
        """
        [? encoding=latin-1 ?]

        Hey [[who]]!

        [# some comment #]
        [mytag aname="foo" name2]
            jsklajsl[]f
        [/mytag]

        The end.
        [##]
        [  ]

        [unnamed=Foo]
    """
    )
    buflen = 3
    while tpl:
        buf, tpl = tpl[:buflen], tpl[buflen:]
        lexer.feed(buf)
    lexer.finalize()

    with raises(_parser.LexerFinalizedError) as e:
        lexer.feed('x')
    assert e.value.args == ('The lexer was already finalized',)

    assert _test.calls(listener) == [
        ('handle_pi', (b'[? encoding=latin-1 ?]',), {}),
        ('handle_text', (b'\n\n',), {}),
        ('handle_text', (b'Hey',), {}),
        ('handle_text', (b' ',), {}),
        ('handle_starttag', (b'who', [], True, b'[[who]]'), {}),
        ('handle_text', (b'!',), {}),
        ('handle_text', (b'\n\n',), {}),
        ('handle_comment', (b'[# some comment #]',), {}),
        ('handle_text', (b'\n',), {}),
        (
            'handle_starttag',
            (
                b'mytag',
                [(b'aname', b'"foo"'), (b'name2', None)],
                False,
                b'[mytag aname="foo" name2]',
            ),
            {},
        ),
        ('handle_text', (b'\n ',), {}),
        ('handle_text', (b'   ',), {}),
        ('handle_text', (b'jsk',), {}),
        ('handle_text', (b'laj',), {}),
        ('handle_text', (b'sl',), {}),
        ('handle_escape', (b'[', b'[]'), {}),
        ('handle_text', (b'f\n',), {}),
        ('handle_endtag', (b'mytag', b'[/mytag]'), {}),
        ('handle_text', (b'\n',), {}),
        ('handle_text', (b'\nTh',), {}),
        ('handle_text', (b'e e',), {}),
        ('handle_text', (b'nd.',), {}),
        ('handle_text', (b'\n',), {}),
        ('handle_comment', (b'[##]',), {}),
        ('handle_text', (b'\n',), {}),
        ('handle_text', (b'[  ]',), {}),
        ('handle_text', (b'\n\n',), {}),
        (
            'handle_starttag',
            (b'', [(b'unnamed', b'Foo')], False, b'[unnamed=Foo]'),
            {},
        ),
        ('handle_text', (b'\n',), {}),
    ]


def test_lexer_unfinished():
    """TextLexer bails on unfinished state"""
    listener = _test.mock.MagicMock()

    lexer = _parser.TextLexer(listener)

    tpl = _test.dedent(
        """
        [? encoding=latin-1 ?]

        [mytag aname="foo" name2
    """
    )
    buflen = 3
    while tpl:
        buf, tpl = tpl[:buflen], tpl[buflen:]
        lexer.feed(buf)

    with raises(_parser.LexerEOFError) as e:
        lexer.finalize()
    assert e.value.args == (
        "Unfinished parser state 'STARTTAG' at position 24 "
        "(line 2, column 0)",
    )

    assert _test.calls(listener) == [
        ('handle_pi', (b'[? encoding=latin-1 ?]',), {}),
        ('handle_text', (b'\n\n',), {}),
    ]


def test_lexer_smallbuf():
    """TextLexer: deals with smallbuf"""
    listener = _test.mock.MagicMock()

    lexer = _parser.TextLexer(listener)

    lexer.feed("[")
    lexer.feed("]")
    lexer.finalize()

    assert _test.calls(listener) == [
        ('handle_escape', (b'[', b'[]'), {}),
    ]
