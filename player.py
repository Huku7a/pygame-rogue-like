import pygame
import math
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        
        # Создаем круглый спрайт игрока
        self.radius = TILESIZE // 2
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        
        # Начальная позиция
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.spawn_position = pygame.math.Vector2(self.rect.center)
        
        # Атрибуты движения
        self.velocity_x = 0
        self.velocity_y = 0
        self.position = pygame.math.Vector2(self.rect.center)
        
        # Атрибуты игрока
        self.hp = PLAYER_START_HP
        self.max_hp = PLAYER_START_HP
        self.level = PLAYER_START_LEVEL
        self.xp = 0
        self.xp_to_next_level = XP_TO_LEVEL
        self.is_invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_duration = 500
        self.knockback = pygame.math.Vector2(0, 0)
        
        # Атрибуты состояния
        self.alive = True
        self.death_time = 0
        self.respawn_delay = 3000  # 3 секунды до возрождения
        
        # Атрибуты атаки
        self.last_attack_time = 0
        self.attack_direction = pygame.math.Vector2(1, 0)
        self.is_attacking = False
        self.attack_start_angle = 0
        self.attack_progress = 0
        self.attack_trail = []
        
        # Атрибуты уклонения
        self.is_dashing = False
        self.dash_direction = pygame.math.Vector2(0, 0)
        self.dash_start_time = 0
        self.last_dash_time = 0

    def get_input(self):
        """Обработка пользовательского ввода"""
        if not self.alive:
            return

        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        # Движение
        self.velocity_x = 0
        self.velocity_y = 0
        
        if not self.is_dashing:  # Движение только если не в уклонении
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.velocity_x = -PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.velocity_x = PLAYER_SPEED
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.velocity_y = -PLAYER_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.velocity_y = PLAYER_SPEED
                
            # Уклонение на SHIFT
            if keys[pygame.K_LSHIFT] and not self.is_dashing:
                self.try_dash()
            
        # Обновление направления атаки на основе позиции мыши
        self.update_attack_direction(mouse_pos)
        
        # Атака левой кнопкой мыши
        if mouse[0]:  # ЛКМ
            self.attack()

    def try_dash(self):
        """Попытка выполнить уклонение"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_dash_time >= DASH_COOLDOWN:
            # Проверяем, есть ли направление движения
            movement = pygame.math.Vector2(self.velocity_x, self.velocity_y)
            if movement.length() > 0:
                self.is_dashing = True
                self.dash_start_time = current_time
                self.last_dash_time = current_time
                # Нормализуем вектор движения и умножаем на скорость уклонения
                self.dash_direction = movement.normalize() * DASH_SPEED

    def update_dash(self):
        """Обновление состояния уклонения"""
        if self.is_dashing:
            current_time = pygame.time.get_ticks()
            if current_time - self.dash_start_time >= DASH_DURATION:
                self.is_dashing = False
                self.dash_direction = pygame.math.Vector2(0, 0)
            else:
                # Применяем движение уклонения
                self.velocity_x = self.dash_direction.x
                self.velocity_y = self.dash_direction.y

    def collide_with_enemies(self, dx=0, dy=0):
        """Проверка круговых коллизий  врагами"""
        # Временно вычисляем новую позицию центра
        center_x = self.rect.centerx + dx
        center_y = self.rect.centery + dy
        
        for enemy in self.game.enemies:
            if enemy.alive:
                # Вычисляем расстояние между центрами
                distance = math.sqrt(
                    (center_x - enemy.rect.centerx) ** 2 + 
                    (center_y - enemy.rect.centery) ** 2
                )
                # Если расстояние меньше суммы радиусов - есть столкновение
                if distance < (self.radius + enemy.radius):
                    return True
        return False

    def collide_with_walls(self, dx=0, dy=0):
        """Проверка коллизий со стенами"""
        # Проверяем четыре угла и центры сторон персонажа
        test_points = [
            (self.rect.centerx + dx, self.rect.centery + dy),  # Центр
            (self.rect.left + dx, self.rect.top + dy),         # Верхний левый
            (self.rect.right + dx, self.rect.top + dy),        # Верхний правый
            (self.rect.left + dx, self.rect.bottom + dy),      # Нижний левый
            (self.rect.right + dx, self.rect.bottom + dy),     # Нижний правый
            (self.rect.centerx + dx, self.rect.top + dy),      # Центр верха
            (self.rect.centerx + dx, self.rect.bottom + dy),   # Центр низа
            (self.rect.left + dx, self.rect.centery + dy),     # Центр левой стороны
            (self.rect.right + dx, self.rect.centery + dy)     # Центр правой стороны
        ]
        
        for x, y in test_points:
            if self.game.level.is_wall_at(x, y):
                return True
        return False

    def move(self):
        """Перемещение игрока"""
        # Обновляем состояние уклонения
        self.update_dash()
        
        # Получаем текущую скорость (обычную или скорость уклонения)
        current_velocity_x = self.velocity_x
        current_velocity_y = self.velocity_y
        
        # Применяем отталкивание
        if self.knockback.length() > 0:
            current_velocity_x += self.knockback.x
            current_velocity_y += self.knockback.y
            self.knockback *= 0.8  # Затухание
            if self.knockback.length() < 0.1:
                self.knockback = pygame.math.Vector2(0, 0)
        
        # Пробуем движение по диагонали
        if current_velocity_x != 0 and current_velocity_y != 0:
            if not self.collide_with_enemies(current_velocity_x, current_velocity_y) and \
               not self.collide_with_walls(current_velocity_x, current_velocity_y):
                self.rect.x += current_velocity_x
                self.rect.y += current_velocity_y
            else:
                # Если есть коллизия, пробуем двигаться по X
                if not self.collide_with_enemies(current_velocity_x, 0) and \
                   not self.collide_with_walls(current_velocity_x, 0):
                    self.rect.x += current_velocity_x
                # Пробуем двигаться по Y
                elif not self.collide_with_enemies(0, current_velocity_y) and \
                     not self.collide_with_walls(0, current_velocity_y):
                    self.rect.y += current_velocity_y
        else:
            # Движение по одной оси
            if not self.collide_with_enemies(current_velocity_x, 0) and \
               not self.collide_with_walls(current_velocity_x, 0):
                self.rect.x += current_velocity_x
            if not self.collide_with_enemies(0, current_velocity_y) and \
               not self.collide_with_walls(0, current_velocity_y):
                self.rect.y += current_velocity_y
        
        # Обновляем вектор позиции после движения
        self.position = pygame.math.Vector2(self.rect.center)

    def update_attack_direction(self, mouse_pos):
        """Обновление направления атаки на основе позиции мыши"""
        # Получаем реальную позицию игрока в мире (с учетом камеры)
        screen_pos = pygame.math.Vector2(
            self.rect.centerx - self.game.camera.offset.x,
            self.rect.centery - self.game.camera.offset.y
        )
        # Вычисляем вектор от позиции игрока на экране к курсору
        mouse_vec = pygame.math.Vector2(mouse_pos)
        self.attack_direction = (mouse_vec - screen_pos).normalize()

    def attack(self):
        """Выполнение атаки"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= PLAYER_ATTACK_COOLDOWN:
            self.last_attack_time = current_time
            self.is_attacking = True
            self.attack_progress = 0
            self.attack_start_angle = math.degrees(math.atan2(self.attack_direction.y, self.attack_direction.x))
            self.attack_trail = []

    def update_attack_animation(self):
        """Обновление анимации атаки"""
        if self.is_attacking:
            current_time = pygame.time.get_ticks()
            time_since_attack = current_time - self.last_attack_time
            
            if time_since_attack < ATTACK_ANIMATION_DURATION:
                # Обновляем прогресс анимации (0 to 1)
                self.attack_progress = time_since_attack / ATTACK_ANIMATION_DURATION
                
                # Вычисляем текущий угол взмаха
                swing_progress = math.sin(self.attack_progress * math.pi)  # Плавное движение
                current_angle = self.attack_start_angle - (ATTACK_SWING_ANGLE / 2) + (ATTACK_SWING_ANGLE * swing_progress)
                
                # Создаем точку для следа
                angle_rad = math.radians(current_angle)
                trail_point = (
                    self.rect.centerx + math.cos(angle_rad) * PLAYER_ATTACK_RANGE,
                    self.rect.centery + math.sin(angle_rad) * PLAYER_ATTACK_RANGE
                )
                
                # Добавляем точку в с��ед
                self.attack_trail.append(trail_point)
                if len(self.attack_trail) > ATTACK_TRAIL_LENGTH:
                    self.attack_trail.pop(0)
                
                # Проверяем попадание по врагам в области взмаха
                self.check_attack_hit(current_angle)
            else:
                self.is_attacking = False
                self.attack_trail = []

    def check_attack_hit(self, current_angle):
        """Проверка попадания по врагам в области взмаха"""
        angle_rad = math.radians(current_angle)
        attack_pos = (
            self.rect.centerx + math.cos(angle_rad) * PLAYER_ATTACK_RANGE,
            self.rect.centery + math.sin(angle_rad) * PLAYER_ATTACK_RANGE
        )
        attack_rect = pygame.Rect(0, 0, TILESIZE, TILESIZE)
        attack_rect.center = attack_pos
        
        for enemy in self.game.enemies:
            if enemy.alive and attack_rect.colliderect(enemy.rect):
                if enemy.take_damage(PLAYER_ATTACK_DAMAGE):
                    self.gain_xp(ENEMY_XP_REWARD)

    def draw_attack_animation(self, screen, camera):
        """Отрисовка анимации атаки"""
        if self.is_attacking and self.attack_trail:
            # Создаем поверхность для свечения
            glow_surface = pygame.Surface((PLAYER_ATTACK_RANGE * 3, PLAYER_ATTACK_RANGE * 3), pygame.SRCALPHA)
            glow_center = (glow_surface.get_width() // 2, glow_surface.get_height() // 2)
            
            # Рисуем след атаки
            screen_points = []
            for i, point in enumerate(self.attack_trail):
                screen_point = camera.apply_point(*point)
                screen_points.append(screen_point)
                
                # Рисуем круги в точках следа
                alpha = int(255 * (i + 1) / len(self.attack_trail))
                glow_color = (*ATTACK_TRAIL_COLOR, alpha)
                pygame.draw.circle(screen, glow_color, screen_point, ATTACK_TRAIL_WIDTH)
            
            # Рисуем линии между точками следа
            if len(screen_points) >= 2:
                pygame.draw.lines(screen, ATTACK_TRAIL_COLOR, False, screen_points, ATTACK_TRAIL_WIDTH)

    def gain_xp(self, amount):
        """Получение опыта"""
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.xp -= self.xp_to_next_level
        # Увеличиваем требования к следующему уровню на 50%
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)

    def draw_attack_indicator(self, screen):
        """Отрисовка индикатора направления атаки"""
        if self.is_attacking:
            end_pos = (self.rect.centerx + self.attack_direction.x * PLAYER_ATTACK_RANGE,
                      self.rect.centery + self.attack_direction.y * PLAYER_ATTACK_RANGE)
            pygame.draw.line(screen, RED, self.rect.center, end_pos, 2)
            self.is_attacking = False

    def draw_xp_bar(self, screen):
        """Отрисовка полоски опыта"""
        # Фон полоски опыта
        xp_bar_bg = pygame.Rect(
            XP_BAR_OFFSET,
            SCREEN_HEIGHT - XP_BAR_OFFSET - XP_BAR_HEIGHT,
            XP_BAR_WIDTH,
            XP_BAR_HEIGHT
        )
        pygame.draw.rect(screen, HEALTH_BAR_BG, xp_bar_bg)
        
        # Текущий опыт
        xp_width = int(XP_BAR_WIDTH * (self.xp / self.xp_to_next_level))
        xp_bar = pygame.Rect(
            XP_BAR_OFFSET,
            SCREEN_HEIGHT - XP_BAR_OFFSET - XP_BAR_HEIGHT,
            xp_width,
            XP_BAR_HEIGHT
        )
        pygame.draw.rect(screen, XP_BAR_COLOR, xp_bar)
        
        # Отображение текста уровня
        font = pygame.font.Font(None, 24)
        level_text = font.render(f"Level {self.level}", True, WHITE)
        screen.blit(level_text, (XP_BAR_OFFSET, SCREEN_HEIGHT - XP_BAR_OFFSET - XP_BAR_HEIGHT - 20))

    def take_damage(self, amount):
        """Получение урона игроком"""
        if not self.is_invulnerable and self.alive:
            self.hp -= amount
            self.is_invulnerable = True
            self.invulnerable_time = pygame.time.get_ticks()
            if self.hp <= 0:
                self.hp = 0
                self.die()
            return True
        return False

    def die(self):
        """Обработка смерти игрока"""
        self.alive = False
        self.death_time = pygame.time.get_ticks()
        # Сбрасываем все временные эффекты
        self.is_attacking = False
        self.is_dashing = False
        self.knockback = pygame.math.Vector2(0, 0)
        self.velocity_x = 0
        self.velocity_y = 0

    def respawn(self):
        """Возрождение игрока"""
        self.alive = True
        self.hp = self.max_hp
        
        # Проверяем точку возрождения на коллизии со стенами
        spawn_x, spawn_y = self.spawn_position
        if self.game.level.is_wall_at(spawn_x, spawn_y):
            # Если точка возрождения в стене, ищем ближайшую свободную точку
            for offset_x in range(-TILESIZE * 2, TILESIZE * 2, TILESIZE // 2):
                for offset_y in range(-TILESIZE * 2, TILESIZE * 2, TILESIZE // 2):
                    test_x = spawn_x + offset_x
                    test_y = spawn_y + offset_y
                    if not self.game.level.is_wall_at(test_x, test_y):
                        spawn_x, spawn_y = test_x, test_y
                        break
                if not self.game.level.is_wall_at(spawn_x, spawn_y):
                    break
        
        self.position = pygame.math.Vector2(spawn_x, spawn_y)
        self.rect.center = self.position
        self.is_invulnerable = True
        self.invulnerable_time = pygame.time.get_ticks()
        self.invulnerable_duration = 2000  # 2 секунды неуязвимости после возрождения

    def check_respawn(self):
        """Проверка возможности возрождения"""
        if not self.alive:
            current_time = pygame.time.get_ticks()
            if current_time - self.death_time >= self.respawn_delay:
                self.respawn()

    def apply_knockback(self, direction, force):
        """Применение отталкивания к игроку"""
        self.knockback = direction * force

    def update_invulnerability(self):
        """Обновление состояния неуязвимости"""
        if self.is_invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerable_time >= self.invulnerable_duration:
                self.is_invulnerable = False

    def draw_health_bar(self, screen):
        """Отрисовка полоски здоровья игрока"""
        health_bar_bg = pygame.Rect(
            10,
            10,
            200,
            20
        )
        pygame.draw.rect(screen, HEALTH_BAR_BG, health_bar_bg)
        
        health_width = int(200 * (self.hp / self.max_hp))
        health_bar = pygame.Rect(
            10,
            10,
            health_width,
            20
        )
        pygame.draw.rect(screen, HEALTH_BAR_HP, health_bar)
        
        # Отображение значения здоровья
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"HP: {self.hp}/{self.max_hp}", True, WHITE)
        screen.blit(health_text, (220, 10))

    def update(self):
        """Обновление состояния игрока"""
        if self.alive:
            self.get_input()
            self.move()
            self.update_attack_animation()
            self.update_invulnerability()
        else:
            self.check_respawn()

    def draw(self, screen, camera):
        """Отрисовка игрока и его состояния"""
        # Отрисовка спрайта
        if self.alive:
            # Мигание при неуязвимости
            if self.is_invulnerable and (pygame.time.get_ticks() // 100) % 2:
                temp_image = self.image.copy()
                temp_image.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(temp_image, camera.apply(self))
            else:
                screen.blit(self.image, camera.apply(self))
        else:
            # Отрисовка "мертвого" состояния
            temp_image = self.image.copy()
            temp_image.fill((100, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(temp_image, camera.apply(self))
            
            # Отображение времени до возрождения
            if not self.alive:
                font = pygame.font.Font(None, 36)
                time_left = max(0, (self.respawn_delay - (pygame.time.get_ticks() - self.death_time)) // 1000)
                text = font.render(f"Возрождение через: {time_left}", True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)) 