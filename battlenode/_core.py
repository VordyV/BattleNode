import os

from ._loader import Loader
from ._events import EventHub, EventData
from ._config import Configurator, Config
from ._database import close_database
from ._plugin_statuses import PluginStatuses
import redis.asyncio as redis
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ._plugin_proxy import PluginProxy
import multiprocessing
import battlenode
import pydantic
import asyncio
import signal
import sys
import logging
import logging.config
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.patch_stdout import StdoutProxy
from callixir import AsyncSimpleShell
import json
from tortoise import Tortoise

logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("asyncmy").setLevel(logging.CRITICAL)

class BattleNodeConfig(pydantic.BaseModel):
    plugins: list[str]
    log_level: str = "INFO"
    database_host: str
    database_port: int
    database_user: str
    database_password: str
    database_name: str
    database_engine: str
    database_minsize: int = 1
    database_maxsize: int = 5
    database_timeout: int = 10
    redis_host: str
    redis_port: int
    redis_name: int
    redis_password: str

class BattleNode:

    def __init__(self, plugin_folder: str = "plugins", parent_dir: str = ""):
        self.__plugin_folder = plugin_folder
        self.__configurator = Configurator(path=os.path.join(parent_dir, f"{battlenode.__name__}.cfg.json"))
        self.__events = EventHub()
        self.__redis: redis.Redis | None = None
        self.__rps: redis.client.PubSub | None = None
        self.__config: Config = None
        self.__loader = Loader(folder=self.__plugin_folder, battlenode=self)
        self.__event = asyncio.Event()
        self.__scheduler = AsyncIOScheduler()
        self.__command_shell = AsyncSimpleShell()

        self.__events.on("battlenode.start", self.__on_event_start)
        self.__events.on("battlenode.stop", self.__on_event_stop)
        self.__events.on("battlenode.error", self.__on_event_error)
        self.__events.on("*.*", self.__on_event_all)
        self.__events.on("*.*.*", self.__on_event_all)
        self.__events.on("battlenode.plugins.statuschange", self.__on_event_pl_statuschange)

        self.__command_shell.register("plugins.stop", self.__on_cmd_plugin_stop, "Stop plugin")
        self.__command_shell.register("plugins.start", self.__on_cmd_plugin_start, "Start plugin")
        self.__command_shell.register("plugins", self.__on_cmd_plugin, "Start plugin")
        self.__command_shell.register("exit", self.__on_cmd_exit, "")
        self.__command_shell.register("install", self.__on_cmd_install, "")
        self.__command_shell.register("help", self.__on_cmd_help, "Help")

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

    @property
    def scheduler(self) -> AsyncIOScheduler:
        return self.__scheduler

    @property
    def command_shell(self) -> AsyncSimpleShell:
        return self.__command_shell

    async def __on_cmd_plugin_stop(self, plugin_name: str):
        plugin = self.__loader.get_plugin(plugin_name)
        if plugin.status != PluginStatuses.RUNNING: raise Exception("Cannot disable a plugin that is not enabled")
        await self.__loader.shutdown_plugin(plugin, "authorized_via_shell")

    async def __on_cmd_plugin_start(self, plugin_name: str):
        plugin = self.__loader.get_plugin(plugin_name)
        if plugin.status == PluginStatuses.RUNNING: raise Exception("Cannot load a plugin that is already init")
        await self.__loader.init_plugin(plugin, pre_init=True)

    async def __on_cmd_plugin(self):
        result = ["ID\tName\tStatus"]
        i = 1
        for name, plugin in self.__loader.plugins.items():
            result.append(f"{i}\t{name}\t{plugin.status.name}{' (%s) ' % plugin.exitcode if plugin.exitcode else ''}")
            i += 1
        print("\n".join(result))

    async def __on_cmd_exit(self):
        self.__signal_handler(None, None)

    async def __on_cmd_install(self):
        await Tortoise.generate_schemas(safe=True)

    async def __on_cmd_help(self):
        print(self.__command_shell.beautiful_help)

    async def __on_event_all(self, event, *args):
        try:
            event_data = json.dumps(args)
        except:
            event_data = None

        try:
            data = {
                "sender": "core",
                "data": event_data
            }
            await self.__redis.publish(event.name, json.dumps(data))
        except Exception as error:
            logger.error(f"Error sending event '{event.name}' to redis: {error}")

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
            return True
        except Exception as error:
            print("Config was not loaded. Further application operation is impossible until errors are fixed")
            if isinstance(error, pydantic.ValidationError): print("\t".join([f"{e['msg']} - `{".".join(e['loc'])}`" for e in error.errors()]))
            else: print(error)
            #self.__events.emit_future(f"{battlenode.__name__}.error", f"configuration has not been loaded: {error}")
        return False

    async def interactive_shell(self):

        session = PromptSession("")

        while True:
            try:
                data = await session.prompt_async(handle_sigint=False)
                cmd = await self.__command_shell.execute(data)
                if cmd.error: print(cmd.error)
            except (EOFError, KeyboardInterrupt):
                self.__signal_handler(None, None)
                return
            except asyncio.CancelledError:
                return

    async def __start(self):
        with patch_stdout(raw=True):
            try:
                await self.__configurator.load()
                if not await self.__load_config(): return
                self.__redis = redis.Redis(host=self.__config.get("redis_host"), port=self.__config.get("redis_port"), db=self.__config.get("redis_name"), password=self.__config.get("redis_password"))
                logger.remove()
                logger.add(StdoutProxy(raw=True), colorize=True, enqueue=True, format="<green>{time:HH:mm:ss}</green> <level>{message}</level>", level=self.__config.get("log_level"), filter=lambda record: "plugin" not in record["extra"])
                logger.add(StdoutProxy(raw=True), colorize=True, enqueue=True, format="<green>{time:HH:mm:ss}</green> <white>[{extra[plugin]}]</white> <level>{message}</level>", level=self.__config.get("log_level"), filter=lambda record: "plugin" in record["extra"])
                self.__events.emit_future(f"{battlenode.__name__}.start")
                #self.__rps = self.__redis.pubsub()
                await self.__loader.init()
                await self.__loader.load_plugins()
                self.__scheduler.start()
                shell = asyncio.create_task(self.interactive_shell())
                channel_handler = asyncio.create_task(self.__channel_handler())
                await self.__event.wait()
                self.__events.emit_future(f"{battlenode.__name__}.stop")
                self.__events.emit_future(f"{battlenode.__name__}.database.close")
                await close_database()
                await self.__redis.close()
                await self.__loader.shutdown_plugins()
                await self.__loader.shutdown()
                self.__scheduler.shutdown()
            except Exception as error:
                logger.exception(error)
            finally:
                self.__event.clear()

    def run(self):
        # The __signal_handler is called by the interactive_shell method on a KeyboardInterrupt exception
        #signal.signal(signal.SIGINT, self.__signal_handler)
        #signal.signal(signal.SIGTERM, self.__signal_handler)
        print(f"BattleNode login server emulator v{battlenode.__version__}\nby VordyV aka Vladislav Netievsky\nweb: vorklab.space")
        asyncio.run(self.__start())

    def get_plugin(self, name: str) -> PluginProxy:
        plugin = self.loader.get_plugin(name=name)
        return PluginProxy(plugin=plugin)

    async def __channel_handler(self):
        pubsub = self.__redis.pubsub()
        await pubsub.psubscribe("*")

        try:
            logger.info("Redis channel listening has started")
            while True:
                message = await pubsub.get_message(timeout=0.1, ignore_subscribe_messages=True)
                if message is not None:
                    if message["type"] in ["message", "pmessage"]:
                        #logger.info(f"CH {message}")
                        data = json.loads(message["data"].decode())
                        if data["sender"] == "core": continue
                        if data["data"]: self.__events.emit_future(message["channel"].decode(), data["data"])
                        else: self.__events.emit_future(message["channel"].decode())

                await asyncio.sleep(0)
        except Exception as error:
            logger.info(f"Redis channel listening has ended: {error}")
            await pubsub.punsubscribe("*")
            await pubsub.close()
