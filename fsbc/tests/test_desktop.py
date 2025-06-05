import nose.tools

import fsbc.desktop


def test_mypy():
    # from nose.plugins.skip import SkipTest
    # raise SkipTest()
    import fstd.mypy

    fstd.mypy.check_module(fsbc.desktop.__name__)


def test_doctest():
    import doctest

    failure_count, test_count = doctest.testmod(fsbc.desktop)
    nose.tools.assert_equals(failure_count, 0)
