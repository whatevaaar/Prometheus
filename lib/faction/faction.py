import random

from pygame import Color

from geometry.point.point import Point
from lib.events.event_log import event_log
from lib.history.identity import Identity, ValueType, Temperament


class Faction:
    def __init__(self, name, leader):
        self.name = name
        self.leader = leader  # Entity
        self.identity = Identity()

        self.tiles = set()  # (x, y)
        self.settlements = set()
        self.population = 0

        self.alive = True

        self.fight_bonus = 0

        self.glyph = random.choice(["▲", "▴", "◆", "■", "⬟"])
        self.color = random.choice([Color(255, 255, 255),  # blanco
                                    Color(0, 0, 0),  # negro
                                    Color(255, 0, 0),  # rojo
                                    Color(0, 255, 0),  # verde
                                    Color(0, 0, 255),  # azul
                                    Color(255, 255, 0),  # amarillo
                                    Color(255, 0, 255),  # magenta
                                    Color(0, 255, 255),  # cyan
                                    Color(255, 165, 0),  # naranja
                                    Color(128, 0, 128),  # morado
                                    ])

    def tick(self, world):
        if not self.tiles:
            self.collapse(world)
            return

        self.expand(world)

    def expand(self, world):
        if self.identity.value != ValueType.EXPANSION:
            return

        frontier = list(self.tiles)
        random.shuffle(frontier)

        for x, y in frontier[:5]:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if not Point(nx, ny).is_in_world():
                    continue

                tile = world.tiles[ny][nx]
                if tile.owner is self or not tile.can_spawn():
                    continue

                self.claim_tile(world, nx, ny)
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
