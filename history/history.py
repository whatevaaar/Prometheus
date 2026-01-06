from collections import defaultdict

from events.event_log import event_log
from history.conflict import Conflict
from history.settlement import Settlement


class History:
    def __init__(self):
        self.events = []  # eventos narrativos importantes
        self.eras = []  # periodos del mundo
        self.stats = defaultdict(int)
        self.settlements = {}
        self.max_population = 0
        self.conflicts = []

        self.current_era = {"name": "La Era del Despertar", "start": 0, "traits": set(), }

    def tick(self, world):
        # cambios lentos, no cada frame
        self.detect_era_shift(world)
        for conflict in self.conflicts:
            conflict.tick(world)

    def add_event(self, text, age):
        self.events.append({"age": age, "text": text, })
        event_log.add()

    def detect_era_shift(self, world):
        pop = len(world.entities)

        traits = set()
        if pop < 3:
            traits.add("casi_extinción")
        if pop > 15:
            traits.add("abundancia")
        if pop > 30:
            traits.add("expansión")

        if traits != self.current_era["traits"]:
            self.end_current_era(world.age)
            self.start_new_era(traits, world.age)

    def start_new_era(self, traits, age):
        name = self.name_era(traits)
        self.current_era = {"name": name, "start": age, "traits": traits, }

    def end_current_era(self, age):
        self.current_era["end"] = age
        self.eras.append(self.current_era)

    @staticmethod
    def name_era(traits):
        if "casi_extinción" in traits:
            return "La Era del Silencio"
        if "expansión" in traits:
            return "La Era del Crecimiento"
        if "abundancia" in traits:
            return "La Era Fértil"
        return "La Era Incierta"

    def has_settlement(self, key):
        return key in self.settlements

    def register_settlement(self, key, name, age):
        self.settlements[key] = Settlement(key, name, age)

    def start_conflict(self, a, b):
        for c in self.conflicts:
            if (c.a == a and c.b == b) or (c.a == b and c.b == a):
                return

        conflict = Conflict(a, b)
        self.conflicts.append(conflict)
