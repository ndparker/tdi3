# TDI - The next evolutional step for templating

TABLE OF CONTENTS
-----------------

1. Introduction
1. Copyright and License
1. System Requirements
1. Installation
1. Documentation
1. Bugs
1. Author Information


## INTRODUCTION

TDI (Template Data Interface) is a markup templating system written in python
with optional speedup code written in C. Unlike most templating systems the
TDI does not invent its own language to provide functionality. Instead you
simply mark the nodes you want to manipulate within the template document. The
template is parsed and the marked nodes are presented to your python code,
where they can be modified in any way you want.

* [Change Log](docs/CHANGES)
* [Development](docs/DEVELOPMENT.md)


DEVELOPMENT STATUS
------------------

Alpha.
This is a fresh implementation of the [tdi](https://github.com/ndparker/tdi)
project with python 2/3 compatibility in mind.


## COPYRIGHT AND LICENSE

Copyright 2006 - 2023
André Malo or his licensors, as applicable.

The whole package is distributed under the Apache License Version 2.0.
You'll find a copy in the root directory of the distribution or online
at: <http://www.apache.org/licenses/LICENSE-2.0>.


## SYSTEM REQUIREMENTS

You need at least python 2.7 or Python 3 starting with version 3.6.

You also need a build environment for python C extensions (i.e. a compiler
and the python development files).


## INSTALLATION

### Using pip

```
$ pip install tdi3
```


### Using distutils

Download the package, unpack it, change into the directory

```
$ python setup.py install
```

The command above will install a new "tdi" package into python's
library path.


## DOCUMENTATION

You'll find a user documentation in the `docs/userdoc/` directory of the
distribution package.

The latest documentation is also available online at
<http://opensource.perlig.de/tdi/>.


## BUGS

No bugs, of course. ;-)

But if you've found one or have an idea how to improve TDI, feel free to
send a pull request on [github](https://github.com/ndparker/tdi3) or
send a mail to <tdi-bugs@perlig.de>.


## AUTHOR INFORMATION

André "nd" Malo <nd@perlig.de>, GPG: 0x029C942244325167


>  If God intended people to be naked, they would be born that way.
>                                                   -- Oscar Wilde
