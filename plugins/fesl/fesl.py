import datetime

from battlenode import BasePlugin, EventCollection, EventData, CommandCollection
from .services import CountryCodeField, AccountService
from .server import main
import pydantic
from rich.table import Table
from rich.console import Console
import math


class Fesl(BasePlugin):

    events = EventCollection()
    commands = CommandCollection()
    app = ["plugins.fesl.models"]

    process_target = main
    run_as_process = True

    class Config(pydantic.BaseModel):
        server_port: int = 18400
        server_address: str = "127.0.0.1"
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
        key: str = ""
        minAge: int = 14

    class Meta(BasePlugin.Meta):
        name = "Fesl"
        requires_battlenode = ">=0.1"
        version = "0.2"
        dependencies = {
        }

    @commands.on("accounts.add", "Add a new account")
    async def on_cmd_add_account(self):
        login = await self.battlenode.prompt("login (A-Z,a-z): ", not_empty=True, regex=r"^[A-Za-z0-9_-]+$", min_length=3, max_length=16)
        if login == None: return

        email = await self.battlenode.prompt("email (user@example.com): ", not_empty=True, regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if email == None: return

        password = await self.battlenode.prompt("password: ", not_empty=True, regex=r"^[A-Za-z0-9]+$", is_password=True, max_length=16)
        if password == None: return

        countries = self.config.countries.keys()
        country_code = await self.battlenode.prompt(f"country ({", ".join(countries)}): ", not_empty=True, enum=countries)
        if country_code == None: return

        date_of_birth = await self.battlenode.prompt(f"date of birth (dd.mm.yyyy): ", not_empty=True, regex=r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$")
        if date_of_birth == None: return
        date_of_birth = datetime.datetime.strptime(date_of_birth,"%d.%m.%Y").date()

        zip_code = await self.battlenode.prompt_int("zip code (y/n)[n]: ", value=0)
        if zip_code == None: return

        ea_mail = await self.battlenode.prompt_bool("send BattleNode emails (EA)? (y/n)[n]: ", value=False)
        if ea_mail == None: return

        tp_mail = await self.battlenode.prompt_bool("third party mail (y/n)[n]: ", value=False)
        if tp_mail == None: return

        parent_email = await self.battlenode.prompt("parent email [null]: ", not_empty=False, regex=r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$")
        if parent_email == None: return

        uid = await AccountService.create(
            login=login,
            password=password,
            email=email,
            country_code=country_code,
            date_of_birth=date_of_birth,
            zip_code=str(zip_code),
            ea_mail_flag=ea_mail,
            third_party_mail_flag=tp_mail,
            is_active=True,
            parent_email=parent_email if parent_email != "" else None
        )

        print(f"A new account ({uid}) has been created")

    @commands.on("accounts", "List of registered accounts")
    async def on_cmd_accounts(self, page: int = 1):
        total = await AccountService.get_total()
        pages = math.ceil(total / self.__num_records_per_page)
        if page > pages or page <= 0: raise Exception(f"Limit exceeded. Total pages: {pages}")

        offset = (page - 1) * self.__num_records_per_page

        accounts = await AccountService.get_all(["id", "login", "is_active", "created_at", "updated_at"], limit=20, offset=offset)
        table = Table(title=f"Accounts - page {page}/{pages}")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Login", justify="right", style="cyan", no_wrap=True)
        table.add_column("Creation date", justify="right", style="cyan", no_wrap=True)
        table.add_column("Update date", justify="right", style="cyan", no_wrap=True)

        for account in accounts:
            login = account.get("login")
            if not account.get("is_active"): login += " (not active)"
            table.add_row(str(account.get("id")), login, account.get("created_at").strftime("%d.%m.%Y"), account.get("updated_at").strftime("%d.%m.%Y"))

        console = Console()
        console.print(table)

    @events.on("test")
    async def on_fesl_test(self, event):
        pass

    @events.on("battlenode.database.init")
    async def on_database_init(self, event: EventData): pass
        #print(await AccountService.get_by_login("user1"))

    @events.on("init")
    async def on_init(self, event: EventData):
        self.__num_records_per_page = 20
        AccountService.min_age = self.config.minAge
        self.logger.info("I'm working")

    @events.on("shutdown")
    async def on_shutdown(self, event: EventData):
        self.logger.info("I'm falling asleep")