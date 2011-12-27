import random
import math
import pygame
from mygame import factory
from mygame.map import generator, Map, Cell

class BaseGame(object):

    def __init__(self):

        self.is_running = False
        self.milliseconds = 0

        self.fps = 60
        self.screen_size = (640, 480)

        self.clock = None
        self.screen = None

        self.on_init()

    @property
    def seconds(self):
        return self.milliseconds / 1000.0

    def start(self):

        pygame.init()

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.screen_size)

        self.on_start()

        self.run()

    def run(self):
        self.is_running = True
        while True:
            self.milliseconds = self.clock.tick(self.fps)
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
                self.on_update()
                self.on_draw()
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

    def on_update(self): pass

    def on_draw(self): pass

class Game(BaseGame):

    def on_init(self):

        self.entities = {}

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
        self.entities['coins'] = []
        for _ in range(25):
            cell = random.choice(empty_cells)
            empty_cells.remove(cell)
            coin = factory.create_coin(cell.coord)
            self.entities['coins'].append(coin)

        # Init bombs
        self.entities['bombs'] = []

        # Init player
        self.player = factory.create_player(coord=random.choice(empty_cells).coord)

#        # Make sure monsters are generated at some distance from the player
#        empty_cells = list(cell for cell in empty_cells
#                                if 15 < math.sqrt((cell.x - self.player.location[0]) ** 2 +
#                                                  (cell.y - self.player.location[1]) ** 2))
#
#        # Init monsters
#        self.entities['monsters'] = []
#
#        harmless_monsters_count = 1
#        coward_monsters_count = 1
#        agressive_monsters_count = 5
#
#        # Harmless
#        for _ in xrange(harmless_monsters_count):
#            cell = random.choice(empty_cells)
#            empty_cells.remove(cell)
#            monster = Player.create_harmless_monster(self, location=cell.coord)
#            monster.color = (0, 128, 255)
#            self.entities['monsters'].append(monster)
#
#        # Coward
#        for _ in xrange(coward_monsters_count):
#            cell = random.choice(empty_cells)
#            empty_cells.remove(cell)
#            monster = Player.create_coward_monster(self, self.player, location=cell.coord)
#            monster.color = (255, 0, 255)
#            self.entities['monsters'].append(monster)
#
#        # Agressive
#        for _ in xrange(agressive_monsters_count):
#            cell = random.choice(empty_cells)
#            empty_cells.remove(cell)
#            monster = Player.create_agressive_monster(self, self.player, location=cell.coord)
#            monster.color = (255, 128, 0)
#            self.entities['monsters'].append(monster)

        # Init drawing surfaces
        self.redraw_cells = []
        self.redraw_map = True
        self.map_surface = pygame.Surface(self.map_size_in_pixels)
        self.draw_surface = pygame.Surface(self.map_size_in_pixels)

    def get_entities(self, types=None, coord=None):

        if types is None:
            types = self.entities.keys()
        else:
            if not hasattr(types, '__iter__'):
                types = [types]
            types = (t for t in types if self.entities.has_key(t))

        entities = (e for t in types
                      for e in self.entities[t]
                      if not e.destroyed)

        if coord is not None:
            entities = (e for e in entities
                          if e.location and e.location.coord == coord)

        return entities

    def on_update(self):

        for e in self.get_entities():
            e.update(self)

        self.player.update(self)

        #if self.player.location_changed:
        #    # Check if player collected a coin
        #    for coin in self.get_entities('coins'):
        #        if coin.location == self.player.location:
        #            coin.collect()

        #for monster in self.get_entities('monsters'):
        #    monster.update(self)

        #for bomb in self.get_entities('bombs'):
        #    bomb.update(self)

    def on_draw(self):

        self._clear_screen()

        self.map.draw(self, self.map_surface)
        self.draw_surface.blit(self.map_surface, (0, 0))

        for e in self.get_entities():
            e.draw(self, self.draw_surface)

        #for coin in self.get_entities('coins'):
        #    coin.draw(self, self.draw_surface, milliseconds)

        #for bomb in self.get_entities('bombs'):
        #    bomb.draw(self, self.draw_surface, milliseconds)

        #self._draw_monsters()
        #self._draw_player()
        self.player.draw(self, self.draw_surface)

        #self._draw_fps()

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

    def on_keydown(self, key):
        if key == pygame.K_ESCAPE:
            self.stop()
