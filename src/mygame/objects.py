import math
import pygame

class GameComponent(object):

    #def __init__(self):
    #    self._destroyed = False

    #@property
    #def destroyed(self):
    #    return self._destroyed

    def update(self, game, milliseconds): pass

    def draw(self, game, surface, milliseconds): pass

    def is_destroyed(self):
        return False

    #def hit(self, damage): pass

class Coin(GameComponent):

    def __init__(self, coord):
        self.location = coord
        self._destroyed = False

    def hit(self, damage):
        self._destroyed = True

    def collect(self):
        self._destroyed = True

    def is_destroyed(self):
        return self._destroyed

    def draw(self, game, surface, milliseconds):
        x = int(game.cell_size[0] * (self.location[0] + 0.5))
        y = int(game.cell_size[1] * (self.location[1] + 0.5))
        pygame.draw.circle(surface, (255, 255, 0), (x, y), 2)


class Bomb(GameComponent):

    def __init__(self, coord, time_to_explode=3000, max_damage=2.0):
        #self.game = game
        self.location = coord
        self.time_to_explode = time_to_explode
        self.max_damage = max_damage

    @property
    def explosion_radius(self):
        return (8 * self.max_damage) ** 0.5

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
                    damage = self.max_damage * (1 - (d / r) ** 2)
                    yield ((x, y), damage)

    def hit(self, damage):
        self.time_to_explode = 0

    def is_destroyed(self):
        return self.time_to_explode <= 0

    def update(self, game, milliseconds):

        self.time_to_explode -= milliseconds

        if not self.is_exploding():
            return

        for coord, damage in self.get_damaged_cells():
            cell = game.map(coord)
            if cell:

                # Damage map
                cell.hit(damage)

                # Damage coins
                for coin in game.coins:
                    if not coin.is_destroyed():
                        if coin.location == coord:
                            coin.hit(damage)

                # Damage monsters
                killed_monsters = []
                for monster in game.monsters:
                    if monster.location == coord:
                        monster.hit(damage)
                        if monster.is_dead():
                            killed_monsters.append(monster)
                for monster in killed_monsters:
                    game.monsters.remove(monster)

        game.bombs.remove(self)

    def draw(self, game, surface, milliseconds):
        x = int(game.cell_size[0] * (self.location[0] + 0.5))
        y = int(game.cell_size[1] * (self.location[1] + 0.5))
        if self.time_to_explode % 1000 <= 500:
            color = (255, 0, 0)
        else:
            color = (128, 0, 0)
        pygame.draw.circle(surface, color, (x, y), 4)
