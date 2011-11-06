import random

class Map(object):

    def __init__(self, game, size):
        self.game = game
        self.size = size

        # Generate empty map
        empty_col = [0] * self.size[1]
        self.cells = [empty_col[:] for _ in xrange(self.size[0])]

        # Generate random map
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                self.cells[x][y] = random.choice((0, 0, 0, 1))

        # List of colors for each cell type
        self.colors = {
                            0: (  0,   0,   0),
                            1: (128, 128, 128),
                            }

    def get_cell(self, x, y=None):
        assert (type(x) == int and type(y) == int) or (hasattr(x, '__iter__') and len(x) == 2 and y is None)
        if hasattr(x, '__iter__'):
            x, y = x
        try:
            return self.cells[x][y]
        except IndexError:
            return None

    def can_move_to(self, x, y=None):
        cell = self.get_cell(x, y)
        return cell == 0
