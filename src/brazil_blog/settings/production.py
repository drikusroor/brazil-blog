from .base import *

DEBUG = False

CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake"
        }
    }

try:
    from .local import *
except ImportError:
    pass
