import config


def get_key(x, y):
    return x // config.CELL_SIZE_X, y // config.CELL_SIZE_Y
