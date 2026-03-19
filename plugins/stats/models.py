from tortoise.models import Model
from tortoise import fields

class StatsModel(Model):
    id = fields.IntField(primary_key=True)
    profile = fields.ForeignKeyField("fesl.Profile", related_name="stats", on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    fields = fields.JSONField()

    class Meta:
        table="bn_stats"
