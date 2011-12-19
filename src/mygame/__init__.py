import random
import math

import pygame

from mygame.player import Player
from mygame.map import generator, Map, Cell
from mygame.objects import Coin

class BaseGame(object):

    def __init__(self):

        self.is_running = False

        self.fps = 60
        self.screen_size = (640, 480)

        self.clock = None
        self.screen = None

        self.on_init()

    def start(self):

        pygame.init()

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.screen_size)

        self.on_start()

        self.run()

    def run(self):
        self.is_running = True
        while True:
            milliseconds = self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                elif event.type == pygame.KEYDOWN:
                    self.on_keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.on_keyup(event.key)
                elif event.type == pygame.MOUSEMOTION:
                    self.on_mouse_motion(event.pos, event.rel)
            if self.is_running:
                self.on_update(milliseconds)
                self.on_draw(milliseconds)
                pygame.display.update()
            else:
                break

    def stop(self):
        if self.is_running:
            self.on_stop()
            pygame.quit()
            self.is_running = False
            self.on_stopped()

    def on_init(self): pass

    def on_start(self): pass

    def on_stop(self): pass

    def on_stopped(self): pass

    def on_keydown(self, key): pass

    def on_keyup(self, key): pass

    def on_mouse_motion(self, pos, rel): pass

    def on_update(self, milliseconds): pass

    def on_draw(self, milliseconds): pass

class Game(BaseGame):

    def on_init(self):

        self.objects = {}

        self.cell_size = (10, 10)

        # Init map
        map_size = [0, 0]
        for i in (0, 1):
            map_size[i] = int(1.0 * self.screen_size[i] / self.cell_size[i])
            if map_size[i] % 2 == 0:
                map_size[i] -= 1
        self.map_size_in_pixels = tuple(map_size[i] * self.cell_size[i] for i in (0, 1))
        map_generator = generator.MazeGenerator()
        self.map = Map(self, map_size, map_generator)
        empty_cells = list(self.map.get_cells(Cell.FLOOR))

        # Init coins
        self.objects['coins'] = []
        for _ in range(25):
            cell = random.choice(empty_cells)
            empty_cells.remove(cell)
            self.objects['coins'].append(Coin(cell.coord))

        # Init bombs
        self.objects['bombs'] = []

        # Init player
        self.player = Player.create_human_player(self, location=random.choice(empty_cells).coord)

        # Make sure monsters are generated at some distance from the player
        empty_cells = list(cell for cell in empty_cells
                                if 15 < math.sqrt((cell.x - self.player.location[0]) ** 2 +
                                                  (cell.y - self.player.location[1]) ** 2))

        # Init monsters
        self.objects['monsters'] = []

        harmless_monsters_count = 1
        coward_monsters_count = 1
        agressive_monsters_count = 5

        # Harmless
        for _ in xrange(harmless_monsters_count):
            cell = random.choice(empty_cells)
            empty_cells.remove(cell)
            monster = Player.create_harmless_monster(self, location=cell.coord)
            monster.color = (0, 128, 255)
            self.objects['monsters'].append(monster)

        # Coward
        for _ in xrange(coward_monsters_count):
            cell = random.choice(empty_cells)
            empty_cells.remove(cell)
            monster = Player.create_coward_monster(self, self.player, location=cell.coord)
            monster.color = (255, 0, 255)
            self.objects['monsters'].append(monster)

        # Agressive
        for _ in xrange(agressive_monsters_count):
            cell = random.choice(empty_cells)
            empty_cells.remove(cell)
            monster = Player.create_agressive_monster(self, self.player, location=cell.coord)
            monster.color = (255, 128, 0)
            self.objects['monsters'].append(monster)

        # Init drawing surfaces
        self.redraw_cells = []
        self.redraw_map = True
        self.map_surface = pygame.Surface(self.map_size_in_pixels)
        self.draw_surface = pygame.Surface(self.map_size_in_pixels)

    def get_objects(self, object_types):
        if not hasattr(object_types, '__iter__'):
            object_types = [object_types]
        object_types = (t for t in object_types if self.objects.has_key(t))
        return (o for t in object_types
                  for o in self.objects[t]
                  if not o.is_destroyed())

    def on_update(self, milliseconds):

        self.player.update(self, milliseconds)
        if self.player.location_changed:
            # Check if player collected a coin
            for coin in self.get_objects('coins'):
                if coin.location == self.player.location:
                    coin.collect()

        for monster in self.get_objects('monsters'):
            monster.update(self, milliseconds)

        for bomb in self.get_objects('bombs'):
            bomb.update(self, milliseconds)

    def on_draw(self, milliseconds):

        self._clear_screen()

        self.map.draw(self, self.map_surface, milliseconds)
        self.draw_surface.blit(self.map_surface, (0, 0))

        for coin in self.get_objects('coins'):
            coin.draw(self, self.draw_surface, milliseconds)

        for bomb in self.get_objects('bombs'):
            bomb.draw(self, self.draw_surface, milliseconds)

        self._draw_monsters()
        self._draw_player()

        self._draw_fps()

        self._update_screen()

    def _clear_screen(self):
        self.screen.fill((0, 0, 0))
        self.draw_surface.fill((0, 0, 0))

    def _update_screen(self):
        offset = [0, 0]
        for i in (0, 1):
            if self.map_size_in_pixels[i] <= self.screen_size[i]:
                offset[i] = (self.screen_size[i] - self.map_size_in_pixels[i]) / 2
            else:
                player_offset = round(self.cell_size[i] * (self.player.location[i] + self.player.offset[i]))
                offset[i] = self.screen_size[i] / 2 - player_offset
                if offset[i] > 0:
                    offset[i] = 0
                elif offset[i] < self.screen_size[i] - self.map_size_in_pixels[i]:
                    offset[i] = self.screen_size[i] - self.map_size_in_pixels[i]
        self.screen.blit(self.draw_surface, offset)

    def _draw_player(self):
        color = (0, 192, 0)
        self._paint_cell(color, self.player.location, self.player.offset)

    def _draw_monsters(self):
        for monster in self.get_objects('monsters'):
            color = monster.color
            if hasattr(monster.controls, 'is_following') and monster.controls.is_following:
                color = (255, 0, 0)
            self._paint_cell(color, monster.location, monster.offset)

    def _draw_fps(self):
        #fps = self.clock.get_fps()
        #print fps
        pass

    def _paint_cell(self, color, coord, offset=(0.0, 0.0), surface=None):
        surface = surface or self.draw_surface
        rect = pygame.rect.Rect((coord[0] + offset[0]) * self.cell_size[0],
                                (coord[1] + offset[1]) * self.cell_size[1],
                                self.cell_size[0],
                                self.cell_size[1])
        pygame.draw.rect(surface, color, rect)

    def on_keydown(self, key):
        if key == pygame.K_ESCAPE:
            self.stop()
