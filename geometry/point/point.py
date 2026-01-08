from random import randint

import config

OFFSETS_1 = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def is_in_world(x, y) -> bool:
    return 0 <= x < config.WIDTH and 0 <= y < config.HEIGHT


def is_on_screen(x, y) -> bool:
    return 0 <= x < config.SCREEN_W and 0 <= y < config.SCREEN_H


def is_on_world_view(x, y) -> bool:
    world_px_h = config.HEIGHT * config.TILE_SIZE

    return 0 <= x < config.SCREEN_W and 0 <= y < world_px_h


def clamp_to_world(x, y):
    x = max(0, min(x, config.WIDTH - 1))
    y = max(0, min(y, config.HEIGHT - 1))


def get_points_in_radius(x, y, radius: int) -> list:
    points = []

    offset = OFFSETS_1 if (radius == 1) else [(-radius, 0), (radius, 0), (0, -radius), (0, radius)]

    for dx, dy in offset:
        points.append((x + dx, y + dy))

    return points


def get_valid_map_points_in_radius(x, y, radius: int):
    points_in_radius = get_points_in_radius(x, y, radius)
    return [(px, py) for (px, py) in points_in_radius if is_in_world(px, py)]


def get_random_point_in_radius(x, y, radius) -> tuple:
    px = x + randint(0, radius)
    py = y + randint(0, radius)
    return px, py


def get_entity_screen_pos(e, anim, tile_px) -> tuple:
    cx = int((e.x + config.ENTITY_CENTER + anim["offset_x"]) * tile_px)
    cy = int((e.y + config.ENTITY_CENTER + anim["offset_y"]) * tile_px)
    return cx, cy
