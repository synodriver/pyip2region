import os
import platform

impl = platform.python_implementation()


def _should_use_cffi() -> bool:
    ev = os.getenv("IP_USE_CFFI")
    if ev is not None:
        return True
    if impl == "CPython":
        return False
    else:
        return True


if not _should_use_cffi():
    from ip2region.backends.cython import *
else:
    from ip2region.backends.cffi import *
