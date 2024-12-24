import pygame
import math
import random
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        super().__init__()
        self.game = game
        self.spawn_position = (x, y)
        self.init_sprite()
        
        # Атрибуты здоровья
        self.max_hp = ENEMY_HP
        self.current_hp = ENEMY_HP
        
        # Флаги состояния
        self.alive = True
        self.is_hit = False
        self.hit_time = 0
        self.death_time = 0
        
        # Позиция и движение
        self.position = pygame.math.Vector2(self.spawn_position)
        self.velocity = pygame.math.Vector2(0, 0)
        self.knockback = pygame.math.Vector2(0, 0)
        
        # Атрибуты ИИ
        self.state = 'wander'  # wander, chase, attack, flee
        self.last_attack_time = 0
        self.wander_target = None
        self.wander_pause_time = 0
        self.last_state_update = 0
        self.last_pathfinding_time = 0
        self.cached_direction = None
        self.direction_cache_time = 0
        
        # Создаем копию изображения для анимации урона
        self.original_image = self.image.copy()

    def init_sprite(self):
        """Инициализация спрайта"""
        self.radius = ENEMY_SIZE // 2
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ENEMY_COLOR, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.spawn_position

    def get_distance_to_player(self, player):
        """Вычисляет расстояние до игрока"""
        return math.sqrt(
            (self.rect.centerx - player.rect.centerx) ** 2 +
            (self.rect.centery - player.rect.centery) ** 2
        )

    def get_direction_to_player(self, player):
        """Вычисляет направление к игроку"""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)
        if distance == 0:
            return pygame.math.Vector2(0, 0)
        return pygame.math.Vector2(dx / distance, dy / distance)

    def get_random_target(self):
        """Выбирает случайную точку для блуждания"""
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, ENEMY_WANDER_RADIUS)
        target_x = self.spawn_position[0] + math.cos(angle) * distance
        target_y = self.spawn_position[1] + math.sin(angle) * distance
        return pygame.math.Vector2(target_x, target_y)

    def update_state(self, player):
        """Обновляет состояние ИИ"""
        current_time = pygame.time.get_ticks()
        
        # Обновляем состояние только каждые 100мс
        if current_time - self.last_state_update < 100:
            return
            
        self.last_state_update = current_time
        distance_to_player = self.get_distance_to_player(player)
        
        # Проверяем здоровье для отступления
        if self.current_hp / self.max_hp <= ENEMY_FLEE_HP_THRESHOLD:
            self.state = 'flee'
        # Проверяем расстояние для атаки
        elif distance_to_player <= ENEMY_ATTACK_RANGE:
            self.state = 'attack'
        # Проверяем расстояние для преследования
        elif distance_to_player <= ENEMY_AGGRO_RANGE:
            self.state = 'chase'
        # Иначе блуждаем
        else:
            self.state = 'wander'

    def apply_knockback(self, direction, force):
        """Применяет отталкивание"""
        self.knockback = direction * force

    def collide_with_walls(self, dx=0, dy=0):
        """Проверка коллизий со стенами"""
        # Проверяем четыре угла и центры сторон противника
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

    def update_movement(self, player):
        """Обновляет движение в зависимости от состояния"""
        # Обновляем отталкивание
        if self.knockback.length() > 0:
            new_pos = self.position + self.knockback
            if not self.collide_with_enemies(new_pos.x - self.position.x, new_pos.y - self.position.y, self.game) and \
               not self.collide_with_walls(new_pos.x - self.position.x, new_pos.y - self.position.y):
                self.position = new_pos
            self.knockback *= 0.8
            if self.knockback.length() < 0.1:
                self.knockback = pygame.math.Vector2(0, 0)
        
        # Обновляем движение в зависимости от состояния
        self.velocity = pygame.math.Vector2(0, 0)
        
        if self.state == 'chase':
            direction = self._get_path_direction(player)
            distance = self.get_distance_to_player(player)
            
            if distance > ENEMY_ATTACK_RANGE:
                self.velocity = direction * ENEMY_SPEED
            elif distance < ENEMY_ATTACK_RANGE * 0.8:
                self.velocity = -direction * ENEMY_SPEED
        
        elif self.state == 'flee':
            flee_direction = -self.get_direction_to_player(player)
            # Упрощенное отталкивание от других врагов
            for other in self.game.enemies:
                if other != self and other.alive:
                    dx = self.rect.centerx - other.rect.centerx
                    dy = self.rect.centery - other.rect.centery
                    dist_sq = dx * dx + dy * dy
                    if dist_sq < ENEMY_ATTACK_RANGE * ENEMY_ATTACK_RANGE * 4:
                        dist = math.sqrt(dist_sq)
                        flee_direction += pygame.math.Vector2(dx/dist, dy/dist) * 0.5
            
            if flee_direction.length() > 0:
                self.velocity = flee_direction.normalize() * ENEMY_SPEED
        
        elif self.state == 'wander':
            current_time = pygame.time.get_ticks()
            if self.wander_target is None or current_time > self.wander_pause_time:
                self.wander_target = self._get_valid_wander_target()
                self.wander_pause_time = current_time + ENEMY_WANDER_PAUSE
            
            if self.wander_target:
                direction = (self.wander_target - self.position).normalize()
                self.velocity = direction * (ENEMY_SPEED * 0.5)
        
        # Применяем групповое поведение только если есть скорость
        if self.velocity.length() > 0:
            self._apply_group_behavior()
            
            # Оптимизированная проверка коллизий
            new_pos = self.position + self.velocity
            if not self.collide_with_walls(new_pos.x - self.position.x, new_pos.y - self.position.y):
                if not self.collide_with_enemies(new_pos.x - self.position.x, new_pos.y - self.position.y, self.game):
                    self.position = new_pos
                else:
                    # Пробуем только основные направления при коллизии
                    for angle in [45, -45]:
                        test_direction = self._rotate_vector(self.velocity.normalize(), angle)
                        test_pos = self.position + test_direction * self.velocity.length()
                        if not self.collide_with_enemies(test_pos.x - self.position.x, test_pos.y - self.position.y, self.game) and \
                           not self.collide_with_walls(test_pos.x - self.position.x, test_pos.y - self.position.y):
                            self.position = test_pos
                            break
        
        self.rect.center = self.position

    def _get_path_direction(self, player):
        """Получает направление к игроку с учетом препятствий"""
        current_time = pygame.time.get_ticks()
        
        # Используем кэшированное направление, если оно актуально
        if self.cached_direction and current_time - self.direction_cache_time < 200:
            return self.cached_direction
            
        direction = self.get_direction_to_player(player)
        
        # Проверяем, есть ли прямой путь к игроку
        test_pos = self.position.copy()
        step = direction * TILESIZE
        
        # Уменьшаем количество проверок
        for _ in range(3):  # Проверяем только 3 шага вперед вместо 5
            test_pos += step
            if self.game.level.is_wall_at(test_pos.x, test_pos.y):
                direction = self._find_alternative_direction(player)
                break
        
        # Кэшируем результат
        self.cached_direction = direction
        self.direction_cache_time = current_time
        return direction

    def _find_alternative_direction(self, player):
        """Находит альтернативный путь к игроку"""
        original_direction = self.get_direction_to_player(player)
        best_direction = original_direction
        min_cost = float('inf')
        
        # Проверяем несколько углов отклонения
        for angle in [-45, -30, -15, 15, 30, 45]:
            test_direction = self._rotate_vector(original_direction, angle)
            test_pos = self.position + test_direction * TILESIZE
            
            if not self.game.level.is_wall_at(test_pos.x, test_pos.y):
                # Оцениваем стоимость пути (расстояние до игрока + штраф за отклонение)
                cost = self.get_distance_to_player(player) + abs(angle) * 0.1
                if cost < min_cost:
                    min_cost = cost
                    best_direction = test_direction
        
        return best_direction

    def _rotate_vector(self, vector, angle):
        """Поворачивает вектор на заданный угол"""
        angle_rad = math.radians(angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        x = vector.x * cos_a - vector.y * sin_a
        y = vector.x * sin_a + vector.y * cos_a
        return pygame.math.Vector2(x, y).normalize()

    def _get_alternative_directions(self):
        """Возвращает список альтернативных направлений движения"""
        if self.velocity.length() == 0:
            return []
            
        normalized = self.velocity.normalize()
        directions = [normalized]
        
        # Добавляем небольшие отклонения
        angles = [15, -15, 30, -30, 45, -45, 60, -60]
        for angle in angles:
            directions.append(self._rotate_vector(normalized, angle))
            
        return directions

    def _apply_group_behavior(self):
        """Применяет групповое поведение"""
        if self.velocity.length() == 0:
            return
            
        separation = pygame.math.Vector2(0, 0)
        alignment = pygame.math.Vector2(0, 0)
        cohesion = pygame.math.Vector2(0, 0)
        
        nearby_enemies = []
        check_distance = MIN_ENEMY_DISTANCE * 3
        
        # Оптимизированная проверка ближайших врагов
        for other in self.game.enemies:
            if other != self and other.alive:
                dx = self.rect.centerx - other.rect.centerx
                dy = self.rect.centery - other.rect.centery
                # Быстрая проверка расстояния без sqrt
                approx_dist = dx * dx + dy * dy
                if approx_dist < check_distance * check_distance:
                    nearby_enemies.append((other, math.sqrt(approx_dist)))
        
        if nearby_enemies:
            for other, distance in nearby_enemies:
                if distance < MIN_ENEMY_DISTANCE:
                    separation += self.get_direction_from_enemy(other) / distance
                if other.velocity.length() > 0:
                    alignment += other.velocity.normalize()
                cohesion += (other.position - self.position)
            
            count = len(nearby_enemies)
            if separation.length() > 0:
                separation = separation.normalize() * 1.5
            if alignment.length() > 0:
                alignment = (alignment / count).normalize() * 0.8
            if cohesion.length() > 0:
                cohesion = (cohesion / count).normalize() * 0.3
            
            # Комбинируем все силы
            self.velocity += (separation + alignment + cohesion) * 0.1
            if self.velocity.length() > 0:
                self.velocity = self.velocity.normalize() * ENEMY_SPEED

    def get_distance_to_enemy(self, other):
        """Вычисляет расстояние до другого врага"""
        return math.sqrt(
            (self.rect.centerx - other.rect.centerx) ** 2 +
            (self.rect.centery - other.rect.centery) ** 2
        )

    def get_direction_from_enemy(self, other):
        """Вычисляет направление от другого врага"""
        dx = self.rect.centerx - other.rect.centerx
        dy = self.rect.centery - other.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)
        if distance == 0:
            return pygame.math.Vector2(0, 0)
        return pygame.math.Vector2(dx / distance, dy / distance)

    def _get_valid_wander_target(self):
        """Получает валидную точку для блуждания"""
        for _ in range(10):  # Пробуем найти валидную точку 10 раз
            target = self.get_random_target()
            if not self.game.level.is_wall_at(target.x, target.y):
                return target
        return self.position

    def _try_pathfinding(self, player):
        """Пытается найти путь к игроку при столкновении с препятствием"""
        if not hasattr(self, 'last_pathfinding_time'):
            self.last_pathfinding_time = 0
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pathfinding_time < 500:  # Проверяем путь каждые 500мс
            return
            
        self.last_pathfinding_time = current_time
        
        # Пробуем найти обходной путь
        for angle in [90, -90, 135, -135]:
            test_direction = self._rotate_vector(self.velocity.normalize(), angle)
            test_pos = self.position + test_direction * TILESIZE
            
            if not self.game.level.is_wall_at(test_pos.x, test_pos.y):
                self.position = test_pos
                break

    def try_attack(self, player):
        """Пытается атаковать игрока"""
        current_time = pygame.time.get_ticks()
        if self.state == 'attack' and current_time - self.last_attack_time >= ENEMY_ATTACK_COOLDOWN:
            self.last_attack_time = current_time
            # Наносим урон и отталкивание
            if player.take_damage(ENEMY_ATTACK_DAMAGE):
                knockback_dir = self.get_direction_to_player(player)
                player.apply_knockback(knockback_dir, ENEMY_KNOCKBACK_FORCE)

    def take_damage(self, amount):
        """Получение урона"""
        self.current_hp -= amount
        self.is_hit = True
        self.hit_time = pygame.time.get_ticks()
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.alive = False
            self.kill()  # Удаляем врага из всех групп спрайтов
            return True  # Враг умер
        return False  # Враг жив

    def update_damage_animation(self):
        """Обновление анимации получения урона"""
        if self.is_hit:
            current_time = pygame.time.get_ticks()
            if current_time - self.hit_time <= ENEMY_DAMAGE_FLASH_DURATION:
                self.image = self.original_image.copy()
                self.image.fill(DAMAGE_FLASH_COLOR, special_flags=pygame.BLEND_ADD)
            else:
                self.image = self.original_image.copy()
                self.is_hit = False

    def update(self):
        """Обновление состояния противника"""
        if self.alive:
            # Получаем игрока из game
            player = self.game.player
            
            # Обновляем состояние и движение
            self.update_state(player)
            self.update_movement(player)
            self.try_attack(player)
            self.update_damage_animation()

    def draw_health_bar(self, screen):
        """Отрисовка полоски здоровья"""
        if self.alive:
            health_bar_bg = pygame.Rect(
                self.rect.centerx - HEALTH_BAR_WIDTH // 2,
                self.rect.top - HEALTH_BAR_OFFSET,
                HEALTH_BAR_WIDTH,
                HEALTH_BAR_HEIGHT
            )
            pygame.draw.rect(screen, HEALTH_BAR_BG, health_bar_bg)
            
            if self.current_hp > 0:
                health_width = int(HEALTH_BAR_WIDTH * (self.current_hp / self.max_hp))
                health_bar = pygame.Rect(
                    self.rect.centerx - HEALTH_BAR_WIDTH // 2,
                    self.rect.top - HEALTH_BAR_OFFSET,
                    health_width,
                    HEALTH_BAR_HEIGHT
                )
                pygame.draw.rect(screen, HEALTH_BAR_HP, health_bar)

    def collide_with_enemies(self, dx=0, dy=0, game=None):
        """Проверка круговых коллизий с другими врагами"""
        if not game:
            return False
            
        # Временно вычисляем новую позицию центра
        center_x = self.rect.centerx + dx
        center_y = self.rect.centery + dy
        
        for other in game.enemies:
            if other != self and other.alive:
                # Вычисляем расстояние между центрами
                distance = math.sqrt(
                    (center_x - other.rect.centerx) ** 2 + 
                    (center_y - other.rect.centery) ** 2
                )
                # Если расстояние меньше суммы радиусов - есть столкновение
                if distance < (self.radius + other.radius):
                    return True
        return False 