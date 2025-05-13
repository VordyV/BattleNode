from battlenode import BasePlugin, EventCollection, EventData
from .services import CountryCodeField, EncryptedInfo
from .server import main
import pydantic

class Fesl(BasePlugin):

    events = EventCollection()
    app = ["plugins.fesl.models"]

    process_target = main
    run_as_process = True

    class Config(pydantic.BaseModel):
        domainPartition_domain: str = "eagames"
        messengerIp: str = "0.0.0.0"
        messengerPort: int = 0
        domainPartition_subDomain: str = "battlefield2142-2006"
        activityTimeoutSecs: int = 0
        theaterIp: str = "0.0.0.0"
        theaterPort: int = 0
        tos: str = "<body>Whether you chose it or it was chosen for you, it is the best city left.<br>I think so highly of City 17 that I have chosen to house my government here, in the Citadel so carefully provided by our Protectors.<br><br>I am proud to call City 17 my home.<br>Русский текст</body>"
        countries: dict[str, CountryCodeField] = {"AU": "Country", "NZ": "Country2"}
        proxy: bool = True

    class Meta(BasePlugin.Meta):
        name = "Fesl"
        requires_battlenode = ">=0.1"
        version = "0.1"
        dependencies = {
        }

    @events.on("battlenode.database.init")
    async def on_database_init(self, event: EventData): pass
        #print(await AccountService.get_by_login("user1"))

    @events.on("init")
    async def on_init(self, event: EventData):
        self.logger.info("I'm working")

    @events.on("shutdown")
    async def on_shutdown(self, event: EventData):
        self.logger.info("I'm falling asleep")