import random

class Map(object):

    CELL_TYPE_FLOOR = 0
    CELL_TYPE_WALL = 1

    def __init__(self, game, size, map_generator):
        self.game = game
        self.size = size

        # Generate empty map
        empty_col = [0] * self.height
        self.cells = [empty_col[:] for _ in xrange(self.width)]

        # List of colors for each cell type
        self.colors = {
                       Map.CELL_TYPE_FLOOR: (  0,   0,   0),
                       Map.CELL_TYPE_WALL:  (128, 128, 128),
                       }

        # Generate random map
        map_generator.generate(self)

    def get_width(self):
        return self.size[0]
    width = property(get_width)

    def get_height(self):
        return self.size[1]
    height = property(get_height)

    def get_cell(self, coord):
        x, y = coord
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[x][y]
        else:
            return None

    def set_cell(self, coord, cell_type):
        x, y = coord
        self.cells[x][y] = cell_type

    def can_move_to(self, coord):
        if (0 <= coord[0] < self.width) and (0 <= coord[1] < self.height):
            return self.get_cell(coord) == Map.CELL_TYPE_FLOOR
        else:
            return False

    def get_random_cell(self, cell_type=None):
        cells = ((x, y) for x in xrange(self.width) for y in xrange(self.height))
        if type:
            cells = (cell for cell in cells if self.get_cell(cell) == cell_type)
        return random.choice(list(cells))

    def get_adjacent_cells(self, coord, cell_type=None):

        adjacent_cells = []

        for dx, dy in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
            adjacent_coord = (coord[0] + dx, coord[1] + dy)
            adjacent_cell = self.get_cell(adjacent_coord)
            if adjacent_cell is not None:
                if cell_type in (None, adjacent_cell):
                    adjacent_cells.append(adjacent_coord)

        return adjacent_cells
