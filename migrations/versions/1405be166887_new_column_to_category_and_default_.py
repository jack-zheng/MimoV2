"""new column to category, and default value of task table

Revision ID: 1405be166887
Revises: 5fba1f7db536
Create Date: 2017-10-07 20:08:39.377387

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1405be166887'
down_revision = '5fba1f7db536'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('category_index', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('category', 'category_index')
    # ### end Alembic commands ###
