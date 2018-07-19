"""add admin_tokens table

Revision ID: d438b879198c
Revises: 4631a2b63317
Create Date: 2017-07-28 14:37:11.008387

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd438b879198c'
down_revision = '4631a2b63317'
branch_labels = None
depends_on = None


def upgrade():
  op.create_table(
    'admin_tokens',
    sa.Column('token', sa.String(64), primary_key=True),
    sa.Column('created_date', sa.DateTime),
  )

def downgrade():
  op.drop_table('admin_tokens')
