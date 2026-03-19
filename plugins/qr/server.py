import asyncio

class QRServer:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        self.transport.sendto(b"\xfe\xfd\x09\x00\x00\x00\x00", addr)

async def handler(config):
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(QRServer,
        local_addr=(config.get("server_address"), config.get("server_port")))

    await asyncio.Event().wait()
    transport.close()

def main(queue, config, app_config):
    try:
        asyncio.run(handler(config))
    except Exception as e:
        queue.put(e)