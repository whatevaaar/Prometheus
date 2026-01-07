import config


class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    # =========================
    # MUNDO LÓGICO (tiles)
    # =========================
    def is_in_world(self) -> bool:
        """
        ¿Está dentro del mundo lógico (coordenadas en tiles)?
        """
        return 0 <= self.x < config.WIDTH and 0 <= self.y < config.HEIGHT

    # =========================
    # PANTALLA COMPLETA (px)
    # =========================
    def is_on_screen(self) -> bool:
        """
        ¿Está dentro de la ventana completa?
        """
        return 0 <= self.x < config.SCREEN_W and 0 <= self.y < config.SCREEN_H

    # =========================
    # VISTA DE MUNDO (sin UI/log)
    # =========================
    def is_on_world_view(self) -> bool:
        """
        ¿Está dentro del área visible del mundo (excluye panel inferior)?
        """
        world_px_h = config.HEIGHT * config.TILE_SIZE

        return 0 <= self.x < config.SCREEN_W and 0 <= self.y < world_px_h

    # =========================
    # HELPERS ÚTILES
    # =========================
    def clamp_to_world(self):
        """
        Fuerza el punto a quedar dentro del mundo.
        Ideal para evitar IndexError.
        """
        self.x = max(0, min(self.x, config.WIDTH - 1))
        self.y = max(0, min(self.y, config.HEIGHT - 1))
