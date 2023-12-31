"""a

Revision ID: 529257898650
Revises: 5ec4eed9d671
Create Date: 2023-07-25 03:19:42.387045

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '529257898650'
down_revision = '5ec4eed9d671'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('document_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'document_id')
    # ### end Alembic commands ###
