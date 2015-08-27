"""Test the commands."""
from alembic_offline.commands import graph


def test_graph(mocker, tmpdir):
    mocked_alembic = mocker.patch('alembic_offline.commands.generate_migration_graph')
    mocked_alembic.return_value = "Hello"
    fp = tmpdir.join('test.dot')
    graph(
        filename=str(fp),
        alembic_config='some_config',
        verbose=False
    )
    assert fp.read() == "Hello"
