import random

from history.identity import generate_identity


class Settlement:
    def __init__(self, key, name, born):
        self.key = key
        self.name = name
        self.born = born

        self.population = 0
        self.food = 10.0
        self.stability = 1.0

        # identidad
        self.identity = generate_identity(name)

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
                world.spawn(x, y)

        # identidad afecta estabilidad
        if self.identity["temperament"] == "aggressive":
            self.stability -= 0.002
        elif self.identity["temperament"] == "spiritual":
            self.stability += 0.001

    def symbol(self):
        if self.population < 5:
            return "▲"
        if self.population < 12:
            return "▣"
        return "⌂"
