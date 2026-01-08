# ---------------------------
# TileView.py
# ---------------------------
import copy
import random


class TileView:
    def __init__(self, world, tile_x, tile_y, screen_width, screen_height):
        self.world = world
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.tile = world.tiles[tile_y][tile_x]
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Copia de entidades del tile
        self.entities = [copy.deepcopy(e) for e in world.entities if
                         tile_x <= e.x < tile_x + 1 and tile_y <= e.y < tile_y + 1]

        self.entity_anims = {}
        self.assign_entity_positions()

        for e in self.entities:
            self.entity_anims[e.name] = {"offset_x": random.uniform(-0.1, 0.1), "offset_y": random.uniform(-0.1, 0.1),
                "speed_x": random.uniform(0.01, 0.05), "speed_y": random.uniform(0.01, 0.05),
                "accessory": random.choice(["hat", "cape", "flag", "none"]), "blink": random.choice([True, False]),
                "happiness": 0.6}

    def tick(self):
        for e in self.entities:
            anim = self.entity_anims[e.name]
            anim["offset_x"] += anim["speed_x"] * random.choice([-1, 1])
            anim["offset_y"] += anim["speed_y"] * random.choice([-1, 1])
            anim["offset_x"] = max(-0.5, min(0.5, anim["offset_x"]))
            anim["offset_y"] = max(-0.5, min(0.5, anim["offset_y"]))
            e.x += random.uniform(-0.01, 0.01)
            e.y += random.uniform(-0.01, 0.01)
            e.x = max(0.0, min(1.0, e.x))
            e.y = max(0.0, min(1.0, e.y))

    def apply_changes_to_world(self):
        w_tile = self.world.tiles[self.tile_y][self.tile_x]
        w_tile.food = self.tile.food
        w_tile.owner = self.tile.owner
        w_tile.settled = self.tile.settled
        for e in self.entities:
            for we in self.world.entities:
                if we.name == e.name:
                    we.energy = e.energy
                    we.days_without_food = e.days_without_food
                    we.settled = e.settled
                    we.settlement = e.settlement

    def assign_entity_positions(self):
        n = len(self.entities)
        if n == 0:
            return

        padding = 0.15  # espacio desde bordes del tile
        max_offset = 0.05  # randomness

        # intentar formar un grid cuadrado
        cols = int(n ** 0.5 + 0.5)
        rows = (n + cols - 1) // cols

        cell_w = (1 - 2 * padding) / cols
        cell_h = (1 - 2 * padding) / rows

        for i, e in enumerate(self.entities):
            col = i % cols
            row = i // cols

            # centramos en la celda y agregamos randomness
            e.x = padding + col * cell_w + cell_w / 2 + random.uniform(-max_offset, max_offset)
            e.y = padding + row * cell_h + cell_h / 2 + random.uniform(-max_offset, max_offset)

            # clamp
            e.x = max(0.0, min(1.0, e.x))
            e.y = max(0.0, min(1.0, e.y))
