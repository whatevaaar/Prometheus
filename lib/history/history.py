from collections import defaultdict

from lib.events.event_log import event_log
from lib.faction.faction import Faction
from lib.history.conflict import Conflict
from lib.history.identity import Temperament


def create_new_faction_log(f: Faction):
    if f.identity.temperament == Temperament.AGGRESSIVE:
        adjective = "valiente"

    elif f.identity.temperament == Temperament.SPIRITUAL:
        adjective = "sagrado"

    elif f.identity.temperament == Temperament.NOMADIC:
        adjective = "libre"

    elif f.identity.temperament == Temperament.PROUD:
        adjective = "orgulloso"
    else:
        adjective = "misterioso"

    event_log.add(f"Ha nacido el {adjective} pueblo de {f.name} {f.glyph}")


class History:
    def __init__(self):
        self.events = []  # eventos narrativos importantes
        self.eras = []  # periodos del mundo
        self.stats = defaultdict(int)
        self.settlements = {}
        self.max_population = 0
        self.conflicts = []
        self.factions = []

        self.current_era = {"name": "La Era del Despertar", "start": 0, "traits": set(), }

    def tick(self, world):
        # cambios lentos, no cada frame
        for faction in self.factions[:]:
            faction.tick(world)

        for conflict in self.conflicts[:]:
            conflict.tick(world)

        for settlement in self.settlements.values():
            settlement.tick(world)

        self.detect_era_shift(world)

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
        event_log.add(f"Empieza {name} en el {age}")

    def end_current_era(self, age):
        self.current_era["end"] = age
        self.eras.append(self.current_era)
        event_log.add(f"Termina {self.current_era.get("name", "")} en el {age}")

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

    def register_settlement(self, key, new_settlement):
        self.settlements[key] = new_settlement
        event_log.add(f"Las entidades se asientan en {new_settlement.name}")

    def start_conflict(self, faction_a, faction_b):
        conflict = Conflict(faction_a, faction_b)
        self.conflicts.append(conflict)

    def create_faction(self, leader):
        name = leader.name if hasattr(leader, "name") else "Los Sin Nombre"
        faction = Faction(name, leader)
        self.factions.append(faction)
        event_log.add(f"Nace la facción de {name}")
        create_new_faction_log(faction)
        return faction

    def remove_faction(self, faction):
        if faction in self.factions:
            self.factions.remove(faction)
