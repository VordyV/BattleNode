from battlenode import BasePlugin, EventCollection, EventData
import multiprocessing
import asyncio
import pydantic
import importlib
import sys
from .timi import main

class SimplePlugin(BasePlugin):

    events = EventCollection()

    class Meta(BasePlugin.Meta):
        name = "SimplePlugin"
        requires_battlenode = ">=0.1"
        version = "0.1"
        dependencies = {
        }

    class Config(pydantic.BaseModel):
        option: str = "Hello"

    models = ["plugins.spmodels"]

    def __import_from_path(self, module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    @events.on("statuschange")
    async def on_statuschange(self, event: EventData, status):
        pass

    @events.on("init")
    async def on_init(self, event: EventData):
        p = multiprocessing.Process(target=main, args=())
        #p.start()
        #self.logger.info("start pl 11 {}", self.battlenode.config.database)
        #module = self.__import_from_path("timi", "plugins/timi.py")
        #print(module)

    @events.on("shutdown")
    async def on_shutdown(self, event: EventData):
        self.logger.info("stop pl 1")
