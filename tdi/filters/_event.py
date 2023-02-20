# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2006 - 2023
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

========================
 Template Event filters
========================

This module provides the base classes and concrete implementations for
event filters.
"""
__author__ = u"Andr\xe9 Malo"

from .. import c as _c


@_c.impl
class BaseEventFilter(object):
    """
    Base event filter class, which actually passes everything unfiltered

    Override the event handlers you need.

    :See: `abstract.BuildingListener`

    Attributes:
      builder (abstract.BuildingListener):
        The next level builder
    """

    __slots__ = ('builder', '__weakref__')

    def __new__(cls, *args, **kwargs):
        """Construction"""
        result = super(BaseEventFilter, cls).__new__(cls)
        result.builder = None
        return result

    def __init__(self, builder):
        """
        Store the next level builder

        Parameters:
          builder (abstract.BuildingListener):
            The next level builder
        """
        self.builder = builder

    def __getattr__(self, name):
        """
        Delegate unknown symbols to the next level builder (upwards)

        Parameters:
          name (str):
            The symbol to look up

        Returns:
          any: The requested symbol

        Raises:
          AttributeError: The symbol was not found
        """
        return getattr(self.builder, name)

    def __delattr__(self, name):
        """
        Delete attribute

        Parameters:
          name (str):
            Name of the attribute to delete
        """
        if name == 'builder':
            self.builder = None
        else:
            super(BaseEventFilter, self).__delattr__(name)


class FilterFilename(BaseEventFilter):
    """
    Provide the filename for down-chain filters

    Attributes:
      filename (str):
        The provided filename
    """

    __slots__ = ('filename',)

    def __init__(self, builder, filename):
        """
        Initialization

        Parameters:
          builder (abstract.BuildingListener):
            The next level builder

          filename (str):
            The filename to provide
        """
        super(FilterFilename, self).__init__(builder)
        self.filename = filename
