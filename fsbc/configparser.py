from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

try:
    from configparser import ConfigParser, NoOptionError, NoSectionError
except ImportError:
    from ConfigParser import ConfigParser, NoOptionError, NoSectionError
