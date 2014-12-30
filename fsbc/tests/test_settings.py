import os
import tempfile
import fsbc.Settings
import nose.tools


# def test_unload():
#     fd, path = tempfile.mkstemp()
#     os.close(fd)
#     fsbc.Settings.set_path(path)
#     fsbc.Settings.load()
#     os.unlink(path)
#
#     fsbc.Settings.set("Key-å", "Value-å")
#     fsbc.Settings.unload()
#
#     fsbc.Settings.set_path("")
#
#     value = fsbc.Settings.get("Key-å")
#     assert_equals(value, "")


def test_load_save():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    fsbc.Settings.set_path(path)
    fsbc.Settings.load()

    fsbc.Settings.set("Key-å", "Value-å")
    fsbc.Settings.save()
    fsbc.Settings.unload()

    fsbc.Settings.load()

    value = fsbc.Settings.get("key-å")
    nose.tools.assert_equals(value, "Value-å")
    fsbc.Settings.unload()


def test_mypy():
    # from nose.plugins.skip import SkipTest
    # raise SkipTest()
    import fstd.mypy
    fstd.mypy.check_module(fsbc.Settings.__name__)


def test_doctest():
    import doctest
    failure_count, test_count = doctest.testmod(fsbc.Settings)
    nose.tools.assert_equals(failure_count, 0)
