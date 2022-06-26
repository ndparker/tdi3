# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2006 - 2022
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

=========================
 Template stream filters
=========================

This module provides the base classes and concrete implementations for
stream filters.
"""
__author__ = u"Andr\xe9 Malo"


class BaseStreamFilter(object):
    """
    Base stream filter class, which actually passes everything unfiltered
    """
    __slots__ = ('_stream', '__weakref__')

    def __new__(cls, *args, **kwargs):
        """ Construction """
        result = super(BaseStreamFilter, cls).__new__(cls)
        result._stream = None
        return result

    def __init__(self, stream):
        """
        Initialization

        Parameters:
          stream (file):
            The stream to decorate
        """
        #: The decorated stream
        #:
        #: :Type: file
        self._stream = stream

    def __getattr__(self, name):
        """
        Delegate unknown symbols to the next stream (downwards)

        Parameters:
          name (str):
            The symbol to look up

        Returns:
          any: The requested symbol

        Raises:
          AttributeError: The symbol was not found
        """
        return getattr(self._stream, name)

    def __delattr__(self, name):
        """
        Delete attribute

        Parameters:
          name (str):
            Name of the attribute to delete
        """
        if name == '_stream':
            self._stream = None
        else:
            super(BaseStreamFilter, self).__delattr__(name)


class StreamFilename(BaseStreamFilter):
    """
    Provide filename for upchain stream filters

    Attributes:
      filename (str):
        The provided filename
    """
    __slots__ = ('filename',)

    def __init__(self, stream, filename):
        """
        Initialization

        Parameters:
          stream (stream):
            The next stream layer

          filename (str):
            The filename to provide
        """
        super(StreamFilename, self).__init__(stream)
        self.filename = filename
