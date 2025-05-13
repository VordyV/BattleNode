from tornado.iostream import StreamClosedError, IOStream

class Client:

    def __init__(self, stream: IOStream, address: tuple[str, str]):
        self.__account_id: int | None = None
        self.__stream = stream
        self.__address = address

    def _set_account_id(self, ident: int):
        self.__account_id = ident

    @property
    def stream(self):
        return self.__stream

    @property
    def address(self):
        return self.__address

    @property
    def account_id(self):
        return self.__account_id
