from ._plugin_statuses import PluginStatuses
from ._events import EventCollection
from ._config import Config as Configure
from abc import ABC
from loguru import logger
from typing import Callable, Optional
from ._shared_data import SharedData
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import battlenode
import pydantic
from ._commands import CommandCollection

class BasePlugin(ABC):

    events: EventCollection = None
    Config: Optional[pydantic.BaseModel] = None
    app: Optional[list[str]] = []
    process_target: Optional[Callable] = None
    run_as_process: Optional[bool] = False
    commands: CommandCollection = None

    def __init__(self, battlenode, config: Configure, logger, shared_data: SharedData, scheduler: AsyncIOScheduler):
        self.__battlenode = battlenode
        self.__config = config
        self.__logger = logger
        self.__shared_data = shared_data
        self.__scheduler = scheduler

    @property
    def battlenode(self):
        return self.__battlenode

    @property
    def config(self) -> Configure:
        return self.__config

    @property
    def logger(self):
        return self.__logger

    @property
    def shared_data(self) -> SharedData:
        return self.__shared_data

    @property
    def scheduler(self) -> AsyncIOScheduler:
        return self.__scheduler

    class Meta:
        name: str = None
        version: str = None
        requires_battlenode: str = None
        dependencies: dict[str, str] = {}

class Plugin:

    def __init__(self, name: str, module: object = None, instance: BasePlugin | None = None):
        self.__name = name
        self.__module = module
        self.__instance = instance
        self.__status: PluginStatuses = PluginStatuses.WAITING
        self.__meta: BasePlugin.Meta = None
        self.__logger = logger.bind(plugin=self.__name)
        self.__app: dict = {}
        self.__exitcode: str | None = None
        self.__error: str | None = None

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

    @property
    def app(self):
        return self.__app

    @property
    def exitcode(self):
        return self.__exitcode

    @property
    def error(self):
        return self.__error

    def _set_instance(self, instance: BasePlugin):
        self.__instance = instance
        self.__meta = instance.Meta
        if self.__meta.name is None: self.__meta.name = self.__name
        if self.__meta.requires_battlenode is None: self.__meta.requires_battlenode = f"=={battlenode.__version__}"

    def _set_status(self, status: PluginStatuses):
        self.__status = status

    def _set_module(self, module: object):
        self.__module = module

    def _set_app(self, app: dict):
        self.__app = app

    def _del_instance(self):
        self.__instance = None

    def _set_exitcode(self, text: str | None):
        self.__exitcode = text

    def _set_error(self, text: str | None):
        self.__error = text