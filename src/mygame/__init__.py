import random
import math

import pygame

from mygame import player
from mygame.map import generator, Map

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

        self.cell_size = (10, 10)

        # Init map
        map_size = tuple(int(self.screen_size[i] / self.cell_size[i]) for i in (0, 1))
        map_generator = generator.MazeGenerator()
        self.map = Map(self, map_size, map_generator)
        empty_cells = list(self.map.get_cells(Map.CELL_TYPE_FLOOR))

        # Init player
        self.player = player.Player(self, player.controls.HumanPlayerControls(self))
        self.player.speed = 10.0
        self.player.location = random.choice(empty_cells)

        # Make sure monsters are generated at some distance from the player
        empty_cells = list((x, y) for (x, y) in empty_cells
                                  if 15 < math.sqrt((x - self.player.location[0]) ** 2 +
                                                    (y - self.player.location[1]) ** 2))

        # Init monsters
        self.monsters = []

        # Harmless
        for _ in xrange(3):

            monster = player.Player(self, player.controls.RandomMovementControls(self))
            monster.speed = 3.0

            monster.location = random.choice(empty_cells)
            empty_cells.remove(monster.location)

            self.monsters.append((monster, (255, 0, 255)))

        # Agressive
        for _ in xrange(3):

            monster_controls = player.controls.MonsterControls(self)
            monster_controls.set_target(self.player)
            monster_controls.target_distance = (10, 15)
            monster_controls.walk_speed = 3.0
            monster_controls.attack_speed = 5.0

            monster = player.Player(self, monster_controls)

            monster.location = random.choice(empty_cells)
            empty_cells.remove(monster.location)

            self.monsters.append((monster, (255, 128, 0)))

        # Init drawing surfaces
        self.update_map = True
        self.map_surface = pygame.Surface(self.screen_size)

    def on_update(self, milliseconds):
        self.player.update(milliseconds)
        for monster, _ in self.monsters:
            monster.update(milliseconds)

    def on_draw(self, milliseconds):
        self._clear_screen()
        self._draw_map()
        self._draw_monsters()
        self._draw_player()
        self._draw_fps()

    def _clear_screen(self):
        self.screen.fill((0, 0, 0))

    def _draw_map(self):
        if self.update_map:
            for x in xrange(self.map.width):
                for y in xrange(self.map.height):
                    cell_type = self.map.cells[x][y]
                    color = self.map.colors[cell_type]
                    self._paint_cell(color, (x, y), surface=self.map_surface)
            self.update_map = False
        self.screen.blit(self.map_surface, (0, 0))

    def _draw_player(self):
        color = (0, 192, 0)
        self._paint_cell(color, self.player.location, self.player.offset)

    def _draw_monsters(self):
        for monster, color in self.monsters:
            if hasattr(monster.controls, 'is_following') and monster.controls.is_following:
                color = (255, 0, 0)
            self._paint_cell(color, monster.location, monster.offset)

    def _draw_fps(self):
        #fps = self.clock.get_fps()
        #print fps
        pass

    def _paint_cell(self, color, coord, offset=(0.0, 0.0), surface=None):
        surface = surface or self.screen
        rect = pygame.rect.Rect((coord[0] + offset[0]) * self.cell_size[0],
                                (coord[1] + offset[1]) * self.cell_size[1],
                                self.cell_size[0],
                                self.cell_size[1])
        pygame.draw.rect(surface, color, rect)

    def on_keydown(self, key):
        if key == pygame.K_ESCAPE:
            self.stop()
