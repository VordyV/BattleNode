from battlenode import BasePlugin, EventCollection, EventData
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

    events = EventCollection()

    class Meta(BasePlugin.Meta):
        name = "SimplePlugin2"
        requires_battlenode = ">=0.1"
        version = "0.1"
        dependencies = {
        }

    @events.on("init")
    async def on_init(self, event: EventData):
        self.logger.info("start pl 2")
        server = EchoServer()
        server.listen(8009)

    @events.on("shutdown")
    async def on_shutdown(self, event: EventData):
        self.logger.info("stop pl 2")
