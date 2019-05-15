"""empty message

Revision ID: 9e1fd01925bd
Revises: 9ab1f18ae1d9
Create Date: 2019-04-21 19:30:18.426042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e1fd01925bd'
down_revision = '9ab1f18ae1d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('notifications_community_invitee_fkey', 'notifications', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('notifications_community_invitee_fkey', 'notifications', 'users', ['community_invitee'], ['id'])
    # ### end Alembic commands ###