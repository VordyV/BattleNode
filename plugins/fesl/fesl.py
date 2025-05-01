from battlenode import BasePlugin, EventCollection, EventData

class Fesl(BasePlugin):

    events = EventCollection()
    app = ["plugins.fesl.models"]

    class Meta(BasePlugin.Meta):
        name = "Fesl"
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