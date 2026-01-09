import random

from lib.tile.tile_type import TileType

TILE_BASE_COLORS = {TileType.FLOOR: (90, 120, 70), TileType.SURFACE: (120, 140, 90), TileType.ROCK: (80, 80, 80),
                    TileType.WATER: (40, 90, 140), }

FACTION_PALETTE = [(110, 85, 65),  # marrón profundo
    (95, 95, 95),  # gris medio
    (130, 115, 90),  # ocre gris
    (125, 90, 125),  # púrpura seco
    (150, 140, 130),  # hueso
    (105, 90, 75),  # tierra húmeda
]


def get_random_faction_color() -> tuple:
    return random.choice(FACTION_PALETTE)


def base_color(tile):
    return TILE_BASE_COLORS[tile.kind]
