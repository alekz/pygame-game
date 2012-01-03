#from mygame import components
import components.draw
import components.location
import components.behavior
from components import Component
from entities import Entity

def create_coin(coord=None):
    return Entity(components={
        Component.LOCATION: components.location.StaticLocationComponent(coord=coord),
        Component.DRAW: components.draw.DrawCircleComponent(size=0.4, color=(255, 255, 0)),
        Component.HEALTH: components.HealthComponent(),
        Component.COLLECTABLE: components.CollectableComponent(),
    })

def create_bomb(coord=None):
    return Entity(components={
        Component.LOCATION: components.location.StaticLocationComponent(coord=coord),
        Component.DRAW: components.draw.DrawCircleComponent(size=0.8, color=(255, 0, 0)),
        Component.EXPLOSION: components.ExplosionComponent(power=2.0, time=3.0),
    })

def create_player(coord=None):
    return Entity(components={
        Component.LOCATION: components.location.MovingLocationComponent(coord=coord, speed=10.0),
        Component.BEHAVIOR: components.behavior.HumanPlayerInputComponent(),
        Component.DRAW: components.draw.DrawRectangleComponent(size=0.8, color=(0, 255, 0)),
        Component.COLLECTOR: components.CollectorComponent(),
    })

def create_monster(coord=None):
    return Entity(components={
        Component.LOCATION: components.location.MovingLocationComponent(coord=coord, speed=3),
        Component.BEHAVIOR: components.behavior.AgressiveAIComponent(
            walk_speed=3,
            attack_speed=5,
            walk_distance=15,
            attack_distance=10,
            walk_color=(255, 128, 0),
            attack_color=(255, 0, 0)
        ),
        Component.HEALTH: components.HealthComponent(),
        Component.DRAW: components.draw.DrawRectangleComponent(size=0.8, color=(255, 128, 0)),
    })
