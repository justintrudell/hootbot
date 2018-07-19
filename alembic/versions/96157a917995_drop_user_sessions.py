"""drop user_sessions

Revision ID: 96157a917995
Revises: 909f934af660
Create Date: 2017-07-20 22:32:43.418053

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96157a917995'
down_revision = '909f934af660'
branch_labels = None
depends_on = None


def upgrade():
  op.drop_table('user_sessions')


def downgrade():
  op.create_table(
    'user_sessions',
    sa.Column('id', sa.String(20), primary_key=True),
    sa.Column('state', sa.String(40), nullable=False),
  )
