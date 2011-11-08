import random

from mygame.map import Map

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

