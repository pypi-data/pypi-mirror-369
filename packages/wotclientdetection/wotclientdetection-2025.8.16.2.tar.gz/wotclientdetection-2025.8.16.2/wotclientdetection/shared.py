import re
from packaging.version import VERSION_PATTERN

VERSION_REGEXP = re.compile(VERSION_PATTERN, re.VERBOSE | re.IGNORECASE)

def is_semver_version(s):
    if not s:
        return False
    return VERSION_REGEXP.match(s) is not None
