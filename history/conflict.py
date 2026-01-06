import random
from enum import Enum

import config
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
        a = self.a
        b = self.b

        a_adv = a.war_advantage_against(b)
        b_adv = 1.0 - a_adv

        if random.random() < config.BASE_HIT * a_adv:
            b.lose_border_tile(world)

        if random.random() < config.BASE_HIT * b_adv:
            a.lose_border_tile(world)
