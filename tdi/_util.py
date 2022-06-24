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

================
 Misc Utilities
================

Misc utilities.
"""
__author__ = u"Andr\xe9 Malo"


def find_public(space):
    """
    Determine all public names in space

    Parameters:
      space (dict):
        Name space to inspect

    Returns:
      list: List of public names
    """
    if '__all__' in space:
        return list(space['__all__'])
    return [key for key in space.keys() if not key.startswith('_')]


# pylint: disable = invalid-name, unnecessary-lambda-assignment
if str is bytes:
    ur = lambda s: s.decode('ascii')
else:
    ur = lambda s: s
