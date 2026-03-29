from .models import GameServer
from tortoise.expressions import Q

class LOSSDuplicateException(Exception): pass
class LOSSUnknownOptionException(Exception): pass
class LOSSUnknownServerException(Exception): pass

class ListOfServersService:

    options = [
        "hostname", "gametype", "mapname", "numplayers", "maxplayers", "hostport", "gamevariant", "password", "gamever", "bf2142_anticheat", "bf2142_ranked", "bf2142_voip", "bf2142_autorec", "bf2142_pure", "bf2142_mapsize", "bf2142_reservedslots", "bf2142_friendlyfire", "bf2142_autobalanced", "bf2142_maxrank", "bf2142_ranked_tournament", "bf2142_averageping"
    ]

    @staticmethod
    async def add(address: str, query_port: int, data: dict | None = None):
        if await GameServer.exists(address=address, query_port=query_port): raise LOSSDuplicateException(f"A server with this address '{address}' and port '{query_port}' is already added to the list")

        if data != None:
            for key, value in data.items():
                if key not in ListOfServersService.options: raise LOSSUnknownOptionException(f"This option '{key}' cannot be specified")

        await GameServer.create(address=address, query_port=query_port, data=data)

    @staticmethod
    async def remove(sid: int):
        gs = await GameServer.get_or_none(id=sid)
        if not gs: raise LOSSUnknownServerException(f"There is no server with this ID '{sid}'")
        await gs.delete()

    @staticmethod
    async def change_data(sid: int, data: dict | None):
        gs = await GameServer.get_or_none(id=sid)
        if not gs: raise LOSSUnknownServerException(f"There is no server with this ID '{sid}'")

        if data != None:
            for key, value in data.items():
                if key not in ListOfServersService.options: raise LOSSUnknownOptionException(f"This option '{key}' cannot be specified")

        gs.data = data
        await gs.save()

    @staticmethod
    async def get_all() -> dict:
        result = {}
        for server in await GameServer.all():
            result[server.id] = {
                "address": server.address,
                "query_port": server.query_port,
                "data": server.data
            }
        return result

    @staticmethod
    async def get(sid: int,) -> dict:
        gs = await GameServer.get_or_none(id=sid).values("id", "address", "query_port", "data")
        if not gs: raise LOSSUnknownServerException(f"There is no server with this ID '{sid}'")
        return gs

    @staticmethod
    def transform_data(server_data: dict) -> dict:
        result = {}
        for key, value in server_data.items():
            if key not in ListOfServersService.options: continue
            result[key] = str(value)
        return result