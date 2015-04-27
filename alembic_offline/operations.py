"""alembic-offline operations."""
import os.path
import alembic

SCRIPT_FORMAT = '-- SCRIPT::{0}::'


def execute_script(file_name):
    """Execute arbitrary script.

    :param file_name: script file name
    :type file_name: str
    """
    file_name = file_name.replace(os.path.commonprefix([alembic.context.script.dir, file_name]), '')[1:]
    alembic.op.execute(SCRIPT_FORMAT.format(file_name))
