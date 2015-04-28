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
    file_name = os.path.relpath(file_name, alembic.context.script.dir)
    context = alembic.context.get_context()
    if context.as_sql:
        alembic.op.execute(SCRIPT_FORMAT.format(file_name))
    else:
        script_file_name = os.path.join(alembic.context.script.dir, file_name)
        output = subprocess.check_output(
            script_file_name)
        context.output_buffer.write(output.decode('utf-8'))
