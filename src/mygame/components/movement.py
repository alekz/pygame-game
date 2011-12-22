import math

from mygame.types import direction
from mygame.components import Component

class MovementComponent(Component):

    def __init__(self, speed=0, direction_=direction.NONE):
        """
        speed      float  Movement speed, map cells per second
        direction  int    Movement direction (one of direction.* values)
        """
        self.speed = speed
        self.direction = direction_
        self._delta = 0.0  # distance moved during latest update
        self._previous_direction = direction.NONE

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = float(value)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value

    @property
    def delta(self):
        return self._delta

    def update(self, game, entity):

        # Get location component; it is required in order to proceed
        try:
            location = entity.components[Component.LOCATION]
        except KeyError:
            return

        # Calculate the actual movement direction: it will not necessary be the
        # input direction specified by other components
        werent_moving = self._previous_direction == direction.NONE
        reverting_direction = direction.is_opposite(self.direction, self._previous_direction)
        if werent_moving or reverting_direction:
            # Accept input only if weren't moving before, or requested movement
            # to the opposite direction
            d = self.direction
            stop_at_new_cell = False
        else:
            # Continue previous movement until new cell is reached
            d = self._previous_direction
            stop_at_new_cell = True

        # No movement
        if d == direction.NONE:
            self._delta = 0.0
            return

        # "Negative" (left/up) or "positive" (right/down) direction?
        sign = direction.get_sign(d)

        # Axis index: 0 (left/right) or 1 (up/down)
        i = direction.get_index(d)

        # How far have we moved?
        delta = sign * self.speed * game.seconds

        # Calculate new location
        zc_old = location.coord[i]
        z = location.location[i] + delta
        zc = self._round_location(d, z)
        zo = z - zc

        # Check if new cell was reached
        changed_cell = zc_old != zc

        # Check if we should stop here and not move anymore
        if changed_cell:

            # Check if further movement is possible
            if not stop_at_new_cell:
                new_coord = list(location.coord)
                new_coord[i] = zc
                if not game.map.can_move_to(new_coord):
                    stop_at_new_cell = True

            # Stop
            if stop_at_new_cell:
                zc = int(round(z))
                zo = 0.0
                d = direction.NONE

        # Update location
        if i == 0:
            location.x = (zc, zo)
        else:
            location.y = (zc, zo)

        self._previous_direction = d

    def _round_location(self, direction_, x):
        round_functions = {
            direction.LEFT: math.floor,
            direction.UP: math.floor,
            direction.RIGHT: math.ceil,
            direction.DOWN: math.ceil,
            direction.NONE: float,  # Is there a function that just returns its input value?
        }
        f = round_functions[direction_]
        return int(f(x))
