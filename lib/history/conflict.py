import random
from enum import Enum

from lib.events.event_log import event_log
from lib.faction.faction import Faction


class ConflictState(Enum):
    COLD = 0
    SKIRMISH = 1
    WAR = 2


class Conflict:
    def __init__(self, a: Faction, b: Faction):
        self.a = a
        self.b = b
        self.intensity = 0.1

    def tick(self, world):
        self.intensity += 0.01

        diff = self.a.war_score - self.b.war_score
        attacker = self.a if diff > 0 else self.b
        defender = self.b if diff > 0 else self.a

        chance = min(0.1 + abs(diff) * 0.03, 0.5)

        if random.random() < chance:
            defender.lose_tile(world)
            event_log.add(f"{attacker.name} arrebata territorio a {defender.name} 🔥")
