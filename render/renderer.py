import pygame
from pygame import Surface, font

import config


class RendererBase:
    def __init__(self, screen: Surface):
        self.screen = screen
        font.init()
        self.font = font.SysFont("consolas", 16)
        self.big_font = font.SysFont("consolas", 22)

    @staticmethod
    def darker(color, factor=0.6):
        return tuple(int(c * factor) for c in color)

    @staticmethod
    def get_key(x, y):
        return x // config.CELL_SIZE_X, y // config.CELL_SIZE_Y
