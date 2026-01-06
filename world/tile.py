from world.tile_type import TileType


class Tile:
    def __init__(self, kind: TileType):
        self.kind = kind

    def char(self):
        return {TileType.ROCK: "A", TileType.FLOOR: ".", TileType.SURFACE: ",", }.get(self.kind, "?")

    def energy_yield(self):
        return {TileType.FLOOR: 0.2, TileType.SURFACE: 0.4, TileType.ROCK: 0.0, }.get(self.kind, 0.0)
