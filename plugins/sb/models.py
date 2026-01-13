from tortoise.models import Model
from tortoise import fields

class GameServer(Model):
    id = fields.IntField(primary_key=True)
    address = fields.CharField(max_length=15)
    query_port = fields.SmallIntField()
    data = fields.JSONField(null=True)
