"""Test migration."""
from sqlalchemy import INTEGER, VARCHAR, NVARCHAR, TIMESTAMP, Column, func
from alembic import op

from alembic_offline import phased

revision = 'not-generator'
down_revision = '1'


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


def downgrade():
    """Downgrade."""
    pass
