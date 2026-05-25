import pydantic
import datetime
from .teams import Teams
from .game_modes import GameModes

class StatsScheme(pydantic.BaseModel):
    gsco: int = 0
    crpt: int = 0
    rnk: int = 0
    rnkcg: int = 0
    tt: int = 0
    pdt: int = 0
    pdtc: int = 0
    kdr: float = 0.0
    ent_1: int = 0
    ent_2: int = 0
    ent_3: int = 0
    bp_1: int = 0
    unavl: int = 0
    klls: int = 0

class RoundPlayerStats(pydantic.BaseModel):
    pid: int
    nick: str
    gsco: int
    crpt: int
    rnk: int
    rnkcg: int
    tt: int
    dths: int
    klls: int
    team: int

class RoundPlayers(pydantic.BaseModel):
    players: dict[int, RoundPlayerStats]