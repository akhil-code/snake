import pygame
from numpy import random, array, reshape
from genetic import Population
from objects import Snake, Color, Ground


class Game:
    FRAME_RATE = 120        # FPS
    FRAMES = 0              # counts number of frames elapsed
    TITLE = 'Snake'         # Window Title
    EXIT = False            # Flag to exit the game
    ICON_PATH = 'res/icon.png'
    MANUAL = True

    def __init__(self):
        pass

    def initialize():
        pygame.init()

        # initializing game objects
        population = Population(layers=(24,24,24,4))

        # screen params
        icon = pygame.image.load(Game.ICON_PATH)
        pygame.display.set_icon(icon)
        pygame.display.set_caption(Game.TITLE)
        screen = pygame.display.set_mode(Ground.get_dimensions())
    
        # reference clock
        clock = pygame.time.Clock()

        return screen, clock, population
    
    def loop(screen, clock, population):
        while not Game.EXIT:
            # update objects for each frame
            Game.update_objects(clock)
            # capture user input
            Game.capture_input(population)
            # draw objects on screen
            Game.draw_objects()

    
    def update_objects(clock):
        clock.tick(Game.FRAME_RATE)
    
    def capture_input(population):
        snake = population.individuals[0].snake
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game.EXIT = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.move_up()
                elif event.key == pygame.K_DOWN:
                    snake.move_down()
                elif event.key == pygame.K_LEFT:
                    snake.move_left()
                elif event.key == pygame.K_RIGHT:
                    snake.move_right()

    def draw_objects():
        pass


