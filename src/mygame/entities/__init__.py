from mygame.messages import Message
from mygame.components import Component
from mygame.components.draw import DrawComponent


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

    def send_message(self, game, message, **kwargs):

        if not isinstance(message, Message):
            message = Message(str(message), **kwargs)

        results = {}

        for component_name, component in self.components.items():

            method_name = 'on_' + message.type

            if hasattr(component, method_name):
                message_handler = getattr(component, method_name)
            else:
                message_handler = component.receive_message
            result = message_handler(game, self, message)

            if result is not None:
                results[component_name] = result

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
            return None

    @property
    def location(self):
        return self(Component.LOCATION)

    @property
    def movement(self):
        return self(Component.MOVEMENT)
