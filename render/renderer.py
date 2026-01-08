import pygame

from lib.events.event_log import event_log
from lib.world.tile_view import TileView
from render.prometheus_colors.prometheus_colors import base_color


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

        # ==== Tiles ====
        for y in range(world.height):
            for x in range(world.width):
                t = world.tiles[y][x]
                rect = pygame.Rect(x * tile, y * tile, tile, tile)
                screen.fill(base_color(t), rect)

                if t.owner:
                    color = t.owner.color
                    overlay = pygame.Surface((tile, tile), pygame.SRCALPHA)
                    overlay.fill((color[0], color[1], color[2], 70))
                    screen.blit(overlay, rect)

                    if t.is_border(world, x, y):
                        pygame.draw.rect(screen, darker(color), rect, 1)

        # ==== Entidades ====
        for e in world.entities:
            color = e.faction.color if e.faction else (120, 120, 120)
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

        # ==== UI ====
        ui_rect = pygame.Rect(0, world_px_h, screen.get_width(), screen.get_height() - world_px_h)
        pygame.draw.rect(screen, (20, 20, 20), ui_rect)
        pygame.draw.line(screen, (70, 70, 70), (0, world_px_h), (screen.get_width(), world_px_h), 2)

        age_text = self.big_font.render(f"Edad: {world.age}", True, (220, 220, 220))
        pop_text = self.big_font.render(f"Población: {len(world.entities)}", True, (220, 220, 220))
        screen.blit(age_text, (10, world_px_h + 10))
        screen.blit(pop_text, (10, world_px_h + 42))

        factions = sorted(world.history.factions, key=lambda f: f.population, reverse=True)[:3]
        fx, fy = 300, world_px_h + 10
        title = self.big_font.render("Facciones dominantes", True, (200, 200, 200))
        screen.blit(title, (fx, fy))
        fy += 32
        for f in factions:
            pygame.draw.rect(screen, f.color, pygame.Rect(fx, fy + 6, 14, 14))
            txt = self.font.render(f"{f.name} ({f.population})", True, (220, 220, 220))
            screen.blit(txt, (fx + 22, fy))
            fy += 22

        # ==== Event log ====
        log_x, log_y, max_lines = 10, world_px_h + 80, 5
        recent = list(event_log.events)[-max_lines:]
        for i, msg in enumerate(recent):
            text_surface = self.font.render(msg, True, (180, 180, 180))
            screen.blit(text_surface, (log_x, log_y + i * 18))

    @staticmethod
    def draw_tile_view(screen, tile_view: TileView):
        tile_view.draw(screen)
