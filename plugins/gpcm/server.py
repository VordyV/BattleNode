import asyncio
from tornado.iostream import StreamClosedError, IOStream
from tornado.tcpserver import TCPServer
from .server_client import Client
from .protocol import ProtocolGPCM
from .package import PackageGPCM
from .server_context import Context
import traceback, sys

class EchoServer(TCPServer):

    def __init__(self, *args, app_config=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._app_config = app_config
        self._clients: list[Client] = []

    async def handle_stream(self, stream, address):
        # client_proxy = await stream.read_bytes(8, partial=True)
        # print("client_proxy", client_proxy)
        client = Client(stream, address)
        #print(client)
        self._clients.append(client)



        await stream.write(b"\\lc\\1\\challenge\\0000000000\\id\\1\\final\\")
        while True:
            try:
                data = await stream.read_until(b"final\\")
                print("UDP recv", data)
                pkg = PackageGPCM.serialize(data)
                async for answer in getattr(ProtocolGPCM, "%s_%s" % pkg.options[0])(
                        Context(pkg=pkg, app_config=self._app_config, client=client)):
                    print("UDP answer", answer)
                    await stream.write(answer)

            except StreamClosedError:
                print("UDP Lost client at host %s", address[0])
                break
            except Exception as e:
                print("UDP Lost client at host %s", address[0], e)
                traceback.print_exc(file=sys.stdout)
                break
        self._clients.remove(client)

async def handler(config):
    # manually specify only what is necessary for work
    #await init_database(apps={"fesl": ["plugins.fesl.models"]})

    server = EchoServer(app_config=config)
    server.listen(29900)

    await asyncio.Event().wait()

    server.stop()

def main(queue, config):
    try:
        asyncio.run(handler(config))
    except Exception as e:
        queue.put(e)