from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import text
from sqlalchemy import pool

from app.db.base_class import Base

# Import models so SQLAlchemy registers tables on Base.metadata
import app.models  # noqa: F401


config = context.config

if config.config_file_name is not None:
	fileConfig(config.config_file_name)


_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_backend_dir, ".env"))

_database_url = os.getenv("DATABASE_URL")
if _database_url:
	config.set_main_option("sqlalchemy.url", _database_url)


target_metadata = Base.metadata


def _seed_default_roles(connection) -> None:
	# Ensure table exists and capture the real name (Windows may store it lowercase).
	table_name = connection.execute(
		text(
			"""
			SELECT table_name
			FROM information_schema.tables
			WHERE table_schema = DATABASE()
			  AND LOWER(table_name) = 'rol'
			LIMIT 1
			"""
		)
	).scalar()
	if not table_name:
		return

	# Idempotent seed: insert only if the row doesn't exist yet.
	connection.execute(
		text(
			f"""
			INSERT IGNORE INTO `{table_name}` (`rol_id`, `nombre`, `descripcion`) VALUES
				(1, 'CLIENTE', 'Usuario final que reserva citas'),
				(2, 'Dueño', 'Dueño de establecimiento'),
				(3, 'Admin', 'Administrador del sistema')
			"""
		)
	)

	# Make sure changes persist even if Alembic ran a no-op migration.
	try:
		connection.commit()
	except Exception:
		pass


def run_migrations_offline() -> None:
	url = config.get_main_option("sqlalchemy.url")
	context.configure(
		url=url,
		target_metadata=target_metadata,
		literal_binds=True,
		dialect_opts={"paramstyle": "named"},
		compare_type=True,
	)

	with context.begin_transaction():
		context.run_migrations()


def run_migrations_online() -> None:
	configuration = config.get_section(config.config_ini_section) or {}
	connectable = engine_from_config(
		configuration,
		prefix="sqlalchemy.",
		poolclass=pool.NullPool,
	)

	with connectable.connect() as connection:
		context.configure(
			connection=connection,
			target_metadata=target_metadata,
			compare_type=True,
		)

		with context.begin_transaction():
			context.run_migrations()

		# Seed data outside of Alembic's migration transaction.
		_seed_default_roles(connection)


if context.is_offline_mode():
	run_migrations_offline()
else:
	run_migrations_online()