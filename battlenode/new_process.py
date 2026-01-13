import queue
import asyncio
from typing import Callable
import redis.asyncio as redis
import os
from ._shared_data import SharedData

class NewProcess:

    def __init__(self, queue: queue.Queue, app_config: dict, app_name: str):
        self.__queue = queue
        self.__app_config = app_config
        self.__app_name = app_name
        self.__redis: redis.Redis | None = None
        self.__shared_data: SharedData | None = None

    def init(self):
        self.__redis = redis.Redis(host=os.getenv("BN_REDIS_HOST"), port=int(os.getenv("BN_REDIS_PORT")), db=int(os.getenv("BN_REDIS_NAME")), password=os.getenv("BN_REDIS_PASSWORD"))
        self.__shared_data = SharedData(redis=self.__redis, name=self.__app_name)

    @property
    def config(self) -> dict:
        return self.__app_config

    @property
    def shared_data(self) -> SharedData:
        return self.__shared_data

    def debug(self, text: str): self.__queue.put(("debug", text))
    def info(self, text: str): self.__queue.put(("info", text))
    def error(self, text: str): self.__queue.put(("error", text))
    def warning(self, text: str): self.__queue.put(("warning", text))