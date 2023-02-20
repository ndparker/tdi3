# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2007 - 2023
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

====================================
 Exceptions used in the tdi package
====================================

The module provides all exceptions and warnings used throughout the
`tdi` package.
"""
__author__ = u"Andr\xe9 Malo"


class Error(Exception):
    """Base exception for this package"""


# Lexer
#######################################################################


class LexerError(Error):
    """Lexer Error"""


class LexerEOFError(LexerError):
    """Unexpected EOF"""


class LexerStateError(LexerError):
    """Invalid state change"""


class LexerFinalizedError(LexerStateError):
    """Lexer was already finalized"""
