from pygame import Rect, draw, SRCALPHA, Surface

import config
from lib.events.event_log import event_log
from render.pro_colors.prometheus_colors import base_color
from render.renderer import RendererBase


class WorldRenderer(RendererBase):
    def __init__(self, screen: Surface, world):
        super().__init__(screen)
        self.world = world

    def draw(self):
        tile = config.TILE_SIZE
        world_px_h = self.world.height * tile

        # ==== Tiles ====
        for y in range(self.world.height):
            for x in range(self.world.width):
                t = self.world.tiles[y][x]
                rect = Rect(x * tile, y * tile, tile, tile)
                self.screen.fill(base_color(t), rect)

                if t.owner:
                    color = t.owner.color
                    overlay = Surface((tile, tile), SRCALPHA)
                    overlay.fill((color[0], color[1], color[2], 70))
                    self.screen.blit(overlay, rect)

                    if t.is_border(self.world, x, y):
                        draw.rect(self.screen, RendererBase.darker(color), rect, 1)

        # ==== Entidades ====
        for e in self.world.entities:
            color = e.faction.color if e.faction else (120, 120, 120)
            cx = e.x * tile + tile // 2
            cy = e.y * tile + tile // 2

            radius = 2
            if e.settled:
                radius = 3
            if e.is_leader:
                radius = 5

            draw.circle(self.screen, color, (cx, cy), radius)
            if e.is_leader:
                draw.circle(self.screen, (240, 240, 240), (cx, cy), radius, 1)

        # ==== UI ====
        ui_rect = Rect(0, world_px_h, self.screen.get_width(), self.screen.get_height() - world_px_h)
        draw.rect(self.screen, (20, 20, 20), ui_rect)
        draw.line(self.screen, (70, 70, 70), (0, world_px_h), (self.screen.get_width(), world_px_h), 2)

        age_text = self.big_font.render(f"Edad: {self.world.age}", True, (220, 220, 220))
        pop_text = self.big_font.render(f"Población: {len(self.world.entities)}", True, (220, 220, 220))
        self.screen.blit(age_text, (10, world_px_h + 10))
        self.screen.blit(pop_text, (10, world_px_h + 42))

        factions = sorted(self.world.history.factions, key=lambda f: f.population, reverse=True)[:3]
        fx, fy = 300, world_px_h + 10
        title = self.big_font.render("Facciones dominantes", True, (200, 200, 200))
        self.screen.blit(title, (fx, fy))
        fy += 32
        for f in factions:
            draw.rect(self.screen, f.color, Rect(fx, fy + 6, 14, 14))
            txt = self.font.render(f"{f.name} ({f.population})", True, (220, 220, 220))
            self.screen.blit(txt, (fx + 22, fy))
            fy += 22

        # ==== Event log ====
        log_x, log_y, max_lines = 10, world_px_h + 80, 5
        recent = list(event_log.events)[-max_lines:]
        for i, msg in enumerate(recent):
            text_surface = self.font.render(msg, True, (180, 180, 180))
            self.screen.blit(text_surface, (log_x, log_y + i * 18))
