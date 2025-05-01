import os
from ._loader import Loader
from ._events import EventHub, EventData
from ._config import Configurator
from ._database import init_database, close_database
from ._plugin_statuses import PluginStatuses
import redis.asyncio as redis
from loguru import logger
import multiprocessing
import battlenode
import pydantic
import asyncio
import signal
import sys

class BattleNodeConfig(pydantic.BaseModel):
    plugins: list[str]

class BattleNode:

    def __init__(self, plugin_folder: str = "plugins"):
        multiprocessing.set_start_method("spawn", force=True)
        self.__plugin_folder = plugin_folder
        self.__configurator = Configurator(filename=f"{battlenode.__name__}.cfg.json")
        self.__events = EventHub()
        self.__redis: redis.Redis | None = None
        self.__rps: redis.client.PubSub | None = None
        self.__config = None
        self.__loader = Loader(folder=self.__plugin_folder, battlenode=self)
        self.__event = asyncio.Event()

        logger.remove()
        logger.add(sys.stdout, colorize=True, enqueue=True, format="<green>{time:HH:mm:ss}</green> <level>{message}</level>", filter=lambda record: "plugin" not in record["extra"])
        logger.add(sys.stdout, colorize=True, enqueue=True, format="<green>{time:HH:mm:ss}</green> <white>[{extra[plugin]}]</white> <level>{message}</level>", filter=lambda record: "plugin" in record["extra"])

        self.__events.on("battlenode.start", self.__on_event_start)
        self.__events.on("battlenode.stop", self.__on_event_stop)
        self.__events.on("battlenode.error", self.__on_event_error)
        self.__events.on("*.*", self.__on_event_all)
        self.__events.on("*.*.*", self.__on_event_all)
        self.__events.on("battlenode.plugins.statuschange", self.__on_event_pl_statuschange)

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

    @property
    def redis(self):
        return self.__redis

    async def __on_event_all(self, event, *args):
        await self.__redis.publish(event.name, "9")

    def __signal_handler(self, sig, frame):
        self.__event.set()

    async def __on_event_pl_statuschange(self, event: EventData, status: PluginStatuses, plugin):
        plugin.logger.debug(f"Status {status.name}")

    async def __on_event_start(self, event: EventData):
        logger.info("BattleNode Launch")

    async def __on_event_stop(self, event: EventData):
        logger.info("Shutting down")

    async def __on_event_error(self, event: EventData, error):
        logger.error(error)

    async def __load_config(self):
        try:
            self.__config = self.__configurator.get_section(battlenode.__name__, BattleNodeConfig)
        except Exception as error:
            self.__events.emit_future(f"{battlenode.__name__}.error", f"configuration has not been loaded: {error}")

    async def __start(self):
        self.__redis = redis.Redis(host=os.getenv("BN_REDIS_HOST"), port=int(os.getenv("BN_REDIS_PORT")), db=int(os.getenv("BN_REDIS_NAME")), password=os.getenv("BN_REDIS_PASSWORD"))
        self.__events.emit_future(f"{battlenode.__name__}.start")
        await self.__configurator.load()
        await self.__load_config()
        #self.__rps = self.__redis.pubsub()
        await self.__loader.init()
        await self.__loader.load_plugins()
        await self.__event.wait()
        self.__events.emit_future(f"{battlenode.__name__}.stop")
        self.__events.emit_future(f"{battlenode.__name__}.database.close")
        await close_database()
        await self.__loader.shutdown_plugins()
        await self.__redis.close()

    def run(self):
        signal.signal(signal.SIGINT, self.__signal_handler)
        signal.signal(signal.SIGTERM, self.__signal_handler)
        asyncio.run(self.__start())

