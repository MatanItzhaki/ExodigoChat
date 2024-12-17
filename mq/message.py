import json


class Message:
    def __init__(self, content: dict) -> None:
        self.__content = content

    @property
    def content(self) -> dict:
        return self.__content
