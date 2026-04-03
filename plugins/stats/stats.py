# Developed by VordyV, aka Vladislav Netievsky
# mail: vorklab@outlook.com
#
#
# v1.1 - 03.04.2026
# ===
# add event stats.received
# ===
#
# v1.0 - 30.03.2026
# ===
# Release version
# ===

# Events:
# stats.received (rid: int) - Server sent round stats

from battlenode import BasePlugin, EventCollection, EventData, CommandCollection
from .server import main
from .services import StatsService, SSProfileNotExistsException
from .schemes import StatsScheme
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
        requires_battlenode = ">=0.4"
        version = "1.0"
        dependencies = {
        }

    @events.on("stats.received")
    async def on_stats_received(self, event: EventData, data):
        self.logger.debug(f"Processing of round {data['rid']} stats")
        round = await StatsService.read_round(data["rid"])

        for pid, round_stats in round.players.items():
            try:
                player_stats = await StatsService.read(pid=pid)
            except SSProfileNotExistsException as error:
                self.logger.debug(f"Player {pid} round stats not processed")
                continue
            print(player_stats, round_stats)


            player_stats.gsco += round_stats.gsco
            player_stats.crpt += round_stats.crpt
            #player_stats.rnk = round_stats.rnk
            player_stats.rnkcg = round_stats.rnkcg
            #player_stats.kdr += round_stats.gsco
            player_stats.gsco += round_stats.gsco
            player_stats.klls += round_stats.klls
            await StatsService.update(pid, player_stats)

    @events.on("fesl.addsubaccount")
    async def on_fesl_addsubaccount(self, event: EventData, data):
        await StatsService.add(data["pid"])

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