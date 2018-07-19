"""add email to users object

Revision ID: ed42ab9c5ef8
Revises: d438b879198c
Create Date: 2017-08-02 17:38:41.752768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed42ab9c5ef8'
down_revision = 'd438b879198c'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table("users") as batch_op:
    batch_op.add_column(sa.Column('email', sa.String(256)))


def downgrade():
  with op.batch_alter_table("users") as batch_op:
    batch_op.drop_column('email')
