from battlenode import BasePlugin, EventCollection, EventData, CommandCollection
from apscheduler.events import EVENT_JOB_SUBMITTED, EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_REMOVED
#from apscheduler.job import Job
import pydantic
from .server import main
from .services import ListOfServersService
from opengsq.protocols.gamespy3 import GameSpy3
import traceback
import asyncio
import datetime

class SB(BasePlugin):

    events = EventCollection()
    commands = CommandCollection()
    app = ["plugins.sb.models"]

    process_target = main
    run_as_process = True

    class Config(pydantic.BaseModel):
        port: int = 28910
        enctypex_key: str = ""

    class Meta(BasePlugin.Meta):
        name = "Servers browser"
        requires_battlenode = ">=0.1"
        version = "0.1"
        dependencies = {
        }

    async def _task_get_status(self, args):
        sid, options = args
        gs3 = GameSpy3(host=options.get("address"), port=options.get("query_port"), timeout=2)
        result = await gs3.get_status()
        return result.info

    def _on_event_submitted(self, event): pass

    def _on_event_executes(self, event):
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
        sid = event.job_id.split("__")[1]

        self._set_server_state(sid=sid, success=False, dt=datetime.datetime.now(), data=event.retval, error=event.exception.__name__, error_detail=event.exception)

        async def func():
            await self.shared_data.set(f"server_{sid}", None)

        task = self._loop.create_task(func())

    def _set_server_state(self, sid: str, success: bool, dt: datetime.datetime, data: dict, error: str = None, error_detail: str = None):
        self.server_states[sid] = {
            "success": success,
            "dt": dt,
            "data": data,
            "error": error,
            "error_detail": error_detail
        }

    @events.on("battlenode.database.init")
    async def on_database_init(self, event: EventData):
        server_data = await ListOfServersService.get_all()
        for sid, options in server_data.items():
            #await ListOfServersService.change_data(sid, {"bf2142_averageping": "32"})
            jid = f"sb_get_status__{sid}"
            self._tasks[jid] = self.scheduler.add_job(self._task_get_status, 'interval', seconds=7, args=((sid, options),), id=jid)
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