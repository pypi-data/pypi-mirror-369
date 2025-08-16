import pyjson5 as json


class DopplerJson(dict):
    def __init__(self, name: str, value: str):
        super().__init__(json.loads(value))

        self.__name__ = name

    def __getattribute__(self, name: str):
        if name.startswith("__"):
            return super().__getattribute__(name)

        if name not in self:
            raise KeyError(f"{self.__name__}.{name} is not a valid secret")

        return self[name]
