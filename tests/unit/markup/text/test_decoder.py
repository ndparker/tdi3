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

===================================
 Tests for tdi.markup.text.decoder
===================================

"""
__author__ = u"Andr\xe9 Malo"
__docformat__ = "restructuredtext en"

import weakref as _weakref

from pytest import raises

from tdi.markup.text import decoder as _decoder
from tdi.markup import abstract as _abstract

from .... import _util as _test

multi = _test.multi_impl(globals(), _decoder)
c = _test.c_impl(_decoder)


@multi
def test_init():
    """ markup.decoder.text.TextDecoder() inits properly """
    inst = _decoder.TextDecoder('foo')
    assert isinstance(inst, _abstract.Decoder)
    assert inst.encoding == 'foo'


@multi
def test_normalize():
    """ markup.decoder.text.TextDecoder().normalize() just passes through """
    inst = _decoder.TextDecoder('foo')
    mocked = object()
    result = inst.normalize(mocked)
    assert result is mocked


@c
def test_normalize_arg_error():
    """ markup.decoder.text.TextDecoder().normalize() checks arguments """
    inst = _decoder.TextDecoder('utf-8')
    with raises(TypeError):
        inst.normalize()  # pylint: disable = no-value-for-parameter


@multi
def test_decode():
    """ markup.decoder.text.TextDecoder().decode() decodes to unicode """
    inst = _decoder.TextDecoder('utf-8')
    result = inst.decode(b'Andr\xc3\xa9')
    assert result == u'Andr\xe9'


@c
def test_decode_arg_error():
    """ markup.decoder.text.TextDecoder().decode() checks arguments """
    inst = _decoder.TextDecoder('utf-8')
    with raises(TypeError):
        inst.decode()  # pylint: disable = no-value-for-parameter


@c
def test_decode_badstring():
    """
    markup.decoder.text.TextDecoder().decode() raises errors on bad input
    """
    inst = _decoder.TextDecoder('utf-8')
    with raises(TypeError):
        inst.decode(b'xxx', _test.badstr)


@multi
def test_decode_strict_error():
    """ markup.decoder.text.TextDecoder().decode() raises on strict error """
    inst = _decoder.TextDecoder('utf-8')
    with raises(UnicodeDecodeError):
        inst.decode(b'Andr\xe9')


@multi
def test_attribute():
    """ markup.decoder.text.TextDecoder().attribute() decodes to unicode """
    inst = _decoder.TextDecoder('utf-8')

    result = inst.attribute(b'Andr\xc3\xa9')
    assert result == u'Andr\xe9'

    with raises(ValueError):
        inst.attribute(b'Andr\xe9')


@multi
def test_attribute_strip():
    """ markup.decoder.text.TextDecoder().attribute() strips decoded value """
    inst = _decoder.TextDecoder('utf-8')

    result = inst.attribute(b'"Andr\xc3\xa9')
    assert result == u'Andr'

    result = inst.attribute(b"'Andr\xc3\xa9")
    assert result == u'Andr'

    result = inst.attribute(b"")
    assert result == u''

    result = inst.attribute(b"''")
    assert result == u''

    result = inst.attribute(b"'x'")
    assert result == u'x'


@multi
def test_attribute_slash():
    """
    markup.decoder.text.TextDecoder().attribute() unslashes decoded value
    """
    inst = _decoder.TextDecoder('utf-8')
    result = inst.attribute(b'A\\n\\\\d\\r\xc3\xa9')
    assert result == u'An\\dr\xe9'

    result = inst.attribute(b'"A\\n\\\\d\\r\\\xc3\xa9')
    assert result == u'An\\dr\\'


@c
def test_attribute_arg_error():
    """ markup.decoder.text.TextDecoder().attribute() checks arguments """
    inst = _decoder.TextDecoder('utf-8')
    with raises(TypeError):
        inst.attribute()  # pylint: disable = no-value-for-parameter


@multi
def test_weakref():
    """ markup.decoder.text.TextDecoder() accepts and clears weakrefs """
    inst = _decoder.TextDecoder('foo')
    ref = _weakref.ref(inst)

    assert ref().encoding == 'foo'
    del inst
    assert ref() is None


@c
def test_new_argerror():
    """ markup.decoder.text.TextDecoder() checks arguments """
    with raises(TypeError):
        _decoder.TextDecoder()  # pylint: disable = no-value-for-parameter

    with raises(RuntimeError):
        _decoder.TextDecoder(_test.badstr)


@c
def test_setencoding():
    """ markup.decoder.text.TextDecoder() accepts encoding """
    inst = _decoder.TextDecoder('foo')
    inst.encoding = 'bar'

    assert inst.encoding == 'bar'

    with raises(RuntimeError):
        inst.encoding = _test.badstr
