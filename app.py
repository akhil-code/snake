import pygame
from attrib import Game

def main():
    Game.get_instance().loop()
    pygame.quit()

if __name__=='__main__':
    main()