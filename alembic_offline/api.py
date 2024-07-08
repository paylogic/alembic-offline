"""alembic-offline api functions."""
import codecs
from collections.abc import Iterable
from mimetypes import guess_type
import os.path
import re
from typing import Callable, Optional

from alembic.config import Config
from sqlalchemy.engine.url import make_url

from alembic.command import upgrade
from alembic.script import ScriptDirectory, Script

from io import StringIO

from .decorators import PHASE_FORMAT
from .operations import SCRIPT_FORMAT

PHASE_RE = re.compile((PHASE_FORMAT + ';\n\n').format("(.+)"), re.MULTILINE | re.UNICODE)
SCRIPT_RE = re.compile((SCRIPT_FORMAT + ';\n\n').format("(.+)"), re.MULTILINE | re.UNICODE)


def grouper(iterable: Iterable, n: int) -> Iterable:
    """Collect data into fixed-length chunks or blocks."""
    # grouper('ABCDEF', 3) --> ABC DEF
    args = [iter(iterable)] * n
    return zip(*args)


def get_migration_data(config: Config, revision: str) -> dict:
    """Get migration data in form of a dict.

    Returns migration data for given revision in form:
        {
            'revision': '123123123',
            'down_revision': '234234234',
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
    script_directory = ScriptDirectory.from_config(config)
    script = script_directory.get_revision(revision)
    phases = frozenset(phase.strip() for phase in config.get_main_option('phases', '').split())
    script_attrs = get_script_attributes(config, script)
    default_phase = config.get_main_option('default-phase')
    if not default_phase or default_phase not in phases:
        raise RuntimeError("'default-phase' should be configured and should be a member of 'phases'")
    revision_range = ':'.join((script.down_revision, revision)) if script.down_revision else revision
    upgrade(config, revision_range, sql=True)
    output_text = config.output_buffer.getvalue()
    dialect = make_url(config.get_main_option('sqlalchemy.url')).get_dialect().name
    phase_texts = PHASE_RE.split(output_text)
    if not script.down_revision and len(phase_texts) > 2:
        phase_texts[1] = phase_texts.pop(0) + phase_texts[1]
    if len(phase_texts) % 2:
        phase_texts.insert(0, default_phase)
    phases = {}
    for phase_name, phase_text in grouper(phase_texts, 2):
        script_texts = SCRIPT_RE.split(phase_text)
        if not script_texts[0]:
            del script_texts[0]
        steps = []
        phases[phase_name] = dict(name=phase_name, steps=steps)
        if len(script_texts) % 2:
            script_texts.insert(0, None)
        for script_name, script_text in grouper(script_texts, 2):
            if script_name:
                steps.append(get_script_data(script_directory, script_name))
            script_text = script_text.strip()
            if script_text:
                steps.append(
                    dict(type=dialect, script=script_text)
                )
    return dict(
        revision=revision,
        down_revision=script.down_revision,
        attributes=script_attrs,
        phases=phases)


def get_script_attributes(config: Config, script: Script) -> dict:
    """Get additional script attributes."""
    attrs = frozenset(attr.strip() for attr in config.get_main_option('script-attributes', '').split())
    result = {}
    for attr in attrs:
        try:
            value = getattr(script.module, attr)
        except AttributeError:
            raise RuntimeError('{0} attribute was configured but not found in {1} script'.format(
                attr, script.revision))
        result[attr] = value
    return result


def get_migrations_data(config: Config) -> list:
    """Get migration data for all migrations in script directory.

    Returns migrations data list in form:
        [<migration data 1>, <migration data 2>, ...]
    """
    script_directory = ScriptDirectory.from_config(config)
    return [get_migration_data(config, script.revision) for script in reversed(list(script_directory.walk_revisions()))]


def get_script_data(script_directory: ScriptDirectory, file_name: str) -> dict:
    """Get script data.

    Returns script data dictionary in form:
         {'type': 'mysql', 'script': 'alter table'[, 'path': 'scripts/script.py']}
    """
    script_type = 'unknown'
    type_, encoding = guess_type(file_name)
    if 'text/x-' in type_:
        script_type = type_[7:]
    script_file_name = os.path.join(script_directory.dir, file_name)
    with codecs.open(script_file_name, encoding='utf-8') as fd:
        script_text = fd.read()
    return dict(type=script_type, script=script_text, path=file_name)


def generate_migration_graph(config: Config, label_callback: Optional[Callable] = None) -> str:
    """Generate a graphviz dot digraph containing a graph of all the revisions.
    Here label_callback will be passed the migration's data from get_migration_data.
    """
    def default_label(migration_data: dict):
        attributes = []
        for key, value in migration_data['attributes'].items():
            attributes.append(u'- {0}: {1}'.format(key, value))
        return u'{0}\n{1}'.format(migration_data['revision'], '\n'.join(attributes))

    if not label_callback:
        label_callback = default_label
    data = get_migrations_data(config)
    labels = []
    graphs = []
    for migration in data:
        labels.append(u'"{0}" [label="{1}"];'.format(
            migration['revision'],
            label_callback(migration).replace('"', '\\"').replace('\n', '\\n'))
        )
        if migration['down_revision']:
            graphs.append(u'"{0}" -> "{1}";'.format(migration['revision'], migration['down_revision']))

    return u"digraph revisions {{\n\t{0}\n\n\t{1}\n}}".format("\n\t".join(labels), "\n\t".join(graphs))
