"""empty message

Revision ID: d406ba244a60
Revises: e7f43ef1ab39
Create Date: 2019-05-07 13:55:09.287008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd406ba244a60'
down_revision = 'e7f43ef1ab39'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mealtable',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name_of_food', sa.String(length=255), nullable=False),
    sa.Column('calories', sa.Integer(), nullable=False),
    sa.Column('is_diabetic', sa.String(), nullable=False),
    sa.Column('breakfast', sa.String(), nullable=False),
    sa.Column('lunch', sa.String(), nullable=False),
    sa.Column('dinner', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('usersetting',
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('average_weight', sa.String(), nullable=False),
    sa.Column('height', sa.String(), nullable=False),
    sa.Column('goal_weight', sa.String(length=255), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('net_calorie_goal', sa.String(), nullable=False),
    sa.Column('is_diabetic', sa.String(), nullable=False),
    sa.Column('activity_level', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('user_id')
    )
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(), nullable=True))
    op.add_column('users', sa.Column('profile_pic', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile_pic')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'age')
    op.drop_table('usersetting')
    op.drop_table('mealtable')
    # ### end Alembic commands ###
