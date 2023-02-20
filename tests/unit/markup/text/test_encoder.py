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

===================================
 Tests for tdi.markup.text.encoder
===================================

Tests for tdi.markup.text.encoder.
"""
__author__ = u"Andr\xe9 Malo"

import weakref as _weakref

from pytest import raises

from tdi.markup.text import encoder as _encoder
from tdi.markup import abstract as _abstract

from .... import _util as _test

multi = _test.multi_impl(globals(), _encoder)
c = _test.c_impl(_encoder)
python = _test.python_impl(_encoder)


@multi
def test_init():
    """markup.encoder.text.TextEncoder() inits properly"""
    inst = _encoder.TextEncoder('foo')
    assert isinstance(inst, _abstract.Encoder)
    assert inst.encoding == 'foo'


@multi
def test_starttag_simple():
    """markup.encoder.text.TextEncoder().starttag() emits regular tags"""
    inst = _encoder.TextEncoder('foo')

    result = inst.starttag(b'xx', iter([]), False)
    assert result == b'[xx]'

    result = inst.starttag(
        b'yy', iter([(b'aa', None), (b'bb', b'cc')]), False
    )
    assert result == b'[yy aa bb=cc]'


@multi
def test_starttag_many_attributes():
    """markup.encoder.text.TextEncoder().starttag() deals with many attrs"""
    inst = _encoder.TextEncoder('foo')

    result = inst.starttag(
        b'yy',
        iter(
            [
                (b'aa', None),
                (b'bb', b'cc'),
                (b'x', None),
                (b'zz', b'vv'),
                (b'lalala', b'lololo'),
                (b'uauaua', b'l'),
            ]
        ),
        False,
    )
    assert result == b'[yy aa bb=cc x zz=vv lalala=lololo uauaua=l]'


@multi
def test_starttag_invalid_attributes():
    """
    markup.encoder.text.TextEncoder().starttag() deals with broken attrs
    """
    inst = _encoder.TextEncoder('foo')

    with raises(TypeError):
        inst.starttag(b'yy', iter([(b'aa', None), (u'bb', b'cc')]), False)

    with raises(TypeError):
        inst.starttag(b'yy', iter([(b'aa', None), (b'bb', u'cc')]), False)

    with raises(TypeError):
        inst.starttag(b'yy', None, False)

    with raises(RuntimeError):
        inst.starttag(b'yy', _test.baditer(RuntimeError()), False)

    with raises(TypeError):
        inst.starttag(b'yy', [None], False)

    with raises(ValueError):
        inst.starttag(b'yy', [()], False)

    with raises(RuntimeError):
        inst.starttag(b'xx', [_test.baditer(RuntimeError())], False)

    with raises(ValueError):
        inst.starttag(b'yy', [(b'x',)], False)

    with raises(RuntimeError):
        inst.starttag(b'xx', [_test.baditer(b'x', RuntimeError())], False)

    with raises(ValueError):
        inst.starttag(b'yy', [(b'x', b'y', b'z')], False)

    with raises(RuntimeError):
        inst.starttag(
            b'xx', [_test.baditer(b'x', b'y', RuntimeError())], False
        )


@multi
def test_starttag_closing():
    """markup.encoder.text.TextEncoder().starttag() emits closing tags"""
    inst = _encoder.TextEncoder('foo')

    result = inst.starttag(b'xx', iter([]), True)
    assert result == b'[[xx]]'

    result = inst.starttag(b'yy', iter([(b'aa', None), (b'bb', b'cc')]), True)
    assert result == b'[[yy aa bb=cc]]'


@multi
def test_starttag_badname():
    """markup.encoder.text.TextEncoder().starttag() deals with bad name"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(TypeError):
        inst.starttag(u'x', [], False)


@multi
def test_starttag_bad_closing():
    """markup.encoder.text.TextEncoder().starttag() deals with bad bool"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(RuntimeError):
        inst.starttag(b'x', [], _test.badbool)


@c
def test_starttag_arg_error():
    """markup.encoder.text.TextEncoder().starttag() checks arguments"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(TypeError):
        inst.starttag()  # pylint: disable = no-value-for-parameter


@multi
def test_endtag():
    """markup.encoder.text.TextEncoder().endtag() emits endtags"""
    inst = _encoder.TextEncoder('foo')

    result = inst.endtag(b'xx')
    assert result == b'[/xx]'


@multi
def test_endtag_badtype():
    """markup.encoder.text.TextEncoder().endtag() deals with bad type"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(TypeError):
        inst.endtag(u's')


@c
def test_endtag_arg_error():
    """markup.encoder.text.TextEncoder().endtag() checks arguments"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(TypeError):
        inst.endtag()  # pylint: disable = no-value-for-parameter


@multi
def test_name_unicode():
    """markup.encoder.text.TextEncoder().name() accepts unicode"""
    inst = _encoder.TextEncoder('utf-8')

    result = inst.name(u'Andr\xe9')
    assert result == b'Andr\xc3\xa9'


@multi
def test_name_bytes():
    """markup.encoder.text.TextEncoder().name() accepts bytes"""
    inst = _encoder.TextEncoder('utf-8')

    result = inst.name(b'Andr\xe9')
    assert result == b'Andr\xe9'


@c
def test_name_badstr():
    """markup.encoder.text.TextEncoder().name() raises on bad string"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(RuntimeError):
        inst.name(_test.badstr)


@c
def test_name_arg_error():
    """markup.encoder.text.TextEncoder().name() checks arguments"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(TypeError):
        inst.name()  # pylint: disable = no-value-for-parameter


@multi
def test_attribute_unicode():
    """markup.encoder.text.TextEncoder().attribute() accepts unicode"""
    inst = _encoder.TextEncoder('utf-8')

    result = inst.attribute(u'Andr\xe9')
    assert result == b'"Andr\xc3\xa9"'

    result = inst.attribute(u'A\\nd"r\xe9')
    assert result == b'"A\\\\nd\\"r\xc3\xa9"'

    result = inst.attribute(u'"An\\dr\xe9\\"')
    assert result == b'"\\"An\\\\dr\xc3\xa9\\\\\\""'


@multi
def test_attribute_bytes():
    """markup.encoder.text.TextEncoder().attribute() accepts bytes"""
    inst = _encoder.TextEncoder('utf-8')

    result = inst.attribute(b'Andr\xe9')
    assert result == b'"Andr\xe9"'

    result = inst.attribute(b'A\\nd"r\xe9')
    assert result == b'"A\\\\nd\\"r\xe9"'

    result = inst.attribute(b'"An\\dr\xe9\\"')
    assert result == b'"\\"An\\\\dr\xe9\\\\\\""'


@c
def test_attribute_badstr():
    """markup.encoder.text.TextEncoder().attribute() raises on bad str"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(RuntimeError):
        inst.attribute(_test.badstr)


@c
def test_attribute_arg_error():
    """markup.encoder.text.TextEncoder().attribute() checks arguments"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(TypeError):
        inst.attribute()  # pylint: disable = no-value-for-parameter


@multi
def test_content_unicode():
    """markup.encoder.text.TextEncoder().content() accepts unicode"""
    inst = _encoder.TextEncoder('utf-8')

    result = inst.content(u'Andr\xe9')
    assert result == b'Andr\xc3\xa9'


@multi
def test_content_bytes():
    """markup.encoder.text.TextEncoder().content() accepts bytes"""
    inst = _encoder.TextEncoder('utf-8')

    result = inst.content(b'Andr\xe9')
    assert result == b'Andr\xe9'


@c
def test_content_badstr():
    """markup.encoder.text.TextEncoder().content() raises on bad string"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(RuntimeError):
        inst.content(_test.badstr)


@c
def test_content_arg_error():
    """markup.encoder.text.TextEncoder().content() checks arguments"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(TypeError):
        inst.content()  # pylint: disable = no-value-for-parameter


@multi
def test_encode_unicode():
    """markup.encoder.text.TextEncoder().encode() accepts unicode"""
    inst = _encoder.TextEncoder('utf-8')

    result = inst.encode(u'Andr\xe9')
    assert result == b'Andr\xc3\xa9'


@multi
def test_encode_bytes():
    """markup.encoder.text.TextEncoder().encode() accepts bytes"""
    inst = _encoder.TextEncoder('utf-8')

    result = inst.encode(b'Andr\xe9')
    assert result == b'Andr\xe9'


@c
def test_encode_arg_error():
    """markup.encoder.text.TextEncoder().encode() checks arguments"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(TypeError):
        inst.encode()  # pylint: disable = no-value-for-parameter


@multi
def test_escape_unicode():
    """markup.encoder.text.TextEncoder().escape() accepts unicode"""
    inst = _encoder.TextEncoder('utf-8')

    result = inst.escape(u'Andr\xe9')
    assert result == u'Andr\xe9'

    result = inst.escape(u'A[ndr\xe9')
    assert result == u'A[]ndr\xe9'


@multi
def test_escape_bytes():
    """markup.encoder.text.TextEncoder().escape() accepts bytes"""
    inst = _encoder.TextEncoder('utf-8')

    result = inst.escape(b'Andr\xe9')
    assert result == b'Andr\xe9'

    result = inst.escape(b'Andr[\xe9')
    assert result == b'Andr[]\xe9'


@c
def test_escape_badstr():
    """markup.encoder.text.TextEncoder().escape() raises on bad str"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(RuntimeError):
        inst.escape(_test.badstr)


@c
def test_escape_arg_error():
    """markup.encoder.text.TextEncoder().escape() checks arguments"""
    inst = _encoder.TextEncoder('utf-8')
    with raises(TypeError):
        inst.escape()  # pylint: disable = no-value-for-parameter


@multi
def test_weakref():
    """markup.encoder.text.TextEncoder() accepts and clears weakrefs"""
    inst = _encoder.TextEncoder('foo')
    ref = _weakref.ref(inst)

    assert ref().encoding == 'foo'
    del inst
    assert ref() is None


@c
def test_new_argerror():
    """markup.encoder.text.TextEncoder() checks arguments"""
    with raises(TypeError):
        _encoder.TextEncoder()  # pylint: disable = no-value-for-parameter

    with raises(RuntimeError):
        _encoder.TextEncoder(_test.badstr)


@c
def test_setencoding():
    """markup.encoder.text.TextEncoder() accepts encoding"""
    inst = _encoder.TextEncoder('foo')
    inst.encoding = 'bar'

    assert inst.encoding == 'bar'

    with raises(RuntimeError):
        inst.encoding = _test.badstr
