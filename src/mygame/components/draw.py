import pygame

from mygame.components import Component


class DrawComponent(Component):

    def draw(self, game, surface, entity): pass


class DrawCircleComponent(DrawComponent):

    def __init__(self, size=1.0, color=(255, 255, 255)):
        self.size = size
        self.color = color

    def draw(self, game, surface, entity):

        try:
            location = entity.components[Component.LOCATION]
        except KeyError:
            return

        x = int(game.cell_size[0] * (location.x + 0.5))
        y = int(game.cell_size[1] * (location.y + 0.5))
        r = int(self.size * (game.cell_size[0] + game.cell_size[1]) / 4)

        pygame.draw.circle(surface, self.color, (x, y), r)


class DrawRectangleComponent(DrawComponent):

    def __init__(self, size=1.0, color=(255, 255, 255)):
        self.size = size
        self.color = color

    def draw(self, game, surface, entity):

        try:
            location = entity.components[Component.LOCATION]
        except KeyError:
            return

        cw, ch = game.cell_size

        x = int(cw * (location.x + (1 - self.size) / 2))
        y = int(ch * (location.y + (1 - self.size) / 2))
        w = int(cw * self.size)
        h = int(ch * self.size)

        rect = pygame.rect.Rect(x, y, w, h)
        pygame.draw.rect(surface, self.color, rect)
