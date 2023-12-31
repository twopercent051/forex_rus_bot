"""rename tables

Revision ID: 27aa66feb324
Revises: 11784c733765
Create Date: 2023-07-24 01:58:41.862504

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '27aa66feb324'
down_revision = '11784c733765'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orders',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('dtime', sa.TIMESTAMP(), server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('client_id', sa.String(), nullable=False),
    sa.Column('client_username', sa.String(), nullable=False),
    sa.Column('coin', sa.String(), nullable=False),
    sa.Column('coin_value', sa.DECIMAL(), nullable=False),
    sa.Column('currency', sa.DECIMAL(), nullable=False),
    sa.Column('bank_name', sa.String(), nullable=False),
    sa.Column('bank_account', sa.String(), nullable=False),
    sa.Column('fiat_value', sa.DECIMAL(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('worker_id', sa.String(), nullable=True),
    sa.Column('moderator_id', sa.String(), nullable=True),
    sa.Column('crypto_account', sa.JSON(), nullable=False),
    sa.Column('comment', sa.TEXT(), nullable=True),
    sa.Column('stop_list', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('transactions')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transactions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('client_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('client_username', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('coin', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('coin_value', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('bank_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('bank_account', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('fiat_value', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('worker_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('moderator_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('crypto_account', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('dtime', postgresql.TIMESTAMP(), server_default=sa.text("timezone('utc'::text, CURRENT_TIMESTAMP)"), autoincrement=False, nullable=False),
    sa.Column('currency', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('comment', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='transactions_pkey')
    )
    op.drop_table('orders')
    # ### end Alembic commands ###
