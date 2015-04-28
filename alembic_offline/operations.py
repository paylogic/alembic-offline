"""alembic-offline operations."""
import os.path
import alembic

SCRIPT_FORMAT = '-- SCRIPT::{0}::'


def execute_script(file_name):
    """Execute arbitrary script.

    :param file_name: script file name
    :type file_name: str
    """
    file_name = os.path.relpath(file_name, alembic.context.script.dir)
    alembic.op.execute(SCRIPT_FORMAT.format(file_name))
