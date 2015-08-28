"""alembic-offline commands."""

from alembic.config import Config
from .api import generate_migration_graph


def graph(alembic_config, filename, verbose=True):
    """Generate a dotfile with an overview of all the migrations."""
    config = Config(alembic_config)

    with open(filename, 'w') as fp:
        fp.write(generate_migration_graph(config))

    if verbose:
        print("Done")
        print("To generate an image use: dot -Tpng -O {0}".format(filename))
