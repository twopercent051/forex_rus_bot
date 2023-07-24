"""a

Revision ID: 11784c733765
Revises: 555cab92387a
Create Date: 2023-07-22 10:56:37.591099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11784c733765'
down_revision = '555cab92387a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transactions', sa.Column('currency', sa.DECIMAL(), nullable=False))
    op.add_column('transactions', sa.Column('comment', sa.TEXT(), nullable=True))
    op.drop_column('transactions', 'course')
    op.add_column('workers', sa.Column('bank_status', sa.JSON(), nullable=False))
    op.add_column('workers', sa.Column('total_month', sa.DECIMAL(), nullable=False))
    op.drop_column('workers', 'sber_status')
    op.drop_column('workers', 'tinkoff_status')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workers', sa.Column('tinkoff_status', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('workers', sa.Column('sber_status', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('workers', 'total_month')
    op.drop_column('workers', 'bank_status')
    op.add_column('transactions', sa.Column('course', sa.NUMERIC(), autoincrement=False, nullable=False))
    op.drop_column('transactions', 'comment')
    op.drop_column('transactions', 'currency')
    # ### end Alembic commands ###
