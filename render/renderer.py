import pygame
from pygame import Surface

import config


class RendererBase:
    def __init__(self, screen: Surface):
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 16)
        self.big_font = pygame.font.SysFont("consolas", 22)

    @staticmethod
    def darker(color, factor=0.6):
        return tuple(int(c * factor) for c in color)

    @staticmethod
    def get_key(x, y):
        return x // config.CELL_SIZE_X, y // config.CELL_SIZE_Y
