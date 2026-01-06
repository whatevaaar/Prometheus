import random

import config
from entity import Entity
from events.event_log import EventLog
from history.history import History
from naming.name_generator import generate_name
from world.tile import Tile
from world.tile_type import TileType


class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.age = 0

        self.event_log = EventLog()
        self.history = History()

        self.tiles = self.generate_world()
        self.entities = []
        self.to_remove = []

        for _ in range(config.INITIAL_POP):
            x, y = self.random_floor_position()
            self.entities.append(Entity(x, y))

        self.event_log.add("El mundo despierta 🌍")

    def generate_world(self):
        tiles = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                if y < self.height // 4:
                    row.append(Tile(TileType.SURFACE))
                else:
                    row.append(Tile(TileType.ROCK) if random.random() < 0.05 else Tile(TileType.FLOOR))
            tiles.append(row)

        return tiles

    def random_floor_position(self):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.tiles[y][x].kind != TileType.ROCK:
                return x, y

    def spawn(self, x, y):
        e = Entity(x, y)
        self.entities.append(e)

        if len(self.entities) % 7 == 0:
            self.event_log.add(f"Nació {e.name} ✨")

    def tick(self):
        self.age += 1
        self.to_remove = []

        for entity in self.entities:
            entity.tick(self)

        for dead in self.to_remove:
            if dead in self.entities:
                self.entities.remove(dead)

        self.detect_population_story()
        self.detect_settlements()

        if self.age % 120 == 0:
            self.event_log.add("El mundo envejece… ⏳")

        self.history.tick(self)

    def detect_population_story(self):
        pop = len(self.entities)

        if pop > self.history.max_population:
            self.history.max_population = pop

            if pop % 10 == 0:
                self.event_log.add("La vida se multiplica sin control…")

    def detect_settlements(self):
        clusters = {}

        for e in self.entities:
            if e.settled:
                key = (e.x // 3, e.y // 3)
                clusters[key] = clusters.get(key, 0) + 1

        for key, size in clusters.items():
            if size >= 4 and not self.history.has_settlement(key):
                settlement_name = generate_name()
                self.history.register_settlement(key=key, name=settlement_name, age=self.age, )
                self.event_log.add(f"{settlement_name} ha echado raíces ▲")

    def count_entities(self, x, y):
        return sum(1 for e in self.entities if abs(e.x - x) <= 1 and abs(e.y - y) <= 1)
