from battlenode import BasePlugin, Events
import asyncio
from tornado.tcpserver import TCPServer
from tornado.iostream import StreamClosedError

class EchoServer(TCPServer):
    async def handle_stream(self, stream, address):
        print(address)
        while True:
            try:
                data = await stream.read_until(b"\n")
                await stream.write(data)
            except StreamClosedError:
                break

class SimplePlugin2(BasePlugin):

    events = Events()

    class Meta(BasePlugin.Meta):
        name = "SimplePlugin2"
        requires_battlenode = ">=0.1"
        version = "0.1"
        dependencies = {
        }

    @events.on("init")
    async def on_init(self):
        self.logger.info("start pl 2")
        server = EchoServer()
        server.listen(8009)

    @events.on("shutdown")
    async def on_shutdown(self):
        self.logger.info("stop pl 2")
