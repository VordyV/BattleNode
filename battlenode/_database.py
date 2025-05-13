from tortoise import Tortoise
import os
from loguru import logger

async def init_database(apps: dict):
    connection = "default"

    config = {
        "connections": {
            connection: {
                "engine": f"tortoise.backends.{os.getenv("BN_DATABASE_ENGINE")}",
                "credentials": {
                    "database": os.getenv("BN_DATABASE_NAME"),
                    "host": os.getenv("BN_DATABASE_HOST"),
                    "password": os.getenv("BN_DATABASE_PASSWORD"),
                    "port": int(os.getenv("BN_DATABASE_PORT")),
                    "user": os.getenv("BN_DATABASE_USER"),
                    "minsize": int(os.getenv("BN_DATABASE_MINSIZE")),
                    "maxsize": int(os.getenv("BN_DATABASE_MAXSIZE")),
                    "connect_timeout": int(os.getenv("BN_DATABASE_TIMEOUT")),
                }
            }
        },
        "apps": {},
    }

    for app, models in apps.items():
        if not models: continue
        config["apps"][app] = {
            "models": models,
            "default_connection": connection
        }

    try:
        await Tortoise.init(config=config)
        await Tortoise.generate_schemas(safe=True)
    except Exception as error:
        print(error)

async def close_database():
    try:
        await Tortoise.close_connections()
    except Exception as error:
        print(error)
