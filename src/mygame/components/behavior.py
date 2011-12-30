import random
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

        entity.location.direction = self._get_movement_direction(entity.location)

        self._time_since_last_bomb += game.seconds
        if self._is_planting_bomb() and self._min_time_between_bombs < self._time_since_last_bomb:
            from mygame import factory
            bomb = factory.create_bomb(entity.location.cs)
            game.entities['bombs'].append(bomb)
            self._time_since_last_bomb = 0.0

    def _get_movement_direction(self, location):

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
                if location.direction in (direction.NONE, opposite_direction):
                    return current_direction

        return direction.NONE

    def _is_planting_bomb(self):
        return pygame.key.get_pressed()[pygame.K_SPACE]


class RandomMovementComponent(BehaviorComponent):

    def __init__(self):
        self._last_direction = direction.NONE

    def update(self, game, entity):
        entity.location.direction = self._get_movement_direction(game, entity)

    def _get_movement_direction(self, game, entity):

        # Already moving, carry on
        if entity.location.direction != direction.NONE:
            return direction.NONE

        new_direction = direction.NONE

        possible_directions = [
            (direction.LEFT,  -1,  0),
            (direction.RIGHT, +1,  0),
            (direction.UP,     0, -1),
            (direction.DOWN,   0, +1),
        ]

        allowed_directions = []

        for possible_direction, dx, dy in possible_directions:
            coord = (entity.location.xr + dx, entity.location.yr + dy)
            if game.map.can_move_to(coord):
                if possible_direction == self._last_direction:
                    weight = 100
                elif possible_direction == direction.get_opposite(self._last_direction):
                    weight = 1
                else:
                    weight = 30
                allowed_directions.append((weight, possible_direction))

        if allowed_directions:
            total_weight = sum(weight for weight, _ in allowed_directions)
            r = random.randint(0, total_weight - 1)
            for weight, new_direction in allowed_directions:
                if r < weight:
                    break
                r -= weight

        self._last_direction = new_direction

        return new_direction


class AgressiveAIComponent(BehaviorComponent):
    pass
