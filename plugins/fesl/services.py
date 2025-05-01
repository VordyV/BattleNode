import datetime
from .models import Account

class AccountService:

    @staticmethod
    async def create(login: str, password: str, email: str, country_code: str, date_of_birth: datetime.date, zip_code: str, ea_mail_flag: bool, third_party_mail_flag: bool, is_active: bool = True):
        print(await Account.exists(login=login))