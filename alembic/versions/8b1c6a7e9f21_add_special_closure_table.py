"""Add special closure table for holiday closures

Revision ID: 8b1c6a7e9f21
Revises: 9a1d7fbe1c2a
Create Date: 2026-04-12 21:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b1c6a7e9f21'
down_revision: Union[str, Sequence[str], None] = '9a1d7fbe1c2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'special_closure',
        sa.Column('cierre_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('establecimiento_id', sa.Integer(), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('motivo', sa.String(length=255), nullable=True),
        sa.Column('creado_en', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['establecimiento_id'], ['establecimiento.establecimiento_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('cierre_id'),
        sa.UniqueConstraint('establecimiento_id', 'fecha', name='unique_establecimiento_fecha_cierre')
    )
    op.create_index('idx_special_closure_establecimiento', 'special_closure', ['establecimiento_id'], unique=False)
    op.create_index('idx_special_closure_fecha', 'special_closure', ['fecha'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_special_closure_fecha', table_name='special_closure')
    op.drop_index('idx_special_closure_establecimiento', table_name='special_closure')
    op.drop_table('special_closure')
