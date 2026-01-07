import config


def in_bounds(x, y):
    return x <= config.WIDTH and y <= config.HEIGHT
