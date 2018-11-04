from math import pow, sqrt

import pygame
from numpy import array, concatenate, int32, random, ravel, reshape, zeros, argmax



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
        self.value = 1000        # score increased upon consuming it

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
