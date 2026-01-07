from enum import Enum, auto


class TileType(Enum):
    WATER = auto()
    SURFACE = auto()
    FLOOR = auto()
    ROCK = auto()

    @property
    def passable(self) -> bool:
        return self in (TileType.FLOOR, TileType.SURFACE)

    @property
    def habitable(self) -> bool:
        return self in (TileType.FLOOR, TileType.SURFACE)

    @property
    def supports_settlement(self) -> bool:
        return self == TileType.SURFACE
