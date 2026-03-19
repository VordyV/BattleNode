import base64
import datetime
import os
import asyncio
from .models import Account, Profile, Chronicle
from typing import Annotated, Union
from pydantic import Field, validate_call, EmailStr
from cryptography.fernet import Fernet
import bcrypt
from .actions import Actions
import redis.asyncio as redis
import uuid

class ASDuplicateException(Exception): pass
class ASAuthorizeException(Exception): pass
class ASDeactivatedException(Exception): pass
class PSDuplicateException(Exception): pass

LoginField = Annotated[str, Field(max_length=16, min_length=3, pattern=r"^[A-Za-z0-9_=.]+$")]
PasswordField = Annotated[str, Field(max_length=16, min_length=5)]
CountryCodeField = Annotated[str, Field(max_length=2, min_length=2, pattern=r"^[A-Z]+$")]
NameField = Annotated[str, Field(max_length=16, min_length=3, pattern=r"^[A-Za-z0-9_=.]+$")]

class EncryptedInfo:

    def __init__(self, key: str):
        self.__fernet = Fernet(key)

    def encode_token(self, login: str, password: str) -> str:
        data = f"{login}\t{password}"
        return self._encode(data)

    def decode_token(self, token: str) -> tuple[str, str]:
        data = self._decode(token)
        return data.split("\t")

    def _encode(self, data: str) -> str:
        return base64.b64encode(self.__fernet.encrypt(data.encode("ascii"))).decode("ascii").rstrip("=")

    def _decode(self, token: str) -> str:
        padding = '=' * (4 - (len(token) % 4))
        token = base64.b64decode((token + padding).encode("ascii"))
        return self.__fernet.decrypt(token).decode("ascii")

class Password:

    @staticmethod
    def encode(value: str) -> str:
        return bcrypt.hashpw(value.encode("ascii"), bcrypt.gensalt()).decode("ascii")

    @staticmethod
    def verify(password: str, hash: str) -> str:
        return bcrypt.checkpw(password.encode("ascii"), hash.encode("ascii"))

class AccountService:

    @staticmethod
    @validate_call
    async def create(login: LoginField, password: PasswordField, email: EmailStr, country_code: CountryCodeField, date_of_birth: datetime.date, zip_code: str, ea_mail_flag: bool, third_party_mail_flag: bool, is_active: bool = True, parent_email: Union[EmailStr, None]  = None):
        if await AccountService.is_exists(login, email): raise ASDuplicateException(f"Cannot create a duplicate account with the same data login {login}, email {email}")

        hashed = Password.encode(password)
        account = await Account.create(login=login, hash=hashed, email=email, parent_email=parent_email, country_code=country_code, date_of_birth=date_of_birth, zip_code=zip_code, ea_mail_flag=ea_mail_flag, third_party_mail_flag=third_party_mail_flag, is_active=is_active)
        return account.id

    @staticmethod
    async def is_exists(login: str, email: EmailStr):
        return await Account.exists(login=login, email=email)

    @staticmethod
    async def get(account_id: int):
        return await Account.get(id=account_id)

    @staticmethod
    async def get_info(account_id: int) -> dict | None:
        account = await Account.get(id=account_id)
        return {
            "id": account.id,
            "login": account.login,
            "email": account.email,
            "parent_email": account.parent_email,
            "country_code": account.country_code,
            "date_of_birth": account.date_of_birth,
            "zip_code": account.zip_code,
            "ea_mail_flag": account.ea_mail_flag,
            "third_party_mail_flag": account.third_party_mail_flag,
            "created_at": account.created_at,
            "updated_at": account.updated_at,
            "is_active": account.is_active
        }

    @staticmethod
    async def get_by_login(login: LoginField):
        account = await Account.get_or_none(login=login)
        return getattr(account, "id", None)

    @staticmethod
    async def authorize(login: LoginField, password: PasswordField):
        account_id = await AccountService.get_by_login(login)
        account = await AccountService.get(account_id)

        if not account.is_active: raise ASDeactivatedException(f"Account {login} deactivated")

        if not account or not await asyncio.to_thread(Password.verify, password, account.hash): raise ASAuthorizeException(f"Authorization by login {login} failed")
        return account_id

class ProfileService:

    @staticmethod
    async def create(account_id: int, name: NameField):
        account = await AccountService.get(account_id)
        if await ProfileService.is_exists(name): raise PSDuplicateException(f"Cannot create a duplicate profile {name}")

        profile = await Profile.create(account=account, name=name)
        return profile.id

    @staticmethod
    async def get_for_name(name: str,  ignore_activ: bool = False) -> dict | None:
        profile = await Profile.get(name=name)
        if not profile.is_active and not ignore_activ: return None
        return {
            "id": profile.id,
            "name": profile.name,
            "uid": profile.account_id,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
            "is_active": profile.is_active,
        }

    @staticmethod
    async def get_all_for_account(account_id: int,  ignore_activ: bool = False) -> dict:
        result = {}
        for p in await Profile.filter(account=account_id):
            if not p.is_active and not ignore_activ: continue
            result[p.id] = {
                "id": p.id,
                "name": p.name,
                "uid": p.account_id,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "is_active": p.is_active,
            }
        return result

    @staticmethod
    async def is_exists(name: str):
        return await Profile.exists(name=name)

    @staticmethod
    async def disable(name: str):
        profile = await Profile.get(name=name)
        if profile.is_active:
            profile.is_active = False
            await profile.save()
        return True

    @staticmethod
    async def enable(name: str):
        profile = await Profile.get(name=name)
        if not profile.is_active:
            profile.is_active = True
            await profile.save()
        return True

    @staticmethod
    async def get(pid: int):
        profile = await Profile.get(id=pid)
        return {
            "id": profile.id,
            "name": profile.name,
            "uid": profile.account_id,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
            "is_active": profile.is_active,
        }

class ChronicleService:

    @staticmethod
    async def register(account_id: int, action: Actions, metadata: dict, ip_address: str, mac_address: str):
        await Chronicle.create(account=account_id, action=action, metadata=metadata, ip_address=ip_address, mac_address=mac_address)

class Ticket:

    section: str = "fesl:ticket:{ticket}"

    def __init__(self, redis: redis.Redis, lifetime: datetime.timedelta = datetime.timedelta(minutes=5)):
        self.__redis = redis
        self.__lifetime = lifetime

    async def add(self, uid: int) -> str:
        ticket = uuid.uuid4().hex
        await self.__redis.set(Ticket.section.format(ticket=ticket), uid, ex=self.__lifetime.seconds)
        return ticket

    async def verify(self, ticket: str) -> int | None:
        section = Ticket.section.format(ticket=ticket)
        if await self.__redis.exists(section):
            uid = await self.__redis.get(section)
            await self.__redis.delete(section)
            return uid.decode()
        return None