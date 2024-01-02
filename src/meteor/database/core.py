import functools
import re
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import MetaData, create_engine, inspect
from sqlalchemy.sql.expression import true
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session, sessionmaker, object_session
from sqlalchemy_utils import get_mapper
from pydantic.errors import PydanticErrorMixin
from starlette.requests import Request

from meteor import config
from meteor.exceptions import NotFoundError
from meteor.search.fulltext import make_searchable

engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI,
    pool_size=config.DATABASE_ENGINE_POOL_SIZE,
    max_overflow=config.DATABASE_ENGINE_MAX_OVERFLOW,
    pool_pre_ping=config.DATABASE_ENGINE_POOL_PING,
)


def get_db(request: Request):
    return request.state.db


DbSession = Annotated[Session, Depends(get_db)]

SessionLocal = sessionmaker(bind=engine)

DB_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


def resolve_table_name(name):
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)  # noqa
    return "_".join([x.lower() for x in names if x])


raise_attribute_error = object()


def resolve_attr(obj, attr, default=None):
    """Attempts to access attr via dotted notation, returns none if attr does not exist."""
    try:
        return functools.reduce(getattr, attr.split("."), obj)
    except AttributeError:
        return default


class BaseEntity:
    __repr_attrs__ = []
    __repr_max_length__ = 15

    @declared_attr
    def __tablename__(self):
        return resolve_table_name(self.__name__)

    def dict(self):
        """Returns a dict representation of a model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @property
    def _id_str(self):
        ids = inspect(self).identity
        if ids:
            return "-".join([str(x) for x in ids]) if len(ids) > 1 else str(ids[0])
        else:
            return "None"

    @property
    def _repr_attrs_str(self):
        max_length = self.__repr_max_length__

        values = []
        single = len(self.__repr_attrs__) == 1
        for key in self.__repr_attrs__:
            if not hasattr(self, key):
                raise KeyError("{} has incorrect attribute '{}' in " "__repr__attrs__".format(self.__class__, key))
            value = getattr(self, key)
            wrap_in_quote = isinstance(value, str)

            value = str(value)
            if len(value) > max_length:
                value = value[:max_length] + "..."

            if wrap_in_quote:
                value = "'{}'".format(value)
            values.append(value if single else "{}:{}".format(key, value))

        return " ".join(values)

    def __repr__(self):
        # get id like '#123'
        id_str = ("#" + self._id_str) if self._id_str else ""
        # join class name, id and repr_attrs
        return "<{} {}{}>".format(
            self.__class__.__name__,
            id_str,
            " " + self._repr_attrs_str if self._repr_attrs_str else "",
        )


Base = declarative_base(cls=BaseEntity)
make_searchable(Base.metadata)


def get_model_name_by_tablename(table_fullname: str) -> str:
    """Returns the model name of a given table."""
    return get_class_by_tablename(table_fullname=table_fullname).__name__


def get_class_by_tablename(table_fullname: str) -> Any:
    """Return class reference mapped to table."""

    def _find_class(name):
        for c in Base._decl_class_registry.values():
            if hasattr(c, "__table__"):
                if c.__table__.fullname.lower() == name.lower():
                    return c

    mapped_name = resolve_table_name(table_fullname)
    mapped_class = _find_class(mapped_name)

    # try looking in the 'meteor_core' schema
    if not mapped_class:
        mapped_class = _find_class(f"meteor_core.{mapped_name}")

    if not mapped_class:
        raise PydanticErrorMixin(
            NotFoundError(msg="Model not found. Check the name of your model."),
            loc="filter",
        )

    return mapped_class


def get_table_name_by_class_instance(class_instance: Base) -> str:
    """Returns the name of the table for a given class instance."""
    return class_instance._sa_instance_state.mapper.mapped_table.name


def ensure_unique_default_per_project(target, value, oldvalue, initiator):
    """Ensures that only one row in table is specified as the default."""
    session = object_session(target)
    if session is None:
        return

    mapped_cls = get_mapper(target)

    if value:
        previous_default = (
            session.query(mapped_cls)
            .filter(mapped_cls.columns.default == true())
            .filter(mapped_cls.columns.project_id == target.project_id)
            .one_or_none()
        )
        if previous_default:
            # we want exclude updating the current default
            if previous_default.id != target.id:
                previous_default.default = False
                session.commit()


def refetch_db_session(organization_slug: str) -> Session:
    schema_engine = engine.execution_options(
        schema_translate_map={
            None: f"meteor_organization_{organization_slug}",
        }
    )
    db_session = sessionmaker(bind=schema_engine)()
    return db_session
