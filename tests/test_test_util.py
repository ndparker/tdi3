# -*- encoding: ascii -*-
"""
Test test utils
~~~~~~~~~~~~~~~

"""

from . import _util


def test_dedent():
    """dedent() works as expected"""
    inp = """
        hey!

           ho!
    """
    assert _util.dedent(inp) == 'hey!\n\n   ho!\n'
