"""add report status column

Revision ID: 9a1d7fbe1c2a
Revises: 0af50fc76025
Create Date: 2026-03-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "9a1d7fbe1c2a"
down_revision: Union[str, Sequence[str], None] = "0af50fc76025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    columns = {col["name"] for col in inspector.get_columns("reporte")}
    if "estado" in columns:
        return

    op.add_column(
        "reporte",
        sa.Column(
            "estado",
            sa.Enum(
                "PENDIENTE",
                "EN_REVISION",
                "RESUELTO",
                "RECHAZADO",
                name="reportstatus",
                native_enum=False,
            ),
            nullable=False,
            server_default="PENDIENTE",
        ),
    )


def downgrade() -> None:
    op.drop_column("reporte", "estado")
