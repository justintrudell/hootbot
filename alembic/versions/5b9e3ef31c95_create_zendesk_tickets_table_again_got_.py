"""create zendesk_tickets table again (got deleted..?)

Revision ID: 5b9e3ef31c95
Revises: cfa4f520845b
Create Date: 2017-07-08 21:10:55.348783

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b9e3ef31c95'
down_revision = 'cfa4f520845b'
branch_labels = None
depends_on = None


def upgrade():
  op.create_table(
    'zendesk_tickets',
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('status', sa.String(80), nullable=False),
    sa.Column('user_id', sa.String(20), sa.ForeignKey('users.id'))
  )


def downgrade():
  op.drop_table('zendesk_tickets')
