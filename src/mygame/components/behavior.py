import random
import math
import pygame
from mygame.types import direction
from mygame.components import Component
from mygame.map import Cell

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
                  (key_left,  key_right, direction.LEFT,  ),
                  (key_right, key_left,  direction.RIGHT, ),
                  (key_up,    key_down,  direction.UP,    ),
                  (key_down,  key_up,    direction.DOWN,  ),
                  ]

        for (key, opposite_key, current_direction) in directions:
            # If both left and right keys are pressed, we ignore them (the same for up/down)
            if key and not opposite_key:
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


class FollowTargetAIComponent(BehaviorComponent):

    def update(self, game, entity):
        entity.location.direction = self._get_movement_direction(game, entity)

    def _get_target(self, game):
        return game.player

    def _get_movement_direction(self, game, entity):

        target = self._get_target(game)

        if not target:
            # Target is not set, just stand still and don't move
            return direction.NONE

        if entity.location.direction != direction.NONE:
            # Still moving
            return direction.NONE

        if entity.location.cs == target.location.cs:  # cs, ct or cr?
            # Target reached!
            return direction.NONE

        new_direction = direction.NONE

        game_map = game.map

        # List item: coord: (parent_coord, G, H)
        open_list = {entity.location.cs: (None, 0, self._get_distance_to_target(entity.location.cs, target))}
        closed_list = {}

        while True:

            if not open_list:
                # Can't find the path: don't move anymore
                break

            # Find "best" cell in the open list, i.e. cell with the shortest
            # predicted path to the target
            best_cell_coord = self._get_best_cell(open_list)

            # Remove "best" cell from the open list and add to the closed list
            best_cell = open_list.pop(best_cell_coord)
            closed_list[best_cell_coord] = best_cell

            # Check if we've reachet the target
            if best_cell_coord == target.location.cs:
                new_direction = self._get_direction_to_target(entity, closed_list, best_cell_coord)
                break

            # Find cells adjacent to the "best" cell
            adjacent_cells = game_map.get_adjacent_cells(best_cell_coord, Cell.FLOOR)

            # Add these adjacent cells to the open list, but only if they
            # are not present in the closed list
            for cell in adjacent_cells:
                if not closed_list.has_key(cell.coord):

                    # Distance from our position to the current cell
                    g = best_cell[1] + 1

                    if not open_list.has_key(cell.coord):

                        # Add new cell to the open list
                        h = self._get_distance_to_target(cell.coord, target)
                        open_list[cell.coord] = (best_cell_coord, g, h)

                    elif g < open_list[cell.coord][1]:

                        # This cell already exists in the open list, but we've found a better route
                        open_list[cell.coord] = (best_cell_coord, g, open_list[cell.coord][2])

        return new_direction

    def _get_distance_to_target(self, coord, target):
        return abs(coord[0] - target.location.xs) + abs(coord[1] - target.location.ys)

    def _get_best_cell(self, cells):
        best_cell_coord = None
        best_cost = None
        for coord, (_, g, h) in cells.items():
            f = g + h
            if best_cost is None or f < best_cost:
                best_cost = f
                best_cell_coord = coord
        return best_cell_coord

    def _get_direction_to_target(self, entity, cells, target_coord):

        # Build backwards path from target to us
        cell = cells[target_coord]
        path = [target_coord]
        while True:
            parent_coord = cell[0]
            if parent_coord is None:
                break
            path.append(parent_coord)
            cell = cells[parent_coord]

        if len(path) <= 1:
            return direction.NONE

        # -1 is our location, -2 is the next cell
        next_cell_coord = path[-2]

        # Calculate direction
        dx = next_cell_coord[0] - entity.location.xs
        dy = next_cell_coord[1] - entity.location.ys
        if dx < 0:
            return direction.LEFT
        elif 0 < dx:
            return direction.RIGHT
        elif dy < 0:
            return direction.UP
        elif 0 < dy:
            return direction.DOWN
        else:
            return direction.NONE


class AgressiveAIComponent(BehaviorComponent):

    def __init__(self, walk_distance=0, attack_distance=0, walk_speed=None, attack_speed=None):

        self.walk_distance = walk_distance
        self.attack_distance = attack_distance

        self.walk_speed = walk_speed
        self.attack_speed = attack_speed

        self.is_following = False

        self._follow_target_behavior = FollowTargetAIComponent()
        self._random_movement_behavior = RandomMovementComponent()

    def update(self, game, entity):

        # Find a target to follow, if can't find any, just walk randomly
        target = self._get_target(game)
        if not target:
            self._random_movement_behavior.update(game, entity)

        # Calculate distance to target
        distance = math.sqrt(
            (entity.location.xs - target.location.xs) ** 2 +
            (entity.location.ys - target.location.ys) ** 2
        )

        if not self.is_following and distance <= self.attack_distance:

            # Start following
            self.is_following = True
            if self.attack_speed is not None:
                entity.location.speed = self.attack_speed
            entity.set_state('chasing')

        elif self.is_following and self.walk_distance <= distance:

            # Stop following
            self.is_following = False
            if self.walk_speed is not None:
                entity.location.speed = self.walk_speed
            entity.unset_state('chasing')

        if self.is_following:
            self._follow_target_behavior.update(game, entity)
        else:
            self._random_movement_behavior.update(game, entity)

    def _get_target(self, game):
        return game.player
