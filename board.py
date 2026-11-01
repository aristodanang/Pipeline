"""
board.py - Logika papan permainan, deteksi tabrakan, penguncian balok,
perhitungan ghost piece, dan penghapusan garis horizontal.
"""

from typing import List, Tuple, Optional
from constants import GRID_COLS, GRID_ROWS
from tetromino import Tetromino


class Board:
    """Kelas yang mengelola kondisi grid papan permainan Tetris."""

    def __init__(self):
        # Grid 2D: baris x kolom (20 x 10). Nilai None jika kosong, atau tuple (R, G, B) jika terisi.
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [
            [None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)
        ]

    def reset(self):
        """Mereset seluruh papan permainan ke kondisi kosong."""
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    def is_valid_position(
        self,
        piece: Tetromino,
        offset_x: int = 0,
        offset_y: int = 0,
        rotation: Optional[int] = None
    ) -> bool:
        """
        Mengecek apakah posisi balok (dengan kemungkinan offset dan rotasi)
        valid di papan tanpa menembus dinding, lantai, atau balok lain.
        """
        blocks = piece.get_blocks(offset_x, offset_y, rotation)
        for x, y in blocks:
            # Cek dinding kiri dan kanan
            if x < 0 or x >= GRID_COLS:
                return False
            # Cek lantai bawah
            if y >= GRID_ROWS:
                return False
            # Jika sel berada di dalam area grid yang terlihat, cek tabrakan dengan balok yang sudah terkunci
            if y >= 0:
                if self.grid[y][x] is not None:
                    return False
        return True

    def try_rotate(self, piece: Tetromino) -> bool:
        """
        Mencoba memutar balok searah jarum jam dengan sistem wall-kick sederhana.
        Jika posisi putaran langsung terhalang dinding atau balok lain,
        coba geser balok sedikit (kiri/kanan/atas).
        """
        new_rotation = (piece.rotation_index + 1) % 4
        # Daftar kick offset (dx, dy) yang diuji
        wall_kicks = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]

        for dx, dy in wall_kicks:
            if self.is_valid_position(piece, offset_x=dx, offset_y=dy, rotation=new_rotation):
                piece.x += dx
                piece.y += dy
                piece.rotation_index = new_rotation
                return True
        return False

    def get_ghost_y(self, piece: Tetromino) -> int:
        """
        Menghitung posisi Y terendah balok sebelum mendarat (ghost piece preview).
        """
        dy = 0
        while self.is_valid_position(piece, offset_x=0, offset_y=dy + 1):
            dy += 1
        return piece.y + dy

    def lock_piece(self, piece: Tetromino):
        """
        Mengunci balok aktif ke dalam grid papan saat mendarat.
        """
        for x, y in piece.get_blocks():
            if 0 <= y < GRID_ROWS and 0 <= x < GRID_COLS:
                self.grid[y][x] = piece.color

    def get_full_lines(self) -> List[int]:
        """
        Mendeteksi indeks baris yang telah terisi penuh.
        """
        full_lines = []
        for y in range(GRID_ROWS):
            if all(self.grid[y][x] is not None for x in range(GRID_COLS)):
                full_lines.append(y)
        return full_lines

    def clear_lines(self, lines: List[int]) -> int:
        """
        Menghapus baris yang terisi penuh dan menurunkan baris di atasnya.
        Mengembalikan jumlah baris yang berhasil dihapus.
        """
        if not lines:
            return 0

        # Urutkan dari atas ke bawah agar penghapusan konsisten
        for y in sorted(lines):
            del self.grid[y]
            # Tambahkan baris kosong baru di paling atas
            self.grid.insert(0, [None for _ in range(GRID_COLS)])

        return len(lines)
