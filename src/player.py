import random
import pygame

class PlayerControls(object):

    def __init__(self, game):
        self.game = game
        self.player = None

    def set_player(self, player):
        self.player = player

    def update(self, milliseconds):
        pass

    def get_movement_direction(self):
        raise NotImplementedError


class NoMovementControls(PlayerControls):

    def get_movement_direction(self):
        return Player.STANDING


class HumanPlayerControls(PlayerControls):

    def get_movement_direction(self):

        # Check, which player control keys are pressed
        keys = pygame.key.get_pressed()
        key_left  = keys[pygame.K_LEFT]
        key_right = keys[pygame.K_RIGHT]
        key_up    = keys[pygame.K_UP]
        key_down  = keys[pygame.K_DOWN]

        # Calculate the next movement state
        states = [
                  (key_left,  key_right, Player.LEFT,  Player.RIGHT ),
                  (key_right, key_left,  Player.RIGHT, Player.LEFT  ),
                  (key_up,    key_down,  Player.UP,    Player.DOWN  ),
                  (key_down,  key_up,    Player.DOWN,  Player.UP    ),
                  ]

        for (key, opposite_key, direction, opposite_direction) in states:
            if key and not opposite_key:
                if self.player.state in (Player.STANDING, opposite_direction):
                    return direction

        return Player.STANDING


class RandomMovementControls(PlayerControls):

    def get_movement_direction(self):

        if self.player.state == Player.STANDING:

            possible_directions = [
                                   (Player.LEFT,  -1,  0),
                                   (Player.RIGHT, +1,  0),
                                   (Player.UP,     0, -1),
                                   (Player.DOWN,   0, +1),
                                   ]

            allowed_states = []

            for state, dx, dy in possible_directions:
                location = (self.player.location[0] + dx, self.player.location[1] + dy)
                if self.game.map.can_move_to(location):
                    allowed_states.append(state)

            if allowed_states:
                return random.choice(allowed_states)

        return Player.STANDING

class Player(object):

    STANDING = 0
    LEFT = 1
    RIGHT = 2
    UP = 4
    DOWN = 8

    def __init__(self, game, controls):
        self.game = game
        self.state = Player.STANDING
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

    def _get_opposite_direction(self, direction=None):
        direction = direction or self.state
        return {
                Player.LEFT:  Player.RIGHT,
                Player.RIGHT: Player.LEFT,
                Player.UP:    Player.DOWN,
                Player.DOWN:  Player.UP,
                }.get(direction, direction)

    def _is_opposite_direction(self, direction1, direction2):
        return self._get_opposite_direction(direction1) == direction2

    def _get_direction_sign(self, direction=None):
        direction = direction or self.state
        return {
                Player.LEFT:  -1,
                Player.RIGHT: +1,
                Player.UP:    -1,
                Player.DOWN:  +1,
                }.get(direction, 0)

    def _get_direction_index(self, direction=None):
        direction = direction or self.state
        return {
                Player.LEFT:  0,
                Player.RIGHT: 0,
                Player.UP:    1,
                Player.DOWN:  1,
                }.get(direction)

    def _get_direction_info(self, direction=None):
        return (self._get_direction_index(direction), self._get_direction_sign(direction))

    def update(self, milliseconds):

        self.controls.update(milliseconds)

        new_state = self.controls.get_movement_direction()

        if new_state != Player.STANDING:

            if self.state == Player.STANDING:
                # Start moving, but first check if it is allowed
                new_location = self._location[:]
                i, k = self._get_direction_info(new_state)
                new_location[i] += k
                if not self.game.map.can_move_to(new_location):
                    new_state = Player.STANDING
                else:
                    self.state = new_state

            elif self._is_opposite_direction(new_state, self.state):
                # Move to the opposite direction (should always be allowed)
                # Direction   K  Before    After
                # L -> R     -1  10; -0.2   9; +0.8
                # R -> L     +1  10; +0.2  11; -0.8
                i, k = self._get_direction_info()
                self._location[i] += k
                self._offset[i] -= k
                self.state = new_state

        # Move to one of directions
        if self.state != Player.STANDING:

            i, k = self._get_direction_info()

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
                if new_state == Player.STANDING:
                    stop = True
                else:
                    new_location = self._location[:]
                    new_location[i] += k
                    if not self.game.map.can_move_to(new_location):
                        stop = True
                if stop:
                    self._offset[i] = 0.0
                    self.state = Player.STANDING
