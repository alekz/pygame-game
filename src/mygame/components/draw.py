import pygame

from mygame.components import Component


class DrawComponent(Component):

    def draw(self, game, surface, entity): pass


class DrawCircleComponent(DrawComponent):

    def __init__(self, size=1.0, color=(255, 255, 255)):
        self.size = size
        self.color = color

    def draw(self, game, surface, entity):

        x = int(game.cell_size[0] * (entity.location.x + 0.5))
        y = int(game.cell_size[1] * (entity.location.y + 0.5))
        r = int(self.size * (game.cell_size[0] + game.cell_size[1]) / 4)

        pygame.draw.circle(surface, self.color, (x, y), r)


class DrawRectangleComponent(DrawComponent):

    def __init__(self, size=1.0, color=(255, 255, 255)):
        self.size = size
        self.color = color

    def draw(self, game, surface, entity):

        cw, ch = game.cell_size

        x = int(cw * (entity.location.x + (1 - self.size) / 2))
        y = int(ch * (entity.location.y + (1 - self.size) / 2))
        w = int(cw * self.size)
        h = int(ch * self.size)

        rect = pygame.rect.Rect(x, y, w, h)
        pygame.draw.rect(surface, self.color, rect)
