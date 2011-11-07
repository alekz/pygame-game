NONE = 0
LEFT = 1
RIGHT = 2
UP = 4
DOWN = 8

directions = (LEFT, RIGHT, UP, DOWN)
directions_with_none = (LEFT, RIGHT, UP, DOWN, NONE)
opposites = { LEFT: RIGHT, RIGHT: LEFT, UP: DOWN, DOWN: UP, NONE: NONE }
signs = { LEFT: -1, RIGHT: +1, UP: -1, DOWN: +1, NONE: 0 }
indices = { LEFT: 0, RIGHT: 0, UP: 1, DOWN: 1, NONE: None }

def get_opposite(direction):
    return opposites[direction]

def is_opposite(direction1, direction2):
    return direction1 == get_opposite(direction2)

def get_directions(with_none=False):
    if with_none:
        return directions_with_none
    else:
        return directions

def get_sign(direction):
    return signs[direction]

def get_index(direction):
    return indices[direction]

def get_info(direction):
    return (get_index(direction), get_sign(direction))
