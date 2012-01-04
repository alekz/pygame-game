from mygame.messages import Message
from mygame.components import Component
from mygame.components.draw import DrawComponent


class Entity(object):

    def __init__(self, components={}, properties={}, states=set()):
        self.components = components
        self.properties = properties
        self.states = states
        self.destroyed = False

    # == Properties ==

    def set_property(self, name, value):
        self.properties[name] = value

    def unset_property(self, name):
        try:
            del self.properties[name]
        except KeyError:
            pass

    def get_property(self, name, default=None):
        return self.properties.get(name, default)

    def has_property(self, name):
        return self.properties.has_key(name)

    def clear_properties(self):
        self.properties = {}

    # == Special properties ==

    @property
    def destroyed(self):
        return self._destroyed

    @destroyed.setter
    def destroyed(self, value):
        self._destroyed = bool(value)

    # == States ==

    def set_state(self, *names):
        self.states = self.states.union(names)

    def unset_state(self, *names):
        self.states = self.states.difference(names)

    def has_state(self, name):
        return name in self.states

    def clear_states(self):
        self.states = set()

    # == Components ==

    def __call__(self, component):
        try:
            return self.components[component]
        except KeyError:
            return None

    @property
    def location(self):
        return self(Component.LOCATION)

    #@property
    #def drawer(self):
    #    return self(Component.DRAW)

    # == Messages ==

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

    # == Update ==

    def update(self, game):
        self.update_components(game)

    def update_components(self, game):
        for component in self.components.values():
            component.update(game, self)

    # == Draw ==

    def draw(self, game, surface):
        self.draw_components(game, surface)

    def draw_components(self, game, surface):
        for component in self.components.values():
            if isinstance(component, DrawComponent):
                component.draw(game, surface, self)

    # == == ==
