from enum import Enum

from numpy import random

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    LEFT_UP = 4
    LEFT_DOWN = 5
    RIGHT_UP = 6
    RIGHT_DOWN = 7
    
    

    def get_opposite_direction(direction):
        if direction == Direction.UP:
            return Direction.DOWN
        elif direction == Direction.DOWN: 
            return Direction.UP
        elif direction == Direction.LEFT:
            return Direction.RIGHT
        elif direction == Direction.RIGHT:
            return Direction.LEFT
    
    def get_direction_to_left(direction):
        if direction == Direction.UP:
            return Direction.LEFT
        elif direction == Direction.DOWN:
            return Direction.RIGHT
        elif direction == Direction.LEFT:
            return Direction.DOWN
        elif direction == Direction.RIGHT:
            return Direction.UP
    
    def get_relative_directions(current_direction):
        # all directions here are relative to snake
        directions = []
        reverse_direction = Direction.get_opposite_direction(current_direction)
        left_direction = Direction.get_direction_to_left(current_direction)
        right_direction = Direction.get_opposite_direction(left_direction)
        left_up_direction = Direction.combine(left_direction, current_direction)
        left_down_direction = Direction.combine(left_direction, reverse_direction)
        right_up_direction = Direction.combine(right_direction, current_direction)
        right_down_direction = Direction.combine(right_direction, reverse_direction)

        directions.append(current_direction)
        directions.append(left_direction)
        directions.append(right_direction)
        directions.append(left_up_direction)
        directions.append(left_down_direction)
        directions.append(right_up_direction)
        directions.append(right_down_direction)

        return directions
    
    def get_relative_deltas(current_direction):
        directions = Direction.get_relative_directions(current_direction)
    
        DELTAS = {
            Direction.LEFT : (-1, 0),
            Direction.RIGHT : (1, 0),
            Direction.UP : (0, -1),
            Direction.DOWN : (0, 1),
            Direction.LEFT_UP : (-1, -1),
            Direction.LEFT_DOWN : (-1, 1),
            Direction.RIGHT_UP : (1, -1),
            Direction.RIGHT_DOWN : (1, 1),
        }

        deltas = []
        for direction in directions:
            deltas.append(DELTAS[direction])
        return deltas

    def combine(dir1, dir2):
        if dir1 == Direction.LEFT or dir2 == Direction.LEFT:
            if dir1 == Direction.UP or dir2 == Direction.UP:
                return Direction.LEFT_UP
            elif dir1 == Direction.DOWN or dir2 == Direction.DOWN:
                return Direction.LEFT_DOWN
        elif dir1 == Direction.RIGHT or dir2 == Direction.RIGHT:
            if dir1 == Direction.UP or dir2 == Direction.UP:
                return Direction.RIGHT_UP
            elif dir1 == Direction.DOWN or dir2 == Direction.DOWN:
                return Direction.RIGHT_DOWN


class Color:
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLUE = (0,0,255)
    WHITE = (255,255,255)
    YELLOW = (255,255,0)
    BLACK = (0,0,0)

    def get_random_color():
        color = (
            random.randint(0, high=256),
            random.randint(0, high=256),
            random.randint(0, high=256),
        )
        return color
    
    def get_color(i):
        colors = (
            Color.RED,
            Color.GREEN,
            Color.BLUE,
            Color.WHITE,
            Color.YELLOW,
        )
        return colors[i % 5]
