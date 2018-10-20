from enum import Enum

import pygame
from numpy import array, int32, random, zeros


class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

    def get_opposite_direction(direction):
        if direction == Direction.UP:
            return Direction.DOWN
        elif direction == Direction.DOWN:
            return Direction.UP
        elif direction == Direction.LEFT:
            return Direction.RIGHT
        elif direction == Direction.RIGHT:
            return Direction.LEFT


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


class Snake:
    def __init__(self):
        self.score = 0
        self.head = None
        self.game_over = False
    
        # body is a list of parts
        self.ground = Ground.get_instance()
        board_center = (int(self.ground.columns/2), int(self.ground.rows/2))

        self.body = [
            {
                'origin' : board_center,
                'direction' : Direction.UP,
                'length' : 30,
            },
        ]
    
    def update(self):
        # if body.size() == 1 then shift origin in that direction
        # if body.size > 1 then 
        #   - increase size of head by 1
        #   - decrease size of tail by 1
        #       - if length of tail == 0 then delete tail
        body_size = len(self.body)
        if body_size == 1:
            head = self.body[0]
            self.body[0] = self.shift_origin(head)
        else:
            self.increase_head_length()
            self.decrease_tail_length()
    
    def increase_head_length(self):
        # increase size of head by 1
        self.body[0]['length'] += 1
        # next_x_, next_y_ = self.find_end_point(self.body[0], delta=1)
    
    def decrease_tail_length(self):
        # decrease size of tail by 1
        self.body[-1]['length'] -= 1
        # reset ground to 0
        # x_, y_ = self.body[-1]['origin']
        # self.ground.grid[y_][x_] = 0
        # shift origin of last part by one unit
        self.body[-1] = self.shift_origin(self.body[-1])
        # if tail length is zero, then delete it
        if self.body[-1]['length'] <= 0:
            del self.body[-1]

    
    def shift_origin(self, part):
        x_, y_ = part['origin']
        direction = part['direction']
        length = part['length']


        if direction == Direction.LEFT:
            origin = (x_-1, y_)
        elif direction == Direction.RIGHT:
            origin = (x_+1, y_)
        elif direction == Direction.UP:
            origin = (x_, y_-1)
        elif direction == Direction.DOWN:
            origin = (x_, y_+1)

        new_part = self.create_part(origin, direction, length)
        return new_part
    
    def consume_food(self):
        # first index for body's head
        self.body[0]['length'] += 1

    def create_part(self, origin, direction, length):
        part = {
            'origin' : origin,
            'direction' : direction, 
            'length' : length,
        }
        return part

    def move(self, new_direction):
        # if new-direction == head-direction then return
        # else add new part at the start of list
        # new part = (find_end_point(previous-head), new-direction, 0)
        head = self.body[0]
        is_same_direction = (head['direction'] == new_direction)
        is_opposite_direction =  (new_direction == Direction.get_opposite_direction(head['direction']))
        
        if is_same_direction or is_opposite_direction:
            return
        else:
            end_point = self.find_end_point(head)
            new_head = self.create_part(end_point, new_direction, 1)
            self.body[0]['length'] -= 1
            self.body = [new_head] + self.body
    
    def find_end_point(self, part):
        x_, y_ = part['origin']
        length = part['length'] - 1
        direction = part['direction']

        if direction == Direction.LEFT:
            v = (x_ - length, y_,)
        elif direction == Direction.RIGHT:
            v = (x_ + length, y_,)
        elif direction == Direction.UP:
            v = (x_, y_ - length,)
        elif direction == Direction.DOWN:
            v = (x_, y_ + length,)    

        return v
    
    def draw(self, screen):
        for part in self.body:
            p1 = part['origin']
            p2 = self.find_end_point(part)
            rect = self.ground.get_rect(p1, p2)
            pygame.draw.rect(screen, Color.WHITE, rect)
    

class Ground:
    __instance__ = None

    def __init__(self):
        self.width = 640
        self.height = 480
        self.box_width = 5
        self.rows = int(self.height / self.box_width)
        self.columns = int(self.width /self.box_width)
        self.grid = zeros((self.rows, self.columns), dtype=int32)

        Ground.__instance__ = self

    def get_instance():
        if Ground.__instance__ == None:
            Ground()
        return Ground.__instance__

    def get_dimensions(self):
        return (self.width, self.height)
    
    def get_rect(self, p1, p2):
        x1_, y1_ = p1
        x2_, y2_ = p2
        if x1_ == x2_:
            left = min((x1_, x2_)) * self.box_width
            top = min((y1_, y2_)) * self.box_width
            width = self.box_width
            height = (abs(y1_-y2_) + 1) * self.box_width
        elif y1_ == y2_:
            left = min((x1_, x2_)) * self.box_width
            top = min((y1_, y2_)) * self.box_width
            width = (abs(x1_ - x2_) + 1) * self.box_width
            height = self.box_width

        return pygame.Rect(left, top, width, height)


class Food:
    __instance__ = None

    def __init__(self):
        Food.__instance__ = self

    def get_instance():
        if Food.__instance__ == None:
            Food()
        return Food.__instance__

    def get_new_position(self):
        ground = Ground.get_instance()
        x_ = random.randint(0, high=ground.width)
        y_ = random.randint(0, high=ground.height)
        
        return (x_, y_)