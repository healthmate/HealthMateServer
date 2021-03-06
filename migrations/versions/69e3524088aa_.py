"""empty message

Revision ID: 69e3524088aa
Revises: d406ba244a60
Create Date: 2019-05-08 12:46:57.916179

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69e3524088aa'
down_revision = 'd406ba244a60'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('usersetting', 'activity_level',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('usersetting', 'average_weight',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('usersetting', 'duration',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('usersetting', 'goal_weight',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('usersetting', 'height',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('usersetting', 'is_diabetic',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('usersetting', 'net_calorie_goal',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_unique_constraint(None, 'usersetting', ['user_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'usersetting', type_='unique')
    op.alter_column('usersetting', 'net_calorie_goal',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('usersetting', 'is_diabetic',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('usersetting', 'height',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('usersetting', 'goal_weight',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('usersetting', 'duration',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('usersetting', 'average_weight',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('usersetting', 'activity_level',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
