import pygame

import config
from lib.world.world import World
from render import Renderer

pygame.init()

screen = pygame.display.set_mode((config.WIDTH * config.TILE_SIZE, config.HEIGHT * config.TILE_SIZE + config.UI_HEIGHT))

pygame.display.set_caption("World Simulation")

clock = pygame.time.Clock()

world = World(config.WIDTH, config.HEIGHT)
renderer = Renderer(config.TILE_SIZE)

running = True
frame = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # simulación más lenta que render
    if frame % 2 == 0:
        world.tick()

    screen.fill((0, 0, 0))
    renderer.draw_world(screen, world)

    pygame.display.flip()
    clock.tick(60)
    frame += 1

pygame.quit()
