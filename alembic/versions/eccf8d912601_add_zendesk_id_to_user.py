"""add zendesk_id to user

Revision ID: eccf8d912601
Revises: ed42ab9c5ef8
Create Date: 2017-08-02 18:29:06.211365

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eccf8d912601'
down_revision = 'ed42ab9c5ef8'
branch_labels = None
depends_on = None



def upgrade():
  with op.batch_alter_table("users") as batch_op:
    batch_op.add_column(sa.Column('zendesk_id', sa.String(32)))


def downgrade():
  with op.batch_alter_table("users") as batch_op:
    batch_op.drop_column('zendesk_id')
