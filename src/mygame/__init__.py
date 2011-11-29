import random
import math

import pygame

from mygame.player import Player
from mygame.map import generator, Map, Cell

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
        empty_cells = list(self.map.get_cells(Cell.FLOOR))

        # Init cookies
        self.cookies = []
        for _ in range(25):
            cell = random.choice(empty_cells)
            empty_cells.remove(cell)
            self.cookies.append(cell.coord)

        # Init bombs
        self.bombs = []

        # Init player
        self.player = Player.create_human_player(self, location=random.choice(empty_cells).coord)

        # Make sure monsters are generated at some distance from the player
        empty_cells = list(cell for cell in empty_cells
                                if 15 < math.sqrt((cell.x - self.player.location[0]) ** 2 +
                                                  (cell.y - self.player.location[1]) ** 2))

        # Init monsters
        self.monsters = []

        harmless_monsters_count = 1
        coward_monsters_count = 1
        agressive_monsters_count = 5

        # Harmless
        for _ in xrange(harmless_monsters_count):
            cell = random.choice(empty_cells)
            empty_cells.remove(cell)
            monster = Player.create_harmless_monster(self, location=cell.coord)
            monster.color = (0, 128, 255)
            self.monsters.append(monster)

        # Coward
        for _ in xrange(coward_monsters_count):
            cell = random.choice(empty_cells)
            empty_cells.remove(cell)
            monster = Player.create_coward_monster(self, self.player, location=cell.coord)
            monster.color = (255, 0, 255)
            self.monsters.append(monster)

        # Agressive
        for _ in xrange(agressive_monsters_count):
            cell = random.choice(empty_cells)
            empty_cells.remove(cell)
            monster = Player.create_agressive_monster(self, self.player, location=cell.coord)
            monster.color = (255, 128, 0)
            self.monsters.append(monster)

        # Init drawing surfaces
        self.update_map = True
        self.map_surface = pygame.Surface(self.screen_size)

    def on_update(self, milliseconds):
        self._update_player(milliseconds)
        self._update_monsters(milliseconds)
        self._update_bombs(milliseconds)

    def _update_player(self, milliseconds):
        self.player.update(milliseconds)
        if self.player.location_changed:
            # Check if player ate a cookie
            if self.player.location in self.cookies:
                self.cookies.remove(self.player.location)

    def _update_monsters(self, milliseconds):
        for monster in self.monsters:
            monster.update(milliseconds)

    def _update_bombs(self, milliseconds):

        bombs_exploded = False

        for bomb in self.bombs:
            bomb.update(milliseconds)
            if bomb.is_exploding():
                for coord, damage in bomb.get_damaged_cells():
                    cell = self.map(coord)
                    if cell:

                        # Damage map
                        cell.hit(damage)

                        # Damage cookies
                        for cookie_coord in self.cookies:
                            if cookie_coord == coord:
                                self.cookies.remove(cookie_coord)

                        # Damage monsters
                        killed_monsters = []
                        for monster in self.monsters:
                            if monster.location == coord:
                                monster.hit(damage)
                                if monster.is_dead():
                                    killed_monsters.append(monster)
                        for monster in killed_monsters:
                            self.monsters.remove(monster)

                bombs_exploded = True
                self.bombs.remove(bomb)

        if bombs_exploded:
            self.update_map = True

    def on_draw(self, milliseconds):
        self._clear_screen()
        self._draw_map()
        self._draw_cookies()
        self._draw_bombs()
        self._draw_monsters()
        self._draw_player()
        self._draw_fps()

    def _clear_screen(self):
        self.screen.fill((0, 0, 0))

    def _draw_map(self):
        if self.update_map:
            for x in xrange(self.map.width):
                for y in xrange(self.map.height):
                    cell = self.map(x, y)
                    self._paint_cell(cell.color, (x, y), surface=self.map_surface)
            self.update_map = False
        self.screen.blit(self.map_surface, (0, 0))

    def _draw_player(self):
        color = (0, 192, 0)
        self._paint_cell(color, self.player.location, self.player.offset)

    def _draw_monsters(self):
        for monster in self.monsters:
            color = monster.color
            if hasattr(monster.controls, 'is_following') and monster.controls.is_following:
                color = (255, 0, 0)
            self._paint_cell(color, monster.location, monster.offset)

    def _draw_cookies(self):
        for coord in self.cookies:
            x = self.cell_size[0] * coord[0] + self.cell_size[0] / 2
            y = self.cell_size[1] * coord[1] + self.cell_size[1] / 2
            pygame.draw.circle(self.screen, (255, 255, 0), (x, y), 2)

    def _draw_bombs(self):
        for bomb in self.bombs:
            x = self.cell_size[0] * bomb.location[0] + self.cell_size[0] / 2
            y = self.cell_size[1] * bomb.location[1] + self.cell_size[1] / 2
            if bomb.time_to_explode % 1000 <= 500:
                color = (255, 0, 0)
            else:
                color = (128, 0, 0)
            pygame.draw.circle(self.screen, color, (x, y), 4)

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
