import pygame
from pygame import Surface

class UIRenderer:
    def __init__(self, screen: Surface):
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 18)

    def draw(self, paused: bool, tick_speed: int):
        """Dibuja estado de pausa y velocidad en pantalla"""
        status_text = "PAUSA" if paused else "RUN"
        speed_text = f"Velocidad: {tick_speed}"
        text_surface = self.font.render(f"{status_text} | {speed_text}", True, (255, 255, 255))
        self.screen.blit(text_surface, (self.screen.get_width() - 200, 10))
