"""remove skip_bot, add created_date to user

Revision ID: 909f934af660
Revises: 5b9e3ef31c95
Create Date: 2017-07-13 18:26:20.726092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '909f934af660'
down_revision = '5b9e3ef31c95'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table("users") as batch_op:
    batch_op.add_column(sa.Column('created_date', sa.DateTime))
    batch_op.drop_column('skip_bot')

def downgrade():
  with op.batch_alter_table("users") as batch_op:
    batch_op.add_column(sa.Column('skip_bot', sa.Boolean, default=False))
    batch_op.drop_column('created_date')

