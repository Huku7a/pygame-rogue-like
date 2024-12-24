import pygame
import sys
from settings import *
from game import Game

class Main:
    def __init__(self):
        # Инициализация Pygame
        pygame.init()
        
        # Создаем окно
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike RPG")
        
        # Создаем часы для контроля FPS
        self.clock = pygame.time.Clock()
        
        # Создаем игру
        self.game = Game()

    def run(self):
        running = True
        while running:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Обновление
            self.game.update()
            
            # Отрисовка
            self.game.draw(self.screen)
            pygame.display.flip()
            
            # Ограничение FPS
            self.clock.tick(FPS)
        
        # Завершение работы
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Main()
    game.run() 