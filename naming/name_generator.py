import random

PREFIXES = ["Ka", "Ur", "Na", "Shi", "Lo", "Va", "Te", "Mo", "A", ]

ROOTS = ["ram", "thal", "nok", "ira", "sen", "mur", "esh", "ka", ]

SUFFIXES = ["a", "en", "ul", "ir", "os", "um", "eth", "", ]


def generate_name():
    return (random.choice(PREFIXES) + random.choice(ROOTS) + random.choice(SUFFIXES))
