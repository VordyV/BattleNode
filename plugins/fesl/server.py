import asyncio
from tornado import gen
from tornado.iostream import StreamClosedError, IOStream
from tornado.tcpserver import TCPServer
from tornado.ioloop import PeriodicCallback
from .package import PackageFesl
from .protocol import ProtocolFesl
from .server_client import Client
from .server_context import Context
import sys, traceback
from battlenode import NewProcess

class EchoServer(TCPServer):

    proxy_header_prefix = "PROXY"

    def __init__(self, *args, new_process: NewProcess, **kwargs):
        super().__init__(*args, **kwargs)
        self._np = new_process
        self._clients: list[Client] = []
        self._event_gpcm_logout = asyncio.create_task(self._np.subscribe("gpcm.logout", self._on_gpcm_logout))

    async def _on_gpcm_logout(self, data):
        try:
            uid = data.get("uid")
            pid = data.get("pid")

            if uid == None or pid == None: return

            for client in self._clients:
                if (client.is_authenticated and client.account_id == uid) and (client.is_profile_authenticated and client.profile_id == pid):
                    client._remove_profile_id()
        except Exception as error:
            print(error)

    async def handle_stream(self, stream, address):
        #client_proxy = await stream.read_bytes(8, partial=True)
        #print("client_proxy", client_proxy)

        #real_address: tuple[str, int] = address
        client = Client(stream, address)
        self._clients.append(client)
        #profiles = await self._np.shared_data.get("profiles")
        self._np.debug(f"{client.address[0]}({client.address[1]}) connected to the server")

        try:
            if self._np.config.get("proxy"):
                data = await stream.read_until(b"\n")

                data = data.decode()
                if data.startswith(EchoServer.proxy_header_prefix):
                    proxy_data = data.split()
                    p_protocol = proxy_data[1]
                    p_real_ip = proxy_data[2]
                    p_real_port = proxy_data[4]
                    self._np.debug(f"proxy data: {p_protocol} {p_real_ip}:{p_real_port}")

                    real_address = (p_real_ip, p_real_port)
                    client._set_address(real_address)

                #print("proxy_data", proxy_data)

            #print("client", client)

            while True:
                try:
                    request_type = await stream.read_bytes(4)
                    package_type = await stream.read_bytes(1)
                    number = await stream.read_bytes(3)
                    size = await stream.read_bytes(4)
                    data = await stream.read_until(b"\x00")
                    #print("f recv", request_type + package_type + number + size + data)
                    pkg = PackageFesl.validate(request_type, package_type, number, size, data)
                    async for answer in getattr(ProtocolFesl, pkg.options["TXN"])(Context(pkg=pkg, new_process=self._np, client=client, server=self)):
                        #print("f answer", answer)
                        await stream.write(answer)

                except StreamClosedError:
                    #print("Lost client at host %s", address[0])
                    break
                except Exception as e:
                    #print("Lost client at host %s", address[0], e)
                    #traceback.print_exc(file=sys.stdout)
                    self._np.debug(str(e))
                    break
        except Exception as error:
            uid = -1
            if client.is_authenticated: uid = client.account_id
            self._np.error(f"nexpected session error {client.address[0]}:{client.address[1]} UID {uid}:\n{error}", "")
        finally:
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

    #task = asyncio.create_task(np.subscribe("fesl.test", t))

    server = EchoServer(new_process=np)
    server.listen(np.config.get("port"))

    pc = PeriodicCallback(server.broadcast, 10000)
    pc.start()

    await asyncio.Event().wait()

    pc.stop()
    server.stop()

def main(queue, config, app_config):
    np = NewProcess(queue=queue, config=config, app_config=app_config, app_name="fesl", db_apps={"fesl": ["plugins.fesl.models"]})
    np.start(handler)