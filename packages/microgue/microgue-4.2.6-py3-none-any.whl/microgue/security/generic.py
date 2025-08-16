from flask import g
from functools import wraps
from ..loggers.logger import Logger

logger = Logger()


def is_allowed_by_all(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        logger.debug("Authentication - is_allowed_by_all", priority=2)
        g.authenticated = True
        return f(*args, **kwargs)
    return wrapped
