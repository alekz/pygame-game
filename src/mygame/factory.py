#from mygame import components
import components.draw
import components.location
import components.movement
import components.behavior
from components import Component
from entities import Entity

def create_coin(coord=None):

    location = components.location.LocationComponent(coord=coord)
    draw = components.draw.DrawCircleComponent(size=0.4, color=(255, 255, 0))

    return Entity(components={
        Component.LOCATION: location,
        Component.DRAW: draw,
    })

def create_bomb(coord=None):

    location = components.location.LocationComponent(coord=coord)
    draw = components.draw.DrawCircleComponent(size=0.8, color=(255, 0, 0))
    explosion = components.ExplosionComponent(power=2.0, time=3.0)

    return Entity(components={
        Component.LOCATION: location,
        Component.DRAW: draw,
        Component.EXPLOSION: explosion,
    })

def create_player(coord=None):

    location = components.location.LocationComponent(coord=coord)
    movement = components.movement.MovementComponent(speed=10.0)
    behavior = components.behavior.HumanPlayerInputComponent()
    draw = components.draw.DrawRectangleComponent(size=0.8, color=(0, 255, 0))

    return Entity(components={
        Component.LOCATION: location,
        Component.MOVEMENT: movement,
        Component.BEHAVIOR: behavior,
        Component.DRAW: draw,
    })
