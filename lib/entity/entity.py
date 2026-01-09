import random

import config
from geometry.point.point import get_valid_map_points_in_radius
from lib.tile.tile import Tile
from lib.utils.name_generator import generate_name


class Entity:
    __slots__ = (
        "x", "y", "name", "age", "energy", "max_age", "settled", "settle_timer", "move_cooldown", "social_satiation",
        "settlement", "_faction", "is_leader", "food_consumption", "days_without_food", "mood")

    def __init__(self, x, y, settled=False, settlement=None, faction=None):
        self.x = x
        self.y = y
        self.name = generate_name()
        self.mood: str = "calm"

        self.age = 0
        self.energy = random.randint(config.MIN_ENERGY, config.MAX_ENERGY)
        self.max_age = random.randint(config.MAX_AGE_MIN, config.MAX_AGE_MAX)

        self.settled = settled
        self.settle_timer = 0
        self.settlement = settlement

        self.move_cooldown = 0
        self.social_satiation = 0.0

        self.food_consumption = config.DAILY_FOOD_CONSUMPTION
        self.days_without_food = 0

        self._faction = None
        self.faction = faction
        self.is_leader: bool = False

    def update_mood(self, world):
        tile = world.tiles[self.y][self.x]

        if self.days_without_food >= 2:
            self.mood = "hungry"
            return

        if tile.is_border(world, self.x, self.y):
            self.mood = "afraid"
            return

        if self.energy < config.MIN_REPRO_ENERGY * 0.8:
            self.mood = "calm"
            return

        if self.settled and self.energy > config.MIN_REPRO_ENERGY * 1.5:
            self.mood = "hopeful"
            return

        self.mood = "calm"

    @property
    def faction(self):
        return self._faction

    @faction.setter
    def faction(self, f):
        if self._faction:
            self._faction.population -= 1

        self._faction = f

        if f:
            f.population += 1

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
        self.get_old()
        self.use_land(world)
        self.move(world)

        if self.will_reproduce(world):
            self.reproduce(world)

        if self.will_die():
            self.die(world)
            return

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
        if not self.days_without_food:
            if self.mood == "calm" and self.settled and random.random() < 0.8:
                return

            if self.move_cooldown > 0:
                self.move_cooldown -= 1
                return

        old_tile = world.tiles[self.y][self.x]
        old_tile.population -= 1

        self.x, self.y = self.find_closest_best_tile_for_entity(world)

        new_tile: Tile = world.tiles[self.y][self.x]
        new_tile.population += 1

        self.move_cooldown = random.randint(2, 4)

        # saciedad social
        local_density = len(world.entity_grid.get(self.get_key(), []))
        if local_density > 3:
            self.social_satiation = min(5.0, self.social_satiation + 0.2)
        else:
            self.social_satiation = max(0.0, self.social_satiation - 0.1)

    def use_land(self, world):
        tile: Tile = world.tiles[self.y][self.x]
        neighbors = len(world.entity_grid.get(self.get_key(), []))

        if tile.food_yield() > 0.15 and (neighbors >= 3 or self.age < 20):
            self.settle_timer += 1
        else:
            self.settle_timer = max(0, self.settle_timer - 1)

        if self.settle_timer > 5:
            self.settled = True

        if tile.food > 0:
            tile.food -= 1
            tile.work()
            if not self.faction:
                self.faction = tile.owner

        else:
            self.days_without_food += 1

    def will_reproduce(self, world) -> bool:
        if self.age < config.MIN_REPRO_AGE or self.energy < config.MIN_REPRO_ENERGY:
            return False

        settlement = world.find_settlement_at_position(self.x, self.y)
        bonus = 2.0 if settlement else 1.0 + (1 if self.mood == "hopeful" else 0)
        return random.random() < config.REPRO_CHANCE * bonus

    def reproduce(self, world):
        self.energy -= config.REPRO_COST

        tile: Tile = world.tiles[self.y][self.x]
        tile.food += 1
        x, y = self.find_closest_best_tile_for_entity(world=world)
        world.spawn(Entity(x, y, settled=self.settled))

        settlement = world.find_settlement_at_position(x, y)
        if settlement:
            settlement.stability += 0.03

    def will_die(self) -> bool:
        return self.energy <= 0 or self.age >= self.max_age or self.days_without_food >= config.MAX_DAY_WITHOUT_FOOD

    def die(self, world):
        world.to_remove.add(self)
        if self.faction:
            self.faction.population -= 1
        old_tile = world.tiles[self.y][self.x]
        old_tile.population = max(0, old_tile.population - 1)

    def find_closest_best_tile_for_entity(self, world) -> tuple:
        best_position = self.x, self.y
        best_score = -999

        possible_positions = []

        for nx, ny in get_valid_map_points_in_radius(self.x, self.y, 1):

            potential_tile: Tile = world.tiles[ny][nx]

            if not potential_tile.can_move():
                continue

            elif potential_tile.is_fully_populated:
                possible_positions.append((nx, ny))
                continue

            key = (nx // config.CELL_SIZE_X, ny // config.CELL_SIZE_Y)
            density = world.grid_densities.get(key, 0)
            energy = potential_tile.food_yield()

            score = (energy + density * (1.1 - self.social_satiation * 0.15) + random.uniform(-0.3, 0.3))

            if score > best_score:
                best_score = score
                best_position = nx, ny
        if best_position == (self.x, self.y) and possible_positions:
            return random.choice(possible_positions)

        return best_position

    def get_key(self):
        return self.x // config.CELL_SIZE_X, self.y // config.CELL_SIZE_Y
