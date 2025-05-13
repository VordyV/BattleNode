import enum
import struct
import re
import io

class SerializationError(Exception): pass

class TypesRequests(enum.Enum):
    FSYS = "fsys"
    ACCT = "acct"
    SUBS = "subs"
    DOBJ = "dobj"

class TypesPackages(enum.Enum):
    SINGLE_CLIENT = b"\xC0" # one packet request
    SINGLE_SERVER = b"\x80" # one packet answer/request
    MULTI_CLIENT = b"\xF0" # part of multipacket request (all parts with one PacketNumber)
    MULTI_SERVER = b"\xB0" # part of multipacket answer/request (all parts with one PacketNumber)

class PackageFesl:
	def __init__(self, request_type: TypesRequests = TypesRequests.FSYS, package_type: TypesPackages = TypesPackages.SINGLE_SERVER, number: int = 1, options: dict = {}):
		self.request_type = request_type
		self.package_type = package_type
		self.number = number
		self.options = options

	def __repr__(self):
		return f"{self.__class__.__name__}({", ".join([f"{k}={v}" for k, v in vars(self).items()])})"

	def deserializer(self):
		buffer = io.BytesIO()
		buffer.write(self.request_type.value.encode('utf-8'))
		buffer.write(self.package_type.value)
		buffer.write(self.number.to_bytes(3, byteorder='big'))
		data_str = ''.join(f"{key}={value}\n" for key, value in self.options.items())
		data_bytes = data_str.encode('utf-8')
		packet_size = 4 + 1 + 3 + 4 + len(data_bytes) + 1
		buffer.write(packet_size.to_bytes(4, byteorder='big'))
		buffer.write(data_bytes)
		buffer.write(b'\x00')
		return buffer.getvalue()

	@staticmethod
	def serialize(bytes):
		request_type = TypesRequests(struct.unpack_from('4s', bytes, 0)[0].decode('utf-8'))
		package_type = TypesPackages(struct.unpack_from('1s', bytes, 4)[0])
		number = int(struct.unpack_from('3s', bytes, 5)[0].hex(), 16)
		size = struct.unpack_from('>I', bytes, 8)[0] # int(b'\x00\x00\x00\xac'.hex(), 16)
		data = bytes[12:-1].decode('utf-8')
		options = {}
		for match in re.finditer(r'(\w+)=(.*)', data):
			k, v = match.groups()
			if v.isdigit(): v = int(v)
			options[k] = v
		if len(bytes) != size: raise SerializationError(
			"Invalid request. The size of the request does not match the one specified in the request itself")
		if bytes[-1:] != b'\x00': raise SerializationError("Invalid request. The request is incomplete")
		return __class__(request_type, package_type, number, options)

	@staticmethod
	def validate(request_type, package_type, number, size, data):
		bytes = request_type + package_type + number + size + data
		request_type = TypesRequests(request_type.decode('utf-8'))
		package_type = TypesPackages(package_type)
		number = int(number.hex(), 16)
		size = int(size.hex(), 16)
		data = data.decode("utf-8")
		options = {}
		for match in re.finditer(r'(\w+)=(.*)', data):
			k, v = match.groups()
			if v.isdigit(): v = int(v)
			options[k] = v
		if len(bytes) != size: raise SerializationError(
			"Invalid request. The size of the request does not match the one specified in the request itself")
		if bytes[-1:] != b'\x00': raise SerializationError("Invalid request. The request is incomplete")
		return __class__(request_type, package_type, number, options)

