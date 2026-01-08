import pygame

import config
from lib.world.tile_view import TileView
from lib.world.world import World
from render.renderer import Renderer

pygame.init()

screen = pygame.display.set_mode((config.WIDTH * config.TILE_SIZE, config.HEIGHT * config.TILE_SIZE + config.UI_HEIGHT))

pygame.display.set_caption("World Simulation")

clock = pygame.time.Clock()

world = World(config.WIDTH, config.HEIGHT)
renderer = Renderer(config.TILE_SIZE)

running = True
frame = 0

tile_size = config.TILE_SIZE

current_tile_view = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            tile_x = int(mouse_x // config.TILE_SIZE)
            tile_y = int(mouse_y // config.TILE_SIZE)

            current_tile_view = TileView(world, tile_x, tile_y, screen.get_width(), screen.get_height())

        if event.type == pygame.KEYDOWN and current_tile_view:
            if event.key == pygame.K_d:
                current_tile_view.apply_changes_to_world()
                current_tile_view = None

    if frame % 5 == 0 and not current_tile_view:
        world.tick()
    elif current_tile_view:
        current_tile_view.tick()

    screen.fill((0, 0, 0))
    if current_tile_view:
        renderer.draw_tile_view(screen, current_tile_view)
    else:
        renderer.draw_world(screen, world)

    pygame.display.flip()
    clock.tick(60)
    frame += 1

# Salir de vista tile

pygame.quit()
