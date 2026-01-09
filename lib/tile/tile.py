import config

from lib.tile.tile_type import TileType


class Tile:
    __slots__ = (
        "y", "x", "kind", "position", "population", "food", "owner", "settled", "conflict", "conflict_progress")

    def __init__(self, kind: TileType, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        # población local (opcional, útil para futuro)
        self.population = 0
        self.conflict = None  # None | Conflict
        self.conflict_progress = 0.0

        self.settled: bool = False

        self.food = 10

        # soberanía política
        # None | Faction
        self.owner = None

    # ──────────────────────────────
    # Recursos
    # ──────────────────────────────
    def food_yield(self):
        return {TileType.FLOOR: 0.2, TileType.SURFACE: 0.4, TileType.ROCK: 0.0, }.get(self.kind, 0.0)

    # ──────────────────────────────
    # Población local (futuro)
    # ──────────────────────────────
    @property
    def is_fully_populated(self) -> bool:
        return self.population >= config.MAX_TILE_POPULATION

    # ──────────────────────────────
    # Fronteras políticas
    # ──────────────────────────────
    def is_border(self, world, x, y) -> bool:
        """
        Un tile es frontera si algún vecino pertenece a otra facción
        """
        if not self.owner:
            return False

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy

            # fuera del mundo NO cuenta como frontera
            if not (0 <= nx < world.width and 0 <= ny < world.height):
                continue

            neighbor = world.tiles[ny][nx]
            if neighbor.owner != self.owner:
                return True

        return False

    def can_spawn(self) -> bool:
        return self.kind.habitable

    def can_move(self) -> bool:
        return self.kind.passable

    def can_settle(self) -> bool:
        return self.kind.supports_settlement

    def work(self):
        self.food += config.MAX_TILE_POPULATION - self.population + 1

    def reset(self):
        self.food = 10
        self.owner = None
        self.settled = False

    def settle_tile(self, faction):
        self.settled = True
        self.owner = faction
