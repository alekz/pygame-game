import pygame
from mygame.types import direction
from mygame.components import Component

class BehaviorComponent(Component):
    pass

class HumanPlayerInputComponent(BehaviorComponent):

    def update(self, game, entity):
        try:
            movement = entity.components[Component.MOVEMENT]
        except KeyError:
            return

        movement.direction = self._get_movement_direction(movement)

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

    #def _is_planting_bomb(self):
    #    return pygame.key.get_pressed()[pygame.K_SPACE]
