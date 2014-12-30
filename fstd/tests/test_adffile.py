import fstd.adffile
import os
import hashlib
import fstd.mypy
from nose.tools import *


def get_transplant_adf() -> fstd.adffile.ADFFile:
    adf = fstd.adffile.ADFFile(os.path.join(os.path.dirname(__file__),
                                            "adffile", "transplant.adf"))
    return adf


def test_namelist():
    adf = get_transplant_adf()
    expected_names = [
        "devs/",
        "devs/system-configuration",
        "l/",
        "l/disk-validator",
        "loader",
        "mainpart",
        "s/",
        "s/startup-sequence",
    ]
    assert_equal(sorted(adf.namelist()), expected_names)


def test_read_startup_sequence():
    adf = get_transplant_adf()
    data = adf.read("s/startup-sequence")
    assert_equal(data, b"loader\n")


def test_read_mainpart():
    adf = get_transplant_adf()
    data = adf.read("mainpart")
    data_sha1 = hashlib.sha1(data).hexdigest()
    assert_equal(data_sha1, "ef467af52c8a886a6bca6ceb7f263fb8cbee2d59")


def test_mypy():
    fstd.mypy.check_module(fstd.adffile.__name__)
