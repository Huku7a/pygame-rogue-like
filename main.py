import pygame
import sys
from settings import *
from game import Game

class DiabloKiller:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Diablo Killer')
        self.clock = pygame.time.Clock()
        self.game = Game()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Обновление
            self.game.update()

            # Отрисовка
            self.screen.fill('black')
            self.game.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = DiabloKiller()
    game.run() 