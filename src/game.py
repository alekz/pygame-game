import random
import pygame

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
            self.clock.tick(self.fps)
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

class Game(BaseGame):

    def on_init(self):

        self.cell_size = (10, 10)
        self.map_size = tuple(int(self.screen_size[i] / self.cell_size[i]) for i in (0, 1))

        # List of colors for each cell type
        self.cell_colors = {
                            0: (  0,   0,   0),
                            1: (128, 128, 128),
                            }

        # Generate empty map
        empty_col = [0] * self.map_size[1]
        self.map = [empty_col[:] for _ in xrange(self.map_size[0])]

        # Generate random map
        for x in xrange(self.map_size[0]):
            for y in xrange(self.map_size[1]):
                self.map[x][y] = random.choice((0, 0, 0, 1))

    def on_update(self):

        cell_width, cell_height = self.cell_size

        # Clear screen
        self.screen.fill((0, 0, 0))

        # Draw map
        for x in xrange(self.map_size[0]):
            for y in xrange(self.map_size[1]):

                # Draw cell
                cell_type = self.map[x][y]
                rect = pygame.rect.Rect(x * cell_width, y * cell_height,
                                        cell_width, cell_height)
                pygame.draw.rect(self.screen, self.cell_colors[cell_type], rect)

    def on_keydown(self, key):
        if key == pygame.K_ESCAPE:
            self.stop()

if __name__ == '__main__':
    game = Game()
    game.start()
