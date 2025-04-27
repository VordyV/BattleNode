from ._loader import Loader
from ._events import EventHub, EventData
from ._config import Configurator
from ._database import init_database, close_database
from loguru import logger
import multiprocessing
import battlenode
import pydantic
import asyncio
import signal
import sys

class DataBaseConfig(pydantic.BaseModel):
    engine: str = "tortoise.backends.mysql"
    use_tz: bool = False
    timezone: str = "UTC"

class BattleNodeConfig(pydantic.BaseModel):
    database: DataBaseConfig
    plugins: list[str]

class BattleNode:

    def __init__(self, plugin_folder: str = "plugins"):
        multiprocessing.set_start_method("spawn", force=True)
        self.__plugin_folder = plugin_folder
        self.__configurator = Configurator(filename=f"{battlenode.__name__}.cfg.json")
        self.__events = EventHub()
        self.__config = None
        self.__loader = Loader(folder=self.__plugin_folder, battlenode=self)
        self.__event = asyncio.Event()

        logger.remove()
        logger.add(sys.stdout, colorize=True, enqueue=True, format="<green>{time:HH:mm:ss}</green> <level>{message}</level>", filter=lambda record: "plugin" not in record["extra"])
        logger.add(sys.stdout, colorize=True, enqueue=True, format="<green>{time:HH:mm:ss}</green> <white>[{extra[plugin]}]</white> <level>{message}</level>", filter=lambda record: "plugin" in record["extra"])

        self.__events.on("battlenode.start", self.__on_event_start)
        self.__events.on("battlenode.stop", self.__on_event_stop)
        self.__events.on("battlenode.error", self.__on_event_error)

    @property
    def events(self):
        return self.__events

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

    async def __on_event_start(self, event: EventData):
        logger.info("BattleNode Launch...")

    async def __on_event_stop(self, event: EventData):
        logger.info("Shutting down...")

    async def __on_event_error(self, event: EventData, error):
        logger.error(error)

    async def __load_config(self):
        try:
            self.__config = self.__configurator.get_section(battlenode.__name__, BattleNodeConfig)
        except Exception as error:
            self.__events.emit_future(f"{battlenode.__name__}.error", f"configuration has not been loaded: {error}")

    async def __start(self):
        self.__events.emit_future(f"{battlenode.__name__}.start")
        await self.__configurator.load()
        await self.__load_config()
        await self.__loader.init()
        await self.__loader.load_plugins()
        await self.__event.wait()
        self.__events.emit_future(f"{battlenode.__name__}.stop")
        await close_database()
        await self.__loader.shutdown_plugins()

    def run(self):
        signal.signal(signal.SIGINT, self.__signal_handler)
        signal.signal(signal.SIGTERM, self.__signal_handler)
        asyncio.run(self.__start())

