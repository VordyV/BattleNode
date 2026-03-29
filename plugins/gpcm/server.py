import asyncio
from tornado.iostream import StreamClosedError, IOStream
from tornado.tcpserver import TCPServer
from .server_client import Client
from .protocol import ProtocolGPCM
from .package import PackageGPCM
from .server_context import Context
import traceback, sys
from battlenode import NewProcess, init_database

class EchoServer(TCPServer):

    def __init__(self, *args, new_process: NewProcess,  **kwargs):
        super().__init__(*args, **kwargs)
        self._np = new_process
        self._clients: list[Client] = []

    async def handle_stream(self, stream, address):
        client = Client(stream, address)
        self._clients.append(client)

        await stream.write(b"\\lc\\1\\challenge\\0000000000\\id\\1\\final\\")
        while True:
            try:
                data = await stream.read_until(b"final\\")
                #print("UDP recv", data)
                pkg = PackageGPCM.serialize(data)
                async for answer in getattr(ProtocolGPCM, "%s_%s" % pkg.options[0])(
                        Context(pkg=pkg, new_process=self._np, client=client)):
                    #print("UDP answer", answer)
                    await stream.write(answer)

            except StreamClosedError:
                #print("UDP Lost client at host %s", address[0])
                break
            except Exception as e:
                print("UDP Lost client at host %s", address[0], e)
                traceback.print_exc(file=sys.stdout)
                break
        await self._np.publish("gpcm.logout", {"uid": client.account_id, "pid": client.profile_id})
        self._clients.remove(client)

async def handler(np: NewProcess):
    # manually specify only what is necessary for work
    #await init_database(apps={"fesl": ["plugins.fesl.models"]})

    server = EchoServer(new_process=np)
    server.listen(29900)

    await asyncio.Event().wait()

    server.stop()

def main(queue, config, app_config):
    np = NewProcess(queue=queue, config=config, app_config=app_config, app_name="gpcm", db_apps={"fesl": ["plugins.fesl.models"]})
    np.start(handler)