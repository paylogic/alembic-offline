"""Test offline alembic extensions."""
from alembic.command import upgrade
from alembic.config import Config


def test_offline(capsys):
    """Test offline generation with alembic-offline helpers used."""
    config = Config()
    config.set_main_option("script_location", "tests:migrations")
    config.set_main_option("sqlalchemy.url", "sqlite:///")

    upgrade(config, revision='1', sql=True)
    resout, reserr = capsys.readouterr()
    assert resout == """
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL
);

-- Running upgrade  -> 1

-- PHASE::0::;

CREATE TABLE account (
    id INTEGER NOT NULL,{space}
    name VARCHAR(50) NOT NULL,{space}
    description NVARCHAR(200),{space}
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,{space}
    PRIMARY KEY (id)
);

-- PHASE::1::;

update account set name='some';

-- PHASE::2::;

-- SCRIPT::/home/vagrant/workspace/alembic-offline/tests/migrations/scripts/script.py::;

INSERT INTO alembic_version (version_num) VALUES ('1');

""".format(space=' ').lstrip()
