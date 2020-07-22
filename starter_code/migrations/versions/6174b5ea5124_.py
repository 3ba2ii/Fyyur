"""empty message

Revision ID: 6174b5ea5124
Revises: c1214fa47004
Create Date: 2020-07-22 16:33:34.758175

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6174b5ea5124'
down_revision = 'c1214fa47004'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('show', 'start_time',
                    existing_type=postgresql.TIMESTAMP(),
                    nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('show', 'start_time',
                    existing_type=postgresql.TIMESTAMP(),
                    nullable=True)
    # ### end Alembic commands ###
