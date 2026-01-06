from naming.name_generator import generate_name


class Settlement:
    def __init__(self, x, y, born):
        self.name = generate_name()
        self.x = x
        self.y = y
        self.born = born

        self.population = 0
        self.stability = 1.0
        self.alive = True

    def symbol(self):
        return "⌂"
