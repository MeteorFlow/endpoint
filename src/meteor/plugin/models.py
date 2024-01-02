import logging

from typing import Any, List, Optional
from pydantic import Field, SecretStr
from pydantic.json import pydantic_encoder

from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import TSVectorType, StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


from meteor.database.core import Base
from meteor.config import METEOR_ENCRYPTION_KEY
from meteor.models import MeteorBase, Pagination
from meteor.plugins.base import plugins

logger = logging.getLogger(__name__)


def show_secrets_encoder(obj):
    if type(obj) == SecretStr:
        return obj.get_secret_value()
    else:
        return pydantic_encoder(obj)


class Plugin(Base):
    __table_args__ = {"schema": "meteor_core"}
    id = Column(Integer, primary_key=True)
    title = Column(String)
    slug = Column(String, unique=True)
    description = Column(String)
    version = Column(String)
    author = Column(String)
    author_url = Column(String)
    type = Column(String)
    multiple = Column(Boolean)

    search_vector = Column(
        TSVectorType(
            "title",
            "slug",
            "type",
            "description",
            weights={"title": "A", "slug": "B", "type": "C", "description": "C"},
        )
    )

    @property
    def configuration_schema(self):
        """Renders the plugin's schema to JSON Schema."""
        try:
            plugin = plugins.get(self.slug)
            return plugin.configuration_schema.schema()
        except Exception as e:
            logger.warning(f"Error trying to load configuration_schema for plugin with slug {self.slug}: {e}")
            return None


class PluginInstance(Base):
    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean)
    _configuration = Column(StringEncryptedType(key=str(METEOR_ENCRYPTION_KEY), engine=AesEngine, padding="pkcs5"))
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
    plugin = relationship(Plugin, backref="instances")

    # this is some magic that allows us to use the plugin search vectors
    # against our plugin instances
    search_vector = association_proxy("plugin", "search_vector")

    @property
    def instance(self):
        """Fetches a plugin instance that matches this record."""
        try:
            plugin = plugins.get(self.plugin.slug)
            plugin.configuration = self.configuration
            plugin.project_id = self.project_id
            return plugin
        except Exception as e:
            logger.warning(f"Error trying to load plugin with slug {self.slug}: {e}")
            return self.plugin

    @property
    def broken(self):
        try:
            plugins.get(self.plugin.slug)
            return False
        except Exception:
            return True

    @property
    def configuration_schema(self):
        """Renders the plugin's schema to JSON Schema."""
        try:
            plugin = plugins.get(self.plugin.slug)
            return plugin.configuration_schema.schema()
        except Exception as e:
            logger.warning(f"Error trying to load plugin {self.plugin.title} {self.plugin.description} with error {e}")
            return None

    @hybrid_property
    def configuration(self):
        """Property that correctly returns a plugins configuration object."""
        try:
            if self._configuration:
                plugin = plugins.get(self.plugin.slug)
                return plugin.configuration_schema.parse_raw(self._configuration)
        except Exception as e:
            logger.warning(f"Error trying to load plugin {self.plugin.title} {self.plugin.description} with error {e}")
            return None

    @configuration.setter
    def configuration(self, configuration):
        """Property that correctly sets a plugins configuration object."""
        if configuration:
            plugin = plugins.get(self.plugin.slug)
            config_object = plugin.configuration_schema.parse_obj(configuration)
            self._configuration = config_object.json(encoder=show_secrets_encoder)


# Pydantic models...
class PluginBase(MeteorBase):
    pass


class PluginRead(PluginBase):
    id: PrimaryKey
    title: str
    slug: str
    author: str
    author_url: str
    type: str
    multiple: bool
    configuration_schema: Any
    description: Optional[str] = Field(None, nullable=True)


class PluginInstanceRead(PluginBase):
    id: PrimaryKey
    enabled: Optional[bool]
    configuration: Optional[dict]
    configuration_schema: Any
    plugin: PluginRead
    broken: Optional[bool]


class PluginInstanceReadMinimal(PluginBase):
    id: PrimaryKey
    enabled: Optional[bool]
    configuration_schema: Any
    plugin: PluginRead
    broken: Optional[bool]


class PluginInstanceCreate(PluginBase):
    enabled: Optional[bool]
    configuration: Optional[dict]
    plugin: PluginRead


class PluginInstanceUpdate(PluginBase):
    id: PrimaryKey = None
    enabled: Optional[bool]
    configuration: Optional[dict]


class KeyValue(MeteorBase):
    key: str
    value: str


class PluginMetadata(MeteorBase):
    slug: str
    metadata: List[KeyValue] = []


class PluginPagination(Pagination):
    items: List[PluginRead] = []


class PluginInstancePagination(Pagination):
    items: List[PluginInstanceReadMinimal] = []
