import random

class Cell(object):

    FLOOR = 0
    WALL = 1

    def __init__(self, coord, cell_type=FLOOR, health=1.0):
        self.coord = coord
        self.type = cell_type
        self.health = health

    @property
    def x(self):
        return self.coord[0]

    @property
    def y(self):
        return self.coord[1]

    @property
    def color(self):
        if self.type == Cell.FLOOR:
            return (16, 16, 0)
        if self.type == Cell.WALL:
            health = max(min(self.health, 1.0), 0.0)
            color = 64 + health * (192 - 64)
            return (color, color, color)
        return (0, 0, 0)

    def hit(self, damage):
        if self.type == Cell.WALL:
            self.health -= damage
            if self.health <= 0:
                self.type = Cell.FLOOR

class Map(object):

    def __init__(self, game, size, map_generator):

        self.game = game
        self.size = size

        # Generate empty map
        self.cells = [[Cell((x, y)) for y in xrange(self.height)] for x in xrange(self.width)]

        # List of colors for each cell type
        self.colors = {
                       Cell.FLOOR: (  0,   0,   0),
                       Cell.WALL:  (128, 128, 128),
                       }

        # Generate random map
        map_generator.generate(self)

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    def __call__(self, x, y=None):

        if hasattr(x, '__iter__'):
            x, y = x

        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[x][y]
        else:
            return None

    def can_move_to(self, coord):
        if (0 <= coord[0] < self.width) and (0 <= coord[1] < self.height):
            return self(coord).type == Cell.FLOOR
        else:
            return False

    def get_cells(self, cell_type=None):
        if cell_type is None:
            cells = (self(x, y) for x in xrange(self.width)
                                for y in xrange(self.height))
        else:
            cells = (self(x, y) for x in xrange(self.width)
                                for y in xrange(self.height)
                                if self(x, y).type == cell_type)
        return cells

    def get_random_cell(self, cell_type=None):
        return random.choice(list(self.get_cells(cell_type)))

    def get_adjacent_cells(self, coord, cell_type=None):

        adjacent_cells = []

        for dx, dy in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
            adjacent_coord = (coord[0] + dx, coord[1] + dy)
            adjacent_cell = self(adjacent_coord)
            if adjacent_cell is not None:
                if cell_type in (None, adjacent_cell.type):
                    adjacent_cells.append(adjacent_cell)

        return adjacent_cells
