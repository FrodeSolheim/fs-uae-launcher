import doctest

import nose.tools

import fsbc.util
import fstd.mypy


def test_mypy():
    fstd.mypy.check_module(fsbc.util.__name__)


def test_doctest():
    failure_count, test_count = doctest.testmod(fsbc.util)
    nose.tools.assert_equals(failure_count, 0)
