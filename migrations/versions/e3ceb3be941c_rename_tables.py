"""rename tables

Revision ID: e3ceb3be941c
Revises: e4fbb6becdb4
Create Date: 2023-07-24 05:38:03.620615

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3ceb3be941c'
down_revision = 'e4fbb6becdb4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('coin_value', sa.Integer(), nullable=False))
    op.add_column('orders', sa.Column('currency', sa.Integer(), nullable=False))
    op.add_column('orders', sa.Column('client_fiat', sa.Integer(), nullable=False))
    op.add_column('orders', sa.Column('worker_fiat', sa.Integer(), nullable=False))
    op.add_column('orders', sa.Column('profit_fiat', sa.Integer(), nullable=False))
    op.add_column('workers', sa.Column('total_month', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('workers', 'total_month')
    op.drop_column('orders', 'profit_fiat')
    op.drop_column('orders', 'worker_fiat')
    op.drop_column('orders', 'client_fiat')
    op.drop_column('orders', 'currency')
    op.drop_column('orders', 'coin_value')
    # ### end Alembic commands ###
