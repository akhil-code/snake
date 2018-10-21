import math
import operator
from enum import Enum
from math import cos, pow, sqrt

import pygame
from numpy import any, array, int32, random, zeros, concatenate, reshape, ravel

MAX_VALUE = 3200

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
    
    def get_all_directions():
        return (Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN)


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
        self.time = 0
        self.game_over = False
    
        # body is a list of parts
        self.ground = Ground()
        self.normalisation_factor = sqrt(pow(self.ground.rows, 2) + pow(self.ground.columns, 2))
        

        board_center = (int(self.ground.columns/2), int(self.ground.rows/2))

        self.body = [
            {
                'origin' : board_center,
                'direction' : Direction.UP,
                'length' : 5,
            },
        ]

        # marking all points on ground's grid
        points = self.find_all_points(self.body[0])
        for point in points:
            self.mark_ground(point, 1)
        
        self.food = Food()
        self.food.get_new_position(self.ground)
        self.closest_distance = [self.normalisation_factor]

    
    def reset(self):
        self.__init__()


    def create_part(self, origin, direction, length):
        part = {
            'origin' : origin,
            'direction' : direction, 
            'length' : length,
        }
        return part

    def update(self):
        # if body.size() == 1 then shift origin in that direction
        # if body.size > 1 then 
        #   - increase size of head by 1
        #   - decrease size of tail by 1
        #       - if length of tail == 0, then delete tail
        
        self.time += 1
        body_size = len(self.body)
        # marking ground before moving
        self.mark_ground(self.body[-1]['origin'], 0)

        if body_size == 1:
            head = self.body[0]
            self.body[0] = self.shift_origin(head)
        else:
            self.increase_head_length()
            self.decrease_tail_length()
        
        # marking ground after moving
        self.mark_ground((self.find_end_point(self.body[0])), 1)

        head_point = self.find_end_point(self.body[0])
        self.closest_distance[-1] = self.find_distance(head_point, self.food.get_current_position())

        if self.consumed_food():
            self.score += 1
            for i in range(2):
                self.body[0]['length'] += 1
                self.mark_ground((self.find_end_point(self.body[0])), 1)
            self.food.get_new_position(self.ground)
            self.closest_distance.append(self.normalisation_factor)

        # find distances (features)
        head_point = self.find_end_point(self.body[0])
        if not self.ground.is_inside_grid(*head_point):
            self.game_over = True
            return

        self.features = concatenate((self.get_normalised_coordinates(), self.get_food_features(), self.find_distances_from_body()))
    
    def find_distance(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return sqrt(pow(x1-x2, 2) + pow(y1-y2, 2))

    def get_normalised_coordinates(self):
        # position
        head = self.body[0]
        head_point_feature = self.find_end_point(head)
        head_point_feature = array(head_point_feature)
        head_point_feature = head_point_feature / self.normalisation_factor
        head_point_feature = reshape(head_point_feature, (2, 1))

        # direction
        direction_feature = [0, 0, 0, 0]
        direction_feature[head['direction'].value] = 1
        direction_feature = array(direction_feature)
        direction_feature = reshape(direction_feature, (4, 1))
        return concatenate((head_point_feature, direction_feature))


    def get_features(self):
        return self.features

    def consumed_food(self):
        # first index for body's head
        head = self.body[0]
        head_point = self.find_end_point(head)
        if head_point == self.food.get_current_position():
            return True
        return False

    def increase_head_length(self):
        # increase size of head by 1
        self.body[0]['length'] += 1
    
    def decrease_tail_length(self):
        # decrease size of tail by 1
        self.body[-1]['length'] -= 1
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
    
    def find_all_points(self, part):
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

    def find_distances_from_food(self):
        head_point = self.find_end_point(self.body[0])

        deltax = (-1, -1, -1, 0, 0, 1, 1, 1)
        deltay = (-1, 0, 1, -1, 1, -1, 0, 1)

        distances = [self.find_distance_from_food_in_direction(head_point, deltax[i], deltay[i]) for i in range(len(deltax))]
        distances = array(distances)
        distances = distances / self.normalisation_factor
        distances = reshape(distances, (8, 1))
        return distances
    
    def find_distance_from_food_in_direction(self, point, deltax, deltay):
        x_, y_ = point

        # base case
        if not (x_ >= 0 and y_ >= 0 and x_ < self.ground.columns and y_ < self.ground.rows):
            return -MAX_VALUE
        
        count = 0
        hit_food = False
        while self.ground.is_inside_grid(x_, y_):
            count += 1
            x_ += deltax
            y_ += deltay
            if self.ground.is_inside_grid(x_, y_) and self.food.get_current_position() == (x_, y_):
                hit_food = True
                break

        # if body doesn't come in way
        if not hit_food:
            return MAX_VALUE

        # if diagnal direction
        if abs(deltax) == 1 and abs(deltay) == 1:
            return count * sqrt(2)
        
        return count
    
    def get_food_features(self):
        pos = array(self.food.get_current_position())
        pos = reshape(pos, (2, 1))
        pos = pos / self.normalisation_factor
        return pos
        

    def find_distances_from_body(self):
        head_point = self.find_end_point(self.body[0])
        normalisation_factor = MAX_VALUE    # donot change

        distances = []

        deltax = (-1, -1, -1, 0, 0, 1, 1, 1)
        deltay = (-1, 0, 1, -1, 1, -1, 0, 1)

        for i in range(len(deltax)):
            dist = self.find_distance_from_body_in_direction(head_point, deltax[i], deltay[i])
            dist /= normalisation_factor    # donot change
            distances.append(dist)
        
        distances = array(distances)
        distances = reshape(distances, (8, 1))
        return distances

    def find_distance_from_body_in_direction(self, point, deltax, deltay):
        x_, y_ = point

        # base case
        if not (x_ >= 0 and y_ >= 0 and x_ < self.ground.columns and y_ < self.ground.rows):
            return -MAX_VALUE

        count = 0
        hit_body = False
        while self.ground.is_inside_grid(x_, y_):
            count += 1
            x_ += deltax
            y_ += deltay
            if self.ground.is_inside_grid(x_, y_) and self.ground.grid[y_][x_] == 1:
                hit_body = True
                break

        # if body doesn't come in way
        if not hit_body:
            return MAX_VALUE

        # if diagnal direction
        if abs(deltax) == 1 and abs(deltay) == 1:
            return count * sqrt(2)
        
        return count


    def find_distances_from_walls(self):
        head_point = self.find_end_point(self.body[0])

        deltax = (-1, -1, -1, 0, 0, 1, 1, 1)
        deltay = (-1, 0, 1, -1, 1, -1, 0, 1)

        distances = [self.find_distance_from_wall_in_direction(head_point, deltax[i], deltay[i]) for i in range(len(deltax))]
        distances = array(distances)
        distances = distances / self.normalisation_factor

        distances = reshape(distances, (8, 1))
        return distances

    def find_distance_from_wall_in_direction(self, point, deltax, deltay):
        x_, y_ = point

        # if head outside the grid then return negative distance
        if not self.ground.is_inside_grid(x_, y_):
            return NINF

        count = 0
        while self.ground.is_inside_grid(x_, y_):
            count += 1
            x_ += deltax
            y_ += deltay

        count -= 1

        # if diagnal direction
        if abs(deltax) == 1 and abs(deltay) == 1:
            return count * sqrt(2)
        
        return count



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
    
    def draw(self, screen):
        # draw food
        point = self.food.get_current_position()
        rect = self.ground.get_rect(point, point)
        pygame.draw.rect(screen, Color.RED, rect)

        # draw snake's parts
        for part in self.body:
            p1 = part['origin']
            p2 = self.find_end_point(part)
            rect = self.ground.get_rect(p1, p2)
            pygame.draw.rect(screen, Color.WHITE, rect)
    
    def mark_ground(self, point, value):
        x_, y_ = point

        if self.ground.is_inside_grid(x_, y_):
            if value == 1 and self.ground.grid[y_][x_] == 1:
                self.game_over = True
            self.ground.grid[y_][x_] = value
    

class Ground:

    def __init__(self):
        self.width = 640
        self.height = 480
        self.box_width = 10
        self.rows = int(self.height / self.box_width)
        self.columns = int(self.width /self.box_width)
        self.grid = zeros((self.rows, self.columns), dtype=int32)


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
    
    def is_inside_grid(self, x_, y_):
        return (x_ >= 0 and y_ >= 0 and x_ < self.columns and y_ < self.rows)
    
    def reset_grid(self):
        self.grid = zeros((self.rows, self.columns), dtype=int32)
    
    def print_grid(self):
        for i in range(self.rows):
            for j in range(self.columns):
                print(self.grid[i][j], end=" ")
            print("")
        print("\n\n\n")



class Food:
    def get_new_position(self, ground):
        while True:
            x_ = random.randint(0, high=ground.columns)
            y_ = random.randint(0, high=ground.rows)
            if ground.grid[y_][x_] == 0:
                break
        
        self.x_, self.y_ = x_, y_
        return (x_, y_)
    
    def get_current_position(self):
        return (self.x_, self.y_)
