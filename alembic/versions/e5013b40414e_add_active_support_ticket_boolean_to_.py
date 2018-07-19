"""add active_support_ticket boolean to user model

Revision ID: e5013b40414e
Revises: 
Create Date: 2017-06-30 22:44:34.519993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5013b40414e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table("users") as batch_op:
    batch_op.add_column(sa.Column('active_support_ticket', sa.Boolean))


def downgrade():
 with op.batch_alter_table("users") as batch_op:
    batch_op.drop_column('active_support_ticket')
