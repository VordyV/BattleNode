from tortoise.models import Model
from tortoise import fields

class Account(Model):
    id = fields.IntField(primary_key=True)
    login = fields.CharField(max_length=16)
    hash = fields.CharField(max_length=16)
    email = fields.CharField(max_length=50)
    country_code = fields.CharField(max_length=2)
    date_of_birth = fields.DateField()
    zip_code = fields.CharField(max_length=32)
    ea_mail_flag = fields.BooleanField()
    third_party_mail_flag = fields.BooleanField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table="bn_account"

class Character(Model):
    id = fields.IntField(primary_key=True)
    account = fields.ForeignKeyField("fesl.Account", related_name="characters")
    name = fields.CharField(max_length=16)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table="bn_character"
