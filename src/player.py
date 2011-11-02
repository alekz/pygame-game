import pygame

class Player(object):

    STANDING = 0
    LEFT = 1
    RIGHT = 2
    UP = 4
    DOWN = 8

    def __init__(self):
        self.state = Player.STANDING
        self.location = [0, 0] # Cell coordinates within a map
        self.offset = [0.0, 0.0] # Offset within a cell, -1.0..1.0
        self.speed = 5.0 # Cells per second

    def update(self, milliseconds):

        # Check, which player control keys are pressed
        keys = pygame.key.get_pressed()
        key_left  = keys[pygame.K_LEFT]
        key_right = keys[pygame.K_RIGHT]
        key_up    = keys[pygame.K_UP]
        key_down  = keys[pygame.K_DOWN]

        # Calculate the next movement state
        states = [
                  (0, -1, key_left,  key_right, Player.LEFT,  Player.RIGHT),
                  (0, +1, key_right, key_left,  Player.RIGHT, Player.LEFT ),
                  (1, -1, key_up,    key_down,  Player.UP,    Player.DOWN ),
                  (1, +1, key_down,  key_up,    Player.DOWN,  Player.UP   ),
                  ]

        for (i, k, key, opposite_key, state, opposite_state) in states:
            if key and not opposite_key:
                if self.state == Player.STANDING:
                    self.state = state
                elif self.state == opposite_state:
                    self.location[i] -= k
                    self.offset[i] = k + self.offset[i]
                    self.state = state

        # Tuple associated with each direction: (i, k, key)
        # i = 0 (horizontal movement) or 1 (vertical)
        # k = -1 (left/up) or 1 (right/down)
        # key - if that direction's key is still pressed
        states = {
                  Player.LEFT:  (0, -1, key_left),
                  Player.RIGHT: (0, +1, key_right),
                  Player.UP:    (1, -1, key_up),
                  Player.DOWN:  (1, +1, key_down),
                  }

        # Move to one of directions
        if states.has_key(self.state):

            i, k, key = states[self.state]

            # Move a bit
            self.offset[i] += k * self.speed * milliseconds / 1000.0

            # Check if moved outside of the current cell
            if abs(self.offset[i]) >= 1.0:

                # Moved to a neighbouring cell
                self.location[i] += k
                self.offset[i] -= k * 1.0

                # Stop movement if key is not pressed anymore
                if not key:
                    self.offset[i] = 0.0
                    self.state = Player.STANDING
