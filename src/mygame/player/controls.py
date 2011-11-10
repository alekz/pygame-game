import random
import math

import pygame

from mygame.types import direction
from mygame.map import Map

class PlayerControls(object):

    def __init__(self, game):
        self.game = game
        self.player = None
        self.init()

    def init(self): pass

    def set_player(self, player):
        self.player = player

    def get_movement_direction(self):
        raise NotImplementedError


class CompositePlayerControls(PlayerControls):

    def __init__(self, game):
        self.controls = {}
        super(CompositePlayerControls, self).__init__(game)

    def set_player(self, player):
        super(CompositePlayerControls, self).set_player(player)
        for controls in self.controls.values():
            controls.set_player(self.player)

    def add_controls(self, name, controls):
        self.controls[name] = controls
        controls.set_player(self.player)

    def get_movement_direction_from_controls(self, name):
        return self.controls[name].get_movement_direction()


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
                        weight = 100
                    elif possible_direction == direction.get_opposite(self.last_direction):
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

            self.last_direction = new_direction

        return new_direction


class FollowPlayerControls(PlayerControls):

    def init(self):
        self.target = None
        #self.last_target_location = (-1, -1)

    def set_target(self, target):
        self.target = target

    def get_movement_direction(self):

        if not self.target:
            # Target is not set, just stand still and don't move
            return direction.NONE

        if self.player.direction != direction.NONE:
            # Still moving
            return direction.NONE

        if self.player.location == self.target.location:
            # Target reached!
            return direction.NONE

        new_direction = direction.NONE

        game_map = self.game.map

        # List item: coord: (parent_coord, G, H)
        open_list = {self.player.location: (None, 0, self._get_distance_to_target(self.player.location))}
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
            if best_cell_coord == self.target.location:
                new_direction = self._get_direction_to_target(closed_list, best_cell_coord)
                break

            # Find cells adjacent to the "best" cell
            adjacent_cells = game_map.get_adjacent_cells(best_cell_coord, Map.CELL_TYPE_FLOOR)

            # Add these adjacent cells to the open list, but only if they
            # are not present in the closed list
            for adjacent_cell_coord in adjacent_cells:
                if not closed_list.has_key(adjacent_cell_coord):

                    # Distance from our position to the current cell
                    g = best_cell[1] + 1

                    if not open_list.has_key(adjacent_cell_coord):

                        # Add new cell to the open list
                        h = self._get_distance_to_target(adjacent_cell_coord)
                        open_list[adjacent_cell_coord] = (best_cell_coord, g, h)

                    elif g < open_list[adjacent_cell_coord][1]:

                        # This cell already exists in the open list, but we've found a better route
                        open_list[adjacent_cell_coord] = (best_cell_coord, g, open_list[adjacent_cell_coord][2])

        return new_direction

    def _get_distance_to_target(self, coord):
        return abs(coord[0] - self.target.location[0]) + abs(coord[1] - self.target.location[1])

    def _get_best_cell(self, cells):
        best_cell_coord = None
        best_cost = None
        for coord, (_, g, h) in cells.items():
            f = g + h
            if best_cost is None or f < best_cost:
                best_cost = f
                best_cell_coord = coord
        return best_cell_coord

    def _get_direction_to_target(self, cells, target_coord):

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
        dx = next_cell_coord[0] - self.player.location[0]
        dy = next_cell_coord[1] - self.player.location[1]
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


class MonsterControls(CompositePlayerControls):

    def init(self):

        self.add_controls('random', RandomMovementControls(self.game))
        self.add_controls('follow', FollowPlayerControls(self.game))

        self.target = None
        self.target_distance = None
        self.is_following = False

        self.default_speed = None
        self.walk_speed = None
        self.attack_speed = None

    def set_player(self, player):
        super(MonsterControls, self).set_player(player)
        self.default_speed = player.speed

    def set_target(self, target):
        self.target = target
        self.controls['follow'].set_target(target)

    def get_movement_direction(self):
        distance = math.sqrt(
                             (self.player.location[0] - self.target.location[0]) ** 2 +
                             (self.player.location[1] - self.target.location[1]) ** 2
                            )

        if not self.is_following and distance <= self.target_distance[0]:
            self.is_following = True
            self.player.speed = self.attack_speed or self.default_speed
        elif self.is_following and self.target_distance[1] < distance:
            self.is_following = False
            self.player.speed = self.walk_speed or self.default_speed

        if self.is_following:
            return self.get_movement_direction_from_controls('follow')
        else:
            return self.get_movement_direction_from_controls('random')
