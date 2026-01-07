import random

from lib.world.tile_type import TileType

TILE_BASE_COLORS = {TileType.FLOOR: (90, 120, 70), TileType.SURFACE: (120, 140, 90), TileType.ROCK: (80, 80, 80),
                    TileType.WATER: (40, 90, 140), }

FACTION_PALETTE = [(180, 80, 80),  # rojo viejo
                   (80, 140, 90),  # verde apagado
                   (90, 110, 160),  # azul gris
                   (170, 150, 90),  # ocre
                   (140, 90, 140),  # púrpura viejo
                   (90, 130, 130),  # teal apagado
                   ]


def get_random_faction_color() -> tuple:
    return random.choice(FACTION_PALETTE)


def base_color(tile):
    return TILE_BASE_COLORS[tile.kind]
