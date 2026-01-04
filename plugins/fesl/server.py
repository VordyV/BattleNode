import asyncio
from tornado import gen
from tornado.iostream import StreamClosedError, IOStream
from tornado.tcpserver import TCPServer
from tornado.ioloop import PeriodicCallback
from battlenode import init_database
from .package import PackageFesl
from .protocol import ProtocolFesl
from .server_client import Client
from .server_context import Context
import sys, traceback
from battlenode import NewProcess

class EchoServer(TCPServer):
    
    def __init__(self, *args, new_process: NewProcess, **kwargs):
        super().__init__(*args, **kwargs)
        self._np = new_process
        self._clients: list[Client] = []

    async def handle_stream(self, stream, address):
        #client_proxy = await stream.read_bytes(8, partial=True)
        #print("client_proxy", client_proxy)
        client = Client(stream, address)
        #print("client", client)
        self._clients.append(client)

        self._np.debug(f"{client.address[0]}({client.address[1]}) connected to the server")

        if self._np.config.get("proxy"):
            proxy_data = await stream.read_until(b"\n")
            self._np.debug(f"proxy data: {proxy_data}")
            #print("proxy_data", proxy_data)

        while True:
            try:
                request_type = await stream.read_bytes(4)
                package_type = await stream.read_bytes(1)
                number = await stream.read_bytes(3)
                size = await stream.read_bytes(4)
                data = await stream.read_until(b"\x00")
                #print("recv", request_type + package_type + number + size + data)
                pkg = PackageFesl.validate(request_type, package_type, number, size, data)
                async for answer in getattr(ProtocolFesl, pkg.options["TXN"])(Context(pkg=pkg, new_process=self._np, client=client)):
                    #print("answer", answer)
                    await stream.write(answer)

            except StreamClosedError:
                #print("Lost client at host %s", address[0])
                break
            except Exception as e:
                #print("Lost client at host %s", address[0], e)
                #traceback.print_exc(file=sys.stdout)
                self._np.error(str(e))
                break
        self._np.debug(f"{client.address[0]}({client.address[1]}) disconnected from the server")
        self._clients.remove(client)

    async def broadcast(self):
        for client in self._clients:
            try:
                await client.stream.write(await ProtocolFesl.PingPing())
            except Exception as e:
                self._np.warning(f"ping request was not sent at host {client.address[0]}({client.address[1]}): {e}")

async def handler(np: NewProcess):
    # manually specify only what is necessary for work
    await init_database(apps={"fesl": ["plugins.fesl.models"]})

    server = EchoServer(new_process=np)
    server.listen(np.config.get("port"))

    pc = PeriodicCallback(server.broadcast, 10000)
    pc.start()

    await asyncio.Event().wait()

    pc.stop()
    server.stop()

def main(queue, config):
    try:
        asyncio.run(handler(NewProcess(queue=queue, app_config=config)))
    except Exception as e:
        queue.put(e)