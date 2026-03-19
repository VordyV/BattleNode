from battlenode import BasePlugin, EventCollection, EventData
import pydantic
import uvicorn
from flet_easy import FletEasy
from views import GeneralView
from . import flet as ft
from . import flet_easy as fs
from .views import LoginView
from flet import fastapi

import asyncio

class AdminPanel(BasePlugin):
    events = EventCollection()

    class Config(pydantic.BaseModel):
        host: str = "127.0.0.1"
        port: int = 8057
        log_level: str = "critical"

    class Meta(BasePlugin.Meta):
        name = "AdminPanel"
        requires_battlenode = ">=0.1"
        version = "0.1"
        dependencies = {
            "fesl": ">=0.1"
        }

    async def _on_login_middleware(self, data: fs.Datasy):
        if data.route == "/login":
            return

        if not data.page.session.get("uid"): return data.redirect("/login")

    @events.on("battlenode.database.init")
    async def on_database_init(self, event: EventData):
        self.fesl = self.battlenode.get_plugin("fesl")
        #print(await AccountService.get_by_login("user1"))

    @events.on("init")
    async def on_init(self, event: EventData):
        self._app = fs.FletEasy(
            route_init="/",
        )

        @self._app.config
        def config(page: ft.Page):
            page.session.set("uid", None)
            page.session.set("plugin", self)

        self._app.add_routes(add_views=[
            fs.Pagesy('/login', LoginView, title='Login', middleware=[self._on_login_middleware]),
            fs.Pagesy('/', GeneralView, title='General', middleware=[self._on_login_middleware]),
        ])

        self._app_fastapi = fastapi.FastAPI()
        self._app_fastapi.mount("/", fastapi.app(self._app.run(fastapi=True)))

        config = uvicorn.Config(self._app_fastapi, host=self.config.get("host"), port=self.config.get("port"), log_level=self.config.get("log_level"))
        self._server = uvicorn.Server(config)

        task = asyncio.create_task(self._server.serve())
        self.logger.info(f'Web app is available at http{"s" if config.is_ssl else ""}://{self.config.get("host")}:{self.config.get("port")}')

        self.logger.info("I'm working")

    @events.on("shutdown")
    async def on_shutdown(self, event: EventData):
        self._server.should_exit = True
        self.logger.info("I'm falling asleep")