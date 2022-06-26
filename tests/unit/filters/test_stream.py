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

===============================
 Tests for tdi.filters._stream
===============================

Tests for tdi.filters._stream.
"""
__author__ = u"Andr\xe9 Malo"

import weakref as _weakref

from pytest import raises

from tdi.filters import _stream

from ... import _util as _test

# pylint: disable = missing-docstring, protected-access


def test_base_init():
    """ BaseStreamFilter inits and delegates properly """
    stream = _test.mock.MagicMock()
    del stream.meh
    inst = _stream.BaseStreamFilter(stream)
    assert inst._stream is stream
    assert type(inst).__name__ == 'BaseStreamFilter'

    with raises(AttributeError):
        inst.meh()

    inst.muh()
    assert _test.calls(stream) == [
        ('muh', (), {}),
    ]


def test_base_assign():
    """ BaseStreamFilter assigns stream """
    stream = _test.mock.MagicMock()
    stream2 = _test.mock.MagicMock()
    inst = _stream.BaseStreamFilter(stream)
    assert inst._stream is stream
    inst._stream = stream2
    assert inst._stream is stream2

    del inst._stream
    assert inst._stream is None

    with raises(RuntimeError) as e:
        delattr(inst, _test.badeqstr)
    assert e.value.args == ('yo',)

    with raises(AttributeError) as e:
        del inst.hah
    assert e.value.args in (
        ("'BaseStreamFilter' object has no attribute 'hah'",),
    )


def test_base_weakref():
    """ BaseStreamFilter accepts and clears weakrefs """
    stream = _test.mock.MagicMock()
    inst = _stream.BaseStreamFilter(stream)
    ref = _weakref.ref(inst)

    assert ref()._stream is stream
    del inst
    assert ref() is None


def test_base_bad_init():
    """ BaseStreamFilter deals with bad init """
    class Foo(_stream.BaseStreamFilter):
        def __init__(self):  # pylint: disable = super-init-not-called
            pass

    inst = Foo()

    assert inst._stream is None
    with raises(AttributeError) as e:
        inst.meh  # pylint: disable = pointless-statement
    assert e.value.args == ("'NoneType' object has no attribute 'meh'",)

    with raises(TypeError) as e:
        _stream.BaseStreamFilter()
    assert e.value.args in (
        # py3.10
        ("BaseStreamFilter.__init__() missing 1 required positional "
         "argument: 'stream'",),

        # py3.9
        ("__init__() missing 1 required positional argument: 'stream'",),

        # py2.7
        ('__init__() takes exactly 2 arguments (1 given)',),
    )


def test_filename_init():
    """ FilterFilename inits and delegates properly """
    stream = _test.mock.MagicMock()
    del stream.meh

    inst = _stream.StreamFilename(stream, 'bar.html')
    assert inst._stream is stream
    assert inst.filename == 'bar.html'

    with raises(AttributeError):
        inst.meh()

    inst.muh()
    assert _test.calls(stream) == [
        ('muh', (), {}),
    ]


def test_filename_weakref():
    """ FilterFilename accepts and clears weakrefs """
    stream = _test.mock.MagicMock()
    inst = _stream.StreamFilename(stream, 'foo.html')
    ref = _weakref.ref(inst)

    assert ref()._stream is stream
    assert ref().filename == 'foo.html'
    del inst
    assert ref() is None
