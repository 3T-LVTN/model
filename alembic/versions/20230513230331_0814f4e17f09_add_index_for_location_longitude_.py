"""add index for location longitude latitude

Revision ID: 0814f4e17f09
Revises: 056c8bd1b0a8
Create Date: 2023-05-13 23:03:31.468498

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0814f4e17f09'
down_revision = '056c8bd1b0a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_location_latitude'), 'location', ['latitude'], unique=False)
    op.create_index(op.f('ix_location_longitude'), 'location', ['longitude'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_location_longitude'), table_name='location')
    op.drop_index(op.f('ix_location_latitude'), table_name='location')
    # ### end Alembic commands ###
