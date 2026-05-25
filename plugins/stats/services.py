import datetime
from .schemes import StatsScheme, RoundPlayers, RoundPlayerStats
from .models import StatsModel, RoundModel
from plugins.fesl.models import Profile
from .teams import Teams
from .game_modes import GameModes

class SSProfileAlreadyAddedException(Exception): pass
class SSProfileNotExistsException(Exception): pass
class SSRoundNotExistsException(Exception): pass

class StatsService:

    @staticmethod
    async def update(pid: int, data: StatsScheme):
        stats = await StatsModel.get(profile_id=pid)
        stats.fields = data.model_dump()
        await stats.save()

    @staticmethod
    async def add(pid: int):
        if await StatsModel.exists(profile_id=pid): raise SSProfileAlreadyAddedException(f"Profile {pid} already added")
        profile = await Profile.get(id=pid)
        await StatsModel.create(profile=profile, fields=StatsScheme().model_dump())

    @staticmethod
    async def read(pid: int) -> StatsScheme:
        data = await StatsModel.get_or_none(profile_id=pid)
        if not data: raise SSProfileNotExistsException(f"Statistics for profile {pid} do not exist")
        return StatsScheme.model_validate(data.fields)

    @staticmethod
    async def append_round(start: datetime.datetime, end: datetime.datetime, duration: datetime.timedelta, winner: Teams, game_mode: GameModes, mode: str, players: RoundPlayers) -> int:
        round = await RoundModel.create(start=start, end=end, duration=duration.seconds, winner=winner, game_mode=game_mode, mode=mode, players=players.model_dump())
        return round.id

    @staticmethod
    async def read_round(rid: int) -> RoundPlayers:
        data = await RoundModel.get_or_none(id=rid)
        if not data: raise SSRoundNotExistsException(f"Round {rid} statistics not found")
        return RoundPlayers.model_validate(data.players)