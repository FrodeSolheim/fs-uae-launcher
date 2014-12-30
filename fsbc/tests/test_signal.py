import fsbc.signal
import nose.tools


def test_mypy():
    from nose.plugins.skip import SkipTest
    raise SkipTest()
    # import fstd.mypy
    # fstd.mypy.check_module(fsbc.signal.__name__)


def test_doctest():
    import doctest
    failure_count, test_count = doctest.testmod(fsbc.signal)
    nose.tools.assert_equals(failure_count, 0)
