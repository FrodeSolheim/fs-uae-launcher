import os
import fsbc.zipfile
import fstd.mypy
import nose.tools


def test_mypy():
    fstd.mypy.check_module(fsbc.zipfile.__name__)


def test_latin1_name():
    zf = fsbc.zipfile.ZipFile(os.path.join(os.path.dirname(__file__),
                                           "zipfile", "iso-8859-1.zip"), "r")
    nose.tools.assert_equals(zf.namelist(), ["F\xf8rde"])
    zf.read("F\xf8rde")
    nose.tools.assert_raises(KeyError, zf.read, "Forde")
    zf.getinfo("F\xf8rde")
    zf.close()


def test_utf8_name():
    zf = fsbc.zipfile.ZipFile(os.path.join(os.path.dirname(__file__),
                                           "zipfile", "utf-8.zip"), "r")
    nose.tools.assert_equals(zf.namelist(), ["F\xf8rde"])
    zf.read("F\xf8rde")
    nose.tools.assert_raises(KeyError, zf.read, "Forde")
    zf.getinfo("F\xf8rde")
    zf.close()
