import random

import config
from naming.name_generator import generate_name
from world.tile import Tile
from world.tile_type import TileType


class Entity:
    __slots__ = (
        "x", "y", "name", "age", "energy", "max_age", "settled", "settle_timer", "move_cooldown", "social_satiation",
        "settlement")

    def __init__(self, x, y, settled=False, settlement=None):
        self.x = x
        self.y = y

        self.name = generate_name()

        self.age = 0
        self.energy = random.randint(config.MIN_ENERGY, config.MAX_ENERGY)
        self.max_age = random.randint(config.MAX_AGE_MIN, config.MAX_AGE_MAX)

        self.settled = settled
        self.settle_timer = 0
        self.settlement = settlement

        self.move_cooldown = 0
        self.social_satiation = 0.0

    # ──────────────────────────────
    # Representación
    # ──────────────────────────────
    def symbol(self):
        if self.settlement:
            return self.settlement.color + self.settlement.glyph + "\033[0m"

        if self.age < 10:
            return "o"
        elif self.age < self.max_age * 0.7:
            return "O"
        else:
            return "Ω"

    # ──────────────────────────────
    # Ciclo principal
    # ──────────────────────────────
    def tick(self, world):
        self.use_land(world)
        self.get_old()
        self.move(world)

        if self.will_die():
            self.die(world)
            return

        if self.will_reproduce(world):
            self.reproduce(world)

    # ──────────────────────────────
    # Envejecimiento
    # ──────────────────────────────
    def get_old(self):
        self.age += 1
        self.energy -= (config.REST_ENERGY_DECAY if self.settled else config.MOVE_ENERGY_DECAY)

    # ──────────────────────────────
    # Movimiento (usando grid)
    # ──────────────────────────────
    def move(self, world):
        if self.settled and random.random() < 0.8:
            return

        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        old_tile = world.tiles[self.y][self.x]
        old_tile.population = max(0, old_tile.population - 1)

        self.x, self.y = self.find_closest_best_tile_for_entity(world)

        new_tile: Tile = world.tiles[self.y][self.x]
        new_tile.increase_population(1)

        self.move_cooldown = random.randint(2, 4)

        # saciedad social
        local_density = len(world.entity_grid.get((self.x // 3, self.y // 3), []))
        if local_density > 3:
            self.social_satiation = min(5.0, self.social_satiation + 0.2)
        else:
            self.social_satiation = max(0.0, self.social_satiation - 0.1)

    # ──────────────────────────────
    # Asentamiento
    # ──────────────────────────────
    def use_land(self, world):
        tile: Tile = world.tiles[self.y][self.x]
        neighbors = len(world.entity_grid.get((self.x // 3, self.y // 3), []))

        if tile.food_yield() > 0.15 and neighbors >= 3 and self.age > 15:
            self.settle_timer += 1
        else:
            self.settle_timer = max(0, self.settle_timer - 1)

        if self.settle_timer > 5:
            self.settled = True

        if random.random() < 0.3:
            self.energy += tile.food_yield()

    # ──────────────────────────────
    # Reproducción
    # ──────────────────────────────
    def will_reproduce(self, world) -> bool:
        if self.age < config.MIN_REPRO_AGE or self.energy < config.MIN_REPRO_ENERGY:
            return False

        settlement = world.get_settlement_at(self.x, self.y)
        bonus = 2.0 if settlement else 1.0
        return random.random() < config.REPRO_CHANCE * bonus

    def reproduce(self, world):
        self.energy -= config.REPRO_COST

        tile: Tile = world.tiles[self.y][self.x]
        tile.increase_population(1)
        nx, ny = self.find_closest_best_tile_for_entity(world=world)
        world.spawn(Entity(x=nx, y=ny, settled=self.settled))

        settlement = world.get_settlement_at(self.x, self.y)
        if settlement:
            settlement.stability += 0.03

    def will_die(self) -> bool:
        return self.energy <= 0 or self.age >= self.max_age

    def die(self, world):
        world.to_remove.add(self)
        old_tile = world.tiles[self.y][self.x]
        old_tile.population = max(0, old_tile.population - 1)

    def find_closest_best_tile_for_entity(self, world):
        best_x, best_y = self.x, self.y
        best_score = -999

        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)):
            nx, ny = self.x + dx, self.y + dy
            if not (0 <= nx < world.width and 0 <= ny < world.height):
                continue

            potential_tile: Tile = world.tiles[ny][nx]

            if potential_tile.kind == TileType.ROCK:
                continue
            if potential_tile.is_fully_populated:
                continue

            key = (nx // 3, ny // 3)
            density = world.grid_densities.get(key, 0)
            energy = potential_tile.food_yield()

            score = (energy + density * (1.1 - self.social_satiation * 0.15) + random.uniform(-0.3, 0.3))

            if score > best_score:
                best_score = score
                best_x, best_y = nx, ny

        return best_x, best_y
