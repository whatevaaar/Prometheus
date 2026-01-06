from collections import defaultdict

from history.settlement import Settlement


class History:
    def __init__(self):
        self.events = []  # eventos narrativos importantes
        self.eras = []  # periodos del mundo
        self.stats = defaultdict(int)
        self.settlements = {}
        self.max_population = 0

        self.current_era = {"name": "La Era del Despertar", "start": 0, "traits": set(), }

    def tick(self, world):
        # cambios lentos, no cada frame
        self.detect_era_shift(world)

    def add_event(self, text, age):
        self.events.append({"age": age, "text": text, })

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

    def name_era(self, traits):
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
