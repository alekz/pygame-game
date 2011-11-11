import random
import pygame

from mygame.player import controls
from mygame.types import direction

class Player(object):

    def __init__(self, game, controls):
        self.game = game
        self.direction = direction.NONE
        self.location = (0, 0) # Cell coordinates within a map
        self.offset = (0, 0) # Offset within a cell, -1.0..1.0
        self.speed = 5.0 # Cells per second
        self.location_changed = False

        if controls is None:
            controls = controls.NoMovementControls()
        self.set_controls(controls)

    def set_controls(self, controls):
        controls.set_player(self)
        self.controls = controls

    def set_location(self, coord):
        self._location = [coord[0], coord[1]]
    def get_location(self):
        return tuple(self._location)
    location = property(get_location, set_location)

    def set_offset(self, coord):
        self._offset = [float(coord[0]), float(coord[1])]
    def get_offset(self):
        return tuple(self._offset)
    offset = property(get_offset, set_offset)

    def update(self, milliseconds):

        self.location_changed = False

        new_direction = self.controls.get_movement_direction()

        if new_direction != direction.NONE:

            if self.direction == direction.NONE:
                # Start moving, but first check if it is allowed
                new_location = self._location[:]
                i, k = direction.get_info(new_direction)
                new_location[i] += k
                if not self.game.map.can_move_to(new_location):
                    new_direction = direction.NONE
                else:
                    self.direction = new_direction

            elif direction.is_opposite(new_direction, self.direction):
                # Move to the opposite direction (should always be allowed)
                i, k = direction.get_info(self.direction)
                self._location[i] += k
                self._offset[i] -= k
                self.direction = new_direction

        # Move to one of directions
        if self.direction != direction.NONE:

            i, k = direction.get_info(self.direction)

            # Move a bit
            self._offset[i] += k * self.speed * milliseconds / 1000.0

            # Check if moved outside of the current cell, i.e. player's location has changed
            if abs(self._offset[i]) >= 1.0:

                self.location_changed = True

                # Moved to a neighbouring cell
                self._location[i] += k
                self._offset[i] -= k

                # Check if further movement is possible: stop if key is not
                # pressed anymore or if there is an obstacle
                stop = False
                if new_direction == direction.NONE:
                    stop = True
                else:
                    new_location = self._location[:]
                    new_location[i] += k
                    if not self.game.map.can_move_to(new_location):
                        stop = True
                if stop:
                    self._offset[i] = 0.0
                    self.direction = direction.NONE
