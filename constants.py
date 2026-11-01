"""
constants.py - Konfigurasi dan konstanta untuk Game Tetris Python.
Sesuai dengan Product Requirements Document (PRD).
"""

from enum import Enum, auto

# Dimensi Layar
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
FPS = 60

# Konfigurasi Papan Tetris
GRID_COLS = 10
GRID_ROWS = 20
CELL_SIZE = 30  # 10 x 30 = 300px lebar, 20 x 30 = 600px tinggi

BOARD_WIDTH = GRID_COLS * CELL_SIZE   # 300px
BOARD_HEIGHT = GRID_ROWS * CELL_SIZE  # 600px

# Posisi papan pada layar (tengah sedikit ke kiri untuk memberi ruang sidebar)
BOARD_X = 60
BOARD_Y = (WINDOW_HEIGHT - BOARD_HEIGHT) // 2  # 50px

# Warna (RGB)
COLOR_BG_DARK = (15, 18, 28)          # Background jendela utama
COLOR_BOARD_BG = (22, 27, 41)         # Background papan permainan
COLOR_GRID_LINE = (35, 42, 63)        # Garis grid papan
COLOR_BORDER = (80, 100, 140)         # Border pembatas
COLOR_BORDER_ACCENT = (100, 160, 255) # Border aksen saat aktif

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY_LIGHT = (210, 215, 225)
COLOR_GRAY_MUTED = (130, 140, 160)
COLOR_GRAY_DARK = (45, 52, 70)

# Warna Tetromino (Sesuai 7 Bentuk Standar)
# I: Cyan, O: Kuning, T: Ungu, S: Hijau, Z: Merah, J: Biru, L: Oranye
TETROMINO_COLORS = {
    'I': (0, 230, 230),    # Cyan
    'O': (245, 215, 30),   # Kuning
    'T': (170, 50, 230),   # Ungu
    'S': (45, 215, 75),    # Hijau
    'Z': (235, 55, 60),    # Merah
    'J': (40, 100, 240),   # Biru
    'L': (245, 140, 30),   # Oranye
}

# Warna Tombol UI
COLOR_BTN_NORMAL = (40, 50, 75)
COLOR_BTN_HOVER = (60, 80, 120)
COLOR_BTN_CLICK = (30, 40, 60)
COLOR_BTN_TEXT = (240, 245, 255)
COLOR_BTN_BORDER = (90, 115, 160)

# Ketentuan Skor (Sesuai PRD Bagian 5.E)
# 1 garis: 100 poin
# 2 garis: 300 poin
# 3 garis: 500 poin
# 4 garis: 800 poin
SCORE_PER_LINES = {
    1: 100,
    2: 300,
    3: 500,
    4: 800,
}

# Konfigurasi Kecepatan dan Level (PRD Bagian 5.F)
LINES_PER_LEVEL = 10
INITIAL_FALL_SPEED_MS = 1000  # Kecepatan awal jatuhnya balok (1 detik)
MIN_FALL_SPEED_MS = 100       # Kecepatan maksimal (0.1 detik)
SPEED_DECREMENT_PER_LEVEL = 75  # Pengurangan delay per level

# Delay Auto Shift (DAS) untuk kontrol responsif
DAS_INITIAL_DELAY_MS = 170   # Jeda awal sebelum continuous move aktif
DAS_REPEAT_INTERVAL_MS = 50  # Interval pergerakan continuos saat tombol ditahan
SOFT_DROP_INTERVAL_MS = 40   # Interval jatuh saat panah bawah ditekan

# State Permainan
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    HOW_TO_PLAY = auto()
