import math
from mygame.messages import Message

class Component(object):

    DRAW = 'draw'
    BEHAVIOR = 'behavior'
    LOCATION = 'location'
    MOVEMENT = 'movement'
    EXPLOSION = 'explosion'
    HEALTH = 'health'
    COLLECTABLE = 'collectable'
    COLLECTOR = 'collector'

    def update(self, game, entity): pass

    def receive_message(self, game, entity, message): pass


class HealthComponent(Component):

    def __init__(self, health=None):
        self.health = health

    def on_damage(self, game, entity, message):

        if self.health is None:
            self.health = 0.0
        else:
            self.health -= message.damage

        if self.health <= 0.0:
            entity.destroyed = True


class ExplosionComponent(Component):

    def __init__(self, power=0, time=None):
        """
        power  float  Maximum damage in the center of explosion
        time   float  Explode after N seconds; None means "never explode until
                      explicitly triggered"; <= 0 means "explode right now"
        """
        self.power = power
        self.time = time

    def trigger(self):
        self.time = 0

    def on_damage(self, game, entity, message):
        self.trigger()

    def update(self, game, entity):

        # Update timer
        if self.time is not None:
            self.time -= game.seconds

        # Check is should explode
        if self.time is not None and self.time <= 0:

            # Prepare lists of entites for each affected cells
            entities = {}
            for e in game.get_entities():
                if not entities.has_key(e.location.coord):
                    entities[e.location.coord] = []
                entities[e.location.coord].append(e)

            # Do some serious damage
            for coord, damage in self._get_damaged_cells(entity.location.coord):
                cell = game.map(coord)
                if cell:

                    # Damage map
                    cell.hit(damage)

                    # Damage entities
                    for e in entities.get(coord, []):
                        e.send_message(game, Message.DAMAGE, damage=damage)

            entity.destroyed = True

    def _get_explosion_radius(self):
        return (8 * self.power) ** 0.5

    def _get_damaged_cells(self, coord):

        r = self._get_explosion_radius()
        ri = int(math.ceil(r))

        for dx in xrange(-ri, ri + 1):
            for dy in xrange(-ri, ri + 1):
                d = math.sqrt(dx ** 2 + dy ** 2)
                if d <= r:
                    x = coord[0] + dx
                    y = coord[1] + dy
                    damage = self.power * (1 - (d / r) ** 2)
                    yield ((x, y), damage)


class CollectableComponent(Component):

    def on_collect(self, game, entity, message):
        entity.destroyed = True


class CollectorComponent(Component):

    def on_change_location(self, game, entity, message):
        for e in game.get_entities(coord=message.coord):
            e.send_message(game, Message.COLLECT, collector=entity)
