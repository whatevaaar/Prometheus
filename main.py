import os
import time

from render import render_world
from world.world import World

WIDTH = 70
HEIGHT = 30

TICK_TIME = 0.5  # segundos

world = World(width=WIDTH, height=HEIGHT)
os.system("cls" if os.name == "nt" else "clear")

while True:
    world.tick()
    render_world(world)
    time.sleep(TICK_TIME)
