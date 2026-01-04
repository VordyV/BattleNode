from .package import PackageGPCM
from .server_context import Context
from plugins.fesl import services

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
			("profileid", "1"),
			("nick", ""),
			("userid", "1"),
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
		yield PackageGPCM([
			("bm", "100"),
			("f", "1"),
			("msg", "|s|1|ss|Online|ls|Battlefield 2142|ip|1565553778|p|51402|qm|0"),
		]).deserializer()

	@staticmethod
	async def login_(ctx: Context):
		yield PackageGPCM([
			("lc", "2"),
			("sesskey", "1728985026"),
			("proof", "00000000000000000000001728985026"),
			("userid", "1"),
			("profileid", "1"),
			("uniquenick", "admin"),
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
