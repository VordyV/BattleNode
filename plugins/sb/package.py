import ipaddress
import struct
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Header:
	transport_ip: str
	transport_port: int
	opcode: int

	def to_bytes(self) -> bytes:
		return (
			ipaddress.IPv4Address(self.transport_ip).packed +
			struct.pack(">H", self.transport_port) +
			bytes([self.opcode])
		)


@dataclass
class Server:
	ip: str
	port: int
	data: Dict[str, str]

	def to_bytes(self, keys: List[str]) -> bytes:
		b = bytearray()

		# server address
		b += ipaddress.IPv4Address(self.ip).packed
		b += struct.pack(">H", self.port)

		# BF2142 padding (9)
		b += b"\x00" * 9

		# values
		for key in keys:
			value = self.data.get(key, "")
			b += b"\x00\xff"
			b += value.encode("utf-8", errors="ignore")

		# server terminator
		b += b"\x00"

		return bytes(b)


@dataclass
class Package:
	header: Header
	keys: List[str]
	servers: List[Server]

	def to_bytes(self) -> bytes:
		b = bytearray()

		# header
		b += self.header.to_bytes()
		b += b"\x00"

		# keys
		for key in self.keys:
			b += key.encode("ascii")
			b += b"\x00\x00"

		# servers
		for server in self.servers:
			b += b"\x7e"   # '~'
			b += server.to_bytes(self.keys)

		# EOF
		b += b"\x00\xff\xff\xff\xff"

		return bytes(b)