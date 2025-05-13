from tortoise.models import Model
from tortoise import fields
from .actions import Actions

class Account(Model):
    id = fields.IntField(primary_key=True)
    login = fields.CharField(max_length=16)
    hash = fields.CharField(max_length=255)
    email = fields.CharField(max_length=50)
    parent_email = fields.CharField(max_length=50, null=True)
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

class Profile(Model):
    id = fields.IntField(primary_key=True)
    account = fields.ForeignKeyField("fesl.Account", related_name="profiles", on_delete=fields.CASCADE)
    name = fields.CharField(max_length=16)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table="bn_profile"

class Chronicle(Model):
    id = fields.IntField(pk=True)
    account = fields.ForeignKeyField("fesl.Account", related_name="actions")
    action = fields.IntEnumField(enum_type=Actions)
    metadata = fields.JSONField(null=True)
    ip_address = fields.CharField(max_length=15, null=True)
    mac_address = fields.CharField(max_length=16, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "bn_chronicle"