from ._loader import Loader
from ._events import eventsEmitter
from ._config import Configurator
from loguru import logger
from typing import Any
import battlenode
import pydantic
import asyncio
import signal
import sys

class DataBaseConfig(pydantic.BaseModel):
    engine: str = "tortoise.backends.mysql"
    host: str
    port: int
    user: str
    password: str
    name: str
    use_tz: bool = False
    timezone: str = "UTC"

class BattleNodeConfig(pydantic.BaseModel):
    database: DataBaseConfig

class BattleNode:

    def __init__(self, plugin_folder: str = "plugins"):
        self.__plugin_folder = plugin_folder
        self.__configurator = Configurator(filename=f"{battlenode.__name__}.cfg.json")
        self.__config = None
        self.__loader = Loader(folder=self.__plugin_folder, battlenode=self)
        self.__event = asyncio.Event()

        logger.remove()
        logger.add(sys.stdout, colorize=True, enqueue=True, format="<green>{time:HH:mm:ss}</green> <level>{message}</level>", filter=lambda record: "plugin" not in record["extra"])
        logger.add(sys.stdout, colorize=True, enqueue=True, format="<green>{time:HH:mm:ss}</green> <white>[{extra[plugin]}]</white> <level>{message}</level>", filter=lambda record: "plugin" in record["extra"])

        eventsEmitter.on("battlenode.start", self.__on_event_start)
        eventsEmitter.on("battlenode.stop", self.__on_event_stop)

    @property
    def configurator(self):
        return self.__configurator

    @property
    def loader(self):
        return self.__loader

    @property
    def config(self):
        return self.__config

    def __signal_handler(self, sig, frame):
        self.__event.set()

    async def __on_event_start(self):
        logger.info("BattleNode Launch...")

    async def __on_event_stop(self):
        logger.info("Shutting down...")

    def __load_config(self):
        try:
            self.__config = self.__configurator.get_section(battlenode.__name__, BattleNodeConfig)
        except Exception as error:
            logger.error("configuration has not been loaded: {error}", error=error)

    async def __start(self):
        eventsEmitter.emit_future(f"{battlenode.__name__}.start")
        await self.__configurator.load()
        self.__load_config()
        await self.__loader.load_plugins()
        await self.__event.wait()
        eventsEmitter.emit_future(f"{battlenode.__name__}.stop")
        await self.__loader.shutdown_plugins()

    def run(self):
        signal.signal(signal.SIGINT, self.__signal_handler)
        signal.signal(signal.SIGTERM, self.__signal_handler)
        asyncio.run(self.__start())

