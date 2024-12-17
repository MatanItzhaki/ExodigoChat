class User:
    def __init__(self, username: str, ip_address: str, port: int) -> None:
        self.__username = username
        self.__ip_address = ip_address
        self.__port = port

    @property
    def username(self) -> str:
        return self.__username

    @property
    def ip_address(self) -> str:
        return self.__ip_address

    @property
    def port(self) -> int:
        return self.__port
