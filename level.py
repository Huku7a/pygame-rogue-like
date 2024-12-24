import pygame
import random
import math
from settings import *
from level_generator import LevelGenerator

class Level:
    def __init__(self, game, level_number=1):
        self.game = game
        self.level_number = level_number
        self.tile_size = TILESIZE
        self.width = 50  # Размер уровня в тайлах
        self.height = 50
        self.checkpoints = []
        self.active_checkpoint = None
        self.portal = None
        self.portal_particles = []
        self.generate_level()

    def generate_level(self):
        """Генерация нового уровня"""
        generator = LevelGenerator(self.width, self.height, self.level_number)
        self.tiles, self.player_pos, enemy_positions, self.portal_pos = generator.generate()
        
        # Конвертируем позицию игрока и портала в пиксели
        self.player_pos = (self.player_pos[0] * self.tile_size, self.player_pos[1] * self.tile_size)
        self.portal_pos = (self.portal_pos[0] * self.tile_size, self.portal_pos[1] * self.tile_size)
        
        # Создаем врагов
        for pos in enemy_positions:
            enemy_x = pos[0] * self.tile_size + self.tile_size // 2  # Центрируем врага в тайле
            enemy_y = pos[1] * self.tile_size + self.tile_size // 2
            self.game.create_enemy((enemy_x, enemy_y))
        
        # Создаем контрольные точки
        self.checkpoints = []
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[x][y] == TILE_CHECKPOINT:
                    self.checkpoints.append(pygame.math.Vector2(x * self.tile_size, y * self.tile_size))

    def is_wall_at(self, x, y):
        """Проверка наличия стены в указанной позиции"""
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.tiles[tile_x][tile_y] == TILE_WALL
        return True  # За пределами уровня считаем стеной

    def check_checkpoint_collision(self, player_pos):
        """Проверка столкновения с контрольными точками"""
        player_vec = pygame.math.Vector2(player_pos)
        
        for checkpoint in self.checkpoints:
            if (player_vec - checkpoint).length() < CHECKPOINT_RADIUS:
                self.active_checkpoint = checkpoint
                return True
        return False

    def check_portal_collision(self, player_pos):
        """Проверка столкновения с порталом"""
        if self.portal_pos:
            portal_vec = pygame.math.Vector2(self.portal_pos)
            player_vec = pygame.math.Vector2(player_pos)
            
            if (player_vec - portal_vec).length() < PORTAL_ACTIVATION_RADIUS:
                return True
        return False

    def update_portal(self):
        """Обновление анимации портала"""
        # Добавляем новые частицы
        if random.random() < 0.2:  # 20% шанс каждый кадр
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            lifetime = random.randint(20, 40)
            self.portal_particles.append({
                'pos': pygame.math.Vector2(self.portal_pos),
                'vel': pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
                'lifetime': lifetime,
                'max_lifetime': lifetime
            })
        
        # Обновляем существующие частицы
        for particle in self.portal_particles[:]:
            particle['pos'] += particle['vel']
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.portal_particles.remove(particle)

    def draw(self, screen, camera):
        """Отрисовка уровня"""
        # Получаем видимую область
        screen_rect = screen.get_rect()
        camera_rect = pygame.Rect(camera.offset.x, camera.offset.y, screen_rect.width, screen_rect.height)
        
        # Вычисляем границы видимой области в тайлах
        start_x = max(0, int(camera_rect.left // self.tile_size))
        end_x = min(self.width, int(camera_rect.right // self.tile_size) + 1)
        start_y = max(0, int(camera_rect.top // self.tile_size))
        end_y = min(self.height, int(camera_rect.bottom // self.tile_size) + 1)
        
        # Отрисовка тайлов
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                tile = self.tiles[x][y]
                if tile != TILE_FLOOR:  # Пол пропускаем
                    rect = pygame.Rect(x * self.tile_size, y * self.tile_size,
                                     self.tile_size, self.tile_size)
                    screen_pos = camera.apply_rect(rect)
                    
                    if tile == TILE_WALL:
                        pygame.draw.rect(screen, (100, 100, 100), screen_pos)
                    elif tile == TILE_CHECKPOINT:
                        color = CHECKPOINT_ACTIVE_COLOR if pygame.math.Vector2(x * self.tile_size, y * self.tile_size) == self.active_checkpoint else CHECKPOINT_COLOR
                        pygame.draw.circle(screen, color,
                                         (screen_pos.centerx, screen_pos.centery),
                                         CHECKPOINT_RADIUS)
        
        # Отрисовка портала
        if self.portal_pos:
            portal_rect = pygame.Rect(self.portal_pos[0] - PORTAL_SIZE//2,
                                    self.portal_pos[1] - PORTAL_SIZE//2,
                                    PORTAL_SIZE, PORTAL_SIZE)
            screen_pos = camera.apply_rect(portal_rect)
            pygame.draw.circle(screen, PORTAL_COLOR,
                             (screen_pos.centerx, screen_pos.centery),
                             PORTAL_SIZE//2)
            
            # Отрисовка частиц портала
            for particle in self.portal_particles:
                alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
                particle_color = (*PORTAL_PARTICLES_COLOR, alpha)
                particle_pos = camera.apply_point(particle['pos'].x, particle['pos'].y)
                particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, particle_color, (2, 2), 2)
                screen.blit(particle_surface, (particle_pos[0] - 2, particle_pos[1] - 2)) 