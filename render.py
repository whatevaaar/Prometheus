import sys


def trim(text, width):
    return text[:width].ljust(width)


def render_world(world):
    sys.stdout.write("\x1b[H")

    panel_width = 52
    separator = " │ "

    grid = [[tile.char() for tile in row] for row in world.tiles]

    for entity in world.entities:
        grid[entity.y][entity.x] = entity.symbol()

    events = list(world.event_log.events)

    for y in range(world.height):
        map_line = "".join(grid[y])

        ui = ""
        if y == 0:
            ui = f"Edad: {world.age}"
        elif y == 2:
            ui = f"Población: {len(world.entities)} 🧍"
        elif y == 4:
            ui = "Eventos"
        elif 5 <= y < 5 + len(events):
            ui = events[y - 5]

        ui = trim(ui, panel_width)
        print(map_line + separator + ui)

    sys.stdout.flush()
