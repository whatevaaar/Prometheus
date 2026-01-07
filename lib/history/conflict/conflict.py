import random
from enum import Enum, auto

from lib.events.event_log import event_log
from lib.faction.faction import Faction


class ConflictState(Enum):
    COLD = auto()
    SKIRMISH = auto()
    WAR = auto()


class Conflict:
    __slots__ = ["a", "b", "intensity"]

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

