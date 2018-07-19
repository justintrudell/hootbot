"""create zendesk_tickets table

Revision ID: cfa4f520845b
Revises: fffc2e1d5fd4
Create Date: 2017-07-08 17:04:13.986573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfa4f520845b'
down_revision = 'fffc2e1d5fd4'
branch_labels = None
depends_on = None


def upgrade():
  op.create_table(
    'zendesk_tickets',
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('state', sa.String(80), nullable=False),
    sa.Column('user_id', sa.String(20), sa.ForeignKey('users.id'))
  )

  with op.batch_alter_table('users') as batch_op:
    batch_op.drop_column('active_support_ticket')

def downgrade():
  op.drop_table('zendesk_tickets')
  
  with op.batch_alter_table('users') as batch_op:
    batch_op.add_column(sa.Column('active_support_ticket', sa.Boolean, default=False))
