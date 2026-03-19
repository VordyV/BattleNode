from typing import List, Dict, Any, Tuple
import io

class PackageGPCM:

	def __init__(self, options: List[Tuple[str, Any]] = None):
		self.options = options

	#def __repr__(self):
	#	return f"{self.__class__.__name__}({", ".join(self._options)})"

	@staticmethod
	def serialize(bytes):

		data = bytes.decode()

		if data.startswith("\\"):
			data = data[1:]
		if data.endswith("\\"):
			data = data[:-1]

		components = data.split("\\")

		result = []

		for i in range(0, len(components) - 1, 2):
			key = components[i]
			value = components[i + 1]
			result.append((key, value))

		return __class__(result)

	def deserializer(self):
		buffer = io.BytesIO()
		buffer.write(b"\\")
		for item in self.options:
			buffer.write("\\".join(item).encode())
			buffer.write(b"\\")
		buffer.write(b"final\\")
		return buffer.getvalue()

	def get(self, option_name: str) -> Any | None:
		if not self.options: return None
		for option in self.options:
			if option[0] == option_name: return option[1]