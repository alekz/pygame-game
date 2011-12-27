#from mygame import components
import components.draw
import components.location
import components.movement
import components.behavior
from components import Component
from entities import Entity

def create_coin(coord=None):
    return Entity(components={
        Component.LOCATION: components.location.LocationComponent(coord=coord),
        Component.DRAW: components.draw.DrawCircleComponent(size=0.4, color=(255, 255, 0)),
        'health': components.HealthComponent(),
    })

def create_bomb(coord=None):
    return Entity(components={
        Component.LOCATION: components.location.LocationComponent(coord=coord),
        Component.DRAW: components.draw.DrawCircleComponent(size=0.8, color=(255, 0, 0)),
        Component.EXPLOSION: components.ExplosionComponent(power=2.0, time=3.0),
    })

def create_player(coord=None):
    return Entity(components={
        Component.LOCATION: components.location.LocationComponent(coord=coord),
        Component.MOVEMENT: components.movement.MovementComponent(speed=10.0),
        Component.BEHAVIOR: components.behavior.HumanPlayerInputComponent(),
        Component.DRAW: components.draw.DrawRectangleComponent(size=0.8, color=(0, 255, 0)),
    })
