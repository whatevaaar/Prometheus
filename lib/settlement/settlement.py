import random

from lib.entity.entity import Entity
from lib.events.event_log import event_log
from lib.history.identity import Temperament
from geometry.point.point import Point

ANSI_COLORS = ["\033[38;5;33m",  # azul
               "\033[38;5;34m",  # verde
               "\033[38;5;160m",  # rojo
               "\033[38;5;220m",  # amarillo
               "\033[38;5;141m",  # púrpura
               "\033[38;5;208m",  # naranja
               ]

RESET = "\033[0m"


class Settlement:
    def __init__(self, key, name, born, point: Point):
        self.key = key
        self.name = name
        self.point = point

        self.born = born

        self.color = random.choice(ANSI_COLORS)
        self.glyph = random.choice(["▲", "▴", "◆", "■", "⬟"])

        self.population = 0
        self.food = 10.0
        self.stability = 1.0
        self.fight_bonus = 0

        self.territory = set()  # (x, y)

        # identidad
        self.faction = None

        # reproducción
        self.birth_timer = 0.0

    def handle_food(self):
        self.food += self.population * 0.05
        self.food -= self.population * 0.03

        if self.food < 0:
            self.stability -= 0.01
            event_log.add(f"{self.name} pasa hambruna")

    def handle_reproduction(self, world):
        # reproducción colectiva
        self.birth_timer += self.population * 0.002
        if self.birth_timer >= 1:
            births = int(self.birth_timer)
            self.birth_timer -= births

            for _ in range(births):
                x = self.key[0] * 3 + random.randint(0, 2)
                y = self.key[1] * 3 + random.randint(0, 2)
                world.spawn(Entity(x, y, settlement=self, settled=True))

    def handle_ideology_tick(self):
        if self.faction.identity.temperament == Temperament.AGGRESSIVE:
            self.stability -= 0.002
        elif self.faction.identity.temperament == Temperament.SPIRITUAL:
            self.stability += 0.001

    def handle_random_events(self):
        if random.random() < 0.001:
            if self.faction.identity.temperament == Temperament.SPIRITUAL:
                event_log.add(f"{self.name} celebra un rito antiguo 🕯️")
                self.fight_bonus += .1
            elif self.faction.identity.temperament == Temperament.AGGRESSIVE:
                event_log.add(f"{self.name} entrena para la guerra ⚔️")
            self.fight_bonus += .5

    def handle_land_pressure(self):
        land_pressure = self.population / max(1, len(self.territory))
        self.stability -= land_pressure * 0.002

    def tick(self, world):
        if self.faction:
            self.handle_food()
            self.handle_land_pressure()
            self.handle_reproduction(world)
            self.handle_ideology_tick()

    def symbol(self):
        return f"{self.color}{self.glyph}{RESET}"
