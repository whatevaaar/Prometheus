import random

from geometry.point.point import get_valid_map_points_in_radius
from graphics.prometheus_colors.prometheus_colors import get_random_faction_color
from lib.events.event_log import event_log
from lib.history.identity import Identity, ValueType, Temperament


class Faction:
    def __init__(self, name, leader):
        self.tile_positions = []
        __slots__ = (
            "name", "leader", "identity", "tiles", "settlements", "population", "alive", "fight_bonus", "glyph",
            "color",)

        self.name = name
        self.leader = leader  # Entity
        self.identity = Identity()

        self.tiles = set()  # (x, y)
        self.settlements = set()
        self.population = 0

        self.alive = True

        self.fight_bonus = 0

        self.glyph = random.choice(["▲", "▴", "◆", "■", "⬟"])
        self.color = get_random_faction_color()

    def tick(self, world):
        if not self.tiles:
            self.collapse(world)
            return

        self.expand(world)

    def expand(self, world):
        if self.identity.value != ValueType.EXPANSION:
            return

        # tiles contiguos: fronteras de tu facción
        frontier = [(x, y) for x, y in self.tiles if
                    any(world.tiles[ny][nx].owner != self for nx, ny in get_valid_map_points_in_radius(x, y, 1))]

        random.shuffle(frontier)

        expanded = 0
        for x, y in frontier:
            for nx, ny in get_valid_map_points_in_radius(x, y, 1):  # radius 1, vecinos inmediatos
                tile = world.tiles[ny][nx]
                if tile.owner is self or not tile.can_spawn():
                    continue

                self.claim_tile(world, nx, ny)
                expanded += 1
                if expanded >= 5:  # máximo tiles por tick
                    return

    def claim_tile(self, world, x, y):
        tile = world.tiles[y][x]
        old = tile.owner

        tile.owner = self
        self.tiles.add((x, y))

        if old and old is not self:
            old.tiles.discard((x, y))
            event_log.add(f"{self.name} arrebata territorio a {old.name}")

    def annex_settlement(self, settlement):
        old = settlement.faction
        settlement.faction = self
        self.settlements.add(settlement)

        if old:
            old.settlements.discard(settlement)

        event_log.add(f"{settlement.name} es anexado por {self.name}")

    def collapse(self, world):
        self.alive = False
        event_log.add(f"La facción {self.name} colapsa ☠️")

        for s in self.settlements:
            s.faction = None

        world.history.remove_faction(self)

    @property
    def war_score(self) -> float:
        score = 0

        if self.identity.temperament == Temperament.AGGRESSIVE:
            score += 0.2

        return len(self.settlements) + score + self.fight_bonus

    def border_tiles_against(self, other, world):
        tiles = []
        for x, y in self.tile_positions:
            tile = world.tiles[y][x]
            possible_points = tile.position.get_valid_map_points_in_radius(x, y, 1)

            for position in possible_points:
                neighbor = world.get_tile_at_position(position)
                if neighbor.owner == other:
                    tiles.append(neighbor)

        return tiles
