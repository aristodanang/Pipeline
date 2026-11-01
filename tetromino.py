"""
tetromino.py - Definisi bentuk balok (Tetromino), rotasi, dan sistem 7-bag randomizer.
"""

import random
from typing import List, Tuple
from constants import TETROMINO_COLORS, GRID_COLS

# Definisi koordinat sel lokal untuk setiap rotasi (0, 90, 180, 270 derajat)
# Setiap bentuk direpresentasikan sebagai list 4 rotasi, di mana setiap rotasi
# berisi 4 tuple (dx, dy) relatif terhadap posisi (x, y) balok.
SHAPES = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    'O': [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'S': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}


class Tetromino:
    """Kelas yang merepresentasikan satu balok aktif di papan permainan."""

    def __init__(self, shape_type: str, x: int = None, y: int = 0):
        self.shape_type = shape_type
        self.color = TETROMINO_COLORS[shape_type]
        self.rotation_index = 0

        # Posisi awal di tengah atas papan
        if x is None:
            self.x = (GRID_COLS - 4) // 2
        else:
            self.x = x
        self.y = y

    @property
    def current_shape(self) -> List[Tuple[int, int]]:
        """Mendapatkan koordinat sel lokal untuk orientasi rotasi saat ini."""
        return SHAPES[self.shape_type][self.rotation_index]

    def get_blocks(self, offset_x: int = 0, offset_y: int = 0, rotation: int = None) -> List[Tuple[int, int]]:
        """
        Mengembalikan daftar koordinat absolut (x, y) pada grid papan.
        Mendukung offset untuk pengecekan prediksi tabrakan / rotasi.
        """
        rot_idx = self.rotation_index if rotation is None else rotation
        shape_cells = SHAPES[self.shape_type][rot_idx]
        base_x = self.x + offset_x
        base_y = self.y + offset_y
        return [(base_x + dx, base_y + dy) for dx, dy in shape_cells]

    def rotate_clockwise(self):
        """Memutar balok 90 derajat searah jarum jam."""
        self.rotation_index = (self.rotation_index + 1) % len(SHAPES[self.shape_type])

    def rotate_counter_clockwise(self):
        """Memutar balok 90 derajat berlawanan jarum jam."""
        self.rotation_index = (self.rotation_index - 1) % len(SHAPES[self.shape_type])

    def clone(self) -> 'Tetromino':
        """Membuat salinan dari objek Tetromino ini."""
        t = Tetromino(self.shape_type, self.x, self.y)
        t.rotation_index = self.rotation_index
        return t


class TetrominoBag:
    """
    Sistem 7-Bag Randomizer.
    Memastikan semua 7 bentuk balok muncul secara adil dan merata sebelum diulang.
    """

    def __init__(self):
        self.bag: List[str] = []

    def _refill(self):
        shapes = list(SHAPES.keys())
        random.shuffle(shapes)
        self.bag.extend(shapes)

    def next_piece(self) -> Tetromino:
        if len(self.bag) <= 3:
            self._refill()
        shape_type = self.bag.pop(0)
        return Tetromino(shape_type)

    def peek_next_piece(self) -> Tetromino:
        if len(self.bag) == 0:
            self._refill()
        return Tetromino(self.bag[0])
