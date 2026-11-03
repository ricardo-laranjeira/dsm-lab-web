
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from api.core.config import settings
from api.models.base import Base
import api.models  # registra Usuario, Cliente, Endereco no Base.metadata


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace("%", "%%"),
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def evitar_migration_vazia(
    migration_context,
    revision,
    directives,
):
    cmd_opts = migration_context.config.cmd_opts

    if not getattr(cmd_opts, "autogenerate", False):
        return

    if not directives:
        return

    script = directives[0]

    if script.upgrade_ops.is_empty():
        directives[:] = []
        print("Nenhuma alteração detectada. Migração não criada.")



def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            process_revision_directives=evitar_migration_vazia,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

