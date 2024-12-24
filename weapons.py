import pygame
import math
import random
from settings import *

class MagicWeapon:
    def __init__(self, game, weapon_type):
        self.game = game
        self.weapon_type = weapon_type
        self.settings = MAGIC_WEAPONS[weapon_type]
        self.last_cast_time = 0
        self.projectiles = pygame.sprite.Group()

    def can_cast(self, player):
        current_time = pygame.time.get_ticks()
        return (current_time - self.last_cast_time >= self.settings['cooldown'] and 
                player.current_mana >= self.settings['mana_cost'])

    def cast(self, player, target_pos):
        if not self.can_cast(player):
            return False
        
        player.current_mana -= self.settings['mana_cost']
        self.last_cast_time = pygame.time.get_ticks()
        return True

class Fireball(MagicWeapon):
    def __init__(self, game):
        super().__init__(game, 'fireball')
    
    def cast(self, player, target_pos):
        if super().cast(player, target_pos):
            # Создаем снаряд
            direction = pygame.math.Vector2(target_pos) - pygame.math.Vector2(player.rect.center)
            if direction.length() > 0:
                direction = direction.normalize()
            
            projectile = FireballProjectile(
                player.rect.centerx,
                player.rect.centery,
                direction,
                self.settings
            )
            self.projectiles.add(projectile)
            return True
        return False

class IceLance(MagicWeapon):
    def __init__(self, game):
        super().__init__(game, 'ice_lance')
    
    def cast(self, player, target_pos):
        if super().cast(player, target_pos):
            direction = pygame.math.Vector2(target_pos) - pygame.math.Vector2(player.rect.center)
            if direction.length() > 0:
                direction = direction.normalize()
            
            projectile = IceLanceProjectile(
                player.rect.centerx,
                player.rect.centery,
                direction,
                self.settings
            )
            self.projectiles.add(projectile)
            return True
        return False

class LightningBolt(MagicWeapon):
    def __init__(self, game):
        super().__init__(game, 'lightning_bolt')
        self.chain_count = 3  # Количество прыжков молнии
        self.chain_range = 200  # Максимальное расстояние между целями для прыжка
    
    def find_next_target(self, current_pos, hit_enemies):
        closest_enemy = None
        min_distance = self.chain_range
        
        for enemy in self.game.enemies:
            if enemy not in hit_enemies:
                distance = pygame.math.Vector2(enemy.rect.center).distance_to(current_pos)
                if distance < min_distance:
                    min_distance = distance
                    closest_enemy = enemy
        
        return closest_enemy

    def cast(self, player, target_pos):
        if super().cast(player, target_pos):
            # Находим первую цель
            first_target = None
            min_distance = float('inf')
            
            for enemy in self.game.enemies:
                distance = pygame.math.Vector2(enemy.rect.center).distance_to(player.rect.center)
                if distance < min_distance:
                    min_distance = distance
                    first_target = enemy
            
            if first_target:
                # Создаем список для хранения всех точек молнии
                chain_points = [pygame.math.Vector2(player.rect.center)]
                hit_enemies = set()
                current_target = first_target
                
                # Создаем цепь молний
                for _ in range(self.chain_count):
                    if current_target:
                        chain_points.append(pygame.math.Vector2(current_target.rect.center))
                        hit_enemies.add(current_target)
                        if current_target.take_damage(self.settings['damage'] * (0.8 ** len(hit_enemies))):  # Уменьшаем урон с каждым прыжком
                            player.gain_xp(ENEMY_XP_REWARD)  # Начисляем опыт за убийство
                        
                        # Ищем следующую цель
                        current_target = self.find_next_target(current_target.rect.center, hit_enemies)
                    else:
                        break
                
                # Создаем эффект молнии и добавляем его в группу эффектов игры
                effect = LightningEffect(chain_points, self.settings)
                self.game.effects.add(effect)
            return True
        return False

class MagicProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, settings):
        super().__init__()
        self.settings = settings
        self.direction = direction
        self.speed = settings['projectile_speed']
        self.distance_traveled = 0
        self.max_range = settings['range']
        
        # Создаем спрайт снаряда
        self.image = pygame.Surface((settings['size'], settings['size']), pygame.SRCALPHA)
        pygame.draw.circle(self.image, settings['color'], 
                         (settings['size']//2, settings['size']//2), 
                         settings['size']//2)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.position = pygame.math.Vector2(self.rect.center)

    def update(self):
        # Обновляем позицию
        movement = self.direction * self.speed
        self.position += movement
        self.rect.center = self.position
        self.distance_traveled += movement.length()
        
        # Уничтожаем снаряд, если он пролетел максимальную дистанцию
        if self.distance_traveled >= self.max_range:
            self.kill()

class FireballProjectile(MagicProjectile):
    def __init__(self, x, y, direction, settings):
        super().__init__(x, y, direction, settings)
        # Добавляем эффект свечения
        self.glow_radius = settings['size'] * 1.5
        self.glow_surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.glow_surface, (*settings['color'], 128), 
                         (self.glow_radius, self.glow_radius), self.glow_radius)

class IceLanceProjectile(MagicProjectile):
    def __init__(self, x, y, direction, settings):
        super().__init__(x, y, direction, settings)
        # Создаем удлиненную форму для ледяного копья
        self.image = pygame.Surface((settings['size'] * 2, settings['size']), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, settings['color'], 
                          (0, 0, settings['size'] * 2, settings['size']))

class LightningEffect(pygame.sprite.Sprite):
    def __init__(self, chain_points, settings):
        super().__init__()
        self.chain_points = chain_points
        self.settings = settings
        self.lifetime = 200
        self.creation_time = pygame.time.get_ticks()
        self.last_update = self.creation_time
        self.update_interval = 50  # Обновление анимации каждые 50мс
        
        # Параметры для анимации
        self.alpha = 255
        self.alpha_direction = -1
        self.branch_offsets = []
        self.generate_branch_offsets()
        
        # Создаем поверхность для спрайта
        max_x = max(point.x for point in chain_points)
        min_x = min(point.x for point in chain_points)
        max_y = max(point.y for point in chain_points)
        min_y = min(point.y for point in chain_points)
        
        self.image = pygame.Surface((max_x - min_x + 1 or 1, max_y - min_y + 1 or 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (min_x, min_y)
    
    def generate_branch_offsets(self):
        self.branch_offsets = []
        for _ in range(len(self.chain_points) - 1):
            segment_branches = []
            for _ in range(3):  # 3 ответвления на сегмент
                offset = (
                    random.randint(-15, 15),
                    random.randint(-15, 15)
                )
                segment_branches.append(offset)
            self.branch_offsets.append(segment_branches)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Проверяем время жизни
        if not self.is_alive():
            self.kill()
            return
            
        # Обновляем анимацию
        if current_time - self.last_update >= self.update_interval:
            # Обновляем альфа-канал для мерцания
            self.alpha += self.alpha_direction * 25
            if self.alpha <= 100:
                self.alpha = 100
                self.alpha_direction = 1
            elif self.alpha >= 255:
                self.alpha = 255
                self.alpha_direction = -1
                
            # Генерируем новые ответвления
            self.generate_branch_offsets()
            self.last_update = current_time
    
    def is_alive(self):
        return pygame.time.get_ticks() - self.creation_time < self.lifetime
    
    def draw(self, screen, camera):
        if self.is_alive():
            # Создаем цвет с текущим альфа-каналом
            current_color = list(self.settings['color'])
            current_color.append(self.alpha)
            
            # Рисуем основные линии молнии между всеми точками цепи
            for i in range(len(self.chain_points) - 1):
                start = camera.apply_point(self.chain_points[i].x, self.chain_points[i].y)
                end = camera.apply_point(self.chain_points[i + 1].x, self.chain_points[i + 1].y)
                
                # Рисуем основную линию
                pygame.draw.line(screen, current_color, start, end, self.settings['width'])
                
                # Рисуем ответвления с уменьшающейся яркостью
                for j, (offset_x, offset_y) in enumerate(self.branch_offsets[i]):
                    mid_point = (
                        (start[0] + end[0]) // 2 + offset_x,
                        (start[1] + end[1]) // 2 + offset_y
                    )
                    
                    # Уменьшаем яркость для каждого последующего ответвления
                    branch_alpha = int(self.alpha * (0.8 - j * 0.2))
                    branch_color = list(self.settings['color'])
                    branch_color.append(branch_alpha)
                    
                    # Добавляем небольшое смещение для начала и конца ответвления
                    start_offset = (
                        start[0] + random.randint(-5, 5),
                        start[1] + random.randint(-5, 5)
                    )
                    end_offset = (
                        end[0] + random.randint(-5, 5),
                        end[1] + random.randint(-5, 5)
                    )
                    
                    pygame.draw.line(screen, branch_color, start_offset, mid_point, self.settings['width'] - 1)
                    pygame.draw.line(screen, branch_color, mid_point, end_offset, self.settings['width'] - 1) 

class Heal(MagicWeapon):
    def __init__(self, game):
        super().__init__(game, 'heal')
        
    def cast(self, player, target_pos):
        if super().cast(player, target_pos):
            # Восстанавливаем здоровье
            heal_amount = self.settings['heal_amount']
            player.hp = min(player.max_hp, player.hp + heal_amount)
            
            # Создаем визуальный эффект
            effect = HealEffect(player.rect.center, self.settings)
            self.game.effects.add(effect)
            return True
        return False

class HealEffect(pygame.sprite.Sprite):
    def __init__(self, center_pos, settings):
        super().__init__()
        self.settings = settings
        self.center_pos = center_pos
        self.lifetime = 1000  # 1 секунда
        self.creation_time = pygame.time.get_ticks()
        self.radius = settings['size']
        self.max_radius = settings['size'] * 2
        
        # Создаем поверхность для спрайта
        size = self.max_radius * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center_pos)
        
    def update(self):
        if not self.is_alive():
            self.kill()
    
    def is_alive(self):
        return pygame.time.get_ticks() - self.creation_time < self.lifetime
    
    def draw(self, screen, camera):
        if self.is_alive():
            # Вычисляем текущий размер эффекта
            progress = (pygame.time.get_ticks() - self.creation_time) / self.lifetime
            current_radius = self.radius + (self.max_radius - self.radius) * progress
            
            # Вычисляем прозрачность (убывает со временем)
            alpha = int(255 * (1 - progress))
            
            # Создаем цвет с текущей прозрачностью
            current_color = list(self.settings['color'])
            current_color.append(alpha)
            
            # Получаем позицию на экране
            screen_pos = camera.apply_point(*self.center_pos)
            
            # Рисуем круги исцеления
            for i in range(3):  # Три круга разного размера
                radius = current_radius * (0.6 + i * 0.2)  # 60%, 80%, 100% от текущего радиуса
                pygame.draw.circle(screen, current_color, screen_pos, int(radius), self.settings['width']) 