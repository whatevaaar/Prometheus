import random

import config
from naming.name_generator import generate_name


class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.name = generate_name()

        # Life and energy
        self.age = 0
        self.energy = random.randint(config.MIN_ENERGY, config.MAX_ENERGY)
        self.max_age = random.randint(config.MAX_AGE_MIN, config.MAX_AGE_MAX)

        # Settle
        self.settled = False
        self.settle_timer = 0

    def symbol(self):
        if self.age < 10:
            return config.SYMBOL_YOUNG
        if self.settled:
            return config.SYMBOL_SETTLED
        if self.age < self.max_age * 0.7:
            return config.SYMBOL_ADULT
        return config.SYMBOL_OLD

    def tick(self, world):
        self.use_land(world)

        self.get_old()

        self.move(world)
        # Le morte
        if self.will_die():
            self.die(world)
            return

        if self.will_reproduce():
            self.reproduce(world)

    def get_old(self):
        self.age += 1
        if self.settled:
            self.energy -= config.REST_ENERGY_DECAY
        else:
            self.energy -= config.MOVE_ENERGY_DECAY

    def move(self, world):
        if self.settled and random.random() < 0.8:
            return  # se queda, descansa

        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)])

        nx, ny = self.x + dx, self.y + dy

        if 0 <= nx < world.width and 0 <= ny < world.height:
            if world.tiles[ny][nx].kind != "rock":
                self.x, self.y = nx, ny

    # Reproducción
    def will_reproduce(self) -> bool:
        return self.age >= config.MIN_REPRO_AGE and self.energy >= config.MIN_REPRO_ENERGY

    def reproduce(self, world):
        pop_factor = max(0.1, 1 - len(world.entities) / config.SOFT_POP_CAP)

        if random.random() < config.REPRO_CHANCE * pop_factor:
            self.energy -= config.REPRO_COST
            world.spawn(self.x, self.y)

    # Muerte
    def will_die(self) -> bool:
        return self.energy <= 0 or self.age >= self.max_age

    def die(self, world):
        world.to_remove.append(self)
        if self.age > self.max_age * 0.9:
            world.event_log.add(f"{self.name} se apaga 💀")
            world.event_log.add("Un ser antiguo se apaga 💀")

    def use_land(self, world):
        tile = world.tiles[self.y][self.x]
        neighbors = world.count_entities(self.x, self.y)
        if tile.energy_yield() > 0.15 and neighbors <= 3 and self.age > 15:
            self.settle_timer += 1
        else:
            self.settle_timer = max(0, self.settle_timer - 1)

        if self.settle_timer > 10:
            self.settled = True

        if random.random() < 0.3:
            self.energy += tile.energy_yield()
