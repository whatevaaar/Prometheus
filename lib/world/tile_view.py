import copy
import random

import pygame

from render.prometheus_colors.prometheus_colors import base_color


class TileView:
    def __init__(self, world, tile_x, tile_y, screen_width, screen_height):
        self.world = world
        self.tile_x = tile_x
        self.tile_y = tile_y

        self.tile = world.tiles[tile_y][tile_x]

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.entity_anims = {}
        self.entities = [copy.deepcopy(e) for e in world.entities if
                         tile_x <= e.x < tile_x + 1 and tile_y <= e.y < tile_y + 1]

        for e in self.entities:
            e.x = random.uniform(0.3, 0.7)
            e.y = random.uniform(0.45, 0.75)

        for e in self.entities: self.entity_anims[e.name] = {"offset_x": random.uniform(-0.3, 0.3),
                                                             "offset_y": random.uniform(-0.3, 0.3),
                                                             "speed_x": random.uniform(0.01, 0.05),
                                                             "speed_y": random.uniform(0.01, 0.05),
                                                             "accessory": random.choice(
                                                                 ["hat", "cape", "flag", "none"]),
                                                             "blink": random.choice([True, False]), "happiness": 0.6}

    def draw(self, screen):
        w, h = self.screen_width, self.screen_height

        # =====================
        # FONDO (tile abstracta)
        # =====================
        base = base_color(self.tile)
        screen.fill(base)

        # grano visual
        for _ in range(120):
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)
            shade = random.randint(-10, 10)
            c = (max(0, min(255, base[0] + shade)), max(0, min(255, base[1] + shade)),
                 max(0, min(255, base[2] + shade)),)
            screen.set_at((x, y), c)

        # =====================
        # ASENTAMIENTO
        # =====================
        if self.tile.settled:
            for i in range(3):
                hx = int(w * (0.25 + i * 0.18))
                hy = int(h * 0.55)
                hw = int(w * 0.08)
                hh = int(h * 0.08)
                pygame.draw.rect(screen, (90, 70, 50), (hx, hy, hw, hh))

            pygame.draw.circle(screen, (255, 140, 60), (w // 2, int(h * 0.65)), int(min(w, h) * 0.03), )

            if self.tile.owner:
                pole_x = int(w * 0.8)
                pole_y = int(h * 0.35)
                pygame.draw.line(screen, (60, 60, 60), (pole_x, pole_y), (pole_x, pole_y + 80), 3)
                pygame.draw.rect(screen, self.tile.owner.color, (pole_x, pole_y, 40, 25), )

        # =====================
        # ENTIDADES
        # =====================
        from render.entity_renderer import draw_entity

        scale = min(w, h) * 0.12

        for e in self.entities:
            anim = self.entity_anims[e.name]
            draw_entity(screen, e, anim, scale)

    def tick(self):
        for e in self.entities:
            anim = self.entity_anims[e.name]

            anim["offset_x"] += anim["speed_x"] * random.choice([-1, 1])
            anim["offset_y"] += anim["speed_y"] * random.choice([-1, 1])

            anim["offset_x"] = max(-0.5, min(0.5, anim["offset_x"]))
            anim["offset_y"] = max(-0.5, min(0.5, anim["offset_y"]))

            e.x += random.uniform(-0.01, 0.01)
            e.y += random.uniform(-0.01, 0.01)

            e.x = max(0.2, min(0.8, e.x))
            e.y = max(0.4, min(0.85, e.y))

    def apply_changes_to_world(self):
        # === Tile ===
        w_tile = self.world.tiles[self.tile_y][self.tile_x]

        w_tile.food = self.tile.food
        w_tile.owner = self.tile.owner
        w_tile.settled = self.tile.settled

        # === Entidades ===
        for e in self.entities:
            for we in self.world.entities:
                if we.name == e.name:
                    we.energy = e.energy
                    we.days_without_food = e.days_without_food
                    we.settled = e.settled
                    we.settlement = e.settlement
