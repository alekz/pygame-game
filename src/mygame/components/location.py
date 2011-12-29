import math
from mygame.types import direction
from mygame.components import Component
from mygame.messages import Message


class LocationComponent(Component):
    pass


class StaticLocationComponent(LocationComponent):

    def __init__(self, coord=(0, 0)):
        self.c = coord

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y

    @property
    def c(self):
        return (self.x, self.y)

    @c.setter
    def c(self, (x, y)):
        self.x = x
        self.y = y

    xr = xt = xs = x

    yr = yt = ys = y

    cr = ct = cs = c


class MovingLocationComponent(LocationComponent):

    def __init__(self, coord=(0.0, 0.0), speed=0.0, direction_=direction.NONE):
        self.c = coord
        self.speed = speed
        self._direction = direction_
        self._next_direction = direction.NONE

    # == Real coordinates ==

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y

    @property
    def c(self):
        return (self.x, self.y)

    @c.setter
    def c(self, (x, y)):
        self.x = x
        self.y = y

    # == Rounded coordinates ==

    @property
    def xr(self):
        return int(round(self.x))

    @property
    def yr(self):
        return int(round(self.y))

    @property
    def cr(self):
        return (self.xr, self.yr)

    # == Target coordinates ==

    @property
    def xt(self):
        if self.direction == direction.LEFT:
            return int(math.floor(self.x))
        if self.direction == direction.RIGHT:
            return int(math.ceil(self.x))
        return self.xr

    @property
    def yt(self):
        if self.direction == direction.UP:
            return int(math.floor(self.y))
        if self.direction == direction.DOWN:
            return int(math.ceil(self.y))
        return self.yr

    @property
    def ct(self):
        return (self.xt, self.yt)

    # == Source coordinates ==

    @property
    def xs(self):
        if self.direction == direction.LEFT:
            return int(math.ceil(self.x))
        if self.direction == direction.RIGHT:
            return int(math.floor(self.x))
        return self.xr

    @property
    def ys(self):
        if self.direction == direction.UP:
            return int(math.ceil(self.y))
        if self.direction == direction.DOWN:
            return int(math.floor(self.y))
        return self.yr

    @property
    def cs(self):
        return (self.xs, self.ys)

    # == Direction ==

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, direction_):
        self._next_direction = direction_

    # == Movement ==

    def update(self, game, entity):

        if self._direction == self._next_direction == direction.NONE:  # Don't move!
            return

        # Change direction to the opposite
        if direction.is_opposite(self._direction, self._next_direction):
            self._direction = self._next_direction

        # Start moving, but first check for collisions
        if self._direction == direction.NONE:
            target_coord = direction.get_adjacent_coord(self.cs, self._next_direction)
            if game.map.can_move_to(target_coord):
                self._direction = self._next_direction
            else:
                # Collision: can't move
                self._direction = self._next_direction = direction.NONE
                return

        # i - Axis index: 0 (left/right) or 1 (up/down)
        # sign - "Negative" (left/up) or "positive" (right/down) directionS
        i, sign = direction.get_info(self._direction)

        # Remember previous source cell
        cs_old = self.cs

        # Update our location
        delta = sign * self.speed * game.seconds
        c = [self.x, self.y]
        c[i] += delta
        self.c = c

        # Check if should stop
        has_changed_cell = cs_old != self.cs
        if has_changed_cell:

            # Update current direction
            self._direction = self._next_direction

            # Check if should stop; either because no more input or collision
            stop = (self._direction == direction.NONE) or not game.map.can_move_to(self.ct)
            if stop:
                self.c = self.cr  # Reset location to the nearest cell
                self._direction = direction.NONE

            # Notice other components about new location
            entity.send_message(game, Message.CHANGE_LOCATION, coord=self.cs, old_coord=cs_old)

        self._next_direction = direction.NONE
