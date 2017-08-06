# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2014 - 2017
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

================
 Test Utilities
================

Test utilities.
"""
__author__ = u"Andr\xe9 Malo"
__docformat__ = "restructuredtext en"

try:
    from unittest import mock  # pylint: disable = unused-import
except ImportError:
    import mock  # noqa

unset = object()


class Bunch(object):
    """ Bunch object - represent all init kwargs as attributes """

    def __init__(self, **kw):
        """ Initialization """
        self.__dict__.update(kw)
