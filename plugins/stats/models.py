from tortoise.models import Model
from tortoise import fields
from .teams import Teams
from .game_modes import GameModes

class StatsModel(Model):
    id = fields.IntField(primary_key=True)
    profile = fields.ForeignKeyField("fesl.Profile", related_name="stats", on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    fields = fields.JSONField()

    class Meta:
        table="bn_stats"

class RoundModel(Model):
    id = fields.IntField(primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    start = fields.DatetimeField()
    end = fields.DatetimeField()
    duration = fields.IntField()
    winner = fields.IntEnumField(Teams)
    game_mode = fields.IntEnumField(GameModes)
    mode = fields.CharField(max_length=16)
    players = fields.JSONField()

    class Meta:
        table="bn_round"

'''
{'round': {'game': 'BF2142', 'server': 'minsk', 'mapstart': 1775156120.01, 'mapend': 1775156185.04, 'win': 1, 'gm': 0, 'm': 3, 'v': 'bf2142', 'pc': 2, 'rwa': 1, 'EOF': 1}, 'players': {0: {'ban': 0, 'c': 1, 'capa': 0, 'cpt': 0, 'crpt': 0, 'cs': 0.0, 'dass': 0, 'dcpt': 0, 'dstrk': 0, 'dths': 0, 'gsco': 0, 'hls': 0, 'kick': 0, 'klla': 0, 'klls': 0, 'klstrk': 0, 'kluav': 0, 'nick': 'Admin', 'ncpt': 0, 'pdt': {}, 'pdtc': 0, 'pid': 6, 'resp': 0, 'rnk': 2, 'rnkcg': 0, 'rps': 0, 'rvs': 0, 'slbspn': 0, 'sluav': 0, 'suic': 0, 'tac': 0, 'talw': 50, 'tas': 0, 'tasl': 0, 'tasm': 0, 'tcd': 0, 'tcrd': 0, 'tdmg': 0, 'tdrps': 0, 'tds': 0, 'tgd': 0, 'tgr': 0, 'tkls': 0, 'toth': 0, 'tots': 0, 'tt': 50, 'tvdmg': 0, 'twsc': 0, 't': 2, 'medalers': 1, 'kdths-0': 0, 'kdths-1': 0, 'kdths-2': 0, 'kdths-3': 0, 'kkls-0': 0, 'kkls-1': 0, 'kkls-2': 0, 'kkls-3': 0, 'ktt-0': 0, 'ktt-1': 50, 'ktt-2': 0, 'ktt-3': 0, 'waccu-7': 0, 'wdths-7': 0, 'wbf-7': 0, 'wkls-7': 0, 'wbh-7': 0, 'wtp-7': 50}, 1: {'ban': 0, 'c': 1, 'capa': 0, 'cpt': 0, 'crpt': 0, 'cs': 0.0, 'dass': 0, 'dcpt': 0, 'dstrk': 0, 'dths': 0, 'gsco': 0, 'hls': 0, 'kick': 0, 'klla': 0, 'klls': 0, 'klstrk': 0, 'kluav': 0, 'nick': 'user1', 'ncpt': 0, 'pdt': {}, 'pdtc': 0, 'pid': 22, 'resp': 0, 'rnk': 0, 'rnkcg': 0, 'rps': 0, 'rvs': 0, 'slbspn': 0, 'sluav': 0, 'suic': 0, 'tac': 0, 'talw': 56, 'tas': 0, 'tasl': 0, 'tasm': 0, 'tcd': 0, 'tcrd': 0, 'tdmg': 0, 'tdrps': 0, 'tds': 0, 'tgd': 0, 'tgr': 0, 'tkls': 0, 'toth': 0, 'tots': 0, 'tt': 56, 'tvdmg': 0, 'twsc': 0, 't': 1, 'medalerg': 1, 'kdths-0': 0, 'kdths-1': 0, 'kdths-2': 0, 'kdths-3': 0, 'kkls-0': 0, 'kkls-1': 0, 'kkls-2': 0, 'kkls-3': 0, 'ktt-0': 0, 'ktt-1': 56, 'ktt-2': 0, 'ktt-3': 0, 'wdths-1': 0, 'waccu-1': 0, 'wbf-1': 0, 'wtp-1': 56, 'wbh-1': 0, 'wkls-1': 0}}}
'''
