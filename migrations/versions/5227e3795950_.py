"""empty message

Revision ID: 5227e3795950
Revises: b81839d5039d
Create Date: 2019-02-28 18:47:42.886354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5227e3795950'
down_revision = 'b81839d5039d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('posts', 'likes',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('posts', 'likes',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###