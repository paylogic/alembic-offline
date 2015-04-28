"""Test online mode."""
from alembic.config import Config
from alembic.command import upgrade


def test_online(capsys):
    """Test online mode with alembic-offline helpers used."""
    config = Config()
    config.set_main_option("script_location", "tests:migrations")
    config.set_main_option("sqlalchemy.url", "sqlite:///")
    config.set_main_option("phases", "before-deploy after-deploy final")

    upgrade(config, revision='1')
    resout, reserr = capsys.readouterr()
    assert resout == "script is executed\n"
