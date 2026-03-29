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
import re

logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("asyncmy").setLevel(logging.CRITICAL)

class BattleNodeConfig(pydantic.BaseModel):
    plugins: list[str]
    log_level: str = "INFO"
    write_logs_file: bool = False
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

    shell_cursor: str = ""
    log_dir: str = "logs"

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
        self.__prompt_session: PromptSession | None = None

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

    @property
    def prompt_session(self) -> PromptSession:
        return self.__prompt_session

    async def prompt(self, message: str, value: str = None, is_password: bool = False, not_empty: bool = False, regex: str = None, min_length: int = None, max_length: int = 128, enum: list = None) -> str | None:
        while 1:
            try:
                result = await self.__prompt_session.prompt_async(message, handle_sigint=False, is_password=is_password)

                result = result.strip()

                if result == "" and not_empty:
                    print("You didn't enter anything. Please specify what is required")
                    continue

                if enum is not None and result not in enum:
                    print(f"Invalid value. Allowed values are: {', '.join(enum)}")
                    continue

                if max_length is not None and len(result) > max_length:
                    print(f"Exceeded the allowed string length ({max_length})")
                    continue

                if min_length is not None and len(result) < min_length:
                    print(f"String is too short ({min_length})")
                    continue

                if regex and not_empty and not bool(re.compile(regex).fullmatch(result)):
                    print("Invalid value")
                    continue

                if result == "" and value:
                    return value
                return result
            except (EOFError, KeyboardInterrupt):
                return None

    async def prompt_int(self, message: str, value: int = None) -> int | None:
        while 1:
            result = await self.prompt(message, str(value))

            if not result.isdigit():
                print("Please specify an integer")
                continue

            return int(result)

    async def prompt_bool(self, message: str, value: bool = None) -> bool | None:
        while 1:
            result = await self.prompt(message, "1" if value else "0")

            if result in ["y", "Y", "1", "t", "T"]: return True
            elif result in ["n", "N", "0", "f", "F"]: return False
            else:
                print("Specify 'y' (yes) or 'n' (no)")
                continue

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
        if event.from_redis: return

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
            logger.debug(f"Error sending event '{event.name}' to redis: {error}")

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

        self.__prompt_session = PromptSession()

        while True:
            try:
                data = await self.__prompt_session.prompt_async(BattleNode.shell_cursor, handle_sigint=False)
                if data.strip() == "": continue

                cmd = await self.__command_shell.execute(data)
                if cmd.error:
                    print(cmd.error)
                    #print(cmd.err_traceback)
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
                if self.config.get("write_logs_file"):
                        logger.add(os.path.join(BattleNode.log_dir, "bn_{time:YYYY-MM-DD}.log"), rotation="00:00", enqueue=True, format="{time:HH:mm:ss} [{level}] - {message}", level="DEBUG", filter=lambda record: "plugin" not in record["extra"])
                        logger.add(os.path.join(BattleNode.log_dir, "bn_plugins_{time:YYYY-MM-DD}.log"), rotation="00:00", enqueue=True, format="{time:HH:mm:ss} [{extra[plugin]}] - {message}", level="DEBUG", filter=lambda record: "plugin" in record["extra"])
                await self.__events.emit_async(f"{battlenode.__name__}.start", False)
                #self.__rps = self.__redis.pubsub()
                await self.__loader.init()
                await self.__loader.load_plugins()
                self.__scheduler.start()
                shell = asyncio.create_task(self.interactive_shell())
                channel_handler = asyncio.create_task(self.__channel_handler())
                await self.__event.wait()
                channel_handler.cancel()
                await self.__events.emit_async(f"{battlenode.__name__}.stop", False)
                await self.__events.emit_async(f"{battlenode.__name__}.database.close", False)
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
                        if data["data"]: self.__events.emit_future(message["channel"].decode(), data["data"], True)
                        else: self.__events.emit_future(message["channel"].decode(), True)

                await asyncio.sleep(0)
        except Exception as error:
            logger.info(f"Redis channel listening has ended: {error}")
            await pubsub.punsubscribe("*")
            await pubsub.close()
