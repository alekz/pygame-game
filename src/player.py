import random
import pygame
from game.types import direction

class PlayerControls(object):

    def __init__(self, game):
        self.game = game
        self.player = None
        self.init()

    def init(self): pass

    def set_player(self, player):
        self.player = player

    def update(self, milliseconds):
        pass

    def get_movement_direction(self):
        raise NotImplementedError


class NoMovementControls(PlayerControls):

    def get_movement_direction(self):
        return direction.NONE


class HumanPlayerControls(PlayerControls):

    def get_movement_direction(self):

        # Check, which player control keys are pressed
        keys = pygame.key.get_pressed()
        key_left  = keys[pygame.K_LEFT]
        key_right = keys[pygame.K_RIGHT]
        key_up    = keys[pygame.K_UP]
        key_down  = keys[pygame.K_DOWN]

        # Calculate the next movement direction
        directions = [
                  (key_left,  key_right, direction.LEFT,  direction.RIGHT ),
                  (key_right, key_left,  direction.RIGHT, direction.LEFT  ),
                  (key_up,    key_down,  direction.UP,    direction.DOWN  ),
                  (key_down,  key_up,    direction.DOWN,  direction.UP    ),
                  ]

        for (key, opposite_key, current_direction, opposite_direction) in directions:
            if key and not opposite_key:
                if self.player.direction in (direction.NONE, opposite_direction):
                    return current_direction

        return direction.NONE


class RandomMovementControls(PlayerControls):

    def init(self):
        self.last_direction = direction.NONE

    def get_movement_direction(self):

        new_direction = direction.NONE

        if self.player.direction == direction.NONE:

            possible_directions = [
                                   (direction.LEFT,  -1,  0),
                                   (direction.RIGHT, +1,  0),
                                   (direction.UP,     0, -1),
                                   (direction.DOWN,   0, +1),
                                   ]

            allowed_directions = []

            for possible_direction, dx, dy in possible_directions:
                location = (self.player.location[0] + dx, self.player.location[1] + dy)
                if self.game.map.can_move_to(location):
                    if possible_direction == self.last_direction:
                        weight = 10
                    elif possible_direction == direction.get_opposite(self.last_direction):
                        weight = 1
                    else:
                        weight = 3
                    allowed_directions.append((weight, possible_direction))

            if allowed_directions:
                total_weight = sum(weight for weight, _ in allowed_directions)
                r = random.randint(0, total_weight - 1)
                for weight, new_direction in allowed_directions:
                    if r < weight:
                        break
                    r -= weight

            self.last_direction = new_direction

        return new_direction

class Player(object):

    def __init__(self, game, controls):
        self.game = game
        self.direction = direction.NONE
        self.location = (0, 0) # Cell coordinates within a map
        self.offset = (0, 0) # Offset within a cell, -1.0..1.0
        self.speed = 5.0 # Cells per second

        if controls is None:
            controls = NoMovementControls()
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

        self.controls.update(milliseconds)

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

            # Check if moved outside of the current cell
            if abs(self._offset[i]) >= 1.0:

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
