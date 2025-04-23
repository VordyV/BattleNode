from tortoise import Tortoise
import os

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
                    "port": os.getenv("BN_DATABASE_PORT"),
                    "user": os.getenv("BN_DATABASE_USER"),
                    "minsize": os.getenv("BN_DATABASE_MINSIZE"),
                    "maxsize": os.getenv("BN_DATABASE_MAXSIZE"),
                    "connect_timeout": os.getenv("BN_DATABASE_TIMEOUT"),
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

    await Tortoise.init(config=config)
    await Tortoise.generate_schemas(safe=True)

async def close_database():
    await Tortoise.close_connections()