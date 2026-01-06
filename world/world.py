import random
from collections import defaultdict

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

        # índice espacial CLAVE
        self.entity_grid = defaultdict(list)

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
        self.entities.append(Entity(x, y))

    def rebuild_entity_grid(self):
        self.entity_grid.clear()
        for e in self.entities:
            key = (e.x // 3, e.y // 3)
            self.entity_grid[key].append(e)

    def tick(self):
        self.age += 1
        self.to_remove = []

        # grid espacial (1 vez por tick)
        self.rebuild_entity_grid()

        for entity in self.entities:
            entity.tick(self)

        for dead in self.to_remove:
            if dead in self.entities:
                self.entities.remove(dead)

        self.detect_population_story()
        self.detect_settlements()
        self.detect_conflicts()

        if self.age % 120 == 0:
            self.event_log.add("El mundo envejece… ⏳")

        # lógica por settlement (no por entidad)
        for settlement in self.history.settlements.values():
            settlement.tick(self)

        self.history.tick(self)

    def detect_population_story(self):
        pop = len(self.entities)
        if pop > self.history.max_population:
            self.history.max_population = pop
            if pop % 50 == 0:
                self.event_log.add("La vida se multiplica sin control…")

    def detect_settlements(self):
        for key, members in self.entity_grid.items():
            if len(members) >= config.SETTLEMENT_MIN_MEMBERS:
                if not self.history.has_settlement(key):
                    name = generate_name()
                    self.history.register_settlement(key, name, self.age)
                    self.event_log.add(f"{name} ha echado raíces ▲")

                settlement = self.history.settlements[key]
                settlement.population = len(members)

                for e in members:
                    e.settled = True

    def detect_conflicts(self):
        settlements = list(self.history.settlements.values())

        for s in settlements:
            x, y = s.key
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                other = self.history.settlements.get((x + dx, y + dy))
                if other:
                    self.handle_settlement_tension(s, other)

    def handle_settlement_tension(self, a, b):
        pressure = min(a.population, b.population) * 0.001
        a.stability -= pressure
        b.stability -= pressure

        if random.random() < 0.01:
            self.event_log.add(f"Tensión entre {a.name} y {b.name} ⚔️")

        if a.stability <= 0:
            self.collapse_settlement(a)
        if b.stability <= 0:
            self.collapse_settlement(b)

    def collapse_settlement(self, settlement):
        self.event_log.add(f"{settlement.name} se fragmenta en el caos 💥")

        members = self.entity_grid.get(settlement.key, [])
        for e in members:
            if random.random() < 0.4:
                self.to_remove.append(e)
            else:
                e.settled = False

        del self.history.settlements[settlement.key]

    def get_settlement_at(self, x, y):
        key = (x // 3, y // 3)
        return self.history.settlements.get(key)

