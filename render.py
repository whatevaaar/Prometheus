import math

import pygame

from graphics.prometheus_colors.prometheus_colors import base_color
from lib.events.event_log import event_log


def darker(color, factor=0.6):
    return tuple(int(c * factor) for c in color)


class Renderer:
    def __init__(self, tile_size):
        self.tile = tile_size

        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 16)
        self.big_font = pygame.font.SysFont("consolas", 22)

    def draw_world(self, screen, world):
        tile = self.tile
        world_px_h = world.height * tile

        # =========================
        # MUNDO
        # =========================
        for y in range(world.height):
            for x in range(world.width):
                t = world.tiles[y][x]
                rect = pygame.Rect(x * tile, y * tile, tile, tile)

                # terreno base
                screen.fill(base_color(t), rect)

                # territorio de facción
                if t.owner:
                    color = t.owner.color

                    overlay = pygame.Surface((tile, tile), pygame.SRCALPHA)
                    overlay.fill((color[0], color[1], color[2], 70))
                    screen.blit(overlay, rect)

                    if t.is_border(world, x, y):
                        pygame.draw.rect(screen, darker(color), rect, 1)

        # =========================
        # ENTIDADES
        # =========================
        for e in world.entities:
            if e.faction:
                color = e.faction.color
            else:
                color = (120, 120, 120)

            cx = e.x * tile + tile // 2
            cy = e.y * tile + tile // 2

            radius = 2
            if e.settled:
                radius = 3
            if e.is_leader:
                radius = 5

            pygame.draw.circle(screen, color, (cx, cy), radius)
            if e.is_leader:
                pygame.draw.circle(screen, (240, 240, 240), (cx, cy), radius, 1)

        # =========================
        # UI PANEL
        # =========================
        ui_rect = pygame.Rect(0, world_px_h, screen.get_width(), screen.get_height() - world_px_h)

        pygame.draw.rect(screen, (20, 20, 20), ui_rect)
        pygame.draw.line(screen, (70, 70, 70), (0, world_px_h), (screen.get_width(), world_px_h), 2)

        # ---- Edad y población ----
        age_text = self.big_font.render(f"Edad: {world.age}", True, (220, 220, 220))
        pop_text = self.big_font.render(f"Población: {len(world.entities)}", True, (220, 220, 220))

        screen.blit(age_text, (10, world_px_h + 10))
        screen.blit(pop_text, (10, world_px_h + 42))

        # =========================
        # TOP FACCIONES
        # =========================
        factions = sorted(world.history.factions, key=lambda f: f.population, reverse=True)[:3]

        fx = 300
        fy = world_px_h + 10

        title = self.big_font.render("Facciones dominantes", True, (200, 200, 200))
        screen.blit(title, (fx, fy))
        fy += 32

        for f in factions:
            pygame.draw.rect(screen, f.color, pygame.Rect(fx, fy + 6, 14, 14))

            txt = self.font.render(f"{f.name} ({f.population})", True, (220, 220, 220))
            screen.blit(txt, (fx + 22, fy))
            fy += 22

        # =========================
        # EVENT LOG
        # =========================
        log_x = 10
        log_y = world_px_h + 80
        max_lines = 5

        recent = list(event_log.events)[-max_lines:]

        for i, msg in enumerate(recent):
            text_surface = self.font.render(msg, True, (180, 180, 180))
            screen.blit(text_surface, (log_x, log_y + i * 18))

    def draw_tile_view(self, screen, tile_view):

        screen_w, screen_h = screen.get_size()
        # tamaño de cada tile en pantalla
        tile_w = screen_w / tile_view.width
        tile_h = screen_h / tile_view.height

        # dibujar tiles
        for y, row in enumerate(tile_view.tiles):
            for x, t in enumerate(row):
                rect = pygame.Rect(x * tile_w, y * tile_h, tile_w, tile_h)
                screen.fill(base_color(t), rect)

                if t.owner:
                    color = t.owner.color
                    overlay = pygame.Surface((tile_w, tile_h), pygame.SRCALPHA)
                    overlay.fill((*color[:3], 70))
                    screen.blit(overlay, rect)

        # dibujar entidades con jiggle y detalles
        t = pygame.time.get_ticks()
        for e in tile_view.entities:
            rel_x = e.x - tile_view.x_start
            rel_y = e.y - tile_view.y_start

            # jiggle animado
            jiggle_x = math.sin(t / 200 + rel_x) * 0.3
            jiggle_y = math.cos(t / 200 + rel_y) * 0.3

            cx = (rel_x + jiggle_x) * tile_w + tile_w / 2
            cy = (rel_y + jiggle_y) * tile_h + tile_h / 2

            # tamaño según rol
            radius = tile_w * 0.3
            if e.settled:
                radius *= 1.5
            if e.is_leader:
                radius *= 2

            color = e.faction.color if e.faction else (200, 200, 200)
            pygame.draw.circle(screen, color, (int(cx), int(cy)), int(radius))

            # detalles de asentamiento
            if e.settled:
                tent_rect = pygame.Rect(cx - radius / 2, cy + radius / 2, radius, radius / 2)
                pygame.draw.rect(screen, (150, 75, 0), tent_rect)

            if e.is_leader:
                pygame.draw.circle(screen, (255, 255, 255), (int(cx), int(cy)), int(radius), 2)
