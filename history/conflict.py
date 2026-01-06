from enum import Enum
import random

from history.settlement import Settlement


class ConflictState(Enum):
    COLD = 0
    SKIRMISH = 1
    WAR = 2


class Conflict:
    def __init__(self, a, b):
        self.a: Settlement = a
        self.b: Settlement = b
        self.state = ConflictState.COLD
        self.intensity = 0.1

    def tick(self, world):
        self.intensity += 0.01

        if self.intensity > 0.5:
            self.state = ConflictState.SKIRMISH
        if self.intensity > 1.2:
            self.state = ConflictState.WAR

        if self.state == ConflictState.WAR:
            self.apply_war(world)

    def apply_war(self, world):
        # daño territorial ligero
        if random.random() < 0.05:
            self.b.lose_border_tile(world)
