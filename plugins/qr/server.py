import asyncio
from battlenode import NewProcess

class QRServer:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        self.transport.sendto(b"\xfe\xfd\x09\x00\x00\x00\x00", addr)

async def handler(np: NewProcess):
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(QRServer,
        local_addr=(np.config.get("server_address"), np.config.get("server_port")))

    await asyncio.Event().wait()
    transport.close()

def main(queue, config, app_config):
    np = NewProcess(queue=queue, config=config, app_config=app_config, app_name="qr")
    np.start(handler)