import random

TEMPERAMENTS = [
    "aggressive",
    "peaceful",
    "spiritual",
    "nomadic",
    "proud",
]

VALUES = [
    "honor",
    "strength",
    "memory",
    "expansion",
    "isolation",
]

MYTHS = [
    "nacieron del polvo",
    "fueron elegidos por las piedras",
    "sobrevivieron al gran silencio",
    "brotaron tras la primera muerte",
    "despertaron bajo un cielo roto",
]


def generate_identity(name):
    temperament = random.choice(TEMPERAMENTS)
    value = random.choice(VALUES)
    myth = random.choice(MYTHS)

    return {
        "temperament": temperament,
        "core_value": value,
        "myth": f"{name} {myth}",
    }
