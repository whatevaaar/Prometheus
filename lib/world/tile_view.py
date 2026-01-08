import copy
import random

import pygame

from render.prometheus_colors.prometheus_colors import base_color


class TileView:
    def __init__(self, world, x_start, y_start, x_end, y_end, screen_width, screen_height):
        self.world = world
        self.x_start = x_start
        self.y_start = y_start
        self.x_end = x_end
        self.y_end = y_end

        self.width = self.x_end - self.x_start
        self.height = self.y_end - self.y_start

        self.screen_width = screen_width
        self.screen_height = screen_height

        # recalcular tile_size para que ocupe toda la pantalla
        self.tile_size_x = screen_width / self.width
        self.tile_size_y = screen_height / self.height

        # copia tiles del sector
        self.tiles = [[copy.copy(world.tiles[y][x]) for x in range(x_start, x_end)] for y in range(y_start, y_end)]

        # entidades dentro del sector
        self.entities = [copy.deepcopy(e) for e in world.entities if x_start <= e.x < x_end and y_start <= e.y < y_end]
        for e in self.entities:
            e.x -= self.x_start
            e.y -= self.y_start

        # animaciones
        self.entity_anims = {}
        for e in self.entities:
            self.entity_anims[e.name] = {"offset_x": random.uniform(-0.3, 0.3), "offset_y": random.uniform(-0.3, 0.3),
                "speed_x": random.uniform(0.01, 0.05), "speed_y": random.uniform(0.01, 0.05),
                "accessory": random.choice(["hat", "cape", "flag", "none"]), "blink": random.choice([True, False]),
                "happiness": 0.6}

    def draw(self, screen):
        for y, row in enumerate(self.tiles):
            for x, t in enumerate(row):
                px = x * self.tile_size_x
                py = y * self.tile_size_y
                rect = pygame.Rect(px, py, self.tile_size_x, self.tile_size_y)
                screen.fill(base_color(t), rect)

        from render.entity_renderer import draw_entity
        for e in self.entities:
            anim = self.entity_anims[e.name]
            # usar mínimo de tile_size_x y tile_size_y para entidades
            draw_entity(screen, e, anim, min(self.tile_size_x, self.tile_size_y))

    def tick(self):
        for e in self.entities:
            anim = self.entity_anims[e.name]
            # oscilar offsets
            anim["offset_x"] += anim["speed_x"] * random.choice([-1, 1])
            anim["offset_y"] += anim["speed_y"] * random.choice([-1, 1])
            anim["offset_x"] = max(-0.5, min(0.5, anim["offset_x"]))
            anim["offset_y"] = max(-0.5, min(0.5, anim["offset_y"]))

            # movimiento ligero dentro del tileview
            e.x += random.choice([-0.05, 0, 0.05])
            e.y += random.choice([-0.05, 0, 0.05])
            e.x = max(0, min(self.width - 1, e.x))
            e.y = max(0, min(self.height - 1, e.y))

    def apply_changes_to_world(self):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                world_x = self.x_start + x
                world_y = self.y_start + y
                w_tile = self.world.tiles[world_y][world_x]
                w_tile.food = tile.food
                w_tile.owner = tile.owner

        for e in self.entities:
            for we in self.world.entities:
                if we.name == e.name:
                    we.energy = e.energy
                    we.days_without_food = e.days_without_food
                    we.settled = e.settled
                    we.settlement = e.settlement
