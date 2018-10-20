import pygame
from numpy import array, random, reshape

from genetic import Population
from objects import Color, Direction, Ground, Snake


class Game:
    __instance__ = None

    def get_instance():
        if Game.__instance__ == None:
            Game()
        return Game.__instance__

    def __init__(self):
        self.frame_rate = 20         # FPS
        self.frames = 0              # counts number of frames elapsed
        self.exit = False            # Flag to exit the game
        self.manual = True
        title = 'Snake'         # Window Title
        icon_filename = 'res/icon.png'

        # loads pygame modules
        pygame.init()

        # initializing game objects
        self.population = Population(layers=(24,24,24,4))

        # screen params
        icon = pygame.image.load(icon_filename)
        pygame.display.set_icon(icon)
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode(Ground.get_instance().get_dimensions())
    
        # reference clock
        self.clock = pygame.time.Clock()

        Game.__instance__ = self
    
    def loop(self):
        for individual in self.population.individuals:
            snake = individual.snake
            while not self.exit:
                # update objects for each frame
                self.update_objects(snake)
                # capture user input
                self.capture_input(snake)
                # draw objects on screen
                self.draw_objects(snake)

    
    def update_objects(self, snake):
        self.clock.tick(self.frame_rate)
        snake.update()
    
    def capture_input(self, snake):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.move(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    snake.move(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    snake.move(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    snake.move(Direction.RIGHT)

    def draw_objects(self, snake):
        self.screen.fill(Color.BLACK)
        snake.draw(self.screen)
        pygame.display.update()
        
