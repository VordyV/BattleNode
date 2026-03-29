import asyncio
from tornado import gen
from tornado.iostream import StreamClosedError, IOStream
from tornado.tcpserver import TCPServer
from tornado.ioloop import PeriodicCallback
from battlenode import init_database
import sys, traceback
from battlenode import NewProcess
from .enctypex import EncTypeX
from .package import Header, Server, Package

class EchoServer(TCPServer):
    def __init__(self, *args, new_process: NewProcess, **kwargs):
        super().__init__(*args, **kwargs)
        self._np = new_process
        self._etx_key = self._np.config.get("enctypex_key", "").encode("ascii")
        self._etx = EncTypeX()

    async def handle_stream(self, stream, address):
        data = await stream.read_until(b"\x00\x00\x00\x00\x00")
        data = data.split(b'\x00')
        if data[0] == b"":
            code = data[8][:8]
        else:
            code = data[7][:8]

        server_data = await self._np.shared_data.get("serverdata")
        keys = server_data.get("keys")

        servers = []
        for sid, options in server_data.get("list").items():
            server_data = await self._np.shared_data.get(f"server_{sid}")
            if server_data:
                servers.append(Server(ip=options.get("address"), port=options.get("query_port"), data=server_data))

        package = Package(
            header=Header(transport_ip="192.168.1.100", transport_port=6500, opcode=len(keys)),
            servers=servers,
            keys=keys
        )

        result = self._etx.encrypt(self._etx_key, code, bytearray(package.to_bytes()))
        await stream.write(result)

async def handler(np: NewProcess):
    # manually specify only what is necessary for work
    #await init_database(apps={"fesl": ["plugins.fesl.models"]})
    server = EchoServer(new_process=np)
    server.listen(np.config.get("port"))

    await asyncio.Event().wait()

    server.stop()

def main(queue, config, app_config):
    np = NewProcess(queue=queue, config=config, app_config=app_config, app_name="sb")
    np.start(handler)