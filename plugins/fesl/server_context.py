from .server_client import Client
from .package import PackageFesl
from battlenode import NewProcess

class Context:

    def __init__(self, pkg: PackageFesl, new_process: NewProcess, client: Client):
        self.__pkg = pkg
        self.__np = new_process
        self.__client = client

    @property
    def pkg(self):
        return self.__pkg

    @property
    def app_config(self):
        return self.__np.app_config

    @property
    def config(self):
        return self.__np.config

    @property
    def client(self):
        return self.__client

    @property
    def np(self):
        return self.__np