import random
import pygame
from settings import *

class Room:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center = (x + width // 2, y + height // 2)
        self.connected = False
        self.enemy_positions = []

    def intersects(self, other, min_distance=0):
        return (self.x - min_distance < other.x + other.width and
                self.x + self.width + min_distance > other.x and
                self.y - min_distance < other.y + other.height and
                self.y + self.height + min_distance > other.y)

    def get_random_position(self):
        """Получение случайной позиции внутри комнаты"""
        # Оставляем отступ от стен
        padding = 1
        x = random.randint(self.x + padding, self.x + self.width - padding - 1)
        y = random.randint(self.y + padding, self.y + self.height - padding - 1)
        return (x, y)

class LevelGenerator:
    def __init__(self, width, height, level_number=1):
        self.width = width
        self.height = height
        self.level_number = level_number
        self.tiles = [[TILE_WALL for _ in range(height)] for _ in range(width)]
        self.rooms = []
        self.checkpoints = []
        self.portal_position = None
        self.spawn_position = None
        self.enemy_positions = []

    def generate(self):
        """Генерация нового уровня"""
        self.rooms = []
        self.enemy_positions = []
        
        print(f"Генерация уровня {self.level_number}")
        
        # Генерация комнат
        self._place_rooms()
        print(f"Создано комнат: {len(self.rooms)}")
        
        # Соединение комнат коридорами
        self._connect_rooms()
        
        # Размещение контрольных точек
        self._place_checkpoints()
        
        # Размещение портала
        self._place_portal()
        print(f"Портал размещен в: {self.portal_position}")
        
        # Размещение врагов
        self._place_enemies()
        print(f"Размещено врагов: {len(self.enemy_positions)}")
        print(f"Позиции врагов: {self.enemy_positions}")
        
        return self.tiles, self.spawn_position, self.enemy_positions, self.portal_position

    def _place_rooms(self):
        """Размещение комнат в сетке"""
        # Определяем размеры сетки
        grid_cols = 4  # Количество столбцов в сетке
        grid_rows = 3  # Количество рядов в сетке
        
        # Вычисляем размеры ячейки сетки
        cell_width = (self.width - 2) // grid_cols
        cell_height = (self.height - 2) // grid_rows
        
        # Создаем список всех возможных позиций в сетке
        grid_positions = []
        for row in range(grid_rows):
            for col in range(grid_cols):
                grid_positions.append((row, col))
        
        # Выбираем случайные позиции для комнат
        selected_positions = random.sample(grid_positions, min(ROOMS_PER_LEVEL, len(grid_positions)))
        
        # Сортируем позиции слева направо и сверху вниз для создания последовательного пути
        selected_positions.sort(key=lambda pos: (pos[0], pos[1]))
        
        for i, (row, col) in enumerate(selected_positions):
            # Определяем размеры комнаты (немного меньше ячейки сетки)
            room_width = random.randint(
                min(ROOM_MIN_SIZE, cell_width - 4),
                min(ROOM_MAX_SIZE, cell_width - 4)
            )
            room_height = random.randint(
                min(ROOM_MIN_SIZE, cell_height - 4),
                min(ROOM_MAX_SIZE, cell_height - 4)
            )
            
            # Вычисляем позицию комнаты внутри ячейки сетки
            cell_x = 1 + col * cell_width
            cell_y = 1 + row * cell_height
            
            # Добавляем случайное смещение внутри ячейки
            x = cell_x + random.randint(2, cell_width - room_width - 2)
            y = cell_y + random.randint(2, cell_height - room_height - 2)
            
            new_room = Room(x, y, room_width, room_height)
            self._carve_room(new_room)
            self.rooms.append(new_room)
            
            # Первая комната - точка спавна
            if i == 0:
                self.spawn_position = new_room.center

    def _carve_room(self, room):
        """Вырезание комнаты в тайлах"""
        for x in range(room.x, room.x + room.width):
            for y in range(room.y, room.y + room.height):
                self.tiles[x][y] = TILE_FLOOR

    def _connect_rooms(self):
        """Соединение комнат коридорами с учетом структуры"""
        for i, room in enumerate(self.rooms[:-1]):
            next_room = self.rooms[i + 1]
            
            # Находим центры комнат
            x1, y1 = room.center
            x2, y2 = next_room.center
            
            # Создаем коридор с промежуточными точками для более структурированного пути
            if random.random() < 0.5:
                # Сначала по горизонтали, потом по вертикали
                self._create_corridor((x1, y1), (x2, y1))
                self._create_corridor((x2, y1), (x2, y2))
            else:
                # Сначала по вертикали, потом по горизонтали
                self._create_corridor((x1, y1), (x1, y2))
                self._create_corridor((x1, y2), (x2, y2))
            
            room.connected = True
            next_room.connected = True

    def _create_corridor(self, start, end):
        """Создание коридора между двумя точками"""
        x1, y1 = start
        x2, y2 = end

        # Сначала идем по X
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for w in range(CORRIDOR_WIDTH):
                y = y1 + w - CORRIDOR_WIDTH // 2
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.tiles[x][y] = TILE_FLOOR

        # Затем по Y
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for w in range(CORRIDOR_WIDTH):
                x = x2 + w - CORRIDOR_WIDTH // 2
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.tiles[x][y] = TILE_FLOOR

    def _place_checkpoints(self):
        """Размещение контрольных точек"""
        room_indices = list(range(1, len(self.rooms) - 1))  # Исключаем первую и последнюю комнаты
        checkpoint_count = len(self.rooms) // 3  # Размещаем КТ примерно в каждой третьей комнате
        
        if room_indices and checkpoint_count > 0:
            selected_rooms = random.sample(room_indices, min(checkpoint_count, len(room_indices)))
            for room_idx in selected_rooms:
                room = self.rooms[room_idx]
                checkpoint_pos = room.get_random_position()
                self.checkpoints.append(checkpoint_pos)
                self.tiles[checkpoint_pos[0]][checkpoint_pos[1]] = TILE_CHECKPOINT

    def _place_portal(self):
        """Размещение портала в последней комнате"""
        if self.rooms:
            last_room = self.rooms[-1]
            self.portal_position = last_room.center
            self.tiles[last_room.center[0]][last_room.center[1]] = TILE_PORTAL

    def _is_valid_enemy_position(self, pos, room, room_index):
        """Проверка валидности позиции для врага"""
        x, y = pos
        
        # Проверка, что позиция находится в пределах уровня
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
            
        # Проверка, что позиция не в стене
        if self.tiles[x][y] != TILE_FLOOR:
            return False
        
        # Проверка расстояния от других врагов
        for enemy_pos in self.enemy_positions:
            dx = x - enemy_pos[0]
            dy = y - enemy_pos[1]
            distance = (dx * dx + dy * dy) ** 0.5
            if distance < MIN_ENEMY_DISTANCE:
                return False
        
        # Проверка расстояния от точки спавна только для первых двух комнат
        if room_index < 2 and self.spawn_position:
            dx = x - self.spawn_position[0]
            dy = y - self.spawn_position[1]
            distance = (dx * dx + dy * dy) ** 0.5
            if distance < MIN_ENEMY_DISTANCE_FROM_PLAYER:
                return False
        
        # Проверка, что позиция внутри текущей комнаты
        if not (room.x < x < room.x + room.width and room.y < y < room.y + room.height):
            return False
            
        return True

    def _place_enemies(self):
        """Размещение врагов в комнатах"""
        self.enemy_positions = []
        
        # Пропускаем первую комнату (стартовую) и последнюю (с порталом)
        rooms_for_enemies = self.rooms[1:-1]
        print(f"Комнат для врагов: {len(rooms_for_enemies)}")
        
        for i, room in enumerate(rooms_for_enemies):
            print(f"\nОбработка комнаты {i + 1}:")
            print(f"Размеры комнаты: x={room.x}, y={room.y}, width={room.width}, height={room.height}")
            
            # Увеличиваем количество врагов с уровнем
            min_enemies = max(1, int(ENEMIES_PER_ROOM[0] * (1 + (self.level_number - 1) * 0.2)))
            max_enemies = max(2, int(ENEMIES_PER_ROOM[1] * (1 + (self.level_number - 1) * 0.2)))
            enemy_count = random.randint(min_enemies, max_enemies)
            
            print(f"Планируется врагов: {enemy_count}")
            
            attempts = 0
            placed_in_room = 0
            
            while placed_in_room < enemy_count and attempts < 50:
                pos = room.get_random_position()
                print(f"Попытка {attempts + 1}: позиция {pos}")
                
                if self._is_valid_enemy_position(pos, room, i):
                    self.enemy_positions.append(pos)
                    placed_in_room += 1
                    
                attempts += 1
            
            print(f"Размещено в комнате {i + 1}: {placed_in_room} врагов") 