"""create user_sessions table

Revision ID: 829524aafd10
Revises: e5013b40414e
Create Date: 2017-07-02 11:11:29.523232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '829524aafd10'
down_revision = 'e5013b40414e'
branch_labels = None
depends_on = None


def upgrade():
  op.create_table(
    'user_sessions',
    sa.Column('id', sa.String(20), primary_key=True),
    sa.Column('state', sa.String(40), nullable=False),
  )


def downgrade():
  op.drop_table('user_sessions')
