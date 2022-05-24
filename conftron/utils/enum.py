import enum


class Enum(str, enum.Enum):
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @classmethod
    def keys(cls):
        return tuple(cls.__members__.keys())

    @classmethod
    def values(cls):
        return tuple(cls.__members__.values())
