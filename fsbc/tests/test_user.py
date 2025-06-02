import nose.tools

import fsbc.user


def test_mypy():
    from nose.plugins.skip import SkipTest

    raise SkipTest()
    # import fstd.mypy
    # fstd.mypy.check_module(fsbc.user.__name__)


def test_doctest():
    import doctest

    failure_count, test_count = doctest.testmod(fsbc.user)
    nose.tools.assert_equals(failure_count, 0)
