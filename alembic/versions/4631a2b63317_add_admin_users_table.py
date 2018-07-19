"""add admin_users table

Revision ID: 4631a2b63317
Revises: 96157a917995
Create Date: 2017-07-21 15:47:56.049561

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4631a2b63317'
down_revision = '96157a917995'
branch_labels = None
depends_on = None


def upgrade():
  op.create_table(
    'admin_users',
    sa.Column('email', sa.String(240), primary_key=True),
    sa.Column('password', sa.String(240), nullable=False),
  )

def downgrade():
  op.drop_table('admin_users')
