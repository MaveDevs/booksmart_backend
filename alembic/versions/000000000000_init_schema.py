"""init schema baseline

Revision ID: 000000000000
Revises: 
Create Date: 2026-03-31 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

from app.db.base_class import Base
import app.models  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = "000000000000"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create full schema for fresh environments."""
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Drop full schema (reverse dependency order)."""
    bind = op.get_bind()
    for table in reversed(Base.metadata.sorted_tables):
        table.drop(bind=bind, checkfirst=True)
