"""add image_url column to scheduled_message_contents

Revision ID: 44dc0fad5a59
Revises: 829524aafd10
Create Date: 2017-07-02 11:55:24.860516

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44dc0fad5a59'
down_revision = '829524aafd10'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table("scheduled_message_contents") as batch_op:
    batch_op.add_column(sa.Column('image_url', sa.String(240)))


def downgrade():
  with op.batch_alter_table("scheduled_message_contents") as batch_op:
    batch_op.drop_column('image_url')
