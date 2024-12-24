# Настройки экрана
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Настройки камеры
CAMERA_SMOOTHNESS = 0.1  # Плавность движения камеры (0-1)
CAMERA_OFFSET_X = SCREEN_WIDTH // 2  # Смещение камеры по X
CAMERA_OFFSET_Y = SCREEN_HEIGHT // 2  # Смещение камеры по Y

# Настройки игрока
PLAYER_SPEED = 5
PLAYER_START_HP = 100
PLAYER_ATTACK_RANGE = 80
PLAYER_ATTACK_COOLDOWN = 500  # миллисекунды
PLAYER_ATTACK_DAMAGE = 8  # Уменьшено с 25 до 8
PLAYER_START_LEVEL = 1
XP_TO_LEVEL = 100  # Базовый опыт для следующего уровня

# Настройки маны
PLAYER_START_MANA = 100
PLAYER_MAX_MANA = 100
MANA_REGEN_BASE = 15  # Базовое восстановление маны в секунду
MANA_REGEN_PER_LEVEL = 1.5  # Дополнительное восстановление маны за уровень

# Настройки магического оружия
MAGIC_WEAPONS = {
    'fireball': {
        'damage': 40,
        'mana_cost': 30,
        'cooldown': 800,
        'projectile_speed': 8,
        'color': (255, 100, 0),  # Оранжевый
        'size': 16,
        'range': 400,
        'width': 3
    },
    'ice_lance': {
        'damage': 25,
        'mana_cost': 20,
        'cooldown': 400,
        'projectile_speed': 12,
        'color': (0, 255, 255),  # Голубой
        'size': 12,
        'range': 300,
        'width': 2
    },
    'lightning_bolt': {
        'damage': 60,
        'mana_cost': 50,
        'cooldown': 1200,
        'color': (255, 255, 0),  # Желтый
        'range': 200,
        'width': 3
    },
    'heal': {
        'heal_amount': 60,
        'mana_cost': 40,
        'cooldown': 20000,  # 20 секунд
        'color': (0, 255, 0),  # Зеленый
        'size': 32,
        'width': 2
    }
}

# Настройки атаки
ATTACK_ANIMATION_DURATION = 200  # Длительность анимации в миллисекундах
ATTACK_SWING_ANGLE = 120  # Угол размаха в градусах
ATTACK_TRAIL_LENGTH = 3  # Количество следов от атаки
ATTACK_TRAIL_COLOR = (100, 149, 237)  # Светло-синий цвет для следа
ATTACK_TRAIL_WIDTH = 3  # Толщина следа
ATTACK_GLOW_COLOR = (173, 216, 230, 100)  # Светло-голубой с прозрачностью

# Настройки уклонения
DASH_SPEED = 15  # Скорость уклонения
DASH_DURATION = 150  # Длительность уклонения в миллисекундах
DASH_COOLDOWN = 1000  # Задержка между уклонениями в миллисекундах

# Настройки противника
ENEMY_SIZE = 48
ENEMY_COLOR = (150, 0, 0)  # Темно-красный
ENEMY_HP = 100
ENEMY_SPEED = 2.5
ENEMY_XP_REWARD = 50  # Опыт за убийство
ENEMY_RESPAWN_TIME = 3000  # 3 секунды в миллисекундах
ENEMY_DAMAGE_FLASH_DURATION = 100  # Длительность подсветки при уроне в миллисекундах

# Настройки ИИ противника
ENEMY_AGGRO_RANGE = 250  # Радиус обнаружения игрока
ENEMY_ATTACK_RANGE = 40  # Радиус атаки
ENEMY_ATTACK_DAMAGE = 10  # Урон от атаки
ENEMY_ATTACK_COOLDOWN = 1000  # Задержка между атаками в миллисекундах
ENEMY_KNOCKBACK_FORCE = 8  # Сила отталкивания при атаке
ENEMY_FLEE_HP_THRESHOLD = 0.3  # Порог здоровья для отступления (30%)
ENEMY_WANDER_RADIUS = 100  # Радиус случайного блуждания
ENEMY_WANDER_PAUSE = 2000  # Пауза между перемещениями при блуждании

# Настройки игры
TILESIZE = 64

# Настройки тайлов
TILE_FLOOR = '.'  # Пол
TILE_WALL = '#'  # Стена
TILE_PLAYER = 'P'  # Начальная позиция игрока
TILE_ENEMY = 'E'  # Позиция противника

# Цвета тайлов
FLOOR_COLOR = (50, 50, 50)  # Темно-серый
WALL_COLOR = (100, 100, 100)  # Серый

# Настройки карты
MAP_WIDTH = 80  # Ширина карты в тайлах (было 50)
MAP_HEIGHT = 60  # Высота карты в тайлах (было 50)

# Пример простой карты для тестирования
TEST_MAP = [
    "##########",
    "#........#",
    "#..P.....#",
    "#........#",
    "#....E...#",
    "#........#",
    "#........#",
    "#........#",
    "#........#",
    "##########"
]

# Настройки прицела
CROSSHAIR_SIZE = 20
CROSSHAIR_COLOR = (255, 0, 0)  # Красный цвет
CROSSHAIR_WIDTH = 2

# Настройки интерфейса
HEALTH_BAR_WIDTH = 40
HEALTH_BAR_HEIGHT = 7
HEALTH_BAR_OFFSET = 10
XP_BAR_WIDTH = 200
XP_BAR_HEIGHT = 20
XP_BAR_OFFSET = 10

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
HEALTH_BAR_BG = (60, 60, 60)
HEALTH_BAR_HP = (111, 210, 46)
XP_BAR_COLOR = (0, 191, 255)  # Голубой
DAMAGE_FLASH_COLOR = (255, 255, 255)  # Белый 

# Настройки генерации уровня
ROOM_MIN_SIZE = 8  # Минимальный размер комнаты (в тайлах)
ROOM_MAX_SIZE = 12  # Максимальный размер комнаты
ROOMS_PER_LEVEL = 8  # Количество комнат на уровень
MIN_ROOM_DISTANCE = 2  # Минимальное расстояние между комнатами
CORRIDOR_WIDTH = 3  # Ширина коридоров

# Настройки контрольных точек
CHECKPOINT_RADIUS = 32  # Радиус активации контрольной точки
CHECKPOINT_COLOR = (0, 255, 255)  # Цвет неактивной контрольной точки
CHECKPOINT_ACTIVE_COLOR = (0, 155, 255)  # Цвет активной контрольной точки

# Настройки портала
PORTAL_SIZE = 48
PORTAL_COLOR = (148, 0, 211)  # Фиолетовый
PORTAL_PARTICLES_COLOR = (186, 85, 211)  # Светло-фиолетовый
PORTAL_ACTIVATION_RADIUS = 64

# Тайлы
TILE_FLOOR = 0
TILE_WALL = 1
TILE_CHECKPOINT = 2
TILE_PORTAL = 3
TILE_SPAWN = 4

# Настройки спавна врагов
ENEMIES_PER_ROOM = (8, 15)  # Мин и макс количество врагов в комнате
MIN_ENEMY_DISTANCE = 2  # Минимальное расстояние между врагами
MIN_ENEMY_DISTANCE_FROM_PLAYER = 10  # Минимальное начальное расстояние от игрока

# Настройки сложности
DIFFICULTY_SCALING = 1.5  # Множитель сложности для каждого следующего уровня 

# Настройки интерфейса оружия
WEAPON_ICON_SIZE = 48
WEAPON_ICON_SPACING = 10
WEAPON_ICON_Y = 100
WEAPON_ICON_START_X = 10
WEAPON_ICON_BG_COLOR = (40, 40, 40)  # Темно-серый фон
WEAPON_ICON_SELECTED_COLOR = (60, 60, 180)  # Синий цвет выделения
WEAPON_ICON_COOLDOWN_COLOR = (100, 100, 100, 128)  # Полупрозрачный серый
WEAPON_ICON_MANA_COLOR = (0, 0, 255, 180)  # Полупрозрачный синий

# Настройки описаний оружия
WEAPON_DESCRIPTIONS = {
    'fireball': 'Огненный шар',
    'ice_lance': 'Ледяное копье',
    'lightning_bolt': 'Молния',
    'heal': 'Исцеление'
} 