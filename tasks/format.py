# -*- encoding: ascii -*-
"""
Formatting tasks
~~~~~~~~~~~~~~~~

"""

import invoke as _invoke


@_invoke.task(default=True)
def black(ctx):
    """ Run black in formatting mode """
    exe = ctx.shell.frompath('black')
    if exe is None:
        raise RuntimeError("black not found")

    with ctx.shell.root_dir():
        ctx.run(ctx.c(
            r''' %(exe)s --config black.toml . ''',
            exe=exe,
        ), echo=True)
