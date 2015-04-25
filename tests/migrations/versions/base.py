"""Test migration."""
import os.path
from sqlalchemy import INTEGER, VARCHAR, NVARCHAR, TIMESTAMP, Column, func
from alembic import op

from alembic_offline import phased, execute_script

from tests.migrations.scripts import script

revision = '1'
down_revision = None


@phased
def upgrade():
    """Upgrade."""
    op.create_table(
        'account',
        Column('id', INTEGER, primary_key=True),
        Column('name', VARCHAR(50), nullable=False),
        Column('description', NVARCHAR(200)),
        Column('timestamp', TIMESTAMP, server_default=func.now())
    )
    yield
    op.execute("update account set name='some'")
    yield
    execute_script(os.path.splitext(script.__file__)[0] + '.py')


def downgrade():
    """Downgrade."""
    pass
