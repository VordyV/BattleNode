import queue
import asyncio
from typing import Callable
import redis.asyncio as redis
import os
from ._shared_data import SharedData
import json
from ._config import Config

class NewProcess:

    def __init__(self, queue: queue.Queue, config: Config, app_config: Config, app_name: str):
        self.__queue = queue
        self.__config = config
        self.__app_config = app_config
        self.__app_name = app_name
        self.__redis: redis.Redis | None = None
        self.__shared_data: SharedData | None = None

    def init(self):
        self.__redis = redis.Redis(host=self.__app_config.get("redis_host"), port=self.__app_config.get("redis_port"), db=self.__app_config.get("redis_name"), password=self.__app_config.get("redis_password"))
        self.__shared_data = SharedData(redis=self.__redis, name=self.__app_name)

    @property
    def app_config(self) -> Config:
        return self.__app_config

    @property
    def config(self) -> Config:
        return self.__config

    @property
    def shared_data(self) -> SharedData:
        return self.__shared_data

    @property
    def redis(self) -> redis.Redis:
        return self.__redis

    def debug(self, text: str): self.__queue.put(("debug", text))
    def info(self, text: str): self.__queue.put(("info", text))
    def error(self, text: str): self.__queue.put(("error", text))
    def warning(self, text: str): self.__queue.put(("warning", text))

    async def publish(self, event_name: str, arg: object = None) -> None:
        try:
            event_data = json.dumps(arg) if arg else None
        except:
            event_data = None

        data = {
            "sender": f"p_{self.__app_name}",
            "data": event_data
        }
        await self.__redis.publish(event_name, json.dumps(data))

    async def subscribe(self, event_name: str, handler: Callable) -> None:
        pubsub = self.__redis.pubsub()
        await pubsub.subscribe(event_name)

        try:
            while True:
                message = await pubsub.get_message(timeout=0.1, ignore_subscribe_messages=True)
                if message is not None:
                    if message["type"] in ["message", "pmessage"]:
                        data = json.loads(message["data"].decode())
                        if data["sender"] == f"p_{self.__app_name}": continue
                        await handler(data["data"])

                await asyncio.sleep(0)
        except Exception as error:
            await pubsub.unsubscribe(event_name)
            await pubsub.close()