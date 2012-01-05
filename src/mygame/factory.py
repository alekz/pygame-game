from collections import OrderedDict
#from mygame import components
import components.draw
import components.location
import components.behavior
from components import Component
from entities import Entity

def create_coin(coord=None):
    return Entity(components=OrderedDict([
        (Component.LOCATION, components.location.StaticLocationComponent(
            coord=coord
        )),
        (Component.HEALTH, components.HealthComponent()),
        (Component.COLLECTABLE, components.CollectableComponent()),
        (Component.DRAW, components.draw.DrawCircleComponent(
            size=0.4,
            color=(255, 255, 0)
        )),
    ]))

def create_bomb(coord=None):
    return Entity(components=OrderedDict([
        (Component.LOCATION, components.location.StaticLocationComponent(
            coord=coord
        )),
        (Component.EXPLOSION, components.ExplosionComponent(
            power=2.0,
            time=3.0
        )),
        (Component.DRAW, components.draw.DrawCircleComponent(
            size=0.8,
            color=(255, 0, 0)
        )),
    ]))

def create_player(coord=None):
    return Entity(components=OrderedDict([
        (Component.BEHAVIOR, components.behavior.HumanPlayerInputComponent()),
        (Component.LOCATION, components.location.MovingLocationComponent(
            coord=coord,
            speed=10.0
        )),
        ('mining', components.MiningComponent()),
        (Component.COLLECTOR, components.CollectorComponent()),
        (Component.DRAW, components.draw.DrawRectangleComponent(
            size=0.8,
            color=(0, 196, 0),
            color_by_state=OrderedDict([
                ('colliding', (255, 255, 0)),
                ('moving', (128, 255, 128)),
            ])
        )),
    ]))

def create_monster(coord=None):
    return Entity(components=OrderedDict([
        (Component.BEHAVIOR, components.behavior.AgressiveAIComponent(
            walk_distance=15,
            attack_distance=10,
            walk_speed=3,
            attack_speed=5
        )),
        (Component.LOCATION, components.location.MovingLocationComponent(
            coord=coord,
            speed=3
        )),
        (Component.HEALTH, components.HealthComponent()),
        (Component.DRAW, components.draw.DrawRectangleComponent(
            size=0.8,
            color=(255, 128, 0),
            color_by_state=OrderedDict([
                ('chasing', (255, 0, 0)),
            ])
        )),
    ]))
