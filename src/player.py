import pygame

class Player(object):

    STANDING = 0
    LEFT = 1
    RIGHT = 2
    UP = 4
    DOWN = 8

    def __init__(self, game):
        self.game = game
        self.state = Player.STANDING
        self.location = [0, 0] # Cell coordinates within a map
        self.offset = [0.0, 0.0] # Offset within a cell, -1.0..1.0
        self.speed = 5.0 # Cells per second

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

    def _get_new_movement_state(self):

        # Check, which player control keys are pressed
        keys = pygame.key.get_pressed()
        key_left  = keys[pygame.K_LEFT]
        key_right = keys[pygame.K_RIGHT]
        key_up    = keys[pygame.K_UP]
        key_down  = keys[pygame.K_DOWN]

        # Calculate the next movement state
        states = [
                  (key_left,  key_right, Player.LEFT  ),
                  (key_right, key_left,  Player.RIGHT ),
                  (key_up,    key_down,  Player.UP    ),
                  (key_down,  key_up,    Player.DOWN  ),
                  ]

        for (key, opposite_key, state) in states:
            if key and not opposite_key:
                if self.state in (Player.STANDING, self._get_opposite_direction()):
                    return state

        return Player.STANDING


    def update(self, milliseconds):

        new_state = self._get_new_movement_state()

        if new_state != Player.STANDING:

            if self.state == Player.STANDING:
                # Start moving, but first check if it is allowed
                new_location = self.location[:]
                i, k = self._get_direction_info(new_state)
                new_location[i] += k
                if not self.game.map.can_move_to(new_location):
                    new_state = Player.STANDING

            elif self._is_opposite_direction(new_state, self.state):
                # Move to the opposite direction (should always be allowed)
                # Direction   K  Before    After
                # L -> R     -1  10; -0.2   9; +0.8
                # R -> L     +1  10; +0.2  11; -0.8
                i, k = self._get_direction_info()
                self.location[i] += k
                self.offset[i] -= k

        # Move to one of directions
        if self.state == Player.STANDING:
            self.state = new_state
        if self.state != Player.STANDING:

            i, k = self._get_direction_info()

            # Move a bit
            self.offset[i] += k * self.speed * milliseconds / 1000.0

            # Check if moved outside of the current cell
            if abs(self.offset[i]) >= 1.0:

                # Moved to a neighbouring cell
                self.location[i] += k
                self.offset[i] -= k

                # Check if further movement is possible: stop if key is not
                # pressed anymore or if there is an obstacle
                stop = False
                if new_state == Player.STANDING:
                    stop = True
                else:
                    new_location = self.location[:]
                    new_location[i] += k
                    if not self.game.map.can_move_to(new_location):
                        stop = True
                if stop:
                    self.offset[i] = 0.0
                    self.state = Player.STANDING
