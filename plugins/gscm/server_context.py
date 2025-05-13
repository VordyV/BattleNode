from .server_client import Client
from .package import PackageGPCM

class Context:

    def __init__(self, pkg: PackageGPCM, app_config: dict, client: Client):
        self.__pkg = pkg
        self.__app_config = app_config
        self.__client = client

    @property
    def pkg(self):
        return self.__pkg

    @property
    def app_config(self):
        return self.__app_config

    @property
    def client(self):
        return self.__client