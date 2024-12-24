import pygame
import math
from settings import *
from weapons import Fireball, IceLance, LightningBolt, Heal

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
        self.knockback = pygame.math.Vector2(0, 0)
        
        # Атрибуты игрока
        self.hp = PLAYER_START_HP
        self.max_hp = PLAYER_START_HP
        self.level = PLAYER_START_LEVEL
        self.xp = 0
        self.xp_to_next_level = XP_TO_LEVEL
        
        # Атрибуты маны
        self.current_mana = PLAYER_START_MANA
        self.max_mana = PLAYER_MAX_MANA
        self.last_mana_regen = pygame.time.get_ticks()
        
        # М��гическое оружие
        self.weapons = {
            'fireball': Fireball(game),
            'ice_lance': IceLance(game),
            'lightning_bolt': LightningBolt(game),
            'heal': Heal(game)
        }
        self.current_weapon = 'fireball'
        
        # Атрибуты состояния
        self.alive = True
        self.death_time = 0
        self.respawn_delay = 3000  # 3 секунды до возрождения
        self.is_invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_duration = 500
        
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
        
        if not self.is_dashing:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.velocity_x = -PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.velocity_x = PLAYER_SPEED
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.velocity_y = -PLAYER_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.velocity_y = PLAYER_SPEED
            
            # Уклонение на SHIFT
            if keys[pygame.K_LSHIFT]:
                self.try_dash()
        
        # Смена оружия
        if keys[pygame.K_1]:
            self.current_weapon = 'fireball'
        elif keys[pygame.K_2]:
            self.current_weapon = 'ice_lance'
        elif keys[pygame.K_3]:
            self.current_weapon = 'lightning_bolt'
        elif keys[pygame.K_4]:
            self.current_weapon = 'heal'
        
        # Обычная атака на F
        if keys[pygame.K_f]:
            self.update_attack_direction(mouse_pos)
            self.attack()
        
        # Магическая атака на ЛКМ
        if mouse[0]:  # ЛКМ
            # Получаем позицию мыши в мировых координатах
            world_mouse_pos = (
                mouse_pos[0] + self.game.camera.offset.x,
                mouse_pos[1] + self.game.camera.offset.y
            )
            self.weapons[self.current_weapon].cast(self, world_mouse_pos)

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
        """Прверка коллизий со стенами"""
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
        # Вычисляем вектор от позиции игрока на экране к курсуру
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
                swing_progress = math.sin(self.attack_progress * math.pi)  # Плавное движ��ние
                current_angle = self.attack_start_angle - (ATTACK_SWING_ANGLE / 2) + (ATTACK_SWING_ANGLE * swing_progress)
                
                # Создаем точку для следа
                angle_rad = math.radians(current_angle)
                trail_point = (
                    self.rect.centerx + math.cos(angle_rad) * PLAYER_ATTACK_RANGE,
                    self.rect.centery + math.sin(angle_rad) * PLAYER_ATTACK_RANGE
                )
                
                # Добавляем точку в след
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
        # Восстанавливаем ману при повышении уровня
        self.current_mana = self.max_mana

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

    def update_mana(self):
        """Обновление маны"""
        current_time = pygame.time.get_ticks()
        time_passed = (current_time - self.last_mana_regen) / 1000.0  # в секундах
        
        if time_passed > 0:
            # Рассчитываем восстановление маны с учетом уровня
            mana_regen = (MANA_REGEN_BASE + (self.level - 1) * MANA_REGEN_PER_LEVEL) * time_passed
            self.current_mana = min(self.max_mana, self.current_mana + mana_regen)
            self.last_mana_regen = current_time

    def draw_mana_bar(self, screen):
        """Отрисовка полоски маны"""
        mana_bar_bg = pygame.Rect(
            10,
            40,  # Располагаем под полоской здоровья
            200,
            20
        )
        pygame.draw.rect(screen, HEALTH_BAR_BG, mana_bar_bg)
        
        mana_width = int(200 * (self.current_mana / self.max_mana))
        mana_bar = pygame.Rect(
            10,
            40,
            mana_width,
            20
        )
        pygame.draw.rect(screen, (0, 0, 255), mana_bar)  # Синий цвет для маны
        
        # Отображение значения маны
        font = pygame.font.Font(None, 24)
        mana_text = font.render(f"MP: {int(self.current_mana)}/{self.max_mana}", True, WHITE)
        screen.blit(mana_text, (220, 40))

    def update(self):
        """Обновление состояния игрока"""
        if self.alive:
            self.get_input()
            self.move()
            self.update_attack_animation()
            self.update_invulnerability()
            self.update_mana()
            
            # Обновляем снаряды
            for weapon in self.weapons.values():
                weapon.projectiles.update()
        else:
            self.check_respawn()

    def draw_weapon_interface(self, screen):
        """Отрисовка интерфейса оружия"""
        for i, (weapon_name, weapon) in enumerate(self.weapons.items()):
            # Позиция иконки
            x = WEAPON_ICON_START_X + (WEAPON_ICON_SIZE + WEAPON_ICON_SPACING) * i
            y = WEAPON_ICON_Y
            
            # Рисуем фон иконки
            icon_rect = pygame.Rect(x, y, WEAPON_ICON_SIZE, WEAPON_ICON_SIZE)
            
            # Е��ли это выбранное оружие, рисуем подсветку
            if weapon_name == self.current_weapon:
                pygame.draw.rect(screen, WEAPON_ICON_SELECTED_COLOR, icon_rect)
            else:
                pygame.draw.rect(screen, WEAPON_ICON_BG_COLOR, icon_rect)
            
            # Рисуем рамку
            pygame.draw.rect(screen, WHITE, icon_rect, 2)
            
            # Рисуем символ оружия
            weapon_surface = pygame.Surface((WEAPON_ICON_SIZE - 8, WEAPON_ICON_SIZE - 8), pygame.SRCALPHA)
            if weapon_name == 'fireball':
                # Рисуем огненный шар
                pygame.draw.circle(weapon_surface, MAGIC_WEAPONS[weapon_name]['color'],
                                 (WEAPON_ICON_SIZE // 2 - 4, WEAPON_ICON_SIZE // 2 - 4),
                                 WEAPON_ICON_SIZE // 3)
            elif weapon_name == 'ice_lance':
                # Рисуем ледяное копье
                start_pos = (4, WEAPON_ICON_SIZE // 2 - 4)
                end_pos = (WEAPON_ICON_SIZE - 12, WEAPON_ICON_SIZE // 2 - 4)
                pygame.draw.line(weapon_surface, MAGIC_WEAPONS[weapon_name]['color'],
                               start_pos, end_pos, 6)
                # Рисуем наконечник
                pygame.draw.polygon(weapon_surface, MAGIC_WEAPONS[weapon_name]['color'],
                                 [(end_pos[0], end_pos[1] - 8),
                                  (end_pos[0] + 8, end_pos[1]),
                                  (end_pos[0], end_pos[1] + 8)])
            else:  # lightning_bolt
                # Рисуем молнию
                points = [(4, 4), (WEAPON_ICON_SIZE//2 - 4, WEAPON_ICON_SIZE//2 - 4),
                         (WEAPON_ICON_SIZE//2 - 12, WEAPON_ICON_SIZE//2 - 4),
                         (WEAPON_ICON_SIZE - 12, WEAPON_ICON_SIZE - 12)]
                pygame.draw.lines(weapon_surface, MAGIC_WEAPONS[weapon_name]['color'],
                                False, points, 3)
            
            screen.blit(weapon_surface, (x + 4, y + 4))
            
            # Проверяем кулдаун
            current_time = pygame.time.get_ticks()
            if current_time - weapon.last_cast_time < weapon.settings['cooldown']:
                # Рисуем затемнение
                cooldown_surface = pygame.Surface((WEAPON_ICON_SIZE, WEAPON_ICON_SIZE), pygame.SRCALPHA)
                cooldown_surface.fill(WEAPON_ICON_COOLDOWN_COLOR)
                screen.blit(cooldown_surface, (x, y))
                
                # Показываем оставшееся время кулдауна
                remaining = (weapon.settings['cooldown'] - (current_time - weapon.last_cast_time)) / 1000
                if remaining > 0:
                    font = pygame.font.Font(None, 20)
                    text = font.render(f"{remaining:.1f}", True, WHITE)
                    text_rect = text.get_rect(center=(x + WEAPON_ICON_SIZE//2, y + WEAPON_ICON_SIZE//2))
                    screen.blit(text, text_rect)
            
            # Проверяем достаточно ли маны
            if self.current_mana < weapon.settings['mana_cost']:
                # Рисуем индикатор нехватки маны
                mana_surface = pygame.Surface((WEAPON_ICON_SIZE, WEAPON_ICON_SIZE), pygame.SRCALPHA)
                mana_surface.fill(WEAPON_ICON_MANA_COLOR)
                screen.blit(mana_surface, (x, y))
            
            # Рисуем стоимость маны
            font = pygame.font.Font(None, 20)
            mana_text = font.render(f"{weapon.settings['mana_cost']}", True, WHITE)
            screen.blit(mana_text, (x + 2, y + WEAPON_ICON_SIZE - 20))
            
            # Рисуем название оружия под иконкой
            name_font = pygame.font.Font(None, 20)
            name_text = name_font.render(WEAPON_DESCRIPTIONS[weapon_name], True, WHITE)
            name_rect = name_text.get_rect(midtop=(x + WEAPON_ICON_SIZE//2, y + WEAPON_ICON_SIZE + 5))
            screen.blit(name_text, name_rect)

    def draw(self, screen, camera):
        """Отрисовка игрока и его состояния"""
        # Отрисовка спрайта
        if self.alive:
            if self.is_invulnerable and (pygame.time.get_ticks() // 100) % 2:
                temp_image = self.image.copy()
                temp_image.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(temp_image, camera.apply(self))
            else:
                screen.blit(self.image, camera.apply(self))
        else:
            temp_image = self.image.copy()
            temp_image.fill((100, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(temp_image, camera.apply(self))
        
        # Отрисовка эффекта атаки мечом
        self.draw_attack_animation(screen, camera)
        
        # Отрисовка снарядов
        for weapon in self.weapons.values():
            for projectile in weapon.projectiles:
                screen.blit(projectile.image, camera.apply(projectile))
        
        # Отрисовка интерфейса
        self.draw_health_bar(screen)
        self.draw_mana_bar(screen)
        self.draw_xp_bar(screen)
        self.draw_weapon_interface(screen)
        
        # Отображение текущего оружия
        font = pygame.font.Font(None, 24)
        weapon_text = font.render(f"Оружие: {self.current_weapon}", True, WHITE)
        screen.blit(weapon_text, (10, 70)) 