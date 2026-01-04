import uvicorn
import asyncio
from fastapi import FastAPI

app = FastAPI()

@app.get("/simple")
async def simple():
    return "simple"

async def handler(config):
    # manually specify only what is necessary for work
    #await init_database(apps={"fesl": ["plugins.fesl.models"]})
    config = uvicorn.Config(app, host="127.0.0.1", port=8081, log_level="critical")
    server = uvicorn.Server(config)
    await server.serve()
    #await asyncio.Event().wait()

def main(queue, config):
    try:
        asyncio.run(handler(config))
    except Exception as e:
        queue.put(e)