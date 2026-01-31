"""align models to ERD

Revision ID: c27ce2d75547
Revises: e7257f7051b1
Create Date: 2026-01-27 15:45:25.003122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'c27ce2d75547'
down_revision: Union[str, Sequence[str], None] = 'e7257f7051b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # --- Drop legacy trabajador-related foreign keys first ---
    op.drop_constraint("agenda_ibfk_1", "agenda", type_="foreignkey")
    op.drop_constraint("cita_ibfk_3", "cita", type_="foreignkey")
    op.drop_constraint("resena_ibfk_2", "resena", type_="foreignkey")
    op.drop_constraint("trabajadorservicio_ibfk_2", "trabajadorservicio", type_="foreignkey")
    op.drop_constraint("bloqueoagenda_ibfk_1", "bloqueoagenda", type_="foreignkey")

    # --- Drop legacy trabajador-related tables ---
    op.drop_table("bloqueoagenda")
    op.drop_table("trabajadorservicio")
    op.drop_table("trabajador")

    # --- Agenda: trabajador_id -> establecimiento_id, and unique constraint ---
    op.drop_index("unique_trabajador_dia", table_name="agenda")
    op.add_column("agenda", sa.Column("establecimiento_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "agenda_ibfk_establecimiento",
        "agenda",
        "establecimiento",
        ["establecimiento_id"],
        ["establecimiento_id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "unique_establecimiento_dia", "agenda", ["establecimiento_id", "dia_semana"]
    )
    op.drop_column("agenda", "trabajador_id")

    # --- Cita: drop trabajador_id + non-ERD columns; enforce required FKs ---
    op.drop_column("cita", "trabajador_id")
    op.drop_column("cita", "notas_cliente")
    op.drop_column("cita", "fecha_modificacion")
    op.alter_column("cita", "cliente_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("cita", "servicio_id", existing_type=sa.Integer(), nullable=False)

    # --- Reseña: remove cita_id/trabajador_id, add establecimiento_id, rename fecha ---
    op.drop_constraint("resena_ibfk_1", "resena", type_="foreignkey")
    op.drop_index("unique_cita_usuario", table_name="resena")
    op.drop_index("trabajador_id", table_name="resena")
    op.add_column("resena", sa.Column("establecimiento_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "resena_ibfk_establecimiento",
        "resena",
        "establecimiento",
        ["establecimiento_id"],
        ["establecimiento_id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "resena",
        "fecha_creacion",
        existing_type=sa.TIMESTAMP(),
        new_column_name="fecha",
    )
    op.drop_column("resena", "cita_id")
    op.drop_column("resena", "trabajador_id")
    op.alter_column("resena", "usuario_id", existing_type=sa.Integer(), nullable=False)

    # --- Reporte: restructure to establecimiento_id + fecha_generacion ---
    op.drop_constraint("reporte_ibfk_1", "reporte", type_="foreignkey")
    op.add_column("reporte", sa.Column("establecimiento_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "reporte_ibfk_establecimiento",
        "reporte",
        "establecimiento",
        ["establecimiento_id"],
        ["establecimiento_id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "reporte",
        "fecha_creacion",
        existing_type=sa.TIMESTAMP(),
        new_column_name="fecha_generacion",
    )
    op.drop_column("reporte", "usuario_id")
    op.drop_column("reporte", "tipo")
    op.drop_column("reporte", "entidad_id")
    op.drop_column("reporte", "estado")
    op.drop_column("reporte", "fecha_resolucion")

    # --- Plan: precio_mensual -> precio, drop non-ERD limits ---
    op.alter_column(
        "plan",
        "precio_mensual",
        existing_type=mysql.DECIMAL(precision=10, scale=2),
        new_column_name="precio",
    )
    op.drop_column("plan", "max_servicios")
    op.drop_column("plan", "max_trabajadores")
    op.drop_column("plan", "max_citas_mes")

    # --- Notificacion: leido -> leida ---
    op.alter_column(
        "notificacion",
        "leido",
        existing_type=sa.Boolean(),
        new_column_name="leida",
    )

    # --- Suscripcion: drop auto_renovacion ---
    op.drop_column("suscripcion", "auto_renovacion")

    # --- Pago: drop transaccion_id ---
    op.drop_column("pago", "transaccion_id")

    # --- Remove non-ERD timestamp columns ---
    op.drop_column("establecimiento", "fecha_creacion")
    op.drop_column("servicio", "fecha_creacion")
    op.drop_column("perfil", "fecha_actualizacion")


def downgrade() -> None:
    """Downgrade schema."""
    # Best-effort downgrade to the pre-ERD schema shape.

    # Recreate trabajador-related tables first (they are referenced by FKs below)
    op.create_table(
        "trabajador",
        sa.Column("trabajador_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("establecimiento_id", sa.Integer(), nullable=True),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("correo", sa.String(length=100), nullable=False),
        sa.Column("telefono", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("trabajador_id"),
    )
    op.create_table(
        "trabajadorservicio",
        sa.Column("trabajador_id", sa.Integer(), nullable=False),
        sa.Column("servicio_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["servicio_id"], ["servicio.servicio_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["trabajador_id"], ["trabajador.trabajador_id"], ondelete="CASCADE"),
    )
    op.create_index(
        "unique_trabajador_servicio",
        "trabajadorservicio",
        ["trabajador_id", "servicio_id"],
        unique=True,
    )
    op.create_table(
        "bloqueoagenda",
        sa.Column("bloqueo_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("trabajador_id", sa.Integer(), nullable=True),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=False),
        sa.Column("hora_fin", sa.Time(), nullable=False),
        sa.ForeignKeyConstraint(["trabajador_id"], ["trabajador.trabajador_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("bloqueo_id"),
    )

    # Re-add timestamp columns
    op.add_column(
        "perfil",
        sa.Column(
            "fecha_actualizacion",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    op.add_column(
        "servicio",
        sa.Column(
            "fecha_creacion",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    op.add_column(
        "establecimiento",
        sa.Column(
            "fecha_creacion",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )

    # Pago
    op.add_column("pago", sa.Column("transaccion_id", sa.String(length=255), nullable=True))

    # Suscripcion
    op.add_column("suscripcion", sa.Column("auto_renovacion", sa.Boolean(), nullable=True))

    # Notificacion
    op.alter_column(
        "notificacion",
        "leida",
        existing_type=sa.Boolean(),
        new_column_name="leido",
    )

    # Plan
    op.add_column("plan", sa.Column("max_servicios", sa.Integer(), nullable=True))
    op.add_column("plan", sa.Column("max_trabajadores", sa.Integer(), nullable=True))
    op.add_column("plan", sa.Column("max_citas_mes", sa.Integer(), nullable=True))
    op.alter_column(
        "plan",
        "precio",
        existing_type=mysql.DECIMAL(precision=10, scale=2),
        new_column_name="precio_mensual",
    )

    # Reporte
    op.add_column("reporte", sa.Column("fecha_resolucion", sa.TIMESTAMP(), nullable=True))
    op.add_column(
        "reporte",
        sa.Column(
            "estado",
            sa.Enum("PENDIENTE", "EN_REVISION", "RESUELTO", "RECHAZADO", name="reportstatus"),
            nullable=True,
        ),
    )
    op.add_column("reporte", sa.Column("entidad_id", sa.Integer(), nullable=False))
    op.add_column(
        "reporte",
        sa.Column(
            "tipo",
            sa.Enum("USUARIO", "ESTABLECIMIENTO", "SERVICIO", "CITA", "TRABAJADOR", name="reporttype"),
            nullable=False,
        ),
    )
    op.add_column("reporte", sa.Column("usuario_id", sa.Integer(), nullable=True))
    op.alter_column(
        "reporte",
        "fecha_generacion",
        existing_type=sa.TIMESTAMP(),
        new_column_name="fecha_creacion",
    )
    op.drop_constraint("reporte_ibfk_establecimiento", "reporte", type_="foreignkey")
    op.drop_column("reporte", "establecimiento_id")
    op.create_foreign_key(
        "reporte_ibfk_1",
        "reporte",
        "usuario",
        ["usuario_id"],
        ["usuario_id"],
        ondelete="SET NULL",
    )

    # Resena
    op.add_column("resena", sa.Column("trabajador_id", sa.Integer(), nullable=True))
    op.add_column("resena", sa.Column("cita_id", sa.Integer(), nullable=True))
    op.alter_column(
        "resena",
        "fecha",
        existing_type=sa.TIMESTAMP(),
        new_column_name="fecha_creacion",
    )
    op.drop_constraint("resena_ibfk_establecimiento", "resena", type_="foreignkey")
    op.drop_column("resena", "establecimiento_id")
    op.create_foreign_key(
        "resena_ibfk_1",
        "resena",
        "cita",
        ["cita_id"],
        ["cita_id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "resena_ibfk_2",
        "resena",
        "trabajador",
        ["trabajador_id"],
        ["trabajador_id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint("unique_cita_usuario", "resena", ["cita_id", "usuario_id"])
    op.create_index("trabajador_id", "resena", ["trabajador_id"], unique=False)

    # Cita
    op.add_column("cita", sa.Column("fecha_modificacion", sa.TIMESTAMP(), nullable=True))
    op.add_column("cita", sa.Column("notas_cliente", sa.Text(), nullable=True))
    op.add_column("cita", sa.Column("trabajador_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "cita_ibfk_3",
        "cita",
        "trabajador",
        ["trabajador_id"],
        ["trabajador_id"],
        ondelete="CASCADE",
    )

    # Agenda
    op.add_column("agenda", sa.Column("trabajador_id", sa.Integer(), nullable=True))
    op.drop_constraint("unique_establecimiento_dia", "agenda", type_="unique")
    op.drop_constraint("agenda_ibfk_establecimiento", "agenda", type_="foreignkey")
    op.drop_column("agenda", "establecimiento_id")
    op.create_foreign_key(
        "agenda_ibfk_1",
        "agenda",
        "trabajador",
        ["trabajador_id"],
        ["trabajador_id"],
        ondelete="CASCADE",
    )
    op.create_index("unique_trabajador_dia", "agenda", ["trabajador_id", "dia_semana"], unique=True)

