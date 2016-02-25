import pkg_resources
import launcher.version

VERSION = launcher.version.VERSION


# noinspection PyPep8Naming
def Stream(package, name):
    return pkg_resources.resource_stream(package, name)
