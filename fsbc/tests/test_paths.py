import fsbc.paths
import nose.tools


def test_mypy():
    from nose.plugins.skip import SkipTest

    raise SkipTest()
    # import fstd.mypy
    # fstd.mypy.check_module(fsbc.Paths.__name__)


def test_doctest():
    import doctest

    failure_count, test_count = doctest.testmod(fsbc.paths)
    nose.tools.assert_equals(failure_count, 0)
