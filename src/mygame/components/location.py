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

        # Start moving or change direction to the opposite
        if self._direction == direction.NONE or direction.is_opposite(self._direction, self._next_direction):
            self._direction = self._next_direction

        # i - Axis index: 0 (left/right) or 1 (up/down)
        # sign - "Negative" (left/up) or "positive" (right/down) directionS
        i, sign = direction.get_info(self._direction)

        # Remember previous source cell
        ct_old = self.ct
        cs_old = self.cs

        # Update our location
        delta = sign * self.speed * game.seconds
        c = [self.x, self.y]
        c[i] += delta
        self.c = c

        # Indicates whether a new direction should be read from input
        update_direction = False

        # Moving to a new cell, check for collisions
        is_colliding = False
        if ct_old != self.ct and not game.map.can_move_to(self.ct):
            self.c = ct_old
            update_direction = True
            is_colliding = True

        # Reached new cell
        if cs_old != self.cs:
            # Notice other components about new location
            entity.send_message(game, Message.CHANGE_LOCATION, coord=self.cs, old_coord=cs_old)
            update_direction = True

        if update_direction:
            if self._direction != self._next_direction:
                self.c = self.cr
            self._direction = self._next_direction

        if self._direction != direction.NONE:
            entity.set_state('moving')
        else:
            entity.unset_state('moving')

        if is_colliding and self._direction != direction.NONE:
            entity.set_state('colliding')
        else:
            entity.unset_state('colliding')
