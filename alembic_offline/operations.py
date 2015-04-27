"""alembic-offline operations."""
import os.path
import alembic

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess

SCRIPT_FORMAT = '-- SCRIPT::{0}::'


def execute_script(file_name):
    """Execute arbitrary script.

    :param file_name: script file name
    :type file_name: str
    """
    file_name = file_name.replace(os.path.commonprefix([alembic.context.script.dir, file_name]), '')[1:]
    if alembic.context.is_offline_mode():
        alembic.op.execute(SCRIPT_FORMAT.format(file_name))
    else:
        script_file_name = os.path.join(alembic.context.script.dir, file_name)
        subprocess.check_call(script_file_name)
