import asyncio
import sys
import traceback
from pydantic import ValidationError
from . package import PackageFesl, TypesPackages, TypesRequests
from typing import Any
from .services import AccountService, ProfileService, ASDuplicateException, PSDuplicateException, ASAuthorizeException, EncryptedInfo
from .server_client import Client
from .server_context import Context
from cryptography.fernet import InvalidToken
import datetime

account_field_errors = {
	"login": "Account.ScreenName",
	"password": "Account.Password",
	"email": "Account.EmailAddress",
	"country_code": "Account.Address.Zip",
	"date_of_birth": "Account.Address.Country",
	"zip_code": "Account.BirthDate"
}

class ProtocolFesl:

	ei = EncryptedInfo()

	@staticmethod
	async def Hello(ctx: Context):
		config = ctx.app_config

		now_utc = datetime.datetime.now(datetime.UTC)
		formatted_time = now_utc.strftime("%b-%d-%Y %H:%M:%S UTC")
		encoded_time = formatted_time.replace(":", "%3a")

		yield PackageFesl(
			request_type=TypesRequests.FSYS,
			package_type=TypesPackages.SINGLE_SERVER,
			number=1,
			options={
				"TXN": "Hello",
				"domainPartition.domain": config.get("domainPartition_domain"),
				"messengerIp": config.get("messengerIp"),
				"messengerPort": config.get("messengerPort"),
				"domainPartition.subDomain": config.get("domainPartition_subDomain"),
				"activityTimeoutSecs": config.get("activityTimeoutSecs"),
				"curTime": f'"{encoded_time}"',
				"theaterIp": config.get("theaterIp"),
				"theaterPort": config.get("theaterPort"),
			}
		).deserializer()

		yield PackageFesl(
			request_type=TypesRequests.FSYS,
			package_type=TypesPackages.SINGLE_SERVER,
			number=1,
			options={
				"TXN": "MemCheck",
				"memcheck.[]": 0,
				"type": 0,
				"salt": 515097424,
			}
		).deserializer()

	@staticmethod
	async def MemCheck(ctx: Context):
		return
		yield

	@staticmethod
	async def GameSpyPreAuth(ctx: Context):
		yield PackageFesl(
			request_type=TypesRequests.ACCT,
			package_type=TypesPackages.SINGLE_SERVER,
			number=ctx.pkg.number,
			options={
				"TXN": "GameSpyPreAuth",
				"challenge": "lrzrmqyh",
				"ticket": "B2BT2YE3HkZHK/BmTKALo84tIwrgfNmGGE0EdTsHdlbXEPVhWVgDP+1MG64xfC2W5nd7WfzAsi5nx7JSbpXm56pOQ%3d%3d",
			}
		).deserializer()

	@staticmethod
	async def GetAccount(ctx: Context):
		data = await AccountService.get_info(ctx.client.account_id)
		yield PackageFesl(
			request_type=TypesRequests.ACCT,
			package_type=TypesPackages.SINGLE_SERVER,
			number=ctx.pkg.number,
			options={
				"TXN": "GetAccount",
				"name": data.get("login"),
				"profileId": data.get("id"),
				"userId": data.get("id"),
				"email": data.get("email"),
				"countryCode": data.get("country_code"),
				"countryDesc": ctx.app_config.get("countries").get(data.get("country_code")),
				"dobDay": data.get("date_of_birth").day,
				"dobMonth": data.get("date_of_birth").month,
				"dobYear": data.get("date_of_birth").year,
				"zipCode": data.get("zip_code"),
				"gender": "U",
				"eaMailFlag": int(data.get("ea_mail_flag")),
				"thirdPartyMail": int(data.get("third_party_mail_flag")),
			}
		).deserializer()

	@staticmethod
	async def LoginSubAccount(ctx: Context):
		profile = await ProfileService.get_for_name(name=ctx.pkg.options.get("name"))

		if profile.get("uid") != ctx.client.account_id:

			yield PackageFesl(
				request_type=TypesRequests.ACCT,
				package_type=TypesPackages.SINGLE_SERVER,
				number=ctx.pkg.number,
				options={
					"TXN": "Login",
					"localizedMessage": "The password was not correct. 1",
					"errorContainer.[]": 0,
					"errorCode": 101
				}
			).deserializer()

		else:

			yield PackageFesl(
				request_type=TypesRequests.ACCT,
				package_type=TypesPackages.SINGLE_SERVER,
				number=ctx.pkg.number,
				options={
					"TXN": "LoginSubAccount",
					"lkey": "111111111111111111111111111.",
					"profileId": profile.get("id"),
					"userId": profile.get("uid"),
				}
			).deserializer()

	@staticmethod
	async def GetSubAccounts(ctx: Context):
		num = 0

		options = {
			"TXN": "GetSubAccounts",
			"subAccounts.[]": num,
		}

		profiles = await ProfileService.get_all_for_account(account_id=ctx.client.account_id)
		for pid, data in profiles.items():
			options[f"subAccounts.{num}"] = data.get("name")
			num += 1

		options["subAccounts.[]"] = num

		yield PackageFesl(
			request_type=TypesRequests.ACCT,
			package_type=TypesPackages.SINGLE_SERVER,
			number=ctx.pkg.number,
			options=options
		).deserializer()

	@staticmethod
	async def GetObjectInventory(ctx: Context):
		yield PackageFesl(
			request_type=TypesRequests.DOBJ,
			package_type=TypesPackages.SINGLE_SERVER,
			number=ctx.pkg.number,
			options={
				"TXN": "GetObjectInventory",
				"entitlements.[]": 0,
			}
		).deserializer()

	@staticmethod
	async def GetEntitlementByBundle(ctx: Context):
		yield PackageFesl(
			request_type=TypesRequests.SUBS,
			package_type=TypesPackages.SINGLE_SERVER,
			number=ctx.pkg.number,
			options={
				"TXN": "GetEntitlementByBundle",
				#"localizedMessage": "The customer has never had entitlement for this bundle.",
				#"errorContainer.[]": 0,
				#"errorCode": 3012
			}
		).deserializer()

	@staticmethod
	async def PingPing():
		return PackageFesl(
			request_type=TypesRequests.FSYS,
			package_type=TypesPackages.SINGLE_SERVER,
			number=1,
			options={
				"TXN": "Ping",
			}
		).deserializer()

	@staticmethod
	async def Ping(ctx: Context):
		return
		yield

	@staticmethod
	async def GetTos(ctx: Context):
		config = ctx.app_config
		yield PackageFesl(
			request_type=TypesRequests.ACCT,
			package_type=TypesPackages.SINGLE_SERVER,
			number=2,
			options={
				"TXN": "GetTos",
				"tos": f'"{config.get("tos")}"',
			}
		).deserializer()

	@staticmethod
	async def AddAccount(ctx: Context):
		try:
			uid = await AccountService.create(
				login=str(ctx.pkg.options.get("name")),
				password=str(ctx.pkg.options.get("password")),
				email=ctx.pkg.options.get("email"),
				country_code=ctx.pkg.options.get("countryCode"),
				date_of_birth=datetime.datetime(year=int(ctx.pkg.options.get("DOBYear")), month=int(ctx.pkg.options.get("DOBMonth")), day=int(ctx.pkg.options.get("DOBDay"))),
				zip_code=str(ctx.pkg.options.get("zipCode")),
				ea_mail_flag=ctx.pkg.options.get("eaMailFlag") == "1",
				third_party_mail_flag=ctx.pkg.options.get("thirdPartyMailFlag") == "1",
				is_active=True,
				parent_email=ctx.pkg.options.get("parentalEmail")
			)

			ctx.client._set_account_id(uid)

			yield PackageFesl(
				request_type=TypesRequests.ACCT,
				package_type=TypesPackages.SINGLE_SERVER,
				number=ctx.pkg.number,
				options={
					"TXN": "AddAccount",
					"userId": uid,
					"profileId": uid,
				}
			).deserializer()
		except ValidationError as error:
			err = error.errors()[0]
			yield PackageFesl(
				request_type=TypesRequests.ACCT,
				package_type=TypesPackages.SINGLE_SERVER,
				number=ctx.pkg.number,
				options={
					"TXN": "AddAccount",
					"errorContainer.[]": 0,
					"errorCode": 21,
					"errorContainer.0.fieldName": account_field_errors.get(err["loc"][0], "Account.ParentalEmailAddress"),
					"errorContainer.0.fieldError": "Unknown"
				}
			).deserializer()

			traceback.print_exc(file=sys.stdout)
		except ASDuplicateException as error:
			yield PackageFesl(
				request_type=TypesRequests.ACCT,
				package_type=TypesPackages.SINGLE_SERVER,
				number=ctx.pkg.number,
				options={
					"TXN": "AddAccount",
					"errorContainer.[]": 0,
					"errorCode": 21,
					"errorContainer.0.fieldName": account_field_errors.get("email", "Account.ParentalEmailAddress"),
					"errorContainer.0.fieldError": "Unknown"
				}
			).deserializer()

	@staticmethod
	async def SendAccountName(ctx: Context):
		yield PackageFesl(
			request_type=TypesRequests.ACCT,
			package_type=TypesPackages.SINGLE_SERVER,
			number=ctx.pkg.number,
			options={
				"TXN": "SendAccountName"
			}
		).deserializer()

	@staticmethod
	async def SendAccountPassword(ctx: Context):
		yield PackageFesl(
			request_type=TypesRequests.ACCT,
			package_type=TypesPackages.SINGLE_SERVER,
			number=ctx.pkg.number,
			options={
				"TXN": "SendAccountPassword"
			}
		).deserializer()

	@staticmethod
	async def RegisterGame(ctx: Context):
		yield PackageFesl(
			request_type=TypesRequests.ACCT,
			package_type=TypesPackages.SINGLE_SERVER,
			number=ctx.pkg.number,
			options={
				"TXN": "RegisterGame"
			}
		).deserializer()

	@staticmethod
	async def GetCountryList(ctx: Context):
		options = {
			"TXN": "GetCountryList",
		}
		num = 0
		for code, name in ctx.app_config.get("countries", {}).items():
			options[f"countryList.{num}.description"] = name
			options[f"countryList.{num}.ISOCode"] = code
			num += 1

		yield PackageFesl(
			request_type=TypesRequests.ACCT,
			package_type=TypesPackages.SINGLE_SERVER,
			number=ctx.pkg.number,
			options=options
		).deserializer()

	@staticmethod
	async def Login(ctx: Context):
		#print(pkg.options)

		try:
			if ctx.pkg.options.get("encryptedInfo"):
				token = ctx.pkg.options.get("encryptedInfo")
				login, password = await asyncio.to_thread(ProtocolFesl.ei.decode_token, token)
			else:
				login = str(ctx.pkg.options.get("name"))
				password = str(ctx.pkg.options.get("password"))
				token = await asyncio.to_thread(ProtocolFesl.ei.encode_token,login, password)

			uid = await AccountService.authorize(login=login, password=password)
			account = await AccountService.get_info(account_id=uid)

			ctx.np.debug(f"{ctx.client.address[0]}({ctx.client.address[1]}) {account.get("login")}#{uid} successfully authorized")

			yield PackageFesl(
				request_type=TypesRequests.ACCT,
				package_type=TypesPackages.SINGLE_SERVER,
				number=ctx.pkg.number,
				options={
					"TXN": "Login",
					"userId": uid,
					"profileId": 0,
					"displayName": account.get("login"),
					"lkey": "123456789012345678901234567.",
					"encryptedLoginInfo": f"{token}",
					"entitledGameFeatureWrappers.0.gameFeatureId": 2590,
					"entitledGameFeatureWrappers.0.status": 0,
					"entitledGameFeatureWrappers.0.entitlementExpirationDate": "",
					"entitledGameFeatureWrappers.0.message": "",
					"entitledGameFeatureWrappers.0.entitlementExpirationDays": -1
				}
			).deserializer()

			ctx.client._set_account_id(uid)
		except Exception as error:

			ctx.np.debug(f"{ctx.client.address[0]}({ctx.client.address[1]}) {error}")

			yield PackageFesl(
				request_type=TypesRequests.ACCT,
				package_type=TypesPackages.SINGLE_SERVER,
				number=ctx.pkg.number,
				options={
					"TXN": "Login",
					"localizedMessage": "The password was not correct. 1",
					"errorContainer.[]": 0,
					"errorCode": 101
				}
			).deserializer()

	@staticmethod
	async def AddSubAccount(ctx: Context):
		try:
			#uid = AccountService.get_by_login(ctx.pkg.options.get("name"))
			#if not uid: raise Exception()

			pid = await ProfileService.create(account_id=ctx.client.account_id, name=ctx.pkg.options.get("name"))

			yield PackageFesl(
				request_type=TypesRequests.ACCT,
				package_type=TypesPackages.SINGLE_SERVER,
				number=ctx.pkg.number,
				options={
					"TXN": "AddSubAccount"
				}
			).deserializer()
		except PSDuplicateException as error:
			print(error)
			yield PackageFesl(
				request_type=TypesRequests.ACCT,
				package_type=TypesPackages.SINGLE_SERVER,
				number=ctx.pkg.number,
				options={
					"TXN": "AddSubAccount",
					"errorContainer.[]": 0,
					"localizedMessage": "LOCERROR_soldiernameexists",
					"errorCode": 160
				}
			).deserializer()

	@staticmethod
	async def DisableSubAccount(ctx: Context):
		try:
			await ProfileService.disable(ctx.pkg.options.get("name"))
		except Exception as error:
			print(error)

		yield PackageFesl(
			request_type=TypesRequests.ACCT,
			package_type=TypesPackages.SINGLE_SERVER,
			number=ctx.pkg.number,
			options={
				"TXN": "DisableSubAccount"
			}
		).deserializer()

	#TXN=UpdateAccount\nemail=123456789@123.12\nparentalEmail=\ncountryCode=AU\neaMailFlag=0\nthirdPartyMailFlag=0

