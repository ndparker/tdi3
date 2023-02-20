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

===================================
 Tests for tdi.markup.text.filters
===================================

Tests for tdi.markup.text.filters.
"""
__author__ = u"Andr\xe9 Malo"

from tdi.markup.text import filters as _filters

from .... import _util as _test

multi = _test.multi_impl(globals(), _filters)
c = _test.c_impl(_filters)


@multi
def test_init():
    """ EncodingDetectFilter() inits properly """
    builder = _test.mock.MagicMock()
    inst = _filters.EncodingDetectFilter(builder)

    assert inst.builder is builder
    # pylint: disable =  use-implicit-booleaness-not-comparison
    assert _test.calls(builder) == []


@multi
def test_handle_pi():
    """ EncodingDetectFilter() inits properly """
    builder = _test.mock.MagicMock()
    inst = _filters.EncodingDetectFilter(builder)

    assert inst.builder is builder
    inst.handle_pi('doh')
    inst.handle_pi('[? encoding latin-1 ?]')
    inst.handle_pi('[? encoding = utf-8 ?]')

    assert _test.calls(builder) == [
        ('handle_pi', ('doh',), {}),

        ('handle_encoding', ('latin-1',), {}),
        ('handle_pi', ('[? encoding latin-1 ?]',), {}),

        ('handle_encoding', ('utf-8',), {}),
        ('handle_pi', ('[? encoding = utf-8 ?]',), {}),
    ]
