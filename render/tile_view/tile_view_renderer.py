# ---------------------------
# TileViewRenderer.py
# ---------------------------
import random
from typing import Optional

import pygame
from pygame import draw, Surface, Rect

import config
from geometry.point.point import get_entity_screen_pos
from lib.entity.entity import Entity
from lib.world.tile_view import TileView
from render.pro_colors.prometheus_colors import base_color
from render.renderer import RendererBase
from render.tile_view.entity.entity_renderer import draw_entity


class TileViewRenderer(RendererBase):
    def __init__(self, screen: Surface, tile_view: TileView):
        super().__init__(screen)
        self.tile_view = tile_view
        self.w, self.h = self.screen.get_size()
        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 14)

    def draw(self, show_info_entity: Optional[Entity] = None):
        self.draw_background()
        self.draw_settlement()
        self.draw_entities()
        if show_info_entity:
            self.draw_entity_info(show_info_entity)

    def draw_background(self):
        base = base_color(self.tile_view.tile)
        self.screen.fill(base)
        for _ in range(120):
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            shade = random.randint(-10, 10)
            c = (
                max(0, min(255, base[0] + shade)), max(0, min(255, base[1] + shade)), max(0, min(255, base[2] + shade)))
            self.screen.set_at((x, y), c)

    def draw_settlement(self):
        tile = self.tile_view.tile
        if not tile.settled:
            return
        for i in range(3):
            hx = int(self.w * (0.25 + i * 0.18))
            hy = int(self.h * 0.55)
            hw = int(self.w * 0.08)
            hh = int(self.h * 0.08)
            draw.rect(self.screen, (90, 70, 50), (hx, hy, hw, hh))
        draw.circle(self.screen, (255, 140, 60), (self.w // 2, int(self.h * 0.65)), int(min(self.w, self.h) * 0.03))
        if tile.owner:
            pole_x = int(self.w * 0.8)
            pole_y = int(self.h * 0.35)
            draw.line(self.screen, (60, 60, 60), (pole_x, pole_y), (pole_x, pole_y + 80), 3)
            draw.rect(self.screen, tile.owner.color, (pole_x, pole_y, 40, 25))

    # TileViewRenderer.draw_entities()
    def draw_entities(self):
        tile_px_w = self.w  # ancho del tile en pantalla
        tile_px_h = self.h  # alto del tile en pantalla
        tile_offset_x = 0
        tile_offset_y = 0

        for e in self.tile_view.entities:
            anim = self.tile_view.entity_anims[e.name]
            draw_entity(self.screen, e, anim, tile_px_w, tile_px_h, tile_offset_x, tile_offset_y)


    def entity_at_pos(self, mouse_x, mouse_y) -> Optional[Entity]:
        """
        Devuelve la entidad bajo el cursor (clic) usando la misma lógica que draw_entity
        """
        tile_px_w = self.w
        tile_px_h = self.h

        for e in self.tile_view.entities:
            anim = self.tile_view.entity_anims[e.name]
            cx, cy = get_entity_screen_pos(e, anim, tile_px_w, tile_px_h)

            # radio clickable basado en tamaño del cuerpo
            body_w = tile_px_w * config.ENTITY_SCALE
            body_h = tile_px_h * config.ENTITY_SCALE
            radius = int(max(body_w, body_h) * config.ENTITY_CLICK_SCALE / 2)

            if (mouse_x - cx) ** 2 + (mouse_y - cy) ** 2 <= radius ** 2:
                return e

        return None

    def draw_entity_info(self, e: Entity):
        rect_w, rect_h = 150, 70
        rect = Rect(10, 10, rect_w, rect_h)
        draw.rect(self.screen, (30, 30, 30), rect)
        draw.rect(self.screen, (200, 200, 200), rect, 1)
        lines = [f"Nombre: {e.name}", f"Energía: {e.energy:.1f}", f"Días sin comida: {e.days_without_food}",
                 f"Asentado: {e.settled}"]
        for i, line in enumerate(lines):
            surf = self.font.render(line, True, (220, 220, 220))
            self.screen.blit(surf, (rect.x + 6, rect.y + 6 + i * 16))
