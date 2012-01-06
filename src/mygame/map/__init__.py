import random
import pygame
#from mygame.objects import GameComponent

class Cell(object):

    FLOOR = 0
    WALL = 1
    STONE = 2
    ROCK = 3

    type_properties = {
        # passable, durability, health
        FLOOR: (True, None, 0),
        WALL: (False, None, 0),
        STONE: (False, 0, 1),
        ROCK: (False, 1, 1),
    }

    updated_cells = []

    def __init__(self, coord, cell_type=FLOOR):
        """
        cell_type (int)
            Visual representation of the cell, affects only rendering
        passable (bool)
            If Player or NPCs can walk through this cell
        durability (float)
            How hard it is to destroy the cell:
            None - Can't destroy
            0 - Basic durability
            1+ - Harder to destroy, not every kind of damage can do it
        health (float)
            How much damage is required to destroy the cell (is not affected
            when durability is None)
            <0 - Destroyed
            0 - Not destroyed, but any damage will destroy it
            >0 - Not destroyed
        """
        self.coord = coord
        self.type = cell_type
        self.passable = False
        self.durability = None
        self.health = 0
        self.change_to(cell_type)
        self.redraw()

    def change_to(self, cell_type):
        self.type = cell_type
        if not self.type_properties.has_key(cell_type):
            return
        self.passable, self.durability, self.health = self.type_properties[cell_type]

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
            return (255, 255, 255)

        if self.type == Cell.ROCK:
            health = max(min(self.health, 1.0), 0.0)
            color = 64 + health * (192 - 64)
            return (color, color, color)

        if self.type == Cell.STONE:
            health = max(min(self.health, 1.0), 0.0)
            color = 64 + health * (160 - 64)
            return (color, int(color * 0.9), int(color * 0.7))

        return (0, 0, 0)

    def hit(self, damage):

        if self.durability is None:
            return

        self.health -= damage
        if self.health < 0:
            self.change_to(Cell.FLOOR)

        self.redraw()

    def redraw(self):
        Cell.updated_cells.append(self)

    def draw(self, game, surface):
        rect = pygame.rect.Rect(self.x * game.cell_size[0],
                                self.y * game.cell_size[1],
                                game.cell_size[0],
                                game.cell_size[1])
        pygame.draw.rect(surface, self.color, rect)

class Map(object):

    def __init__(self, game, size, map_generator):

        self.game = game
        self.size = size

        # Generate empty map
        self.cells = [[Cell((x, y)) for y in xrange(self.height)] for x in xrange(self.width)]

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
            return self(coord).passable
        else:
            return False

    def get_cells(self, cell_types=None):
        if cell_types is None:
            cells = (self(x, y) for x in xrange(self.width)
                                for y in xrange(self.height))
        else:
            if not hasattr(cell_types, '__iter__'):
                cell_types = [cell_types]
            cells = (self(x, y) for x in xrange(self.width)
                                for y in xrange(self.height)
                                if self(x, y).type in cell_types)
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

    def draw(self, game, surface):
        for cell in Cell.updated_cells:
            cell.draw(game, surface)
        Cell.updated_cells = []
