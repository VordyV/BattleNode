from tortoise import Tortoise
import os
from loguru import logger
from ._config import Config

async def init_database(apps: dict, app_config: Config):
    connection = "default"

    config = {
        "connections": {
            connection: {
                "engine": f"tortoise.backends.{app_config.get('database_engine')}",
                "credentials": {
                    "database": app_config.get('database_name'),
                    "host": app_config.get('database_host'),
                    "password": app_config.get('database_password'),
                    "port": app_config.get('database_port'),
                    "user": app_config.get('database_user'),
                    "minsize": app_config.get('database_minsize'),
                    "maxsize": app_config.get('database_maxsize'),
                    "connect_timeout": app_config.get('database_timeout'),
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
    except Exception as error:
        print(error)

async def close_database():
    try:
        await Tortoise.close_connections()
    except Exception as error:
        print(error)
