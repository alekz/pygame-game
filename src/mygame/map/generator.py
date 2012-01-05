import random

from mygame.map import Cell

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
                    cell_type = Cell.STONE
                else:
                    cell_type = Cell.FLOOR
                map_(x, y).type = cell_type

class MazeGenerator(MapGenerator):

    def generate(self, map_):

        # Maze size, which is about twice as small as the final map
        w = int((map_.size[0] - 1) / 2)
        h = int((map_.size[1] - 1) / 2)

        # Pre-fill map with start pattern
        for x in xrange(map_.size[0]):
            for y in xrange(map_.size[1]):
                if x in (0, map_.size[0] - 1) or y in (0, map_.size[1] - 1):
                    map_(x, y).type = Cell.WALL
                else:
                    map_(x, y).type = Cell.STONE
        for x in xrange(w):
            for y in xrange(h):
                map_(2 * x + 1, 2 * y + 1).type = Cell.FLOOR

        # Generate list of all maze cells
        cells = {}
        for x in xrange(w):
            for y in xrange(h):
                cells[(x, y)] = True

        # Generate random rooms
        rooms = []
        for _ in xrange(1):
            d = 1  # Minimum distance from map borders
            rw = int(w / 3)
            rh = int(h / 3)
            rx = random.randint(d, w - rw - d)
            ry = random.randint(d, h - rh - d)
            for x in xrange(rx, rx + rw):
                for y in xrange(ry, ry + rh):
                    cells[(x, y)] = False
            rooms.append((rw, rh, rx, ry))

        # Choose start cell
        while True:
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)
            c = (x, y)
            if cells[c]:
                break

        visited_cells = [c]
        cells[c] = False

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
                map_(nx, ny).type =  Cell.FLOOR

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
            map_(x, y).type = Cell.FLOOR

        # Draw rooms

        # Walls
        for rw, rh, rx, ry in rooms:
            for x in xrange(2 * rx, 2 * (rx + rw) + 1):
                for y in xrange(2 * ry, 2 * (ry + rh) + 1):
                    map_(x, y).type = Cell.STONE
        # Floor
        for rw, rh, rx, ry in rooms:
            for x in xrange(2 * rx + 1, 2 * (rx + rw)):
                for y in xrange(2 * ry + 1, 2 * (ry + rh)):
                    map_(x, y).type = Cell.FLOOR
        # Doors
        for rw, rh, rx, ry in rooms:
            d = 1
            doors = [
                     (2 * random.randint(rx + d, rx + rw - 1 - d) + 1, 2 * ry),
                     (2 * random.randint(rx + d, rx + rw - 1 - d) + 1, 2 * (ry + rh)),
                     (2 * rx, 2 * random.randint(ry + d, ry + rh - 1 - d) + 1),
                     (2 * (rx + rw), 2 * random.randint(ry + d, ry + rh - 1 - d) + 1),
                     ]
            for door_coord in doors:
                map_(door_coord).type = Cell.FLOOR
