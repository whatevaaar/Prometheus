from enum import Enum, auto


class ConflictState(Enum):
    COLD = auto()
    SKIRMISH = auto()
    WAR = auto()


from lib.events.event_log import event_log
from lib.faction.faction import Faction


class Conflict:
    __slots__ = ("a", "b", "progress")

    def __init__(self, a: Faction, b: Faction):
        self.a = a
        self.b = b
        self.progress = 0.0  # progreso global narrativo (opcional)

    def tick(self, world):
        """
        Cada tick:
        - se evalúan tiles frontera entre A y B
        - cada tile progresa hacia uno de los dos lados
        """

        # diferencia de fuerza (determinista)
        score_a = self.a.war_score
        score_b = self.b.war_score

        if score_a == score_b:
            return  # estancamiento real, no random

        winner = self.a if score_a > score_b else self.b
        loser = self.b if winner is self.a else self.a

        pressure = abs(score_a - score_b)
        delta = 0.05 * min(pressure, 5)  # clamp para no explotar el mapa

        for tile in world.border_tiles():
            if tile.owner not in (self.a, self.b):
                continue

            neighbor_owner = world.get_neighbor_owner(tile)
            if neighbor_owner not in (self.a, self.b):
                continue

            # marcamos la tile como en conflicto
            tile.conflict = self
            tile.conflict_progress = getattr(tile, "conflict_progress", 0.0)

            # avanzar o retroceder progreso
            if tile.owner == winner:
                tile.conflict_progress += delta
            else:
                tile.conflict_progress -= delta

            # resolución
            if tile.conflict_progress >= 1.0:
                self.capture(tile, winner, loser)

            elif tile.conflict_progress <= -1.0:
                self.capture(tile, loser, winner)

    @staticmethod
    def capture(tile, winner, loser):
        tile.owner = winner
        tile.conflict = None
        tile.conflict_progress = 0.0

        event_log.add(f"{winner.name} toma territorio a {loser.name} ⚔️")
