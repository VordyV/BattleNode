from typing import Callable

class CommandCollection:

    def __init__(self):
        self.__commands: list[dict] = []

    def get(self):
        return self.__commands

    def __add_listener(self, command: str, func: Callable, desc: str = ""):
        self.__commands.append({
            "command": command,
            "func": func,
            "desc": desc
        })

    def on(self, command: str, desc: str = ""):
        def decorator(func: Callable):
            self.__add_listener(command, func.__name__, desc)
            return func
        return decorator