from tornado.iostream import StreamClosedError, IOStream

class ClientStatus:

    def __init__(self, statstring: str, locstring: str):
        self.__statstring = statstring
        self.__locstring = locstring

    @property
    def statstring(self) -> str:
        return self.__statstring

    @property
    def locstring(self) -> str:
        return self.__locstring

class Client:

    def __init__(self, stream: IOStream, address: tuple[str, str]):
        self.__account_id: int | None = None
        self.__profile_id: int | None = None
        self.__profile_name: str | None = None
        self.__status: ClientStatus | None = None
        self.__sesskey: str | None = None
        self.__stream = stream
        self.__address = address

    def _set_account_id(self, ident: int):
        self.__account_id = ident

    def _set_profile_id(self, ident: int):
        self.__profile_id = ident

    def _set_profile_name(self, name: str):
        self.__profile_name = name

    def _set_status(self, statstring: str, locstring: str):
        self.__status = ClientStatus(statstring=statstring, locstring=locstring)

    def _set_sesskey(self, key: str):
        self.__sesskey = key

    @property
    def stream(self):
        return self.__stream

    @property
    def address(self):
        return self.__address

    @property
    def account_id(self):
        return self.__account_id

    @property
    def profile_id(self):
        return self.__profile_id

    @property
    def profile_name(self):
        return self.__profile_name

    @property
    def sesskey(self) -> str:
        return self.__sesskey