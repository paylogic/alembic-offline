"""alembic-offline operations."""
import alembic

SCRIPT_FORMAT = '-- SCRIPT::{0}::'


def execute_script(file_name):
    """Execute arbitrary script."""
    alembic.op.execute(SCRIPT_FORMAT.format(file_name))
