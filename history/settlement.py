import random

from entity.entity import Entity
from events.event_log import event_log
from history.identity import Identity, Temperament, ValueType
from world.tile_type import TileType

ANSI_COLORS = ["\033[38;5;33m",  # azul
               "\033[38;5;34m",  # verde
               "\033[38;5;160m",  # rojo
               "\033[38;5;220m",  # amarillo
               "\033[38;5;141m",  # púrpura
               "\033[38;5;208m",  # naranja
               ]

RESET = "\033[0m"


class Settlement:
    def __init__(self, key, name, born):
        self.key = key
        self.name = name
        self.born = born

        self.color = random.choice(ANSI_COLORS)
        self.glyph = random.choice(["▲", "▴", "◆", "■", "⬟"])

        self.population = 0
        self.food = 10.0
        self.stability = 1.0
        self.fight_bonus = 0

        self.territory = set()  # (x, y)

        # identidad
        self.identity = Identity()

        # reproducción
        self.birth_timer = 0.0

    def tick(self, world):
        # comida
        self.food += self.population * 0.05
        self.food -= self.population * 0.03

        if self.food < 0:
            self.stability -= 0.01

        # reproducción colectiva
        self.birth_timer += self.population * 0.002
        if self.birth_timer >= 1:
            births = int(self.birth_timer)
            self.birth_timer -= births

            for _ in range(births):
                x = self.key[0] * 3 + random.randint(0, 2)
                y = self.key[1] * 3 + random.randint(0, 2)
                world.spawn(Entity(x, y, settlement=self, settled=True))

        # identidad afecta estabilidad
        if self.identity.temperament == Temperament.AGGRESSIVE:
            self.stability -= 0.002
        elif self.identity.temperament == Temperament.SPIRITUAL:
            self.stability += 0.001

        if random.random() < 0.001:
            if self.identity.temperament == Temperament.SPIRITUAL:
                event_log.add(f"{self.name} celebra un rito antiguo 🕯️")
                self.fight_bonus += .1
            elif self.identity.temperament == Temperament.AGGRESSIVE:
                event_log.add(f"{self.name} entrena para la guerra ⚔️")
            self.fight_bonus += .5
        self.expand_territory(world)

    def symbol(self):
        return f"{self.color}{self.glyph}{RESET}"

    def expand_territory(self, world):
        frontier = list(self.territory)[:5]  # limitamos
        for x, y in frontier:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if not world.in_bounds(nx, ny):
                    continue
                tile = world.tiles[ny][nx]
                if tile.kind == TileType.ROCK:
                    continue
                if tile.owner is None:
                    tile.owner = self
                    self.territory.add((nx, ny))

    @property
    def ideology_score(self) -> float:
        score = 0

        if self.identity.temperament == Temperament.AGGRESSIVE:
            score += 0.6
        if self.identity.value == ValueType.EXPANSION:
            score += 0.4
        if self.identity.temperament == Temperament.PEACEFUL:
            score -= 0.3

        return score

    @property
    def war_score(self) -> float:
        score = 0

        if self.identity.temperament == Temperament.AGGRESSIVE:
            score += 0.2

        return self.population + score + self.fight_bonus

    def is_neighbor(self, other) -> bool:
        ax, ay = self.key
        bx, by = other.key

        return abs(ax - bx) + abs(ay - by) == 1

    def lose_border_tile(self, world):
        x, y = self.key

        border_keys = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), ]

        random.shuffle(border_keys)

        for key in border_keys:
            if key not in world.history.settlements:
                # expulsar entidades en ese tile
                members = world.entity_grid.get(key, [])
                for e in members:
                    e.settled = False
                    e.settlement = None

                self.stability -= 0.1
                event_log.add(f"{self.name} pierde territorio ⚠️")
                return

    def war_advantage_against(self, other):
        """
        Devuelve un número entre 0 y 1
        0.5 = fuerzas parejas
        >0.5 = ventaja
        <0.5 = desventaja
        """
        diff = self.war_score - other.war_score

        # suaviza para que no explote
        return 0.5 + max(min(diff * 0.1, 0.4), -0.4)
