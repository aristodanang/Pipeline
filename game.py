"""
game.py - Mesin inti logika game Tetris, mengelola state permainan, skor, level,
kecepatan jatuh, dan interaksi pemain.
"""

import json
import os
from typing import Optional, List
from constants import (
    SCORE_PER_LINES,
    LINES_PER_LEVEL,
    INITIAL_FALL_SPEED_MS,
    MIN_FALL_SPEED_MS,
    SPEED_DECREMENT_PER_LEVEL,
)
from board import Board
from tetromino import Tetromino, TetrominoBag
from sound import SoundManager

HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), "highscore.json")


class TetrisGame:
    """Mengelola siklus hidup permainan Tetris dan status permainan."""

    def __init__(self, sound_manager: Optional[SoundManager] = None):
        self.sound = sound_manager if sound_manager else SoundManager()
        self.board = Board()
        self.bag = TetrominoBag()

        self.current_piece: Optional[Tetromino] = None
        self.next_piece: Optional[Tetromino] = None

        self.score = 0
        self.high_score = self.load_high_score()
        self.lines_cleared = 0
        self.level = 1

        self.game_over = False
        self.is_paused = False

        self.fall_timer = 0.0
        self.fall_speed_ms = INITIAL_FALL_SPEED_MS

        # Animasi penghapusan garis
        self.clearing_lines: List[int] = []
        self.clearing_timer = 0.0
        self.clear_anim_duration_ms = 180.0

        self.reset()

    def load_high_score(self) -> int:
        """Membaca skor tertinggi dari file JSON lokal."""
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return int(data.get("high_score", 0))
        except Exception:
            pass
        return 0

    def save_high_score(self):
        """Menyimpan skor tertinggi ke file JSON lokal."""
        try:
            with open(HIGHSCORE_FILE, 'w', encoding='utf-8') as f:
                json.dump({"high_score": self.high_score}, f)
        except Exception:
            pass

    def reset(self):
        """Mereset kondisi permainan untuk memulai sesi baru."""
        self.board.reset()
        self.bag = TetrominoBag()

        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.is_paused = False
        self.fall_timer = 0.0
        self.update_fall_speed()

        self.clearing_lines = []
        self.clearing_timer = 0.0

        # Ambil balok pertama dan balok berikutnya
        self.next_piece = self.bag.next_piece()
        self.spawn_next_piece()

    def update_fall_speed(self):
        """Menghitung interval kecepatan jatuh berdasarkan level saat ini."""
        speed = INITIAL_FALL_SPEED_MS - (self.level - 1) * SPEED_DECREMENT_PER_LEVEL
        self.fall_speed_ms = max(MIN_FALL_SPEED_MS, speed)

    def spawn_next_piece(self):
        """Memunculkan balok berikutnya ke area permainan."""
        self.current_piece = self.next_piece
        self.next_piece = self.bag.next_piece()

        # Cek kondisi Game Over: jika balok baru langsung menabrak balok yang ada di papan
        if not self.board.is_valid_position(self.current_piece):
            self.game_over = True
            self.sound.play('game_over')
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def move_left(self) -> bool:
        """Menggerakkan balok aktif 1 langkah ke kiri jika memungkinkan."""
        if self.game_over or self.is_paused or self.clearing_lines:
            return False
        if self.board.is_valid_position(self.current_piece, offset_x=-1):
            self.current_piece.x -= 1
            self.sound.play('move')
            return True
        return False

    def move_right(self) -> bool:
        """Menggerakkan balok aktif 1 langkah ke kanan jika memungkinkan."""
        if self.game_over or self.is_paused or self.clearing_lines:
            return False
        if self.board.is_valid_position(self.current_piece, offset_x=1):
            self.current_piece.x += 1
            self.sound.play('move')
            return True
        return False

    def rotate(self) -> bool:
        """Memutar balok aktif 90 derajat jika valid atau jika wall kick berhasil."""
        if self.game_over or self.is_paused or self.clearing_lines:
            return False
        if self.board.try_rotate(self.current_piece):
            self.sound.play('rotate')
            return True
        return False

    def soft_drop(self) -> bool:
        """
        Menurunkan balok 1 langkah ke bawah.
        Mengembalikan True jika berhasil turun, False jika terhalang.
        """
        if self.game_over or self.is_paused or self.clearing_lines:
            return False
        if self.board.is_valid_position(self.current_piece, offset_y=1):
            self.current_piece.y += 1
            return True
        else:
            self.lock_current_piece()
            return False

    def hard_drop(self):
        """Menjatuhkan balok langsung ke posisi terbawah dan menguncinya seketika."""
        if self.game_over or self.is_paused or self.clearing_lines:
            return
        target_y = self.board.get_ghost_y(self.current_piece)
        self.current_piece.y = target_y
        self.lock_current_piece()

    def lock_current_piece(self):
        """Mengunci balok aktif ke papan, mendeteksi garis penuh, dan memperbarui skor."""
        if not self.current_piece:
            return

        self.board.lock_piece(self.current_piece)
        full_lines = self.board.get_full_lines()

        if full_lines:
            # Memulai animasi flash garis penuh
            self.clearing_lines = full_lines
            self.clearing_timer = self.clear_anim_duration_ms

            count = len(full_lines)
            if count == 4:
                self.sound.play('tetris')
            else:
                self.sound.play('clear')

            # Perhitungan skor sesuai ketentuan PRD (Bagian 5.E):
            # 1 garis: 100 poin, 2 garis: 300, 3 garis: 500, 4 garis: 800
            earned_score = SCORE_PER_LINES.get(count, count * 200)
            self.score += earned_score

            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

            self.lines_cleared += count
            new_level = 1 + (self.lines_cleared // LINES_PER_LEVEL)
            if new_level != self.level:
                self.level = new_level
                self.update_fall_speed()
        else:
            self.sound.play('drop')
            self.spawn_next_piece()

    def toggle_pause(self):
        """Menjeda atau melanjutkan permainan."""
        if not self.game_over:
            self.is_paused = not self.is_paused

    def update(self, dt_ms: float):
        """
        Pembaruan state per frame berdasarkan delta time (ms).
        Mengontrol timer jatuh alami balok dan timer animasi penghapusan garis.
        """
        if self.game_over or self.is_paused:
            return

        # Animasi pembersihan garis
        if self.clearing_lines:
            self.clearing_timer -= dt_ms
            if self.clearing_timer <= 0:
                self.board.clear_lines(self.clearing_lines)
                self.clearing_lines = []
                self.spawn_next_piece()
            return

        # Gravitasi / jatuh alami balok
        self.fall_timer += dt_ms
        if self.fall_timer >= self.fall_speed_ms:
            self.fall_timer = 0.0
            self.soft_drop()
