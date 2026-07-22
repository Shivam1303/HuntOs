"""Alembic environment configured from the application database URL."""

from sqlalchemy import engine_from_config, pool

from alembic import context
from core.config.settings import get_database_url
from core.database.models import Base
from modules.opportunities.models import (
    ApplicationOutcomeRecord,
    DeveloperProfileRecord,
    ParsedOpportunityRecord,
    RawOpportunityRecord,
)
from modules.proposals.models import ProposalDraftRecord
from modules.scoring.models import OpportunityScoreRecord

REGISTERED_MODELS = (
    ApplicationOutcomeRecord,
    DeveloperProfileRecord,
    ParsedOpportunityRecord,
    ProposalDraftRecord,
    RawOpportunityRecord,
    OpportunityScoreRecord,
)

config = context.config

database_url = config.attributes.get("database_url") or get_database_url()
config.set_main_option("sqlalchemy.url", database_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live database connection."""

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live Psycopg 3 database connection."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
