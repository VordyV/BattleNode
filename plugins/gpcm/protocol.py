from .package import PackageGPCM
from .server_context import Context
from plugins.fesl.services import Ticket, ProfileService, AccountService
import time

class ProtocolGPCM:

	commands = [
		"lc",
		"login"
	]

	@staticmethod
	async def getprofile_(ctx: Context):
		#account = await services.AccountService

		yield PackageGPCM([
			("pi", ""),
			("profileid", "6"),
			("nick", "123"),
			("userid", "4"),
			("sig", "06d5aec9dea758d868f7259c4dbf5321"),
			("uniquenick", ""),
			("pid", "1"),
			("lon", "0.000000"),
			("lat", "0.000000"),
			("loc", ""),
			("id", "2"),
		]).deserializer()

	@staticmethod
	async def status_1(ctx: Context):
		statstring = ctx.pkg.get("statstring")
		locstring = ctx.pkg.get("locstring")
		ctx.client._set_status(statstring=statstring, locstring=locstring)
		ctx.np.debug(f'For profile {ctx.client.profile_name}, the status has changed to {statstring} {locstring}')

		yield PackageGPCM([
			("bm", "100"),
			("f", "1"),
			("msg", "|s|1|ss|Online|ls|Battlefield 2142|ip|1565553778|p|51402|qm|0"),
		]).deserializer()

	@staticmethod
	async def login_(ctx: Context):
		ticket = ctx.pkg.get("authtoken")
		pid = await Ticket(ctx.np.redis).verify(ticket)

		profile = await ProfileService.get(pid=pid)
		sesskey = str(int(time.time()))

		ctx.client._set_account_id(profile.get("uid"))
		ctx.client._set_profile_id(pid)
		ctx.client._set_profile_name(profile.get("name"))
		ctx.client._set_sesskey(sesskey)
		ctx.np.debug(f'#{profile.get("uid")} has logged into the profile {profile.get("name")}')
		yield PackageGPCM([
			("lc", "2"),
			("sesskey", sesskey),
			("proof", "00000000000000000000001728985026"),
			("userid", str(profile.get("uid"))),
			("profileid", str(pid)),
			("uniquenick", profile.get("name")),
			("id", "1")
		]).deserializer()

	@staticmethod
	async def lc_1(ctx: Context):
		return PackageGPCM([
			("lc", "1"),
			("challenge", "0000000000"),
			("id", "1")
		]).deserializer()

	@staticmethod
	async def logout_(ctx: Context):
		yield
		return
