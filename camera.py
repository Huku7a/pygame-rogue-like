import pygame
from settings import *

class Camera:
    def __init__(self, target):
        self.target = target
        self.offset = pygame.math.Vector2(0, 0)
        self.DISPLAY_W = SCREEN_WIDTH
        self.DISPLAY_H = SCREEN_HEIGHT
        self.offset_float = pygame.math.Vector2(0, 0)

    def scroll(self):
        """Плавное следование за целью"""
        # Вычисляем желаемое положение камеры
        desired_x = self.target.rect.centerx - self.DISPLAY_W // 2
        desired_y = self.target.rect.centery - self.DISPLAY_H // 2
        
        # Плавно перемещаем камеру к желаемой позиции
        self.offset_float.x += (desired_x - self.offset_float.x) * CAMERA_SMOOTHNESS
        self.offset_float.y += (desired_y - self.offset_float.y) * CAMERA_SMOOTHNESS
        
        # Обновляем целочисленное смещение для отрисовки
        self.offset.x = int(self.offset_float.x)
        self.offset.y = int(self.offset_float.y)

    def apply(self, entity):
        """Применяет смещение камеры к спрайту"""
        return pygame.Rect(entity.rect.x - self.offset.x,
                         entity.rect.y - self.offset.y,
                         entity.rect.width,
                         entity.rect.height)

    def apply_rect(self, rect):
        """Применяет смещение камеры к прямоугольнику"""
        return pygame.Rect(rect.x - self.offset.x,
                         rect.y - self.offset.y,
                         rect.width,
                         rect.height)

    def apply_point(self, x, y):
        """Применяет смещение камеры к точке"""
        return (x - self.offset.x, y - self.offset.y)

    def reset(self):
        """Сброс позиции камеры"""
        self.offset = pygame.math.Vector2(0, 0)
        self.offset_float = pygame.math.Vector2(0, 0) 