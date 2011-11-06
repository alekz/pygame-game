import random

import pygame

import player
from map import Map, RandomMapGenerator

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

        self.cell_size = (20, 20)

        # Init map
        map_size = tuple(int(self.screen_size[i] / self.cell_size[i]) for i in (0, 1))
        map_generator = RandomMapGenerator()
        self.map = Map(self, map_size, map_generator)

        # Init player
        self.player = player.Player(self, player.HumanPlayerControls(self))
        self.player.location = [int(self.map.size[0] / 2), int(self.map.size[1] / 2)]
        self.map.set_cell(self.player.location, Map.CELL_TYPE_FLOOR) # Initial player's position should be empty

        # Init monsters
        self.monsters = []
        for _ in xrange(4):
            monster = player.Player(self, player.RandomMovementControls(self))
            monster.location = (random.randint(0, self.map.size[0] - 1), random.randint(0, self.map.size[1] - 1))
            self.map.set_cell(monster.location, Map.CELL_TYPE_FLOOR) # Initial monster's position should be empty
            self.monsters.append(monster)


    def on_update(self, milliseconds):
        self.player.update(milliseconds)
        for monster in self.monsters:
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
        for x in xrange(self.map.size[0]):
            for y in xrange(self.map.size[1]):
                cell_type = self.map.cells[x][y]
                color = self.map.colors[cell_type]
                self._paint_cell(color, (x, y))

    def _draw_player(self):
        color = (0, 192, 0)
        self._paint_cell(color, self.player.location, self.player.offset)

    def _draw_monsters(self):
        color = (192, 0, 0)
        for monster in self.monsters:
            self._paint_cell(color, monster.location, monster.offset)

    def _draw_fps(self):
        fps = self.clock.get_fps()
        #print fps

    def _paint_cell(self, color, coord, offset=(0.0, 0.0)):
        rect = pygame.rect.Rect((coord[0] + offset[0]) * self.cell_size[0],
                                (coord[1] + offset[1]) * self.cell_size[1],
                                self.cell_size[0],
                                self.cell_size[1])
        pygame.draw.rect(self.screen, color, rect)

    def on_keydown(self, key):
        if key == pygame.K_ESCAPE:
            self.stop()

if __name__ == '__main__':
    game = Game()
    game.start()
