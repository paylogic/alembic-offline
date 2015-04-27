"""alembic-offline decorators."""
from itertools import chain
from collections import Iterable
from functools import wraps

import alembic

PHASE_FORMAT = '-- PHASE::{0}::'


def phased(func):
    """Convert upgrade function into phased one."""
    @wraps(func)
    def decorated(*args, **kwargs):
        iterator = func(*args, **kwargs)
        if not isinstance(iterator, Iterable):
            raise RuntimeError('Staged upgrade function should be a generator')
        config = alembic.context.get_context().config
        config_phases = config.get_main_option('phases')
        if not config_phases:
            raise RuntimeError("For phased migration, 'phases' option is required to be set")
        phases = [
            phase.strip() for phase in config_phases.split()
        ]
        for index, phase in enumerate(chain([0], iterator)):
            alembic.op.execute(PHASE_FORMAT.format(phases[index]))
        if index != len(phases) - 1:
            raise RuntimeError("Migration phases don't match the configured ones")

    return decorated
