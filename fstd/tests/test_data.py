import fstd.data
import fstd.mypy


def test_mypy():
    fstd.mypy.check_module(fstd.data.__name__)
