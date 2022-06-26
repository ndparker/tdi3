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

==============================
 Tests for tdi.filters._event
==============================

Tests for tdi.filters._event.
"""
__author__ = u"Andr\xe9 Malo"

import weakref as _weakref

from pytest import raises

from tdi.filters import _event

from ... import _util as _test

multi = _test.multi_impl(globals(), _event)
c = _test.c_impl(_event)

# pylint: disable = missing-docstring


@multi
def test_base_init():
    """ BaseEventFilter inits and delegates properly """
    builder = _test.mock.MagicMock()
    del builder.meh
    inst = _event.BaseEventFilter(builder)
    assert inst.builder is builder
    assert type(inst).__name__ == 'BaseEventFilter'

    with raises(AttributeError):
        inst.meh()

    inst.muh()
    assert _test.calls(builder) == [
        ('muh', (), {}),
    ]


@multi
def test_base_assign():
    """ BaseEventFilter assigns builder """
    builder = _test.mock.MagicMock()
    builder2 = _test.mock.MagicMock()
    inst = _event.BaseEventFilter(builder)
    assert inst.builder is builder
    inst.builder = builder2
    assert inst.builder is builder2

    del inst.builder
    assert inst.builder is None

    with raises(RuntimeError) as e:
        delattr(inst, _test.badeqstr)
    assert e.value.args == ('yo',)

    with raises(AttributeError) as e:
        del inst.hah
    assert e.value.args in (
        ("'BaseEventFilter' object has no attribute 'hah'",),
        ("'tdi.c._tdi_impl.BaseEventFilter' object has no attribute 'hah'",),
    )


@multi
def test_base_weakref():
    """ BaseEventFilter accepts and clears weakrefs """
    builder = _test.mock.MagicMock()
    inst = _event.BaseEventFilter(builder)
    ref = _weakref.ref(inst)

    assert ref().builder is builder
    del inst
    assert ref() is None


@multi
def test_base_bad_attr():
    """ BaseEventFilter deals with bad attributes """
    class Foo(_event.BaseEventFilter):
        @property
        def bad(self):
            raise RuntimeError('Duh')

    class Bar(_event.BaseEventFilter):
        def __getattr__(self, name):
            raise RuntimeError('Doh')

    class Baz(_event.BaseEventFilter):
        @property
        def __getattr__(self):
            # pylint: disable = invalid-overridden-method, unexpected-special-method-signature
            raise RuntimeError('Dah')

    builder = _test.mock.MagicMock()
    inst = Foo(builder)

    assert inst.builder is builder
    with raises(RuntimeError) as e:
        inst.bad  # pylint: disable = pointless-statement
    assert e.value.args == ('Duh',)

    inst = Bar(builder)
    assert inst.builder is builder
    with raises(RuntimeError) as e:
        inst.bad  # pylint: disable = pointless-statement
    assert e.value.args == ('Doh',)

    inst = Baz(builder)
    assert inst.builder is builder
    with raises(RuntimeError) as e:
        inst.bad  # pylint: disable = pointless-statement
    assert e.value.args == ('Dah',)


@multi
def test_base_bad_eq():
    """ BaseEventFilter deals with bad attribute names """
    builder = _test.mock.MagicMock()
    inst = _event.BaseEventFilter(builder)

    assert inst.builder is builder
    with raises(RuntimeError) as e:
        getattr(inst, _test.badeqstr)
    assert e.value.args == ('yo',)


@multi
def test_base_bad_init():
    """ BaseEventFilter deals with bad init """
    class Foo(_event.BaseEventFilter):
        def __init__(self):  # pylint: disable = super-init-not-called
            pass

    inst = Foo()

    assert inst.builder is None
    with raises(AttributeError) as e:
        inst.meh  # pylint: disable = pointless-statement
    assert e.value.args == ("'NoneType' object has no attribute 'meh'",)

    with raises(TypeError) as e:
        _event.BaseEventFilter()
    assert e.value.args in (
        # py3.10
        ("BaseEventFilter.__init__() missing 1 required positional "
         "argument: 'builder'",),

        # py3.9
        ("__init__() missing 1 required positional argument: 'builder'",),
        ("function missing required argument 'builder' (pos 1)",),

        # py2.7
        ('__init__() takes exactly 2 arguments (1 given)',),
        ("Required argument 'builder' (pos 1) not found",),
    )


@multi
def test_filename_init():
    """ FilterFilename inits and delegates properly """
    builder = _test.mock.MagicMock()
    del builder.meh
    inst = _event.FilterFilename(builder, 'bar.html')
    assert inst.builder is builder
    assert inst.filename == 'bar.html'

    with raises(AttributeError):
        inst.meh()

    inst.muh()
    assert _test.calls(builder) == [
        ('muh', (), {}),
    ]


@multi
def test_filename_weakref():
    """ FilterFilename accepts and clears weakrefs """
    builder = _test.mock.MagicMock()
    inst = _event.FilterFilename(builder, 'foo.html')
    ref = _weakref.ref(inst)

    assert ref().builder is builder
    assert ref().filename == 'foo.html'
    del inst
    assert ref() is None
