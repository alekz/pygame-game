import random
import pygame

from mygame.player import controls
from mygame.types import direction
from mygame import objects

class Player(object):

    @classmethod
    def create_player(cls, game, controls, speed=None, location=None):
        player = cls(game, controls)
        if speed is not None:
            player.speed = speed
        if location is not None:
            player.location = location
        return player

    @classmethod
    def create_human_player(cls, game, **kwargs):
        return cls.create_player(game, controls.HumanPlayerControls(game), speed=10.0, **kwargs)

    @classmethod
    def create_harmless_monster(cls, game, **kwargs):
        return cls.create_player(game, controls.RandomMovementControls(game), speed=3.0, **kwargs)

    @classmethod
    def create_agressive_monster(cls, game, target, **kwargs):
        player_controls = controls.MonsterControls(game)
        player_controls.set_target(target)
        player_controls.target_distance = (10, 15)
        player_controls.walk_speed = 3.0
        player_controls.attack_speed = 5.0
        return cls.create_player(game, player_controls, speed=3.0, **kwargs)

    def __init__(self, game, controls):

        # Global objects
        self._game = game
        self._map = game.map

        # Player properties
        self._speed = 5.0 # Cells per second
        self._min_time_between_bombs = 1000 # in milliseconds

        # Player state
        self.location = (0, 0) # Cell coordinates within a map
        self.offset = (0, 0) # Offset within a cell, -1.0..1.0
        self._direction = direction.NONE
        self._location_changed = False
        self._time_until_next_bomb = 0

        # Player controls
        if controls is None:
            controls = controls.NoMovementControls()
        self.set_controls(controls)

    def set_controls(self, controls):
        controls.set_player(self)
        self.controls = controls

    @property
    def location(self):
        return tuple(self._location)

    @location.setter
    def location(self, coord):
        self._location = [coord[0], coord[1]]

    @property
    def offset(self):
        return tuple(self._offset)

    @offset.setter
    def offset(self, coord):
        self._offset = [float(coord[0]), float(coord[1])]

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        self._speed = float(speed)

    @property
    def location_changed(self):
        return self._location_changed

    @property
    def direction(self):
        return self._direction

    def update(self, milliseconds):
        self._update_movement(milliseconds)
        self._update_action(milliseconds)

    def _update_movement(self, milliseconds):

        self._location_changed = False

        new_direction = self.controls.get_movement_direction()

        if new_direction != direction.NONE:

            if self._direction == direction.NONE:
                # Start moving, but first check if it is allowed
                new_location = self._location[:]
                i, k = direction.get_info(new_direction)
                new_location[i] += k
                if not self._map.can_move_to(new_location):
                    new_direction = direction.NONE
                else:
                    self._direction = new_direction

            elif direction.is_opposite(new_direction, self._direction):
                # Move to the opposite direction (should always be allowed)
                i, k = direction.get_info(self._direction)
                self._location[i] += k
                self._offset[i] -= k
                self._direction = new_direction

        # Move to one of directions
        if self._direction != direction.NONE:

            i, k = direction.get_info(self._direction)

            # Move a bit
            self._offset[i] += k * self._speed * milliseconds / 1000.0

            # Check if moved outside of the current cell, i.e. player's location has changed
            if abs(self._offset[i]) >= 1.0:

                self._location_changed = True

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
                    if not self._map.can_move_to(new_location):
                        stop = True
                if stop:
                    self._offset[i] = 0.0
                    self._direction = direction.NONE

    def _update_action(self, milliseconds):

        self._time_until_next_bomb -= milliseconds
        can_plant_bomb = self._time_until_next_bomb <= 0

        if can_plant_bomb:
            self._time_until_next_bomb = 0
            if self.controls.is_planting_bomb():
                bomb = objects.Bomb(self.location, 5000)
                self._game.bombs.append(bomb)
                self._time_until_next_bomb += self._min_time_between_bombs
