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
