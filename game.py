import pygame
from settings import *
from player import Player
from crosshair import Crosshair
from enemy import Enemy
from camera import Camera
from level import Level

class Game:
    def __init__(self):
        # Спрайты
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()  # Группа для визуальных эффектов
        
        # Игровые параметры
        self.current_level = 1
        self.score = 0
        
        # Создаем уровень
        self.level = Level(self, self.current_level)
        
        # Создаем игрока в позиции, определенной картой
        self.player = Player(self)
        self.player.rect.center = self.level.player_pos
        self.player.position = pygame.math.Vector2(self.player.rect.center)
        self.player.spawn_position = self.player.position
        self.all_sprites.add(self.player)
        
        # Создаем прицел
        self.crosshair = Crosshair()
        self.all_sprites.add(self.crosshair)
        
        # Создаем камеру
        self.camera = Camera(self.player)

    def create_enemy(self, pos):
        """Создание врага в указанной позиции"""
        enemy = Enemy(*pos, self)
        self.add_enemy(enemy)

    def next_level(self):
        """Переход на следующий уровень"""
        self.current_level += 1
        
        # Очищаем группы спрайтов
        for enemy in self.enemies:
            enemy.kill()
        
        # Создаем новый уровень
        self.level = Level(self, self.current_level)
        
        # Обновляем позицию игрока
        self.player.position = pygame.math.Vector2(self.level.player_pos)
        self.player.rect.center = self.level.player_pos
        self.player.spawn_position = self.player.position
        
        # Сбрасываем камеру
        self.camera.reset()

    def update(self):
        """Обновление игровой логики"""
        # Обновляем все спрайты
        self.all_sprites.update()
        
        # Обновляем камеру
        self.camera.scroll()
        
        # Обновляем портал
        self.level.update_portal()
        
        # Проверяем контрольные точки
        if self.level.check_checkpoint_collision(self.player.position):
            self.player.spawn_position = pygame.math.Vector2(self.level.active_checkpoint)
        
        # Проверяем портал
        if self.level.check_portal_collision(self.player.position):
            self.next_level()
        
        # Проверяем попадания снарядов по врагам
        self.check_projectile_hits()

    def check_projectile_hits(self):
        """Проверка попаданий снарядов по врагам"""
        for weapon in self.player.weapons.values():
            for projectile in weapon.projectiles:
                hits = pygame.sprite.spritecollide(
                    projectile,
                    self.enemies,
                    False,
                    pygame.sprite.collide_circle
                )
                for enemy in hits:
                    if enemy.alive:
                        if enemy.take_damage(weapon.settings['damage']):
                            self.player.gain_xp(ENEMY_XP_REWARD)  # Начисляем опыт за убийство
                        projectile.kill()
                        break

    def draw(self, screen):
        """Отрисовка всех игровых объектов"""
        # Заполняем экран черным цветом
        screen.fill('black')
        
        # Отрисовка уровня
        self.level.draw(screen, self.camera)
        
        # Отрисовка всех спрайтов с учетом камеры
        for sprite in self.all_sprites:
            if sprite == self.player:
                self.player.draw(screen, self.camera)
            elif sprite != self.crosshair:
                screen.blit(sprite.image, self.camera.apply(sprite))
            else:
                screen.blit(sprite.image, sprite.rect)
        
        # Отрисовка эффектов
        for effect in list(self.effects):
            if hasattr(effect, 'draw'):
                effect.draw(screen, self.camera)
            if hasattr(effect, 'is_alive') and not effect.is_alive():
                self.effects.remove(effect)
        
        # Отрисовка полосок здоровья врагов с учетом камеры
        for enemy in self.enemies:
            if enemy.alive:
                health_bar_bg = pygame.Rect(
                    self.camera.apply_point(enemy.rect.centerx - HEALTH_BAR_WIDTH // 2,
                                          enemy.rect.top - HEALTH_BAR_OFFSET)[0],
                    self.camera.apply_point(0, enemy.rect.top - HEALTH_BAR_OFFSET)[1],
                    HEALTH_BAR_WIDTH,
                    HEALTH_BAR_HEIGHT
                )
                pygame.draw.rect(screen, HEALTH_BAR_BG, health_bar_bg)
                
                if enemy.current_hp > 0:
                    health_width = int(HEALTH_BAR_WIDTH * (enemy.current_hp / enemy.max_hp))
                    health_bar = pygame.Rect(
                        health_bar_bg.x,
                        health_bar_bg.y,
                        health_width,
                        HEALTH_BAR_HEIGHT
                    )
                    pygame.draw.rect(screen, HEALTH_BAR_HP, health_bar)
        
        # Отображение текущего уровня
        font = pygame.font.Font(None, 36)
        level_text = font.render(f"Уровень: {self.current_level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - 150, 10))

    def add_enemy(self, enemy):
        """Добавление врага в игру"""
        self.all_sprites.add(enemy)
        self.enemies.add(enemy) 