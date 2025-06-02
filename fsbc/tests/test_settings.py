import os
import tempfile

import nose.tools

import fsbc.settings

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
    fsbc.settings.set_path(path)
    fsbc.settings.load()

    fsbc.settings.set("Key-å", "Value-å")
    fsbc.settings.save()
    fsbc.settings.unload()

    fsbc.settings.load()

    value = fsbc.settings.get("key-å")
    nose.tools.assert_equals(value, "Value-å")
    fsbc.settings.unload()


def test_mypy():
    # from nose.plugins.skip import SkipTest
    # raise SkipTest()
    import fstd.mypy

    fstd.mypy.check_module(fsbc.settings.__name__)


def test_doctest():
    import doctest

    failure_count, test_count = doctest.testmod(fsbc.settings)
    nose.tools.assert_equals(failure_count, 0)
