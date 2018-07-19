"""add timestamp to user objectives

Revision ID: e628c051d9d1
Revises: 960addd28829
Create Date: 2017-07-02 20:59:22.488378

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e628c051d9d1'
down_revision = '960addd28829'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table("user_objectives") as batch_op:
    batch_op.add_column(sa.Column('timestamp', sa.DateTime))


def downgrade():
  with op.batch_alter_table("user_objectives") as batch_op:
    batch_op.drop_column("timestamp")
