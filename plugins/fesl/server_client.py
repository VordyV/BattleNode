from tornado.iostream import StreamClosedError, IOStream

class Client:

    def __init__(self, stream: IOStream, address: tuple[str, str]):
        self.__account_id: int | None = None
        self.__stream = stream
        self.__address = address
        self.__is_authenticated: bool = False
        self.__profile_id: int | None = None

    def _set_account_id(self, ident: int):
        self.__account_id = ident
        self.__is_authenticated = True

    def _set_profile_id(self, ident: int):
        self.__profile_id = ident

    @property
    def stream(self) -> IOStream:
        return self.__stream

    @property
    def address(self) -> tuple[str, str]:
        return self.__address

    @property
    def account_id(self) -> int:
        if not self.__account_id: raise Exception("Client is not authorized")
        return self.__account_id

    @property
    def is_authenticated(self) -> bool:
        return self.__is_authenticated

    @property
    def profile_id(self) -> int:
        if not self.__profile_id: raise Exception("Client is not logged into the profile")
        return self.__profile_id