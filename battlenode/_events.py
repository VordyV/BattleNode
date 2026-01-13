from pymitter import EventEmitter
from typing import Callable, Any
import asyncio
from loguru import logger
import traceback

class EventData:

    def __init__(self, name: str, args: tuple[Any] = None, kwargs: dict = None):
        self.name = name
        self.args = args
        self.kwargs = kwargs

class EventHub:

    def __init__(self):
        self.__eventsEmitter: EventEmitter = EventEmitter(wildcard=True)

    def _get_event_ins(self, name: str, args: Any, kwargs: Any):
        return EventData(name, args=args, kwargs=kwargs)

    def on(self, name: str, func: Callable):
        self.__eventsEmitter.on(name, func)

    def emit_future(self, name: str, *args: Any, **kwargs: Any):
        #self.__eventsEmitter.emit_future(name, self._get_event_ins(name, args, kwargs), *args, **kwargs)
        async def wrapped_coro():
            try:
                return await self.__eventsEmitter.emit_async(name, self._get_event_ins(name, args, kwargs), *args, **kwargs)
            except Exception as error:
                tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
                logger.error(f"Failed to execute event method - {name}: {error}\n{tb}")

        task = asyncio.create_task(wrapped_coro())

    async def emit_async(self, name: str, *args: Any, **kwargs: Any):
        await self.__eventsEmitter.emit_async(name, self._get_event_ins(name, args, kwargs), *args, **kwargs)

    def off(self, name: str, func: Callable):
        self.__eventsEmitter.off(name, func)

#eventsEmitter = EventEmitter(wildcard=True)

class EventCollection:

    def __init__(self):
        self.__events: list[dict] = []

    def get(self):
        return self.__events

    def __add_listener(self, event: str, func: Callable):
        self.__events.append({
            "event": event,
            "func": func
        })

    def on(self, event: str):
        def decorator(func: Callable):
            self.__add_listener(event, func.__name__)
            return func
        return decorator