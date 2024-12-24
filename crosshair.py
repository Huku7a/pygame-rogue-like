import pygame
from settings import *

class Crosshair(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Создаем поверхность для прицела
        self.image = pygame.Surface((CROSSHAIR_SIZE, CROSSHAIR_SIZE), pygame.SRCALPHA)
        
        # Рисуем прицел
        half_size = CROSSHAIR_SIZE // 2
        # Горизонтальная линия
        pygame.draw.line(self.image, CROSSHAIR_COLOR, 
                        (0, half_size), 
                        (CROSSHAIR_SIZE, half_size), 
                        CROSSHAIR_WIDTH)
        # Вертикальная линия
        pygame.draw.line(self.image, CROSSHAIR_COLOR, 
                        (half_size, 0), 
                        (half_size, CROSSHAIR_SIZE), 
                        CROSSHAIR_WIDTH)
        
        self.rect = self.image.get_rect()
        
        # Скрываем системный курсор
        pygame.mouse.set_visible(False)

    def update(self):
        # Обновляем позицию прицела в соответствии с позицией мыши
        pos = pygame.mouse.get_pos()
        self.rect.center = pos 