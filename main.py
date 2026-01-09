from typing import Optional

import pygame

import config
from geometry.point.point import is_in_world
from lib.entity.entity import Entity
from lib.world.tile_view import TileView
from lib.world.world import World
from render.tile_view.tile_view_renderer import TileViewRenderer
from render.ui.ui_renderer import UIRenderer  # nuevo renderer UI
from render.world_view.world_renderer import WorldRenderer

# --------------------------
# Configuración inicial
# --------------------------
pygame.init()
screen = pygame.display.set_mode((config.WIDTH * config.TILE_SIZE, config.HEIGHT * config.TILE_SIZE + config.UI_HEIGHT))
pygame.display.set_caption("World Simulation")
clock = pygame.time.Clock()

world = World(config.WIDTH, config.HEIGHT)

# Renderers
world_renderer = WorldRenderer(screen, world)
ui_renderer = UIRenderer(screen)

# Estado de simulación
current_tile_view: Optional[TileView] = None
tile_view_renderer: Optional[TileViewRenderer] = None
paused = False
tick_speed = 5  # frames por tick
frame = 0
clicked_entity: Optional[Entity] = None


# --------------------------
# Funciones de control
# --------------------------
def handle_input():
    """Maneja teclado y mouse"""
    global current_tile_view, tile_view_renderer, paused, tick_speed, clicked_entity
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        # Click para seleccionar TileView
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3 and not current_tile_view:
                world_renderer.handle_event(event)
                continue
            mouse_x, mouse_y = pygame.mouse.get_pos()
            tile_x = int(mouse_x // config.TILE_SIZE)
            tile_y = int(mouse_y // config.TILE_SIZE)
            if current_tile_view:
                clicked_entity = tile_view_renderer.entity_at_pos(mouse_x, mouse_y)

            elif is_in_world(tile_x, tile_y):
                current_tile_view = TileView(world, tile_x, tile_y, screen.get_width(), screen.get_height())
                tile_view_renderer = TileViewRenderer(screen, current_tile_view)
                clicked_entity = None

        # Teclado
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused  # pausar / resumir

            if event.key == pygame.K_1:
                tick_speed = 10  # lento
            elif event.key == pygame.K_2:
                tick_speed = 5  # normal
            elif event.key == pygame.K_3:
                tick_speed = 2  # rápido

            if current_tile_view and event.key == pygame.K_d:
                current_tile_view.apply_changes_to_world()
                current_tile_view = None
                tile_view_renderer = None
                clicked_entity = None

    return True


def update_simulation():
    """Avanza la simulación según el tick_speed y pausa"""
    global frame
    if not paused and frame % tick_speed == 0:
        if current_tile_view:
            current_tile_view.tick()
        else:
            world.tick()


def draw():
    """Dibuja todo en pantalla delegando a los renderers"""
    global clicked_entity
    screen.fill((0, 0, 0))

    if current_tile_view:
        tile_view_renderer.draw(clicked_entity)
    else:
        world_renderer.draw()

    ui_renderer.draw(paused, tick_speed)  # indicador global
    pygame.display.flip()


# --------------------------
# Loop principal
# --------------------------
running = True
while running:
    running = handle_input()
    update_simulation()
    draw()
    clock.tick(60)
    frame += 1

pygame.quit()
