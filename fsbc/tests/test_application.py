import fsbc.application
import nose.tools


def test_mypy():
    from nose.plugins.skip import SkipTest
    raise SkipTest()
    # import fstd.mypy
    # fstd.mypy.check_module(fsbc.Application.__name__)


def test_doctest():
    import doctest
    failure_count, test_count = doctest.testmod(fsbc.application)
    nose.tools.assert_equals(failure_count, 0)
