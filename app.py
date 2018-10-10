import pygame
from attrib import Game

def main():
    screen, clock, population = Game.initialize()
    Game.loop(screen, clock, population)
    pygame.quit()

if __name__=='__main__':
    main()