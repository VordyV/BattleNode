from ._plugin_statuses import PluginStatuses
from ._events import EventCollection
from ._config import Config as Configure
from abc import ABC
from loguru import logger
import battlenode
import pydantic

class BasePlugin(ABC):

    events: EventCollection = None
    Config: pydantic.BaseModel = None
    models: list[str] = []

    def __init__(self, battlenode, config: Configure, logger):
        self.__battlenode = battlenode
        self.__config = config
        self.__logger = logger

    @property
    def battlenode(self):
        return self.__battlenode

    @property
    def config(self):
        return self.__config

    @property
    def logger(self):
        return self.__logger

    class Meta:
        name: str = None
        version: str = None
        requires_battlenode: str = None
        dependencies: dict[str, str] = {}

class Plugin:

    def __init__(self, name: str, module: object = None, instance: object = None):
        self.__name = name
        self.__module = module
        self.__instance = instance
        self.__status: PluginStatuses = PluginStatuses.WAITING
        self.__meta: BasePlugin.Meta = None
        self.__logger = logger.bind(plugin=self.__name)

    @property
    def instance(self):
        return self.__instance

    @property
    def name(self):
        return self.__name

    @property
    def module(self):
        return self.__module

    @property
    def status(self):
        return self.__status

    @property
    def meta(self):
        return self.__meta

    @property
    def logger(self):
        return self.__logger

    def _set_instance(self, instance: BasePlugin):
        self.__instance = instance
        self.__meta = instance.Meta
        if self.__meta.name is None: self.__meta.name = self.__name
        if self.__meta.requires_battlenode is None: self.__meta.requires_battlenode = f"=={battlenode.__version__}"

    def _set_status(self, status: PluginStatuses):
        self.__status = status

    def _set_module(self, module: object):
        self.__module = module