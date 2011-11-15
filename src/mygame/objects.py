import math

class Bomb(object):

    def __init__(self, coord, time_to_explode):
        self.location = coord
        self.time_to_explode = time_to_explode
        self.explosion_radius = 3.0
        self.max_damage = 1.0

    def update(self, milliseconds):
        self.time_to_explode -= milliseconds

    def is_exploding(self):
        return self.time_to_explode <= 0

    def get_damaged_cells(self):

        r = self.explosion_radius
        ri = int(math.ceil(self.explosion_radius))

        for dx in xrange(-ri, ri + 1):
            for dy in xrange(-ri, ri + 1):
                d = math.sqrt(dx ** 2 + dy ** 2)
                if d <= r:
                    x = self.location[0] + dx
                    y = self.location[1] + dy
                    damage = self.max_damage * (d / r)
                    yield ((x, y), damage)
