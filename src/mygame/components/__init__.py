class Component(object):

    DRAW = 'draw'
    BEHAVIOR = 'behavior'
    LOCATION = 'location'
    MOVEMENT = 'movement'
    EXPLOSION = 'explosion'

    def update(self, game, entity): pass


class ExplosionComponent(Component):

    def __init__(self, power=0, time=None):
        """
        power  float  Maximum damage in the center of explosion
        time   float  Explode after N seconds; None means "never explode until
                      explicitly triggered"; <= 0 means "explode right now"
        """
        self.power = power
        self.time = time

    def update(self, game, entity):

        # Update timer
        if self.time is not None:
            self.time -= game.seconds

        # Check is should explode
        if self.time is not None and self.time <= 0:
            # Do some serious damage
            pass

    def trigger(self):
        self.time = 0
