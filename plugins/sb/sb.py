from battlenode import BasePlugin, EventCollection, EventData, CommandCollection
from apscheduler.events import EVENT_JOB_SUBMITTED, EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
#from apscheduler.job import Job
import pydantic
from .server import main
from .services import ListOfServersService
from opengsq.protocols.gamespy3 import GameSpy3
import asyncio
import datetime
from rich.table import Table
from rich.console import Console
import re

class SB(BasePlugin):

    events = EventCollection()
    commands = CommandCollection()
    app = ["plugins.sb.models"]

    process_target = main
    run_as_process = True

    class Config(pydantic.BaseModel):
        server_port: int = 28910
        server_address: str = "127.0.0.1"
        enctypex_key: str = ""

    class Meta(BasePlugin.Meta):
        name = "Servers browser"
        requires_battlenode = ">=0.1"
        version = "0.1"
        dependencies = {
        }

    # < ! ! > Sometimes the server returns incorrect query data, and the server name may be missing, making it unclear in the monitoring
    # *ranked = server is unranked, forced rank icon display is set in monitoring
    @commands.on("servers", "Get list of servers")
    async def on_cmd_get_servers(self):
        table = Table(title=f"Servers - total {len(self.server_states)}")
        table.add_column("ID")
        table.add_column("Options")
        table.add_column("Name")
        table.add_column("Address")
        table.add_column("Query port")
        table.add_column("Last update")
        table.add_column("Status")
        table.add_column("Error")

        server_data = await ListOfServersService.get_all()
        for sid, options in server_data.items():
            server_state = self.server_states.get(str(sid), {})
            data = server_state.get("data")


            hostname = ""
            server_options = ""
            if data != None:
                hostname = data.get("hostname")
                if data.get("bf2142_ranked") == "1":
                    server_options = "ranked"

            if options.get("data") != None:
                if options.get("data").get("bf2142_ranked") == "1":
                    server_options = "*ranked"

            status = "No data"
            error = ""

            if server_state != {}:
                status = "working" if server_state.get("success", False) else "error"
                if server_state.get("error") != None:
                    error = "%s %s" % (server_state.get("error"), server_state.get("error_detail"))

            table.add_row(str(sid), server_options, hostname, options.get("address", "?"), str(options.get("query_port", 0)), server_state.get("dt", datetime.datetime(2000,1,1,0,0,0)).strftime('%M:%S'), status, error)

        console = Console()
        console.print(table)

    @commands.on("servers.add", "Add a new server to the list")
    async def on_cmd_add_server(self, address: str, query_port: int, ranked: bool = False):
        if not self._check_ip(address): raise Exception("Address format is incorrect")

        data = None
        if data: data = {"bf2142_ranked", "1"}

        await ListOfServersService.add(address, query_port, data)
        print(f"Server {address}:{query_port} added")

    def _check_ip(self, string: str) -> bool:
        pattern = r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if isinstance(pattern, str):
            try:
                pattern = re.compile(pattern)
            except re.error as e:
                return False
        return bool(pattern.fullmatch(string))

    @commands.on("servers.data", "Get current server data")
    async def on_cmd_get_data_server(self, server_id: int):
        server = self.server_states.get(str(server_id))
        if not server: raise Exception(f"Server {server_id} is not in list")

        table = Table(title=f"Current data of server {server_id}")
        table.add_column("Option")
        table.add_column("Value")

        data = server.get("data", {})

        for k, v in data.items():
            table.add_row(str(k), str(v))

        console = Console()
        console.print(table)

    @commands.on("servers.del", "Remove server from list")
    async def on_cmd_delete_server(self, server_id: int):
        await ListOfServersService.remove(server_id)

        jid = f"sb_get_status__{server_id}"
        task = self._tasks.get(jid)
        task.remove()

        del self._tasks[jid]
        print(f"Server {server_id} has been removed from list")

    @commands.on("servers.rank", "Rank the server. Only sets the icon display")
    async def on_cmd_rank_server(self, server_id: int):
        server = await ListOfServersService.get(server_id)
        data = server.get("data", {})
        if data == None: data = {}

        if data.get("bf2142_ranked", "0") == "1": raise Exception("Server is already ranked")

        data["bf2142_ranked"] = "1"
        await ListOfServersService.change_data(server_id, data)
        print("Forced icon display is set")

    @commands.on("servers.unrank", "Unrank the server. Only sets the icon display")
    async def on_cmd_unrank_server(self, server_id: int):
        server = await ListOfServersService.get(server_id)
        data = server.get("data", {})
        if data == None: data = {}

        if data.get("bf2142_ranked", "0") == "0": raise Exception("Server is already unranked")

        data["bf2142_ranked"] = "0"
        await ListOfServersService.change_data(server_id, data)
        print("Forced icon display is unset")

    async def _task_get_status(self, args):
        sid, options = args
        gs3 = GameSpy3(host=options.get("address"), port=options.get("query_port"), timeout=2)
        result = await gs3.get_status()
        return result.info

    def _on_event_submitted(self, event): pass

    def _on_event_executes(self, event):
        #print("1")
        sid = event.job_id.split("__")[1]

        self._set_server_state(sid=sid, success=True, dt=datetime.datetime.now(), data=event.retval)

        job = self.scheduler.get_job(event.job_id)
        options = job.args[0][1]
        server_data = options.get("data")

        async def func():
            server_info = ListOfServersService.transform_data(event.retval)
            if server_data: server_info.update(server_data)
            await self.shared_data.set(f"server_{sid}", server_info)

        task = self._loop.create_task(func())

    def _on_event_error(self, event):
        #print("2")
        sid = event.job_id.split("__")[1]

        error=event.exception.__class__.__name__
        error_detail=event.exception

        server = self.server_states.get(sid, {})
        data = server.get("data")
        self._set_server_state(sid=sid, success=False, dt=datetime.datetime.now(), data=data, error=error, error_detail=error_detail)
        async def func():
            await self.shared_data.set(f"server_{sid}", None)
        task = self._loop.create_task(func())

    def _set_server_state(self, sid: str, success: bool, dt: datetime.datetime, data: dict, error: str = None, error_detail: str = None):
        try:
            self.server_states[sid] = {
                "success": success,
                "dt": dt,
                "data": data,
                "error": error,
                "error_detail": error_detail
            }
        except Exception as e:
            print(e)

    @events.on("battlenode.database.init")
    async def on_database_init(self, event: EventData):
        server_data = await ListOfServersService.get_all()
        for sid, options in server_data.items():
            #await ListOfServersService.change_data(sid, {"bf2142_averageping": "32"})
            jid = f"sb_get_status__{sid}"
            self._tasks[jid] = self.scheduler.add_job(self._task_get_status, 'interval', seconds=3, args=((sid, options),), id=jid)
        await self.shared_data.set("serverdata", {
            "list": server_data,
            "keys": ListOfServersService.options
        })

    @events.on("init")
    async def on_init(self, event: EventData):
        self._tasks: dict = {}
        self._loop = asyncio.get_running_loop()

        self.server_states: dict = {}

        self.scheduler.add_listener(self._on_event_submitted, EVENT_JOB_SUBMITTED)
        self.scheduler.add_listener(self._on_event_executes, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._on_event_error, EVENT_JOB_ERROR)

        self.logger.info("I'm working")

    @events.on("shutdown")
    async def on_shutdown(self, event: EventData):
        for tid, task in self._tasks.items():
            task.remove()

        self.scheduler.remove_listener(self._on_event_submitted)
        self.scheduler.remove_listener(self._on_event_executes)
        self.scheduler.remove_listener(self._on_event_error)

        self.logger.info("I'm falling asleep")