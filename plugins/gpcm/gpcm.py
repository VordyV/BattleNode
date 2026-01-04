from battlenode import BasePlugin, EventCollection, EventData
from .server import main
import pydantic

class GPCM(BasePlugin):

    events = EventCollection()
    #app = ["plugins.fesl.models"]

    process_target = main
    run_as_process = True

    class Config(pydantic.BaseModel):
        server_address: str = "127.0.0.1"
        server_port: int = 29900

    class Meta(BasePlugin.Meta):
        name = "GSCM"
        requires_battlenode = ">=0.1"
        version = "0.1"
        dependencies = {
        }

    @events.on("init")
    async def on_init(self, event: EventData):
        self.logger.info("I'm working")

    @events.on("shutdown")
    async def on_shutdown(self, event: EventData):
        self.logger.info("I'm falling asleep")