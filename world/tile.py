import config
from world.tile_type import TileType


class Tile:
    def __init__(self, kind: TileType):
        self.kind = kind
        self.population = 0
        self.owner = None

    def char(self, world=None, x=None, y=None):
        if self.kind == TileType.ROCK:
            return "A"

        if self.owner and world is not None:
            if self.is_border(world, x, y):
                return "▒"  # frontera
            return "░"  # interior settlement

        return "."  # terreno libre

    def food_yield(self):
        return {TileType.FLOOR: 0.2, TileType.SURFACE: 0.4, TileType.ROCK: 0.0, }.get(self.kind, 0.0)

    @property
    def is_fully_populated(self) -> bool:
        return self.population >= config.MAX_TILE_POPULATION

    def increase_population(self, population):
        self.population += population

    def is_border(self, world, x, y):
        if not self.owner:
            return False

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < world.width and 0 <= ny < world.height):
                return True
            if world.tiles[ny][nx].owner != self.owner:
                return True
        return False
