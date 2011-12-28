class Message(object):

    CHANGE_LOCATION = 'change_location'
    COLLECT = 'collect'
    DAMAGE = 'damage'

    def __init__(self, message_type, **params):
        self._type = message_type
        self._params = params

    @property
    def type(self): #@ReservedAssignment
        return self._type

    @property
    def params(self):
        return self._params

    def __getattr__(self, name):
        try:
            return self._params[name]
        except KeyError:
            raise AttributeError
