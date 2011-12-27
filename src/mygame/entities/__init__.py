from mygame.components import Component
from mygame.components.draw import DrawComponent


class NoComponentException(Exception): pass


class Entity(object):

    def __init__(self, components={}, properties={}, state=None):
        self.components = components
        self.properties = properties
        self.state = state
        self.destroyed = False

    def update(self, game):
        self.update_components(game)

    def update_components(self, game):
        for component in self.components.values():
            component.update(game, self)

    def draw(self, game, surface):
        self.draw_components(game, surface)

    def draw_components(self, game, surface):
        for component in self.components.values():
            if isinstance(component, DrawComponent):
                component.draw(game, surface, self)

    @property
    def destroyed(self):
        return self._destroyed

    @destroyed.setter
    def destroyed(self, value):
        self._destroyed = bool(value)

    def __call__(self, component):
        try:
            return self.components[component]
        except KeyError:
            raise NoComponentException

    @property
    def location(self):
        return self(Component.LOCATION)

    @property
    def movement(self):
        return self(Component.MOVEMENT)
