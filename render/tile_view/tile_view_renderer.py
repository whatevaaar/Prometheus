import random

from pygame import draw, Surface

from lib.world.tile_view import TileView
from render.pro_colors.prometheus_colors import base_color
from render.renderer import RendererBase
from render.tile_view.entity.entity_renderer import draw_entity


class TileViewRenderer(RendererBase):
    def __init__(self, screen: Surface, tile_view: TileView):
        super().__init__(screen)
        self.tile_view = tile_view
        self.w, self.h = self.screen.get_size()

    def draw(self):
        self.draw_background()
        self.draw_settlement()
        self.draw_entities()

    def draw_background(self):
        base = base_color(self.tile_view.tile)
        self.screen.fill(base)
        for _ in range(120):
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            shade = random.randint(-10, 10)
            c = (
            max(0, min(255, base[0] + shade)), max(0, min(255, base[1] + shade)), max(0, min(255, base[2] + shade)),)
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

    def draw_entities(self):
        scale = min(self.w, self.h) * 0.12
        for e in self.tile_view.entities:
            anim = self.tile_view.entity_anims[e.name]
            draw_entity(self.screen, e, anim, scale)
