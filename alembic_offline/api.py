"""alembic-offline api functions."""
import codecs
from mimetypes import guess_type
import os.path
import re

from sqlalchemy.engine.url import make_url

from alembic.command import upgrade
from alembic.script import ScriptDirectory

try:
    from StringIO import StringIO
except ImportError:  # pragma: no cover
    from io import StringIO

from .decorators import PHASE_FORMAT
from .operations import SCRIPT_FORMAT

PHASE_RE = re.compile((PHASE_FORMAT + ';\n\n').format("(.+)"), re.MULTILINE | re.UNICODE)
SCRIPT_RE = re.compile((SCRIPT_FORMAT + ';\n\n').format("(.+)"), re.MULTILINE | re.UNICODE)


def grouper(iterable, n):
    """Collect data into fixed-length chunks or blocks.

    :param iterable:
    :type iterable: collections.Iterable
    :param n: length of chunk
    :type n: int

    :return: iterator of chunks
    :rtype: collections.Iterable
    """
    # grouper('ABCDEF', 3) --> ABC DEF
    args = [iter(iterable)] * n
    return zip(*args)


def get_migration_data(config, revision):
    """Get migration data in form of a dict.

    :param config: alembic config object
    :type config: alembic.config.Config
    :param revision: revision name
    :type revision: str

    :return: migration data for given revision in form:
        {
            'revision': '123123123',
            'phases': [
                {
                    'name': 'before-deploy',
                    'steps': [
                        {
                            'type': 'mysql',
                            'script': 'alter table example add column int'
                        }
                    ]
                }
            ]
        }
    """
    config.output_buffer = StringIO()
    script = ScriptDirectory.from_config(config)
    phases = frozenset(phase.strip() for phase in config.get_main_option('phases', '').split())
    default_phase = config.get_main_option('default-phase')
    if not default_phase or default_phase not in phases:
        raise RuntimeError("'default-phase' should be configured and should be a member of 'phases'")
    for sc in script.get_revisions(revision):
        revision_range = ':'.join((sc.down_revision, revision)) if sc.down_revision else revision
        upgrade(config, revision_range, sql=True)
    output_text = config.output_buffer.getvalue()
    dialect = make_url(config.get_main_option('sqlalchemy.url')).get_dialect().name
    phase_texts = PHASE_RE.split(output_text)
    if len(phase_texts) < 2:
        phase_texts.insert(0, default_phase)
    if not sc.down_revision and len(phase_texts) > 2:
        phase_texts[1] = phase_texts.pop(0) + phase_texts[1]
    phases = []
    for phase_name, phase_text in grouper(phase_texts, 2):
        script_texts = SCRIPT_RE.split(phase_text)
        if not script_texts[0]:
            del script_texts[0]
        steps = []
        phases.append(dict(name=phase_name, steps=steps))
        if len(script_texts) < 2:
            script_texts.insert(0, None)
        for script_name, script_text in grouper(script_texts, 2):
            if script_name:
                steps.append(get_script_data(script, script_name))
            steps.append(
                dict(type=dialect, script=script_text.strip())
            )
    return dict(
        revision=revision,
        phases=phases)


def get_script_data(script, file_name):
    """Get script data.

    :param script: alembic script directory object
    :type script: alembic.script.ScriptDirectory
    :param file_name: script file name
    :type file_name: str

    :return: script data dictionary in form:
         {'type': 'mysql', 'script': 'alter table'[, 'path': 'scripts/script.py']}
    """
    script_type = 'unknown'
    type_, encoding = guess_type(file_name)
    if 'text/x-' in type_:
        script_type = type_[7:]
    script_file_name = os.path.join(script.dir, file_name)
    with codecs.open(script_file_name, encoding='utf-8') as fd:
        script = fd.read()
    return dict(type=script_type, script=script, path=file_name)
