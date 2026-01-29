import redis.asyncio as redis
import json
import datetime

class SharedData:

    TTL: datetime.timedelta = datetime.timedelta(hours=24)
    section: str = "bn:sd:{name}"

    def __init__(self, redis: redis.Redis, name: str):
        self.__redis = redis
        self.__section = SharedData.section.format(name=name)

    async def get(self, option: str):
        data = await self.__redis.hget(name=self.__section, key=option)
        if data == None: return None
        return json.loads(data)

    async def set(self, option: str, value: object):
        await self.__redis.hset(name=self.__section, key=option, value=json.dumps(value))
        await self.__redis.expire(self.__section, time=SharedData.TTL)

    async def get_all(self):
        mapp = await self.__redis.hgetall(name=self.__section)
        return {k.decode() : json.loads(v) for k, v in mapp.items()}