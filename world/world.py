import random
from collections import defaultdict

import config
from entity.entity import Entity
from events.event_log import event_log
from history.history import History
from history.settlement import Settlement
from naming.name_generator import generate_name
from world.tile import Tile
from world.tile_type import TileType


class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.age = 0
        self.history = History()
        self.tiles = self.generate_world()
        self.entities = []

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
        return [[Tile(TileType.ROCK) if random.random() < 0.05 else Tile(TileType.FLOOR) for _ in range(self.width)] for
                _ in range(self.height)]

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
        self.detect_settlements()
        self.detect_conflicts()

        # 4. Lógica de asentamientos
        history_settlements = self.history.settlements.values()
        for settlement in history_settlements:
            settlement.tick(self)

        self.history.tick(self)

    def spawn(self, entity: Entity) -> None:
        self.entities.append(entity)

    def detect_settlements(self):
        clusters = defaultdict(list)
        for e in self.entities:
            if e.settled:
                clusters[(e.x // 3, e.y // 3)].append(e)

        for key, members in clusters.items():
            num_members = len(members)
            if num_members < config.SETTLEMENT_MIN_MEMBERS:
                continue

            if not self.history.has_settlement(key):
                name = generate_name()
                self.history.register_settlement(key, name, self.age)
                s = self.history.settlements[key]
                event_log.add(f"{name} ha echado raíces {s.glyph}")

            settlement = self.history.settlements[key]
            settlement.population = num_members
            for e in members:
                e.settlement = settlement

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

    def get_settlement_at(self, x, y):
        return self.history.settlements.get((x // 3, y // 3))

    def detect_population_story(self):
        pop = len(self.entities)
        if pop > self.history.max_population:
            self.history.max_population = pop
            # Usar % para eventos grandes evita saturar el log
            if pop % 500 == 0:
                event_log.add(f"La población ha alcanzado los {pop} seres...")

    def detect_conflicts(self):
        settlements = list(self.history.settlements.values())

        for i, a in enumerate(settlements):
            for b in settlements[i + 1:]:
                if self.should_conflict(a, b):
                    self.history.start_conflict(a, b)

    @staticmethod
    def should_conflict(a: Settlement, b: Settlement):
        if a == b:
            return False

        border = a.is_neighbor(b)
        if not border:
            return False

        tension = (a.ideology_score + b.ideology_score)

        return tension > config.CONFLICT_THRESHOLD
