from lib.faction.faction import Faction


def choose_target_tile(attacker: Faction, defender: Faction):
    candidates = [t for t in defender.border_tiles() if t.food_yield() > 0]
    return max(candidates, key=lambda t: t.food_yield(), default=None)
