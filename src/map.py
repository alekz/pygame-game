import random

class MapGenerator(object):
    def generate(self, map_):
        raise NotImplementedError

class RandomMapGenerator(MapGenerator):
    def generate(self, map_):
        width, height = map_.size
        for x in xrange(width):
            for y in xrange(height):
                r = random.randint(0, 3)
                if r == 0:
                    cell = Map.CELL_TYPE_WALL
                else:
                    cell = Map.CELL_TYPE_FLOOR
                map_.set_cell((x, y), cell)

class Map(object):

    CELL_TYPE_FLOOR = 0
    CELL_TYPE_WALL = 1

    def __init__(self, game, size, map_generator):
        self.game = game
        self.size = size

        # Generate empty map
        empty_col = [0] * self.size[1]
        self.cells = [empty_col[:] for _ in xrange(self.size[0])]

        # List of colors for each cell type
        self.colors = {
                       Map.CELL_TYPE_FLOOR: (  0,   0,   0),
                       Map.CELL_TYPE_WALL:  (128, 128, 128),
                       }

        # Generate random map
        map_generator.generate(self)

    def get_cell(self, coord):
        x, y = coord
        return self.cells[x][y]

    def set_cell(self, coord, cell_type):
        x, y = coord
        self.cells[x][y] = cell_type

    def can_move_to(self, coord):
        if (0 <= coord[0] < self.size[0]) and (0 <= coord[1] < self.size[1]):
            return self.get_cell(coord) == Map.CELL_TYPE_FLOOR
        else:
            return False
