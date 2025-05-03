import datetime
from .models import Account, Profile
from typing import Annotated
from pydantic import Field, validate_call, EmailStr
import bcrypt

class ASDuplicateException(Exception): pass
class ASAuthorizeException(Exception): pass
class PSDuplicateException(Exception): pass

LoginField = Annotated[str, Field(max_length=16, min_length=3, pattern=r"^[A-Za-z0-9_=.]+$")]
PasswordField = Annotated[str, Field(max_length=16, min_length=5)]
CountryCodeField = Annotated[str, Field(max_length=2, min_length=2, pattern=r"^[A-Z]+$")]
NameField = Annotated[str, Field(max_length=16, min_length=3, pattern=r"^[A-Za-z0-9_=.]+$")]

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
    async def create(login: LoginField, password: PasswordField, email: EmailStr, country_code: CountryCodeField, date_of_birth: datetime.date, zip_code: str, ea_mail_flag: bool, third_party_mail_flag: bool, is_active: bool = True):
        if await AccountService.is_exists(login, email): raise ASDuplicateException(f"Cannot create a duplicate account with the same data login {login}, email {email}")

        hashed = Password.encode(password)
        account = await Account.create(login=login, hash=hashed, email=email, country_code=country_code, date_of_birth=date_of_birth, zip_code=zip_code, ea_mail_flag=ea_mail_flag, third_party_mail_flag=third_party_mail_flag, is_active=is_active)
        return account.id

    @staticmethod
    async def is_exists(login: str, email: EmailStr):
        return await Account.exists(login=login, email=email)

    @staticmethod
    async def get(account_id: int):
        return await Account.get(id=account_id)

    @staticmethod
    async def get_by_login(login: LoginField):
        return await Account.get_or_none(login=login)

    @staticmethod
    async def authorize(login: LoginField, password: PasswordField):
        account = await AccountService.get_by_login(login)
        if not account or not Password.verify(password=password, hash=account.hash): raise ASAuthorizeException(f"Authorization by login {login} failed")
        return account.id

class ProfileService:

    @staticmethod
    async def create(account_id: int, name: NameField):
        account = await AccountService.get(account_id)
        if await ProfileService.is_exists(account.id, name): raise PSDuplicateException(f"Cannot create a duplicate profile {name} for account {account.id}")

        profile = await Profile.create(account=account, name=name)
        return profile.id

    @staticmethod
    async def is_exists(account_id: int, name: NameField):
        return await Profile.exists(account=account_id, name=name)
