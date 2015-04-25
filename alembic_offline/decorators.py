"""alembic-offline decorators."""
import alembic
from collections import Iterable
from functools import wraps

PHASE_FORMAT = '-- PHASE::{0}::'


def phased(func):
    """Convert upgrade function into phased one."""
    @wraps(func)
    def decorated(*args, **kwargs):
        iterator = func(*args, **kwargs)
        if not isinstance(iterator, Iterable):
            raise RuntimeError('Staged upgrade function should be a generator')
        alembic.op.execute(PHASE_FORMAT.format(0))
        for index, stage in enumerate(iterator, 1):
            alembic.op.execute(PHASE_FORMAT.format(index))

    return decorated
