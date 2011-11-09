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

class MazeGenerator(MapGenerator):

    def generate(self, map_):

        # Maze size, which is about twice as small as the final map
        w = int((map_.size[0] - 1) / 2)
        h = int((map_.size[1] - 1) / 2)

        # Pre-fill map with start pattern
        for x in xrange(map_.size[0]):
            for y in xrange(map_.size[1]):
                map_.set_cell((x, y), Map.CELL_TYPE_WALL)
        for x in xrange(w):
            for y in xrange(h):
                map_.set_cell((2 * x + 1, 2 * y + 1), Map.CELL_TYPE_FLOOR)

        # Generate list of all maze cells
        cells = {}
        for x in xrange(w):
            for y in xrange(h):
                cells[(x, y)] = True

        # Choose start cell
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        c = (x, y)

        visited_cells = [c]
        cells[c] = True

        while visited_cells:

            # Choose one cell from the list
            c = visited_cells[-1]
            #c = random.choice(visited_cells)
            #c = visited_cells[0]

            # Get cell's neighbours
            neighbours = []
            for dx, dy in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
                x = c[0] + dx
                y = c[1] + dy
                if cells.get((x, y), False):
                    neighbours.append((x, y))

            if neighbours:

                # Choose random neighbour and add to the list
                nc = random.choice(neighbours)
                visited_cells.append(nc)
                cells[nc] = False

                # Connect two cells on the map
                nx = c[0] + nc[0] + 1
                ny = c[1] + nc[1] + 1
                map_.set_cell((nx, ny), Map.CELL_TYPE_FLOOR)

            # Remove cell if it does't have unvisited neighbours anymore
            if len(neighbours) <= 1:
                visited_cells.remove(c)

        # Add random holes to the maze
        for _ in xrange(w * h / 2):
            if random.randint(0, 1) == 1:
                x = 2 * random.randint(1, w - 1)
                y = 2 * random.randint(1, h) - 1
            else:
                x = 2 * random.randint(1, w) - 1
                y = 2 * random.randint(1, h - 1)
            map_.set_cell((x, y), Map.CELL_TYPE_FLOOR)
