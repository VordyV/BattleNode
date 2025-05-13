from typing import ByteString, Any
import json
import pydantic
from anyio import open_file
from pathlib import Path

class Config:

    def __init__(self, configurator, model):
        self.__configurator = configurator
        self.__model = model
        self.__options = model.dict()

        for name, value in self.__options.items():
            setattr(self, name, value)

    def dict(self):
        return self.__options

    def get(self, name: str):
        return self.__options.get(name)

class Configurator:

    def __init__(self, filename: str):
        self.__filename = filename
        self.config: dict = {}

        Path(self.__filename).touch(exist_ok=True)

    async def __read_file(self):
        async with await open_file(self.__filename) as file:
            return await file.read()

    def __write_file(self, data: ByteString):
        with open(self.__filename, "wb") as file:
            file.write(data)

    async def load(self):
        data = await self.__read_file()
        if data: self.config = json.loads(data)

    def get_section(self, name: str, config: pydantic.BaseModel):
        section = self.config.get(name, {})
        return Config(self, config.model_validate(section))


