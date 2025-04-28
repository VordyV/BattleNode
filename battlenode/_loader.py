import os
import sys
import importlib
import importlib.util
import traceback
import asyncio
from ._loader_exceptions import *
from ._plugin import Plugin, BasePlugin
from ._plugin_statuses import PluginStatuses
from ._events import EventHub, EventCollection
from ._database import init_database, close_database
from ._process import ProcessSupervisor
import inspect
import packaging.version
import packaging.specifiers
import battlenode
import pydantic

class Loader:

    def __init__(self, folder: str, battlenode):
        self.__folder = folder
        self.__battlenode = battlenode
        self.__events = self.__battlenode.events
        self.__plugins: dict[str, Plugin] = {}
        self.__prodis = ProcessSupervisor(
            on_submitted=self._on_event_prodis_submitted,
            on_executes=self._on_event_prodis_executes,
            on_error=self._on_event_prodis_error
        )

    async def _on_event_prodis_submitted(self, event):
        self.__events.emit_future(f"{event.job_id}.process.submitted", event)

    async def _on_event_prodis_executes(self, event):
        self.__events.emit_future(f"{event.job_id}.process.executes", event)

    async def _on_event_prodis_error(self, event):
        self.__events.emit_future(f"{event.job_id}.process.error", event)
        #self.shutdown_plugin()

    async def init(self):
        await self.__prodis.init()

    async def load_plugins(self):
        if len(self.__plugins) > 1: raise LoaderReLoadPluginException("Plugins have already been loaded. Use reload methods")
        tasks = []
        for module_name in self._get_all_plugin():
            tasks.append(asyncio.create_task(self.load_plugin(module_name)))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for plugin, result in zip(self.__plugins.values(), results):
            if isinstance(result, Exception):
                await self.__set_status(plugin, PluginStatuses.ERROR)
                plugin.logger.exception("plugin not loaded: {error}", error=result)

        await self.init_database()

    def __get_apps(self):
        return {pl.name: pl.app for pl in self.__plugins.values()}

    async def init_database(self):
        print(self.__get_apps())

        await init_database(self.__get_apps())

    async def shutdown_plugins(self):
        tasks = []
        for plugin in self.__plugins.values():
            if plugin.status != PluginStatuses.RUNNING: continue
            tasks.append(asyncio.create_task(self.shutdown_plugin(plugin)))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for plugin, result in zip(self.__plugins.values(), results):
            if isinstance(result, Exception):
                await self.__set_status(plugin, PluginStatuses.ERROR)
                plugin.logger.exception("plugin didn't shut down properly: {error}", error=result)
                #print("SHUTDOWN ERROR", plugin.name, result)

        await close_database()

    async def reload_plugins(self):
        tasks = []
        for plugin in self.__plugins.values():
            if plugin.status != PluginStatuses.RUNNING: continue
            tasks.append(asyncio.create_task(self.reload_plugin(plugin)))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for plugin, result in zip(self.__plugins.values(), results):
            if isinstance(result, Exception):
                await self.__set_status(plugin, PluginStatuses.ERROR)
                plugin.logger.exception("plugin did not reload correctly: {error}", error=result)
                #print("RELOAD ERROR", plugin.name, result)

    async def load_plugin(self, module_name: str):
        plugin = self._add_new_pl(module_name)
        if module_name[0] == "_": raise LoaderDisableModuleException(f"Module {module_name} is disabled")
        try:
            await self.__set_status(plugin, PluginStatuses.WAITING)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._import_pl,
                plugin
            )
            await self.__set_status(plugin, PluginStatuses.LOADED)
        except:
            await self.__set_status(plugin, PluginStatuses.ERROR)
            raise

        try:
            await self.__set_status(plugin, PluginStatuses.INITIALIZING)
            await self._init_pl(plugin)
            await self.__set_status(plugin, PluginStatuses.RUNNING)
        except:
            await self.__set_status(plugin, PluginStatuses.ERROR)
            raise

    async def shutdown_plugin(self, plugin: Plugin):
        if plugin.status != PluginStatuses.RUNNING: raise LoaderShutNonWorkException(f"Plugin {plugin.name} is inoperable and cannot be turned off")
        try:
            await self.__set_status(plugin, PluginStatuses.STOPPING)
            await self._shutdown_plugin(plugin)
        except:
            await self.__set_status(plugin, PluginStatuses.ERROR)
            raise

    async def _shutdown_plugin(self, plugin: Plugin):
        await self.__events.emit_async(f"{plugin.name}.shutdown")

        if plugin.instance.run_as_process and plugin.instance.process_target and plugin.status.RUNNING:
            self.__prodis.stop_process(plugin.name)

        await self.__set_status(plugin, PluginStatuses.STOPPED)
        _events = plugin.instance.events.get()
        for e in _events:
            if "." in e["event"]: self.__events.off(e["event"], getattr(plugin.instance, e["func"]))
            else: self.__events.off(f"{plugin.name}.{e["event"]}", getattr(plugin.instance, e["func"]))

    async def reload_plugin(self, plugin: Plugin):
        if plugin.status != PluginStatuses.RUNNING: raise LoaderShutNonWorkException(f"Plugin {plugin.name} is inoperable and cannot be turned off")
        try:
            await self.__set_status(plugin, PluginStatuses.RESTARTING)
            await self._shutdown_plugin(plugin)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._reload_module,
                plugin.module
            )
            self._pre_init_pl(plugin, plugin.module)
            await self._init_pl(plugin)
            await self.__set_status(plugin, PluginStatuses.RUNNING)
        except Exception as error:
            await self.__set_status(plugin, PluginStatuses.ERROR)
            raise

    def _reload_module(self, module: object):
        importlib.reload(module)

    async def __set_status(self, plugin: Plugin, status: PluginStatuses):
        plugin._set_status(status)
        self.__events.emit_future(f"{plugin.name}.statuschange", status)

    def _import_pl(self, plugin: Plugin):
        path = f"{self.__folder}.{plugin.name}"
        spec = importlib.util.find_spec(path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[path] = module
        spec.loader.exec_module(module)

        self._pre_init_pl(plugin, module)

    def __get_cls_pl(self, name: str, module: object) -> BasePlugin:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if inspect.isclass(attr) and attr_name.lower() == name.lower():
                return attr

        raise LoaderNoClassException(f"Plugin {name} module does not have a main class")

    def _pre_init_pl(self, plugin: Plugin, module: object):
        cls = self.__get_cls_pl(plugin.name, module)

        config = None
        if cls.Config and issubclass(cls.Config, pydantic.BaseModel):
            config = self.__battlenode.configurator.get_section(plugin.name, cls.Config)

        instance = cls(self.__battlenode, config, plugin.logger)

        if instance is None or not isinstance(instance, EventCollection): LoaderNoEventInstException(f"Plugin {plugin.name} does not contain an instance of the Events class")
        #"minsize": app.get("minsize", os.getenv("BN_DATABASE_MINSIZE")),
        #"maxsize": app.get("maxsize", os.getenv("BN_DATABASE_MAXSIZE")),
        #"connect_timeout": app.get("connect_timeout", os.getenv("BN_DATABASE_TIMEOUT")),
        plugin._set_instance(instance)
        plugin._set_module(module)
        plugin._set_app(cls.app)

        _events = instance.events.get()
        for e in _events:
            if "." in e["event"]: self.__events.on(e["event"], getattr(instance, e["func"]))
            else: self.__events.on(f"{plugin.name}.{e["event"]}", getattr(instance, e["func"]))

        if cls.run_as_process and cls.process_target:
            self.__prodis.add_process(plugin.name, cls.process_target)

    async def _init_pl(self, plugin: Plugin):
        spec_ver_pl = packaging.specifiers.SpecifierSet(plugin.meta.requires_battlenode)
        ver_bn = packaging.version.parse(battlenode.__version__)
        if ver_bn not in spec_ver_pl: raise LoaderInvalidVerSpecException(f"Plugin {plugin.name} cannot run on this version {battlenode.__version__}. Possible versions: {plugin.meta.requires_battlenode}")
        self.__check_dependencies_pl(plugin)
        await self.__events.emit_async(f"{plugin.name}.init")

        if plugin.instance.run_as_process and plugin.instance.process_target:
            self.__prodis.run_process(plugin.name)

    def __check_dependencies_pl(self, plugin: Plugin):
        for name, spec_ver in plugin.meta.dependencies.items():
            try:
                dep_plugin = self.__plugins[name]
                dep_ver = dep_plugin.meta.version
                spec_ver_pl = packaging.specifiers.SpecifierSet(spec_ver)
                if dep_ver not in spec_ver_pl: raise
            except:
                raise LoaderNoDepPluginException(f"Plugin {plugin.name} requires {name} with version {spec_ver}")

    def _add_new_pl(self, module_name: str) -> Plugin:
        if module_name in self.__plugins: raise LoaderPluginExistsException(f"Plugin {module_name} already added")
        plugin = Plugin(module_name)
        self.__plugins[module_name] = plugin
        return plugin

    def _get_all_plugin(self) -> list[str]:
        return self.__battlenode.config.plugins

