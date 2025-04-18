from pymitter import EventEmitter
from typing import Callable

class EventHub:

    def __init__(self):
        self.__eventsEmitter = EventEmitter(wildcard=True)

eventsEmitter = EventEmitter(wildcard=True)

class Events:

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