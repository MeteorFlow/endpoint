import logging
import os

import click
import uvicorn

from meteor import __version__, config
from meteor.enums import UserRoles

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

log = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
def meteor_cli():
    """Command-line interface to Meteor."""
    from .logging import configure_logging

    configure_logging()


@meteor_cli.group("user")
def meteor_user():
    """Container for all user commands."""
    pass


@meteor_user.command("register")
@click.argument("email")
@click.option(
    "--organization",
    "-o",
    required=True,
    help="Organization to set role for.",
)
@click.password_option()
@click.option(
    "--role",
    "-r",
    required=True,
    type=click.Choice(UserRoles),
    help="Role to be assigned to the user.",
)
def register_user(email: str, role: str, password: str, organization: str):
    """Registers a new user."""
    from meteor.auth import service as user_service
    from meteor.auth.models import UserOrganization, UserRegister
    from meteor.database.core import refetch_db_session

    db_session = refetch_db_session(organization_slug=organization)
    user = user_service.get_by_email(email=email, db_session=db_session)
    if user:
        click.secho(f"User already exists. Email: {email}", fg="red")
        return

    user_organization = UserOrganization(role=role, organization={"name": organization})
    user_service.create(
        user_in=UserRegister(email=email, password=password, organizations=[user_organization]),
        db_session=db_session,
        organization=organization,
    )
    click.secho("User registered successfully.", fg="green")


@meteor_user.command("update")
@click.argument("email")
@click.option(
    "--organization",
    "-o",
    required=True,
    help="Organization to set role for.",
)
@click.option(
    "--role",
    "-r",
    required=True,
    type=click.Choice(UserRoles),
    help="Role to be assigned to the user.",
)
def update_user(email: str, role: str, organization: str):
    """Updates a user's roles."""
    from meteor.auth import service as user_service
    from meteor.auth.models import UserOrganization, UserUpdate
    from meteor.database.core import SessionLocal

    db_session = SessionLocal()
    user = user_service.get_by_email(email=email, db_session=db_session)
    if not user:
        click.secho(f"No user found. Email: {email}", fg="red")
        return

    organization = UserOrganization(role=role, organization={"name": organization})
    user_service.update(
        user=user,
        user_in=UserUpdate(id=user.id, organizations=[organization]),
        db_session=db_session,
    )
    click.secho("User successfully updated.", fg="green")


@meteor_user.command("reset")
@click.argument("email")
@click.password_option()
def reset_user_password(email: str, password: str):
    """Resets a user's password."""
    from meteor.auth import service as user_service
    from meteor.auth.models import UserUpdate
    from meteor.database.core import SessionLocal

    db_session = SessionLocal()
    user = user_service.get_by_email(email=email, db_session=db_session)
    if not user:
        click.secho(f"No user found. Email: {email}", fg="red")
        return

    user_service.update(user=user, user_in=UserUpdate(id=user.id, password=password), db_session=db_session)
    click.secho("User successfully updated.", fg="green")


@meteor_cli.group("database")
def meteor_database():
    """Container for all meteor database commands."""
    pass


@meteor_database.command("init")
def database_init():
    """Initializes a new database."""
    click.echo("Initializing new database...")
    from .database.core import engine
    from .database.manage import init_database

    init_database(engine)
    click.secho("Success.", fg="green")


@meteor_database.command("restore")
@click.option(
    "--dump-file",
    default="meteor-backup.dump",
    help="Path to a PostgreSQL text format dump file.",
)
def restore_database(dump_file):
    """Restores the database via psql."""
    from sh import ErrorReturnCode_1, createdb, psql

    from meteor.config import (
        DATABASE_CREDENTIALS,
        DATABASE_HOSTNAME,
        DATABASE_NAME,
        DATABASE_PORT,
    )

    username, password = str(DATABASE_CREDENTIALS).split(":")

    try:
        print(
            createdb(
                "-h",
                DATABASE_HOSTNAME,
                "-p",
                DATABASE_PORT,
                "-U",
                username,
                DATABASE_NAME,
                _env={"PGPASSWORD": password},
            )
        )
    except ErrorReturnCode_1:
        print("Database already exists.")

    print(
        psql(
            "-h",
            DATABASE_HOSTNAME,
            "-p",
            DATABASE_PORT,
            "-U",
            username,
            "-d",
            DATABASE_NAME,
            "-f",
            dump_file,
            _env={"PGPASSWORD": password},
        )
    )
    click.secho("Success.", fg="green")


@meteor_database.command("dump")
@click.option(
    "--dump-file",
    default="meteor-backup.dump",
    help="Path to a PostgreSQL text format dump file.",
)
def dump_database(dump_file):
    """Dumps the database via pg_dump."""
    from sh import pg_dump

    from meteor.config import (
        DATABASE_CREDENTIALS,
        DATABASE_HOSTNAME,
        DATABASE_NAME,
        DATABASE_PORT,
    )

    username, password = str(DATABASE_CREDENTIALS).split(":")

    pg_dump(
        "-f",
        dump_file,
        "-h",
        DATABASE_HOSTNAME,
        "-p",
        DATABASE_PORT,
        "-U",
        username,
        DATABASE_NAME,
        _env={"PGPASSWORD": password},
    )


@meteor_database.command("drop")
@click.option("--yes", is_flag=True, help="Silences all confirmation prompts.")
def drop_database(yes):
    """Drops all data in database."""
    from sqlalchemy_utils import database_exists, drop_database

    if database_exists(str(config.SQLALCHEMY_DATABASE_URI)):
        if yes:
            drop_database(str(config.SQLALCHEMY_DATABASE_URI))
            click.secho("Success.", fg="green")

        if click.confirm(f"Are you sure you want to drop: '{config.DATABASE_HOSTNAME}:{config.DATABASE_NAME}'?"):
            drop_database(str(config.SQLALCHEMY_DATABASE_URI))
            click.secho("Success.", fg="green")
    else:
        click.secho(f"'{config.DATABASE_HOSTNAME}:{config.DATABASE_NAME}' does not exist!!!", fg="red")


@meteor_database.command("upgrade")
@click.option("--tag", default=None, help="Arbitrary 'tag' name - can be used by custom env.py scripts.")
@click.option(
    "--sql",
    is_flag=True,
    default=False,
    help="Don't emit SQL to database - dump to standard output instead.",
)
@click.option("--revision", nargs=1, default="head", help="Revision identifier.")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]))
def upgrade_database(tag, sql, revision, revision_type):
    """Upgrades database schema to newest version."""
    import sqlalchemy
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig
    from sqlalchemy import inspect
    from sqlalchemy_utils import database_exists

    from .database.core import engine
    from .database.manage import init_database

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)

    if not database_exists(str(config.SQLALCHEMY_DATABASE_URI)):
        click.secho("Found no database to upgrade, initializing new database...")
        init_database(engine)
    else:
        conn = engine.connect()

        # detect if we need to convert to a multi-tenant schema structure
        schema_names = inspect(engine).get_schema_names()
        if "meteor_core" not in schema_names:
            click.secho("Detected single tenant database, converting to multi-tenant...")
            conn.execute(sqlalchemy.text(open(config.ALEMBIC_MULTI_TENANT_MIGRATION_PATH).read()))

        if revision_type:
            if revision_type == "core":
                path = config.ALEMBIC_CORE_REVISION_PATH

            elif revision_type == "tenant":
                path = config.ALEMBIC_TENANT_REVISION_PATH

            alembic_cfg.set_main_option("script_location", path)
            alembic_command.upgrade(alembic_cfg, revision, sql=sql, tag=tag)
        else:
            for path in [config.ALEMBIC_CORE_REVISION_PATH, config.ALEMBIC_TENANT_REVISION_PATH]:
                alembic_cfg.set_main_option("script_location", path)
                alembic_command.upgrade(alembic_cfg, revision, sql=sql, tag=tag)

    click.secho("Success.", fg="green")


@meteor_database.command("merge")
@click.argument("revisions", nargs=-1)
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
@click.option("--message")
def merge_revisions(revisions, revision_type, message):
    """Combines two revisions."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
    if revision_type == "core":
        path = config.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = config.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.merge(alembic_cfg, revisions, message=message)


@meteor_database.command("heads")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
def head_database(revision_type):
    """Shows the heads of the database."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
    if revision_type == "core":
        path = config.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = config.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.heads(alembic_cfg)


@meteor_database.command("history")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
def history_database(revision_type):
    """Shows the history of the database."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
    if revision_type == "core":
        path = config.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = config.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.history(alembic_cfg)


@meteor_database.command("downgrade")
@click.option("--tag", default=None, help="Arbitrary 'tag' name - can be used by custom env.py scripts.")
@click.option(
    "--sql",
    is_flag=True,
    default=False,
    help="Don't emit SQL to database - dump to standard output instead.",
)
@click.option("--revision", nargs=1, default="head", help="Revision identifier.")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
def downgrade_database(tag, sql, revision, revision_type):
    """Downgrades database schema to next newest version."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    if sql and revision == "-1":
        revision = "head:-1"

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
    if revision_type == "core":
        path = config.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = config.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.downgrade(alembic_cfg, revision, sql=sql, tag=tag)
    click.secho("Success.", fg="green")


@meteor_database.command("stamp")
@click.argument("revision", nargs=1, default="head")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
@click.option("--tag", default=None, help="Arbitrary 'tag' name - can be used by custom env.py scripts.")
@click.option(
    "--sql",
    is_flag=True,
    default=False,
    help="Don't emit SQL to database - dump to standard output instead.",
)
def stamp_database(revision, revision_type, tag, sql):
    """Forces the database to a given revision."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)

    if revision_type == "core":
        path = config.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = config.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.stamp(alembic_cfg, revision, sql=sql, tag=tag)


@meteor_database.command("revision")
@click.option("-m", "--message", default=None, help="Revision message")
@click.option(
    "--autogenerate",
    is_flag=True,
    help=("Populate revision script with candidate migration " "operations, based on comparison of database to model"),
)
@click.option("--revision-type", type=click.Choice(["core", "tenant"]))
@click.option("--sql", is_flag=True, help=("Don't emit SQL to database - dump to standard output " "instead"))
@click.option(
    "--head",
    default="head",
    help=("Specify head revision or <branchname>@head to base new " "revision on"),
)
@click.option("--splice", is_flag=True, help=('Allow a non-head revision as the "head" to splice onto'))
@click.option("--branch-label", default=None, help=("Specify a branch label to apply to the new revision"))
@click.option("--version-path", default=None, help=("Specify specific path from config for version file"))
@click.option("--rev-id", default=None, help=("Specify a hardcoded revision id instead of generating " "one"))
def revision_database(message, autogenerate, revision_type, sql, head, splice, branch_label, version_path, rev_id):
    """Create new database revision."""
    import types

    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
    if revision_type:
        if revision_type == "core":
            path = config.ALEMBIC_CORE_REVISION_PATH
        elif revision_type == "tenant":
            path = config.ALEMBIC_TENANT_REVISION_PATH

        alembic_cfg.set_main_option("script_location", path)
        alembic_cfg.cmd_opts = types.SimpleNamespace(cmd="revision")
        alembic_command.revision(
            alembic_cfg,
            message,
            autogenerate=autogenerate,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id,
        )
    else:
        for path in [
            config.ALEMBIC_CORE_REVISION_PATH,
            config.ALEMBIC_TENANT_REVISION_PATH,
        ]:
            print(path)
            alembic_cfg.set_main_option("script_location", path)
            alembic_cfg.cmd_opts = types.SimpleNamespace(cmd="revision")
            alembic_command.revision(
                alembic_cfg,
                message,
                autogenerate=autogenerate,
                sql=sql,
                head=head,
                splice=splice,
                branch_label=branch_label,
                version_path=version_path,
                rev_id=rev_id,
            )


@meteor_cli.group("server")
def meteor_server():
    """Container for all meteor server commands."""
    pass


@meteor_server.command("routes")
def show_routes():
    """Prints all available routes."""
    from tabulate import tabulate

    from meteor.main import api_router

    table = []
    for r in api_router.routes:
        table.append([r.path, ",".join(r.methods)])

    click.secho(tabulate(table, headers=["Path", "Authenticated", "Methods"]), fg="blue")


@meteor_server.command("config")
def show_config():
    """Prints the current config as meteor sees it."""
    import inspect
    import sys

    from tabulate import tabulate

    from meteor import config

    func_members = inspect.getmembers(sys.modules[config.__name__])

    table = []
    for key, value in func_members:
        if key.isupper():
            table.append([key, value])

    click.secho(tabulate(table, headers=["Key", "Value"]), fg="blue")


@meteor_server.command("develop")
@click.option(
    "--log-level",
    type=click.Choice(["debug", "info", "error", "warning", "critical"]),
    default="debug",
    help="Log level to use.",
)
def run_server(log_level):
    """Runs a simple server for development."""
    # Uvicorn expects lowercase logging levels; the logging package expects upper.
    os.environ["LOG_LEVEL"] = log_level.upper()
    if not os.path.isdir(config.STATIC_DIR):
        import atexit
        from subprocess import Popen

        # take our frontend vars and export them for the frontend to consume
        envvars = os.environ.copy()
        envvars.update({x: getattr(config, x) for x in dir(config) if x.startswith("VITE_")})
        is_windows = os.name == "nt"
        windows_cmds = ["cmd", "/c"]
        default_cmds = ["npm", "run", "serve"]
        cmds = windows_cmds + default_cmds if is_windows else default_cmds
        p = Popen(
            cmds,
            cwd=os.path.join("src", "meteor", "static", "meteor"),
            env=envvars,
        )
        atexit.register(p.terminate)
    uvicorn.run("meteor.main:app", reload=True, log_level=log_level)


meteor_server.add_command(uvicorn.main, name="start")


def entrypoint():
    """The entry that the CLI is executed from"""
    from .exceptions import MeteorException

    try:
        meteor_cli()
    except MeteorException as e:
        click.secho(f"ERROR: {e}", bold=True, fg="red")


if __name__ == "__main__":
    entrypoint()
