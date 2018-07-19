"""alter session table to use int instead of string

Revision ID: 960addd28829
Revises: 44dc0fad5a59
Create Date: 2017-07-02 12:10:16.309610

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '960addd28829'
down_revision = '44dc0fad5a59'
branch_labels = None
depends_on = None


def upgrade():
   op.alter_column("user_sessions", "state", type_=sa.Integer)


def downgrade():
   op.alter_column("user_sessions", "state", type_=sa.String(40))
