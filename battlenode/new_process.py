import queue
import asyncio
from typing import Callable

class NewProcess:

    def __init__(self, queue: queue.Queue, app_config: dict):
        self.__queue = queue
        self.__app_config = app_config

    @property
    def config(self): return self.__app_config

    def debug(self, text: str): self.__queue.put(("debug", text))
    def info(self, text: str): self.__queue.put(("info", text))
    def error(self, text: str): self.__queue.put(("error", text))
    def warning(self, text: str): self.__queue.put(("warning", text))