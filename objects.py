from enum import Enum
from math import pow, sqrt

import pygame
from numpy import array, concatenate, int32, random, ravel, reshape, zeros, argmax


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


class Snake:
    def __init__(self):
        self.score = 0                  
        self.game_over = False
        self.min_score = -1000

        # ground objects
        self.ground = Ground()

        # center of board
        board_center = (int(self.ground.columns/2), int(self.ground.rows/2))
        # body is a list of parts
        self.body = [
            {
                'origin' : board_center,
                'direction' : Direction.UP,
                'length' : 5,
            },
        ]

        # marking all points of snake on grid
        points = self.find_all_points(self.body[0])
        for point in points:
            self.mark_ground(point, 1)
        
        # food object
        self.food = Food()
        self.food.get_new_position(self.ground)

        # distance between snake and food
        self.delta_distance = self.find_distance(
            self.food.get_current_position(),
            self.find_end_point(self.body[0])
        )
    
    def reset(self):
        """ reset's snake object by calling it's constructor """
        self.__init__()


    def create_part(self, origin, direction, length):
        """ return new part with specified attributes """
        part = {
            'origin' : origin,
            'direction' : direction, 
            'length' : length,
        }
        return part

    def update(self):
        """
        if body has only one part then shift the origin in it's current direction
        else if it has more than one part then
            - increase size of head by one
            - decrease size of tail by 1 and after decreasing tail's length,
              if tail's length is zero then delete that part
        """
        body_size = len(self.body)
        # marking ground before moving
        self.mark_ground(self.body[-1]['origin'], 0)

        # if snake is made of only one part
        if body_size == 1:
            head = self.body[0]
            self.body[0] = self.shift_origin(head)
        # if snake is made up of more than one part
        else:
            self.increase_head_length()
            self.decrease_tail_length()
        
        # marking ground after moving
        self.mark_ground((self.find_end_point(self.body[0])), 1)

        # if food is consumed, then increase the length of head by two and mark the grid as well
        # then find new position for food
        if self.consumed_food():
            self.score += self.food.value
            for i in range(self.food.delta_increase):
                self.body[0]['length'] += 1
                self.mark_ground((self.find_end_point(self.body[0])), 1)
            self.food.get_new_position(self.ground)

        # check if head of snake lies inside the grid
        head_point = self.find_end_point(self.body[0])
        if not self.ground.is_inside_grid(*head_point) or self.score < self.min_score:
            self.game_over = True
            return

        # updating distance between food and snake
        # and score related to it as well
        current_delta_distance = self.find_distance(
            self.food.get_current_position(),
            self.find_end_point(self.body[0])
        )

        if current_delta_distance < self.delta_distance:
            self.score += 1
        else:
            self.score -= 1.5
        self.delta_distance = current_delta_distance
        
        # features for snake's neural network
        self.features = concatenate((
            self.get_wall_distances(),
            self.get_body_distances(),
            self.get_food_features(),
        ))
    
    
    def get_wall_distances(self):
        head = self.body[0]
        deltas = Direction.get_relative_deltas(head['direction'])

        distances = [self.find_wall_distance_in_direction(head, delta) for delta in deltas]
        distances = array(distances)
        distances = distances / self.ground.diagonal
        distances = reshape(distances, (len(deltas), 1))
        return distances
    

    def find_wall_distance_in_direction(self, head, delta):
        x_, y_ = self.find_end_point(head)
        deltax, deltay = delta
        distance = 0
        while True:
            x_ += deltax
            y_ += deltay
            if self.ground.is_inside_grid(x_, y_):
                if abs(deltax) == 1 and abs(deltay) == 1:
                    distance += sqrt(2)
                else:
                    distance += 1
            else:
                return distance
        return distance
    
    def get_body_distances(self):
        head = self.body[0]
        deltas = Direction.get_relative_deltas(head['direction'])

        distances = [self.find_body_distance_in_direction(head, delta) for delta in deltas]
        distances = array(distances)
        print(ravel(distances))
        distances = distances / self.ground.diagonal
        distances = reshape(distances, (len(deltas), 1))
        return distances
    
    def find_body_distance_in_direction(self, head, delta):
        x_, y_ = self.find_end_point(head)
        deltax, deltay = delta
        distance = 0
        while True:
            x_ += deltax
            y_ += deltay
            if self.ground.is_inside_grid(x_, y_):
                if self.ground.grid[y_][x_] != 1:
                    if abs(deltax) == 1 and abs(deltay) == 1:
                        distance += sqrt(2)
                    else:
                        distance += 1
                else:
                    return distance
            else:
                return self.ground.diagonal
        return distance
    
    def get_food_features(self):
        """ features = (front, left, right, back) """
        if self.is_food_ahead():
            features = (1, 0, 0, 0)
        elif self.is_food_to_left(self.body[0]['direction']):
            features = (0, 1, 0, 0)
        elif self.is_food_to_right(self.body[0]['direction']):
            features = (0, 0, 1, 0)
        else:
            features = (0, 0, 0, 1)
        
        features = array(features)
        features = reshape(features, (len(features), 1))
        return features

    def is_food_ahead(self):
        head = self.body[0]
        x_, y_ = self.find_end_point(head)
        direction = head['direction']

        while self.ground.is_inside_grid(x_, y_):
            if direction == Direction.LEFT:
                x_ -= 1
            elif direction == Direction.RIGHT:
                x_ += 1
            elif direction == Direction.UP:
                y_ -= 1
            elif direction == Direction.DOWN:
                y_ += 1
            
            if self.ground.is_inside_grid(x_, y_):
                if self.food.get_current_position == (x_, y_):
                    return True
            else:
                return False
    
    def is_food_to_left(self, direction):
        xf, yf = self.food.get_current_position()       # food position
        xs, ys = self.find_end_point(self.body[0])      # snake position

        if direction == Direction.LEFT:
            if yf > ys:
                return True
        elif direction == Direction.RIGHT:
            if yf < ys:
                return True
        elif direction == Direction.UP:
            if xf < xs:
                return True
        elif direction == Direction.DOWN:
            if xf > xs:
                return True

        return False
    
    def is_food_to_right(self, direction):
        xf, yf = self.food.get_current_position()       # food position
        xs, ys = self.find_end_point(self.body[0])      # snake position

        if direction == Direction.LEFT:
            if yf < ys:
                return True
        elif direction == Direction.RIGHT:
            if yf > ys:
                return True
        elif direction == Direction.UP:
            if xf > xs:
                return True
        elif direction == Direction.DOWN:
            if xf < xs:
                return True

        return False


    def find_distance(self, p1, p2):
        """ find's euclidean distance between two points """
        x1, y1 = p1
        x2, y2 = p2
        return sqrt(pow(x1-x2, 2) + pow(y1-y2, 2))

    def get_features(self):
        """ return feature vector X for neural network """
        return self.features

    def respond(self, y):
        # finding relative directions
        current_direction = self.body[0]['direction']
        left_direction = Direction.get_direction_to_left(current_direction)
        right_direction = Direction.get_opposite_direction(left_direction)
        
        # One Vs All for multiclass neural network
        index = argmax(y)
        if y[index] > 0.5:
            if index == 0:
                self.move(left_direction)
            elif index == 1:
                self.move(current_direction)
            elif index == 2:
                self.move(right_direction)

    def consumed_food(self):
        """ checks if snake has consumed new food """
        # first index for body's head
        head = self.body[0]
        head_point = self.find_end_point(head)
        if head_point == self.food.get_current_position():
            return True
        return False

    def increase_head_length(self):
        """ increase size of head by 1 """
        self.body[0]['length'] += 1
    
    def decrease_tail_length(self):
        """ decrease size of tail by 1 """
        self.body[-1]['length'] -= 1
        # shift origin of last part by one unit
        self.body[-1] = self.shift_origin(self.body[-1])
        # if tail length is zero, then delete it
        if self.body[-1]['length'] <= 0:
            del self.body[-1]
    
    def shift_origin(self, part, delta=1):
        """ shifts origin of the part by amount of delta units """
        x_, y_ = part['origin']
        direction = part['direction']
        length = part['length']

        if direction == Direction.LEFT:
            origin = (x_ - delta, y_)
        elif direction == Direction.RIGHT:
            origin = (x_ + delta, y_)
        elif direction == Direction.UP:
            origin = (x_, y_ - delta)
        elif direction == Direction.DOWN:
            origin = (x_, y_ + delta)

        new_part = self.create_part(origin, direction, length)
        return new_part
    
    def find_end_point(self, part):
        """ finds end point of the part other than origin """
        x_, y_ = part['origin']
        length = part['length'] - 1
        direction = part['direction']

        if direction == Direction.LEFT:
            end_point = (x_ - length, y_,)
        elif direction == Direction.RIGHT:
            end_point = (x_ + length, y_,)
        elif direction == Direction.UP:
            end_point = (x_, y_ - length,)
        elif direction == Direction.DOWN:
            end_point = (x_, y_ + length,)    

        return end_point
    
    def find_all_points(self, part):
        """ returns all the points included for a given part """
        x_, y_ = part['origin']
        length = part['length']
        direction = part['direction']

        # stores array of points
        points = []

        # creates points array
        for i in range(length):
            if direction == Direction.LEFT:
                point = (x_ - i, y_)
            elif direction == Direction.RIGHT:
                point = (x_ + i, y_)
            elif direction == Direction.UP:
                point = (x_, y_ - i)
            elif direction == Direction.DOWN:
                point = (x_, y_ + i)
            points.append(point)

        return points



    def move(self, new_direction):
        """
        if new-direction == current/opposite to head-direction then return
        else, add new part at the start of list
        reduce the length of current head by 1
        new part = (find_end_point(previous-head), new-direction, 1)


        """
        head = self.body[0]
        is_same_direction = (head['direction'] == new_direction)
        is_opposite_direction =  (new_direction == Direction.get_opposite_direction(head['direction']))
        
        if is_same_direction or is_opposite_direction:
            return
        else:
            end_point = self.find_end_point(head)
            # creating new head of length 1
            new_head = self.create_part(end_point, new_direction, 1)
            # reducing the length of current head by 1
            self.body[0]['length'] -= 1
            # appending the new head to the snake's body
            self.body = [new_head] + self.body
    
    def draw(self, screen):
        # draw food
        point = self.food.get_current_position()
        rect = self.ground.get_rect(point, point)
        pygame.draw.rect(screen, Color.RED, rect)

        # draw snake's parts
        for part in self.body:
            """ for each part find rectangle and draw it using pygame draw function """
            p1 = part['origin']
            p2 = self.find_end_point(part)
            rect = self.ground.get_rect(p1, p2)
            pygame.draw.rect(screen, Color.WHITE, rect)
    
    def mark_ground(self, point, value):
        x_, y_ = point

        if self.ground.is_inside_grid(x_, y_):
            """
            if a particular cell is already occupied
            and again trying to occupy, then game over

            """
            if value == 1 and self.ground.grid[y_][x_] == 1:
                self.game_over = True
            self.ground.grid[y_][x_] = value
    

class Ground:

    def __init__(self):
        # pixel dimensions
        self.width = 640
        self.height = 480
        self.box_width = 10
        # grid dimensions
        self.rows = int(self.height / self.box_width)
        self.columns = int(self.width /self.box_width)
        self.diagonal = sqrt(pow(self.rows, 2) + pow(self.columns, 2))
        # grid layout
        self.grid = zeros((self.rows, self.columns), dtype=int32)

    def get_dimensions(self):
        """ returns grid dimensions """
        return (self.width, self.height)
    
    def get_rect(self, p1, p2):
        """ returns pygame's rectangle object for rectangle created by two points on grid """
        x1_, y1_ = p1
        x2_, y2_ = p2
        # vertical grid
        if x1_ == x2_:
            left = min((x1_, x2_)) * self.box_width
            top = min((y1_, y2_)) * self.box_width
            width = self.box_width
            height = (abs(y1_-y2_) + 1) * self.box_width
        # horizontal grid
        elif y1_ == y2_:
            left = min((x1_, x2_)) * self.box_width
            top = min((y1_, y2_)) * self.box_width
            width = (abs(x1_ - x2_) + 1) * self.box_width
            height = self.box_width

        return pygame.Rect(left, top, width, height)
    
    def is_inside_grid(self, x_, y_):
        """ checks if a point lies inside the grid """
        return (x_ >= 0 and y_ >= 0 and x_ < self.columns and y_ < self.rows)
    
    def reset_grid(self):
        """ resets entire grid layout to initial state """
        self.grid = zeros((self.rows, self.columns), dtype=int32)
    

class Food:
    def __init__(self):
        self.value = 100        # score increased upon consuming it
        self.delta_increase = 2 # increase in length of snake upon consumption of food

    def get_new_position(self, ground):
        """ finds new poisition for food on ground that's free """
        while True:
            x_ = random.randint(0, high=ground.columns)
            y_ = random.randint(0, high=ground.rows)
            if ground.grid[y_][x_] == 0:
                break
        
        self.x_, self.y_ = x_, y_
        return (x_, y_)
    
    def get_current_position(self):
        """ returns current position of food """
        return (self.x_, self.y_)
