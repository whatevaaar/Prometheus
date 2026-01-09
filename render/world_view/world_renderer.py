from pygame import Rect, draw, SRCALPHA, Surface, MOUSEBUTTONDOWN

import config
from lib.events.event_log import event_log
from render.pro_colors.prometheus_colors import base_color
from render.renderer import RendererBase

FACTION_LABEL_MIN_TILES = 25
FACTION_OVERLAY_ALPHA = 70
FACTION_STRIPE_WIDTH = 6


class WorldRenderer(RendererBase):
    def __init__(self, screen: Surface, world):
        super().__init__(screen)
        self.tile_px = None
        self.world_px_h = None
        self.world = world
        self._faction_centroids = {}

    # ──────────────────────────────
    # Entry point
    # ──────────────────────────────
    def draw(self):
        self.tile_px = config.TILE_SIZE
        self.world_px_h = self.world.height * self.tile_px

        self.compute_faction_centroids()

        self.draw_tiles()
        self.draw_entities()
        self.draw_faction_labels()
        self.draw_ui()
        self.draw_event_log()

    # ──────────────────────────────
    # Tiles
    # ──────────────────────────────
    def draw_tiles(self):
        tile = self.tile_px

        for y in range(self.world.height):
            for x in range(self.world.width):
                t = self.world.tiles[y][x]
                rect = Rect(x * tile, y * tile, tile, tile)

                self.draw_base_tile(t, rect)
                self.draw_tile_border_edges(t, rect, x, y)
                self.draw_faction_marker(t, rect)

                if getattr(t, "at_war", False):
                    self.draw_war_icon(rect)

    def draw_base_tile(self, tile, rect):
        self.screen.fill(base_color(tile), rect)

    # ───────── Overlay con bandas visibles
    def draw_tile_owner_pattern(self, tile, rect):
        if not tile.owner:
            return

        overlay = Surface((self.tile_px, self.tile_px), SRCALPHA)
        r, g, b = tile.owner.color

        for x in range(0, self.tile_px, FACTION_STRIPE_WIDTH * 2):
            stripe = Rect(x, 0, FACTION_STRIPE_WIDTH, self.tile_px)
            overlay.fill((r, g, b, FACTION_OVERLAY_ALPHA), stripe)

        self.screen.blit(overlay, rect)

    # ───────── Bordes exteriores reales
    def draw_tile_border_edges(self, tile, rect, x, y):
        if not tile.owner:
            return

        color = RendererBase.darker(tile.owner.color)
        w = 3  # más grueso

        def same_owner(nx, ny):
            if nx < 0 or ny < 0 or nx >= self.world.width or ny >= self.world.height:
                return False
            return self.world.tiles[ny][nx].owner == tile.owner

        if not same_owner(x, y - 1):
            draw.line(self.screen, color, rect.topleft, rect.topright, w)
        if not same_owner(x, y + 1):
            draw.line(self.screen, color, rect.bottomleft, rect.bottomright, w)
        if not same_owner(x - 1, y):
            draw.line(self.screen, color, rect.topleft, rect.bottomleft, w)
        if not same_owner(x + 1, y):
            draw.line(self.screen, color, rect.topright, rect.bottomright, w)

    # ───────── Icono de guerra CLARO
    def draw_war_icon(self, rect):
        bg = Surface((rect.width, rect.height), SRCALPHA)
        bg.fill((120, 20, 20, 90))
        self.screen.blit(bg, rect)

        cx, cy = rect.center
        s = self.tile_px // 2 - 2

        draw.line(self.screen, (240, 240, 240), (cx - s, cy - s), (cx + s, cy + s), 3)
        draw.line(self.screen, (240, 240, 240), (cx - s, cy + s), (cx + s, cy - s), 3)

    # ──────────────────────────────
    # Entities
    # ──────────────────────────────
    def draw_entities(self):
        tile = self.tile_px

        for e in self.world.entities:
            cx = e.x * tile + tile // 2
            cy = e.y * tile + tile // 2

            color = e.faction.color if e.faction else (120, 120, 120)
            radius = self.get_entity_radius(e)

            draw.circle(self.screen, color, (cx, cy), radius)

            if e.is_leader:
                draw.circle(self.screen, (240, 240, 240), (cx, cy), radius, 1)

    def get_entity_radius(self, entity):
        if entity.is_leader:
            return 5
        if entity.settled:
            return 3
        return 2

    # ──────────────────────────────
    # Faction labels
    # ──────────────────────────────
    def compute_faction_centroids(self):
        self._faction_centroids.clear()
        counts = {}
        sums = {}

        for y in range(self.world.height):
            for x in range(self.world.width):
                t = self.world.tiles[y][x]
                if not t.owner:
                    continue

                f = t.owner
                counts[f] = counts.get(f, 0) + 1
                sx, sy = sums.get(f, (0, 0))
                sums[f] = (sx + x, sy + y)

        for f, n in counts.items():
            if n >= FACTION_LABEL_MIN_TILES:
                sx, sy = sums[f]
                self._faction_centroids[f] = (int((sx / n) * self.tile_px), int((sy / n) * self.tile_px),)

    def draw_faction_labels(self):
        for f, (px, py) in self._faction_centroids.items():
            txt = self.font.render(f.name, True, (235, 235, 235))
            r = txt.get_rect(center=(px, py))
            self.screen.blit(txt, r)

    # ──────────────────────────────
    # UI
    # ──────────────────────────────
    def draw_ui(self):
        self.draw_ui_background()
        self.draw_world_stats()
        self.draw_factions_panel()

    def draw_ui_background(self):
        ui_rect = Rect(0, self.world_px_h, self.screen.get_width(), self.screen.get_height() - self.world_px_h, )
        draw.rect(self.screen, (20, 20, 20), ui_rect)
        draw.line(self.screen, (70, 70, 70), (0, self.world_px_h), (self.screen.get_width(), self.world_px_h), 2, )

    def draw_world_stats(self):
        age_text = self.big_font.render(f"Edad: {self.world.age}", True, (220, 220, 220))
        pop_text = self.big_font.render(f"Población: {len(self.world.entities)}", True, (220, 220, 220))

        self.screen.blit(age_text, (10, self.world_px_h + 10))
        self.screen.blit(pop_text, (10, self.world_px_h + 42))

    def draw_factions_panel(self):
        factions = sorted(self.world.history.factions, key=lambda f: f.population, reverse=True, )[:3]

        fx, fy = 300, self.world_px_h + 10
        title = self.big_font.render("Facciones dominantes", True, (200, 200, 200))
        self.screen.blit(title, (fx, fy))

        fy += 32
        for f in factions:
            draw.rect(self.screen, f.color, Rect(fx, fy + 6, 14, 14))
            txt = self.font.render(f"{f.name} ({f.population})", True, (220, 220, 220))
            self.screen.blit(txt, (fx + 22, fy))
            fy += 22

    # ──────────────────────────────
    # Event log
    # ──────────────────────────────
    def draw_event_log(self):
        log_x = 10
        log_y = self.world_px_h + 80
        max_lines = 5

        recent = list(event_log.events)[-max_lines:]

        for i, msg in enumerate(recent):
            text_surface = self.font.render(msg, True, (180, 180, 180))
            self.screen.blit(text_surface, (log_x, log_y + i * 18))

    # ──────────────────────────────
    # Input (click derecho)
    # ──────────────────────────────
    def handle_event(self, event):
        if event.type != MOUSEBUTTONDOWN or event.button != 3:
            return

        mx, my = event.pos
        if my >= self.world_px_h:
            return

        tx = mx // self.tile_px
        ty = my // self.tile_px

        tile = self.world.tiles[ty][tx]
        if tile.owner:
            event_log.add(f"Facción: {tile.owner.name}")

    def draw_faction_marker(self, tile, rect):
        if not tile.owner:
            return

        # tamaño grande, imposible no verlo
        s = self.tile_px // 2

        # esquina por facción (estable)
        corner = hash(tile.owner) % 4

        if corner == 0:  # top-left
            r = Rect(rect.left, rect.top, s, s)
        elif corner == 1:  # top-right
            r = Rect(rect.right - s, rect.top, s, s)
        elif corner == 2:  # bottom-left
            r = Rect(rect.left, rect.bottom - s, s, s)
        else:  # bottom-right
            r = Rect(rect.right - s, rect.bottom - s, s, s)

        draw.rect(self.screen, tile.owner.color, r)
