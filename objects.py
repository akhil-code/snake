from numpy import array
from enum import Enum

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

class Color:
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLUE = (0,0,255)
    WHITE = (255,255,255)
    YELLOW = (255,255,0)
    BLACK = (0,0,0)

    colors = array([RED, GREEN, BLUE, WHITE, YELLOW])

class Snake:
    def __init__(self):
        self.score = 0
        self.head = None
    
        # body is a list of parts
        # part = (origin, direction, length)
        board_center = None
        self.body = [ (board_center, Direction.UP, 4) ]
    
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
            # increase size of head by 1
            self.body[0][2] += 1
            # decrease size of tail by 1
            self.body[-1][2] -= 1
            # if tail length is zero, then delete it
            if self.body[-1][2] <= 0:
                del self.body[-1]
    
    def shift_origin(self, part):
        origin = part[0]
        x = origin[0]
        y = origin[1]
        direction = part[1]
        length = part[2]

        if direction == Direction.LEFT:
            origin = (x-1, y)
        elif direction == Direction.RIGHT:
            origin = (x+1, y)
        elif direction == Direction.UP:
            origin = (x, y-1)
        elif direction == Direction.DOWN:
            origin = (x, y+1)

        return (origin, direction, length)
    
    def consume_food(self):
        # first index for body part
        # second index for length of first body part i.e head
        self.body[0][2] += 1


    def move(self, new_direction):
        # if new-direction == head-direction then return
        # else add new part at the start of list
        # new part = (find_end_point(previous-head), new-direction, 0)
        head = self.body[0]
        if head[1] == new_direction:
            return
        else:
            part = (self.find_end_point(head), new_direction, 0)
            self.body = [part] + self.body
    
    def find_end_point(self, part):
        origin = part[0]
        x = origin[0]
        y = origin[1]
        length = part[2]
        direction = part[1]
        if direction == Direction.LEFT:
            v = (x-length, y)
        elif direction == Direction.RIGHT:
            v = (x+length, y)
        elif direction == Direction.UP:
            v = (x, y-length)
        elif direction == Direction.DOWN:
            v = (x, y+length)    

        return v
    

class Ground:
    WIDTH = 640                     # width of screen
    HEIGHT = 480                    # height of screen
    BOX_WIDTH = 5                   # width of each box on screen

    ROWS = HEIGHT / BOX_WIDTH
    COLUMNS = WIDTH / BOX_WIDTH

    def get_dimensions():
        return (Ground.WIDTH, Ground.HEIGHT)