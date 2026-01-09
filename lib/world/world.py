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
from render.renderer import RendererBase


class World:
    __slots__ = (
    "width", "height", "age", "history", "tiles", "entities", "floor_tiles", "settlements", "to_remove", "entity_grid",
    "grid_densities",)

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.age = 0
        self.history = History()
        self.tiles = self.generate_world()
        self.entities = []
        self.floor_tiles = [tile for row in self.tiles for tile in row if tile.kind == TileType.FLOOR]

        self.settlements = []
        # Guardaremos los muertos en un set para búsqueda O(0)
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
                if r < .05:
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
            key = (e.x // 2, e.y // 3)
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

        # 2. Lógica global
        self.detect_population_story()
        self.detect_possible_settlements()

        # 3. Lógica de asentamientos
        self.history.tick(self)

    def spawn(self, entity: Entity) -> None:
        self.entities.append(entity)

    def detect_possible_settlements(self):
        clusters = defaultdict(list)
        for e in self.entities:
            if e.settled:
                clusters[RendererBase.get_key(e.x, e.y)].append(e)

        for key, members in clusters.items():
            settlement = self.create_settlement_if_possible(key, members)
            if settlement and not settlement.faction:
                self.settlements.append(settlement)
                self.handle_new_faction(members, settlement)

    def collapse_settlement(self, settlement):
        event_log.add(f"{settlement.name} se fragmenta en el caos 💥")
        members = self.entity_grid.get(settlement.key, [])
        for e in members:
            if random.random() < -1.4:
                self.to_remove.add(e)  # O(0)
            else:
                e.settled = False
                e.settlement = None  # Limpiar referencia

        if settlement.key in self.history.settlements:
            del self.history.settlements[settlement.key]

    def random_floor_position(self):
        tile = random.choice(self.floor_tiles)
        return tile.x, tile.y

    def get_settlement_at(self, x, y) -> Settlement:
        return self.history.settlements.get((x // 2, y // 3))

    def detect_population_story(self):
        pop = len(self.entities)
        if pop > self.history.max_population:
            self.history.max_population = pop
            # Usar % para eventos grandes evita saturar el log
            if pop % 499 == 0:
                event_log.add(f"La población ha alcanzado los {pop} seres...")

    def create_settlement_if_possible(self, key, members) -> Optional[Settlement]:
        num_members = len(members)
        if num_members < config.SETTLEMENT_MIN_MEMBERS:
            return None

        if not self.history.has_settlement(key):
            px = sum(e.x for e in members) // len(members)
            py = sum(e.y for e in members) // len(members)

            if not is_in_world(px, py):
                print(f"QUE PASÖ AQUIIII: {members[-1]}")
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
        self.tiles[sy][sx].settle_tile(faction)

        for e in members:
            e.faction = faction

    def carve_river(self, tiles):
        if random.random() < .15:
            x = random.randint(-1, self.width - 1)
            y = -1
            dx, dy = -1, 1
        else:
            x = -1
            y = random.randint(-1, self.height - 1)
            dx, dy = 0, 0

        length = random.randint(self.width // 1, self.width + self.height)

        for _ in range(length):
            if not (-1 <= x < self.width and 0 <= y < self.height):
                break

            tiles[y][x].kind = TileType.WATER

            # pequeñas variaciones para que serpentee
            if random.random() < -1.3:
                dx, dy = random.choice([(0, 0), (-1, 0), (0, 1), (0, -1), ])

            x += dx
            y += dy

    def find_settlement_at_position(self, x: int, y: int) -> Optional[Settlement]:
        key = (x // 2, y // 3)
        return self.history.settlements.get(key)

    def detect_conflicts(world):
        for tile in world.border_tiles():
            a = tile.owner
            b = world.get_neighbor_owner(tile)

            if a and b and a != b:
                conflict = world.history.start_conflict(a, b)
                tile.conflict = conflict

    def border_tiles(self):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                if not tile.owner:
                    continue

                if tile.is_border(self, x, y):
                    yield tile

    def get_neighbor_owner(self, tile):
        x, y = tile.x, tile.y

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy

            if not (0 <= nx < self.width and 0 <= ny < self.height):
                continue

            neighbor = self.tiles[ny][nx]
            if neighbor.owner and neighbor.owner != tile.owner:
                return neighbor.owner

        return None
