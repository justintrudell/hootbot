"""change type of zendesk ticket id

Revision ID: a2ecd47d1e01
Revises: eccf8d912601
Create Date: 2017-08-04 10:04:51.086688

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a2ecd47d1e01'
down_revision = 'eccf8d912601'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table("zendesk_tickets") as batch:
    batch.drop_column('id')
    batch.add_column(sa.Column('id', sa.String(32), primary_key=True))


def downgrade():
  with op.batch_alter_table("zendesk_tickets") as batch:
    batch.drop_column('id')
    batch.add_column(sa.Column('id', sa.Integer, primary_key=True))
