import random
from enum import Enum, auto


class Temperament(Enum):
    AGGRESSIVE = auto()
    PEACEFUL = auto()
    SPIRITUAL = auto()
    NOMADIC = auto()
    PROUD = auto()


class ValueType(Enum):
    HONOR = auto()
    STRENGTH = auto()
    MEMORY = auto()
    EXPANSION = auto()
    ISOLATION = auto()


class MythType(Enum):
    DUST = "nacieron del polvo"
    STONES = "fueron elegidos por las piedras"
    SILENCE = "sobrevivieron al gran silencio"
    FIRST_DEATH = "brotaron tras la primera muerte"
    BROKEN_SKY = "despertaron bajo un cielo roto"


class Identity:
    __slots__ = ("temperament", "value", "myth",)

    def __init__(self):
        self.temperament: Temperament = random.choice(tuple(Temperament))
        self.value: ValueType = random.choice(tuple(ValueType))
        self.myth: MythType = random.choice(tuple(MythType))
