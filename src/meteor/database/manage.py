import os
import logging

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig

from sqlalchemy import text
from sqlalchemy.schema import CreateSchema
from sqlalchemy_utils import create_database, database_exists

from meteor import config
from meteor.organization.models import Organization
from meteor.search import fulltext
from meteor.search.fulltext import (
    sync_trigger,
)

from .core import Base, sessionmaker

METEOR_ORGANIZATION_SCHEMA_PREFIX = "meteor_organization"


log = logging.getLogger(__file__)


def version_schema(script_location: str):
    """Applies alembic versioning to schema."""

    # add it to alembic table
    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_command.stamp(alembic_cfg, "head")


def get_core_tables():
    """Fetches tables that belong to the 'meteor_core' schema."""
    core_tables = []
    for _, table in Base.metadata.tables.items():
        if table.schema == "meteor_core":
            core_tables.append(table)
    return core_tables


def get_tenant_tables():
    """Fetches tables that belong to their own tenant tables."""
    tenant_tables = []
    for _, table in Base.metadata.tables.items():
        if not table.schema:
            tenant_tables.append(table)
    return tenant_tables


def init_database(engine):
    """Initializes the database."""
    if not database_exists(str(config.SQLALCHEMY_DATABASE_URI)):
        create_database(str(config.SQLALCHEMY_DATABASE_URI))

    schema_name = "meteor_core"
    if not engine.dialect.has_schema(engine, schema_name):
        with engine.connect() as connection:
            connection.execute(CreateSchema(schema_name))
            print(f"Created schema: {schema_name}")

    tables = get_core_tables()

    Base.metadata.create_all(engine, tables=tables)

    version_schema(script_location=config.ALEMBIC_CORE_REVISION_PATH)
    setup_fulltext_search(engine, tables)

    # setup an required database functions
    session = sessionmaker(bind=engine)
    db_session = session()

    # we create the default organization if it doesn't exist
    organization = db_session.query(Organization).filter(Organization.name == "default").one_or_none()
    if not organization:
        print("Creating default organization...")
        organization = Organization(
            name="default",
            slug="default",
            default=True,
            description="Default Meteor organization.",
        )

        db_session.add(organization)
        db_session.commit()

    # we initialize the database schema
    init_schema(engine=engine, organization=organization)

    # we install all plugins
    # from meteor.common.utils.cli import install_plugins
    # from meteor.plugins.base import plugins

    # install_plugins()

    # for p in plugins.all():
    #     plugin = Plugin(
    #         title=p.title,
    #         slug=p.slug,
    #         type=p.type,
    #         version=p.version,
    #         author=p.author,
    #         author_url=p.author_url,
    #         multiple=p.multiple,
    #         description=p.description,
    #     )
    #     db_session.add(plugin)
    # db_session.commit()


def init_schema(*, engine, organization: Organization):
    """Initializes a new schema."""
    schema_name = f"{METEOR_ORGANIZATION_SCHEMA_PREFIX}_{organization.slug}"

    if not engine.dialect.has_schema(engine, schema_name):
        with engine.connect() as connection:
            connection.execute(CreateSchema(schema_name))

    # set the schema for table creation
    tables = get_tenant_tables()

    schema_engine = engine.execution_options(
        schema_translate_map={
            None: schema_name,
        }
    )

    Base.metadata.create_all(schema_engine, tables=tables)

    # put schema under version control
    version_schema(script_location=config.ALEMBIC_TENANT_REVISION_PATH)

    with engine.connect() as connection:
        # we need to map this for full text search as it uses sql literal strings
        # and schema translate map does not apply
        for t in tables:
            t.schema = schema_name

        setup_fulltext_search(connection, tables)

    session = sessionmaker(bind=schema_engine)
    db_session = session()

    organization = db_session.merge(organization)
    db_session.add(organization)
    db_session.commit()
    return organization


def setup_fulltext_search(connection, tables):
    """Syncs any required fulltext table triggers and functions."""
    # parsing functions
    function_path = os.path.join(os.path.dirname(os.path.abspath(fulltext.__file__)), "expressions.sql")
    connection.execute(text(open(function_path).read()))

    for table in tables:
        table_triggers = []
        for column in table.columns:
            if column.name.endswith("search_vector"):
                if hasattr(column.type, "columns"):
                    table_triggers.append(
                        {
                            "conn": connection,
                            "table": table,
                            "tsvector_column": "search_vector",
                            "indexed_columns": column.type.columns,
                        }
                    )
                else:
                    log.warning(f"Column search_vector defined but no index columns found. Table: {table.name}")

        for trigger in table_triggers:
            sync_trigger(**trigger)