"""Test offline alembic extensions."""
from alembic.command import upgrade
from alembic.config import Config

from alembic_offline import get_migration_data

import pytest


def test_offline(capsys):
    """Test offline generation with alembic-offline helpers used."""
    config = Config()
    config.set_main_option("script_location", "tests:migrations")
    config.set_main_option("sqlalchemy.url", "sqlite:///")
    config.set_main_option("phases", "before-deploy after-deploy final")

    upgrade(config, revision='1', sql=True)
    resout, reserr = capsys.readouterr()
    assert resout == """
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL
);

-- Running upgrade  -> 1

-- PHASE::before-deploy::;

CREATE TABLE account (
    id INTEGER NOT NULL,{space}
    name VARCHAR(50) NOT NULL,{space}
    description NVARCHAR(200),{space}
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,{space}
    PRIMARY KEY (id)
);

-- PHASE::after-deploy::;

update account set name='some';

-- PHASE::final::;

-- SCRIPT::scripts/script.py::;

INSERT INTO alembic_version (version_num) VALUES ('1');

""".format(space=' ').lstrip()


def test_phased_not_configured():
    """Test phased migration when configuration is not set properly."""
    config = Config()
    config.set_main_option("script_location", "tests:migrations")
    config.set_main_option("sqlalchemy.url", "sqlite:///")
    with pytest.raises(RuntimeError) as exc:
        upgrade(config, revision='1')
    assert exc.value.args == ("For phased migration, 'phases' option is required to be set",)


def test_phased_not_generator():
    """Test phased migration when upgrade function is not a generator."""
    config = Config()
    config.set_main_option("script_location", "tests:migrations")
    config.set_main_option("sqlalchemy.url", "sqlite:///")
    with pytest.raises(RuntimeError) as exc:
        upgrade(config, revision='1:not-generator', sql=True)
    assert exc.value.args == ('Staged upgrade function should be a generator',)


def test_phased_mismatch():
    """Test phased migration when migration phases don't match the configured ones."""
    config = Config()
    config.set_main_option("script_location", "tests:migrations")
    config.set_main_option("sqlalchemy.url", "sqlite:///")
    config.set_main_option("phases", "before-deploy after-deploy final")
    with pytest.raises(RuntimeError) as exc:
        upgrade(config, revision='1:phase-mismatch', sql=True)
    assert exc.value.args == ("Migration phases don't match the configured ones",)


def test_migration_data_no_phases():
    """Test migration data without phases set up."""
    config = Config()
    config.set_main_option("script_location", "tests:migrations")
    config.set_main_option("sqlalchemy.url", "sqlite:///")
    with pytest.raises(RuntimeError) as exc:
        get_migration_data(config, revision='1')
    assert exc.value.args == ("'default-phase' should be configured and should be a member of 'phases'",)


def test_migration_data_simple():
    """Test migration data for simple case: no phases, no scripts."""
    config = Config()
    config.set_main_option("script_location", "tests:migrations")
    config.set_main_option("sqlalchemy.url", "sqlite:///")
    config.set_main_option("phases", "before-deploy after-deploy final")
    config.set_main_option("default-phase", "after-deploy")
    config.set_main_option("script-attributes", "some_attribute")
    data = get_migration_data(config, revision='simple')
    assert data == {
        'attributes': {'some_attribute': 'some-value'},
        'phases': {
            'after-deploy':
                {
                    'name': 'after-deploy',
                    'steps': [
                        {
                            'type': 'sqlite',
                            'script': u"""
-- Running upgrade 1 -> simple

ALTER TABLE account DROP COLUMN id;

UPDATE alembic_version SET version_num='simple' WHERE alembic_version.version_num = '1';
"""[1:-1]
                        }
                    ],
                }
        },
        'revision': 'simple',
        'down_revision': '1',
    }


def test_migration_data():
    """Test get migration data with complex case: phases, scripts."""
    config = Config()
    config.set_main_option("script_location", "tests:migrations")
    config.set_main_option("sqlalchemy.url", "sqlite:///")
    config.set_main_option("phases", "before-deploy after-deploy final")
    config.set_main_option("default-phase", "after-deploy")
    data = get_migration_data(config, revision='1')
    expected_data = {
        'phases': {
            'before-deploy': {
                'name': u'before-deploy',
                'steps': [
                    {
                        'type': 'sqlite',
                        'script': u"""
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL
);

-- Running upgrade  -> 1

CREATE TABLE account (
    id INTEGER NOT NULL,{space}
    name VARCHAR(50) NOT NULL,{space}
    description NVARCHAR(200),{space}
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,{space}
    PRIMARY KEY (id)
);
"""[1:-1].format(space=' ')
                    }
                ]
            },
            'after-deploy': {
                'name': u'after-deploy',
                'steps': [
                    {
                        'type': 'sqlite',
                        'script': u"update account set name='some';"
                    }
                ]
            },
            'final': {
                'name': u'final',
                'steps': [
                    {
                        'type': 'python',
                        'script': u"""#! /usr/bin/python


if __name__ == '__main__':
    print('script is executed')
""",
                        'path': 'scripts/script.py'
                    },
                    {
                        'type': 'sqlite',
                        'script': u"INSERT INTO alembic_version (version_num) VALUES ('1');",
                    },
                ],
            }
        },
        'attributes': {},
        'revision': '1',
        'down_revision': None,
    }
    assert data == expected_data
