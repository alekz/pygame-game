import pygame
from mygame.types import direction
from mygame.components import Component

class BehaviorComponent(Component):
    pass

class HumanPlayerInputComponent(BehaviorComponent):

    def __init__(self):
        self._min_time_between_bombs = 1.0  # seconds
        self._time_since_last_bomb = 0.0

    def update(self, game, entity):

        entity.movement.direction = self._get_movement_direction(entity.movement)

        self._time_since_last_bomb += game.seconds
        if self._is_planting_bomb() and self._min_time_between_bombs < self._time_since_last_bomb:
            from mygame import factory
            bomb = factory.create_bomb(entity.location.coord)
            game.entities['bombs'].append(bomb)
            self._time_since_last_bomb = 0.0

    def _get_movement_direction(self, movement):

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
                if movement.direction in (direction.NONE, opposite_direction):
                    return current_direction

        return direction.NONE

    def _is_planting_bomb(self):
        return pygame.key.get_pressed()[pygame.K_SPACE]
