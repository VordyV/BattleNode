from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_SUBMITTED, EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_REMOVED
from typing import Callable, Any
from enum import Enum
from ._plugin import Plugin
import datetime
import multiprocessing
import logging
import asyncio
import queue

class PSNnknownException(Exception): pass
class PSException(Exception): pass

class ProcessStatuses(Enum):
    STOPPED = 0
    RUNNING = 1
    #STOPPING = 2

class PluginProcess:

    def __init__(self, target: Callable, plugin: Plugin):
        self.target = target
        self.plugin = plugin
        self.status: ProcessStatuses = ProcessStatuses.STOPPED
        self.process: multiprocessing.Process | None = None

class ProcessSupervisor:

    def __init__(self, on_submitted: Callable = None, on_executes: Callable = None, on_error: Callable = None):
        self._on_submitted = on_submitted
        self._on_executes = on_executes
        self._on_error = on_error

        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.CRITICAL)

        self.__scheduler = AsyncIOScheduler()
        self.__scheduler.add_listener(self.__on_event_submitted, EVENT_JOB_SUBMITTED)
        self.__scheduler.add_listener(self.__on_event_executes, EVENT_JOB_EXECUTED)
        self.__scheduler.add_listener(self.__on_event_error, EVENT_JOB_ERROR)
        #self.__scheduler.add_listener(self.__on_event_removed, EVENT_JOB_REMOVED)
        self.__process: dict[str, PluginProcess] = {}

    def __on_event_submitted(self, event):
        asyncio.create_task(self._handle_event_submitted(event))

    async def _handle_event_submitted(self, event):
        if callable(self._on_submitted): await self._on_submitted(event)

    def __on_event_executes(self, event):
        asyncio.create_task(self._handle_event_executes(event))

    async def _handle_event_executes(self, event):
        pp = self.__process[event.job_id]
        pp.status = ProcessStatuses.STOPPED
        if callable(self._on_executes): await self._on_executes(event)

    def __on_event_error(self, event):
        asyncio.create_task(self._handle_event_error(event))

    async def _handle_event_error(self, event):
        pp = self.__process[event.job_id]
        pp.status = ProcessStatuses.STOPPED
        if callable(self._on_error): await self._on_error(event)

    def __on_event_removed(self, event):
        print(event.job_id, 3)

    async def init(self):
        self.__scheduler.start()

    async def shutdown(self):
        self.__scheduler.shutdown()

    def add_process(self, plugin: Plugin, target: Callable):
        self.__process[plugin.name] = PluginProcess(target, plugin)

    def __handler_process(self, name: str, args: Any):
        pp = self.__process[name]
        p_queue = multiprocessing.Queue(maxsize=10)
        pp.process = multiprocessing.Process(target=pp.target, args=(p_queue, *args))
        pp.status = ProcessStatuses.RUNNING
        pp.process.start()

        while pp.process.is_alive():
            try:
                msg = p_queue.get(timeout=0.5)
                if isinstance(msg, Exception): raise PSException(str(msg))
                if msg[0] == "debug": pp.plugin.logger.debug(msg[1])
                elif msg[0] == "info": pp.plugin.logger.info(msg[1])
                elif msg[0] == "error": pp.plugin.logger.error(msg[1])
                elif msg[0] == "warning": pp.plugin.logger.warning(msg[1])
            except queue.Empty: pass

        pp.process.join()
        #if not queue.empty():
        #    error = queue.get()
        #    raise PSException(f"{error} (exitcode: {pp.process.exitcode})")

    def run_process(self, name: str, *args):
        if name not in self.__process: raise PSNnknownException(f"Process with this name ({name}) has not been added")

        pp = self.__process[name]
        if pp.process and pp.process.is_alive():
            raise PSNnknownException(f"Process {name} is already running")

        self.__scheduler.add_job(self.__handler_process, "date", run_date=datetime.datetime.now(), id=name, args=(name, args))

    def stop_process(self, name: str):
        if name not in self.__process: raise PSNnknownException(f"Process with this name ({name}) has not been added")
        pp = self.__process[name]

        if pp.process and pp.process.is_alive():
            pp.process.terminate()
            pp.process.join()
            pp.status = ProcessStatuses.STOPPED