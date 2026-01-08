import copy
import random

from lib.tile.tile import Tile


class TileView:
    """
    Vista temporal de un conjunto de tiles y entidades.
    Permite animación, movimiento y cierta variabilidad visual sin afectar el mundo real
    hasta que se aplique con apply_changes_to_world.
    """

    def __init__(self, world, x_start, y_start, x_end, y_end):
        self.world = world

        # asegurar que no sea vacío
        self.x_start = max(0, x_start)
        self.y_start = max(0, y_start)
        self.x_end = min(world.width, x_end + 1)
        self.y_end = min(world.height, y_end + 1)

        if self.x_start >= self.x_end or self.y_start >= self.y_end:
            raise ValueError("TileView vacío")

        # copia simple de tiles
        self.tiles = [[copy.copy(world.tiles[y][x]) for x in range(self.x_start, self.x_end)] for y in
                      range(self.y_start, self.y_end)]

        # copiar solo entidades dentro del área
        self.entities = [copy.deepcopy(e) for e in world.entities if
                         self.x_start <= e.x < self.x_end and self.y_start <= e.y < self.y_end]

        # offsets para centrar en pantalla
        self.width = self.x_end - self.x_start
        self.height = self.y_end - self.y_start
        for e in self.entities:
            e.x -= self.x_start
            e.y -= self.y_start

    # ------------------------
    # Animación / Movimiento
    # ------------------------
    def tick(self):
        for e in self.entities:
            self._move_entity(e)

    def _move_entity(self, e):
        """Movimiento simple dentro del TileView"""
        # cooldown aleatorio para no moverse todo al mismo tiempo
        if getattr(e, "move_cooldown", 0) > 0:
            e.move_cooldown -= 1
            return

        # posibles posiciones dentro del TileView
        positions = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = e.x + dx, e.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    tile = self.tiles[ny][nx]
                    if tile.can_spawn():
                        positions.append((nx, ny))

        if positions:
            e.x, e.y = random.choice(positions)
            e.move_cooldown = random.randint(2, 5)

    # ------------------------
    # Aplicar cambios al mundo real
    # ------------------------
    def apply_changes_to_world(self):
        # aplicar tiles
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                world_x = self.x_start + x
                world_y = self.y_start + y
                w_tile: Tile = self.world.tiles[world_y][world_x]
                w_tile.food = tile.food
                w_tile.owner = tile.owner

        # aplicar cambios relevantes de entidades
        for tv_e in self.entities:
            # coordenadas originales en el world
            world_x = self.x_start + tv_e.x
            world_y = self.y_start + tv_e.y

            # buscar entidad por nombre (único)
            for w_e in self.world.entities:
                if w_e.name == tv_e.name:
                    w_e.energy = tv_e.energy
                    w_e.days_without_food = tv_e.days_without_food
                    w_e.settled = tv_e.settled
                    break

    # ------------------------
    # Helper visual
    # ------------------------
    def get_tile(self, x, y):
        """Obtiene tile relativo al TileView, devuelve None si fuera del área"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
