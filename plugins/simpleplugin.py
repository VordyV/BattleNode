from battlenode import BasePlugin, Events, eventsEmitter
from tornado.tcpserver import TCPServer
from tornado.iostream import StreamClosedError
import asyncio
import pydantic

class EchoServer(TCPServer):
    async def handle_stream(self, stream, address):
        print(address)
        while True:
            try:
                data = await stream.read_until(b"\n")
                await stream.write(data)
            except StreamClosedError:
                break

class SimplePlugin(BasePlugin):

    events = Events()

    class Meta(BasePlugin.Meta):
        name = "SimplePlugin"
        requires_battlenode = ">=0.1"
        version = "0.1"
        dependencies = {
        }

    class Config(pydantic.BaseModel):
        option: str = "Hello"

    @events.on("statuschange")
    async def on_statuschange(self, status):
        pass

    @events.on("init")
    async def on_init(self):
        self.logger.info("start pl 11 {}", self.battlenode.config.database)
        server = EchoServer()
        server.listen(8008)

    @events.on("shutdown")
    async def on_shutdown(self):
        self.logger.info("stop pl 1")
