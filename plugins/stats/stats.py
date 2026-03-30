from battlenode import BasePlugin, EventCollection, EventData, CommandCollection
from .server import main
import pydantic

class Stats(BasePlugin):

    events = EventCollection()
    commands = CommandCollection()
    app = ["plugins.stats.models"]

    process_target = main
    run_as_process = True

    class Config(pydantic.BaseModel):
        server_address: str = "127.0.0.1"
        server_port: int = 80
        ranks: dict[int, int] = {}
        awards: dict[str | int, list[str]] = {}
        options: list[str] = [] # additional data for the backend, beyond ranks and awards
        log_level_uvicorn: str = "critical"

    class Meta(BasePlugin.Meta):
        name = "Stats"
        requires_battlenode = ">=0.1"
        version = "0.1"
        dependencies = {
        }

    @events.on("battlenode.database.init")
    async def on_database_init(self, event: EventData): pass
        #print(await StatsService.read(6))
        #print(await AccountService.get_by_login("user1"))

    @events.on("init")
    async def on_init(self, event: EventData):
        #print(self.config.ranks)
        self.logger.info("I'm working")

    @events.on("shutdown")
    async def on_shutdown(self, event: EventData):
        self.logger.info("I'm falling asleep")