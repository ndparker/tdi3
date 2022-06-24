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

==========================
 Modules implemented in C
==========================

The modules in this package implement (or reimplement) various functionality
in C for reasons of performance or availability. The performance
implementations are always re-implementations of accompanying python
functions.

The standard way to import these modules is to use the `load` function. It
catches ImportError and disabled C overrides via environment.
"""
__author__ = u"Andr\xe9 Malo"

import os as _os

#: Default environment variable name
#:
#: This variable can be set to ``1`` in order to disable loading of tdi's c
#: extensions
#:
#: :Type: ``str``
DEFAULT_ENV_OVERRIDE = 'TDI_NO_C_OVERRIDE'

#: Default template for the fully qualified module name
#:
#: :Type: ``str``
DEFAULT_TPL = 'tdi.c._tdi_%s'


def impl(symbol=None, **kwargs):
    """ replace symbol with C implementation if available """
    def inner(value):
        """ Decorator """
        lookup = value.__name__ if symbol is None else symbol
        modname = kwargs.pop('modname', None) or 'impl'
        cimpl = load(modname, **kwargs)
        if cimpl is not None:
            value = getattr(cimpl, lookup, value)
        return value
    if callable(symbol) and not kwargs:
        value, symbol = symbol, None
        return inner(value)
    return inner


def load(modname, space=None, env_override=None, tpl=None):
    """
    Module loading facade

    :Parameters:
      `modname` : ``str``
        Module name part (like ``util`` for ``tdi.c._tdi_util``), see `tpl`

      `space` : ``dict``
        Namespace to modify in place. Every key in `space` (not starting with
        ``_``) also appearing in the imported module is replaced by the module
        attribute. Additionally the key with the name 'c' is deleted from
        `space`.

      `env_override` : ``str``
        Name of the environment variable, which can disable the c extension
        import if set to ``1``. If omitted or ``None``,
        `DEFAULT_ENV_OVERRIDE` is applied.

      `tpl` : ``str``
        Template for the fully qualified module name. It has to contain one
        %s format specifier which takes the `modname` part. If omitted or
        ``None``, `DEFAULT_TPL` is applied.

    :Return: The requested module or ``None`` (either by env request or
             ``ImportError``)
    :Rtype: ``module``
    """
    if env_override is None:
        env_override = DEFAULT_ENV_OVERRIDE
    if _os.environ.get(env_override) != '1':
        if tpl is None:
            tpl = DEFAULT_TPL
        try:
            mod = __import__(tpl % modname, globals(), locals(), ['*'])
        except ImportError:
            mod = None
        else:
            if space is not None:
                symbols = set(space.keys()) & set(vars(mod).keys())
                for symbol in symbols:
                    if not symbol.startswith('_'):
                        space[symbol] = getattr(mod, symbol)
                if 'c' in space:
                    del space['c']
    else:
        mod = None
    return mod
