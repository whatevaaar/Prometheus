import random
from collections import defaultdict
from typing import Optional

import config
from geometry.point.point import is_in_world
from lib.entity.entity import Entity
from lib.events.event_log import event_log
from lib.history.history import History
from lib.settlement.settlement import Settlement
from lib.tile.tile import Tile
from lib.tile.tile_type import TileType
from lib.utils.name_generator import generate_name


class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.age = 0
        self.history = History()
        self.tiles = self.generate_world()
        self.entities = []

        self.settlements = []
        # Guardaremos los muertos en un set para búsqueda O(1)
        self.to_remove = set()
        self.entity_grid = defaultdict(list)
        # Caché de densidades para evitar que cada entidad haga len() constantemente
        self.grid_densities = {}

        for _ in range(config.INITIAL_POP):
            x, y = self.random_floor_position()
            self.entities.append(Entity(x, y))

        event_log.add("El mundo despierta 🌍")

    def generate_world(self) -> list:
        tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                r = random.random()
                if r < 0.05:
                    kind = TileType.ROCK
                else:
                    kind = TileType.FLOOR
                row.append(Tile(kind, x, y))
            tiles.append(row)

        # =========================
        # RÍOS
        # =========================
        for _ in range(config.RIVERS):
            self.carve_river(tiles)

        return tiles

    def rebuild_entity_grid(self):
        self.entity_grid.clear()
        self.grid_densities.clear()

        # Optimización: Variable local para el acceso rápido
        grid = self.entity_grid
        for e in self.entities:
            key = (e.x // 3, e.y // 3)
            grid[key].append(e)

        # Pre-calculamos la densidad de cada celda una sola vez por tick
        for key, members in grid.items():
            self.grid_densities[key] = len(members)

    def tick(self):
        self.age += 1
        self.to_remove = set()  # Usar set es vital para el rendimiento

        self.rebuild_entity_grid()

        for entity in self.entities:
            entity.tick(self)

        if self.to_remove:
            self.entities = [e for e in self.entities if e not in self.to_remove]
            self.to_remove.clear()

        # 3. Lógica global
        self.detect_population_story()
        self.detect_possible_settlements()

        # 4. Lógica de asentamientos
        self.history.tick(self)

    def spawn(self, entity: Entity) -> None:
        self.entities.append(entity)

    def detect_possible_settlements(self):
        clusters = defaultdict(list)
        for e in self.entities:
            if e.settled:
                clusters[(e.x // 3, e.y // 3)].append(e)

        for key, members in clusters.items():
            settlement = self.create_settlement_if_possible(key, members)
            if settlement and not settlement.faction:
                self.settlements.append(settlement)
                self.handle_new_faction(members, settlement)

    def collapse_settlement(self, settlement):
        event_log.add(f"{settlement.name} se fragmenta en el caos 💥")
        members = self.entity_grid.get(settlement.key, [])
        for e in members:
            if random.random() < 0.4:
                self.to_remove.add(e)  # O(1)
            else:
                e.settled = False
                e.settlement = None  # Limpiar referencia

        if settlement.key in self.history.settlements:
            del self.history.settlements[settlement.key]

    def random_floor_position(self):
        # Lógica sin cambios, es eficiente para inicialización
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.tiles[y][x].kind != TileType.ROCK:
                return x, y

    def get_settlement_at(self, x, y) -> Settlement:
        return self.history.settlements.get((x // 3, y // 3))

    def detect_population_story(self):
        pop = len(self.entities)
        if pop > self.history.max_population:
            self.history.max_population = pop
            # Usar % para eventos grandes evita saturar el log
            if pop % 500 == 0:
                event_log.add(f"La población ha alcanzado los {pop} seres...")

    def create_settlement_if_possible(self, key, members) -> Optional[Settlement]:
        num_members = len(members)
        if num_members < config.SETTLEMENT_MIN_MEMBERS:
            return None

        if not self.history.has_settlement(key):
            px, py = members[0].x, members[0].y
            if not is_in_world(px, py):
                print(f"QUE PASÖ AQUIIII: {members[0]}")
                return None
            new_settlement = Settlement(key, generate_name(), self.age, self.tiles[py][px])
            self.history.register_settlement(key, new_settlement)

        settlement = self.history.settlements[key]
        settlement.population = num_members
        for e in members:
            e.settlement = settlement

        return settlement

    def handle_new_faction(self, members: list, settlement: Settlement):
        leader = random.choice(members)
        faction = self.history.create_faction(leader)
        settlement.faction = faction
        faction.settlements.add(settlement)

        # asignar tile inicial
        sx, sy = settlement.key
        faction.tiles.add((sx, sy))
        self.tiles[sy][sx].owner = faction

        for e in members:
            e.faction = faction

    def carve_river(self, tiles):
        if random.random() < 0.5:
            x = random.randint(0, self.width - 1)
            y = 0
            dx, dy = 0, 1
        else:
            x = 0
            y = random.randint(0, self.height - 1)
            dx, dy = 1, 0

        length = random.randint(self.width // 2, self.width + self.height)

        for _ in range(length):
            if not (0 <= x < self.width and 0 <= y < self.height):
                break

            tiles[y][x].kind = TileType.WATER

            # pequeñas variaciones para que serpentee
            if random.random() < 0.3:
                dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), ])

            x += dx
            y += dy

    def find_settlement_at_position(self, x: int, y: int) -> Optional[Settlement]:
        key = (x // 3, y // 3)
        return self.history.settlements.get(key)
