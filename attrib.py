import pygame
from numpy import array, random, reshape, ravel

from genetic import Population
from objects import Color, Direction, Ground, Snake


class Game:
    __instance__ = None

    def get_instance():
        if Game.__instance__ == None:
            Game()
        return Game.__instance__

    def __init__(self):
        self.frame_rate = 1000       # FPS
        self.frames = 0              # counts number of frames elapsed
        self.exit = False            # Flag to exit the game
        self.manual = False
        title = 'Snake'         # Window Title
        icon_filename = 'res/icon.png'

        # loads pygame modules
        pygame.init()

        # initializing game objects
        self.population = Population(layers=(6, 6, 6, 6, 6, 3))

        # screen params
        icon = pygame.image.load(icon_filename)
        pygame.display.set_icon(icon)
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode(Ground().get_dimensions())
    
        # reference clock
        self.clock = pygame.time.Clock()

        Game.__instance__ = self
    
    def loop(self):
        while not self.exit:
            for individual in self.population.individuals:
                snake = individual.snake
                while not self.exit and not snake.game_over:
                    # update objects for each frame
                    self.update_objects(snake)

                    # if game over skip
                    if snake.game_over:
                        continue

                    # get feature vector
                    X = snake.get_features()
                    # print(ravel(X))
                    
                    # output of feed forward of neural network
                    y = ravel(individual.nn.feed_forward(X))
                    snake.respond(y)

                    # capture user input
                    self.capture_input(snake)
                    # draw objects on screen
                    self.draw_objects(snake)
                # print(individual.nn.weights)
            self.population.evolve()

    
    def update_objects(self, snake):
        self.clock.tick(self.frame_rate)
        snake.update()
    
    def capture_input(self, snake):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit = True
            elif event.type == pygame.KEYDOWN:
                if self.manual:
                    if event.key == pygame.K_UP:
                        snake.move(Direction.UP)
                    elif event.key == pygame.K_DOWN:
                        snake.move(Direction.DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.move(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.move(Direction.RIGHT)
                if event.key == pygame.K_u:
                    self.frame_rate = 1000
                if event.key == pygame.K_i:
                    self.frame_rate = 100
                if event.key == pygame.K_o:
                    self.frame_rate = 10
                if event.key == pygame.K_p:
                    self.frame_rate = 1
                
                if event.key == pygame.K_q:
                    snake.game_over = True

    def draw_objects(self, snake):
        self.screen.fill(Color.BLACK)
        snake.draw(self.screen)
        pygame.display.update()
        
