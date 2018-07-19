"""add primary key to user objectives

Revision ID: fffc2e1d5fd4
Revises: e628c051d9d1
Create Date: 2017-07-02 22:14:55.005799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fffc2e1d5fd4'
down_revision = 'e628c051d9d1'
branch_labels = None
depends_on = None


def upgrade():
  op.create_table(
    'user_objectives',
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('user_id', sa.String(20), sa.ForeignKey('users.id')),
    sa.Column('objective_id', sa.Integer, sa.ForeignKey('learning_objectives.id')),
    sa.Column('timestamp', sa.DateTime)
  )          

def downgrade():
  op.drop_table('user_objectives')
