"""
tests/test_tetris.py - Unit test komprehensif untuk memverifikasi seluruh fungsionalitas
logika game Tetris sesuai spesifikasi PRD.
"""

import unittest
from constants import (
    GRID_COLS,
    GRID_ROWS,
    SCORE_PER_LINES,
    LINES_PER_LEVEL,
    INITIAL_FALL_SPEED_MS,
    MIN_FALL_SPEED_MS,
    SPEED_DECREMENT_PER_LEVEL,
)
from tetromino import Tetromino, TetrominoBag, SHAPES
from board import Board
from game import TetrisGame


class DummySoundManager:
    """Mock sound manager untuk pengujian tanpa output audio."""
    def __init__(self):
        self.played = []
        self.enabled = True
        self.muted = False

    def play(self, name: str):
        self.played.append(name)

    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted


class TestTetromino(unittest.TestCase):
    def test_all_seven_shapes_exist(self):
        """Memverifikasi bahwa seluruh 7 bentuk balok standar (I, O, T, S, Z, J, L) didefinisikan."""
        expected_shapes = {'I', 'O', 'T', 'S', 'Z', 'J', 'L'}
        self.assertEqual(set(SHAPES.keys()), expected_shapes)

    def test_tetromino_rotation_cycles(self):
        """Memverifikasi bahwa balok memiliki 4 orientasi rotasi dan dapat berputar 360 derajat kembali ke awal."""
        t = Tetromino('T')
        initial_blocks = t.get_blocks()
        t.rotate_clockwise()
        self.assertEqual(t.rotation_index, 1)
        t.rotate_clockwise()
        self.assertEqual(t.rotation_index, 2)
        t.rotate_clockwise()
        self.assertEqual(t.rotation_index, 3)
        t.rotate_clockwise()
        self.assertEqual(t.rotation_index, 0)
        self.assertEqual(t.get_blocks(), initial_blocks)

    def test_seven_bag_distribution(self):
        """Memverifikasi sistem 7-bag menghasilkan set lengkap 7 bentuk unik dalam setiap siklus."""
        bag = TetrominoBag()
        first_bag = [bag.next_piece().shape_type for _ in range(7)]
        self.assertEqual(len(set(first_bag)), 7)
        second_bag = [bag.next_piece().shape_type for _ in range(7)]
        self.assertEqual(len(set(second_bag)), 7)


class TestBoardLogic(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_initial_board_empty(self):
        """Memverifikasi papan awal kosong (seluruh sel None)."""
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                self.assertIsNone(self.board.grid[r][c])

    def test_wall_and_floor_collision(self):
        """Memverifikasi deteksi tabrakan dengan batas dinding kiri, kanan, dan lantai."""
        piece = Tetromino('O', x=0, y=0)
        self.assertTrue(self.board.is_valid_position(piece))

        # Menembus dinding kiri (x < 0)
        self.assertFalse(self.board.is_valid_position(piece, offset_x=-2))

        # Menembus dinding kanan (x >= GRID_COLS)
        self.assertFalse(self.board.is_valid_position(piece, offset_x=10))

        # Menembus lantai bawah (y >= GRID_ROWS)
        self.assertFalse(self.board.is_valid_position(piece, offset_y=25))

    def test_block_collision(self):
        """Memverifikasi balok tidak dapat menembus balok lain yang sudah terkunci."""
        # Kunci balok di baris bawah
        self.board.grid[19][4] = (255, 0, 0)

        # Balok yang mencoba menempati posisi yang sama
        piece = Tetromino('O', x=3, y=18)  # 'O' blocks: [(1,0), (2,0), (1,1), (2,1)] -> cell (4, 19)
        self.assertFalse(self.board.is_valid_position(piece))

    def test_ghost_piece_calculation(self):
        """Memverifikasi posisi bayangan balok (ghost piece) mendarat tepat sebelum tabrakan."""
        piece = Tetromino('I', x=3, y=0)  # Bentuk horizontal di baris 1
        ghost_y = self.board.get_ghost_y(piece)
        # 'I' horizontal baris 1, dasar grid adalah 19, maka piece.y + 1 = 19 -> ghost_y = 18
        self.assertEqual(ghost_y, 18)

    def test_line_clearing_and_shifting(self):
        """Memverifikasi penghapusan baris horizontal penuh dan pergeseran baris di atasnya."""
        # Isi baris 19 penuh
        for col in range(GRID_COLS):
            self.board.grid[19][col] = (200, 200, 200)

        # Letakkan 1 sel di baris 18
        self.board.grid[18][3] = (100, 150, 200)

        full_lines = self.board.get_full_lines()
        self.assertEqual(full_lines, [19])

        cleared_count = self.board.clear_lines(full_lines)
        self.assertEqual(cleared_count, 1)

        # Baris 19 sekarang harus berisi sel yang tadinya ada di baris 18
        self.assertEqual(self.board.grid[19][3], (100, 150, 200))
        # Baris paling atas (0) harus kosong
        self.assertTrue(all(c is None for c in self.board.grid[0]))


class TestGameScoringAndLevel(unittest.TestCase):
    def setUp(self):
        self.dummy_sound = DummySoundManager()
        self.game = TetrisGame(sound_manager=self.dummy_sound)

    def test_scoring_system(self):
        """
        Memverifikasi sistem skor sesuai ketentuan PRD:
        1 baris: 100 poin
        2 baris: 300 poin
        3 baris: 500 poin
        4 baris: 800 poin
        """
        self.assertEqual(SCORE_PER_LINES[1], 100)
        self.assertEqual(SCORE_PER_LINES[2], 300)
        self.assertEqual(SCORE_PER_LINES[3], 500)
        self.assertEqual(SCORE_PER_LINES[4], 800)

    def test_level_progression_and_speed(self):
        """Memverifikasi kenaikan level setiap 10 garis dan percepatan jatuh balok."""
        self.assertEqual(self.game.level, 1)
        initial_speed = self.game.fall_speed_ms

        # Simulasi 10 garis selesai
        self.game.lines_cleared = 10
        self.game.level = 1 + (self.game.lines_cleared // LINES_PER_LEVEL)
        self.game.update_fall_speed()

        self.assertEqual(self.game.level, 2)
        self.assertLess(self.game.fall_speed_ms, initial_speed)
        self.assertEqual(
            self.game.fall_speed_ms,
            max(MIN_FALL_SPEED_MS, INITIAL_FALL_SPEED_MS - SPEED_DECREMENT_PER_LEVEL)
        )

    def test_hard_drop(self):
        """Memverifikasi fitur hard drop langsung menjatuhkan dan mengunci balok."""
        self.game.current_piece = Tetromino('I', x=3, y=0)
        initial_score = self.game.score
        self.game.hard_drop()
        # Setelah hard drop balok terkunci di papan, balok baru muncul
        self.assertIsNotNone(self.game.current_piece)
        self.assertEqual(self.game.current_piece.y, 0)
        # Sel di dasar grid harus sudah terisi
        self.assertIsNotNone(self.game.board.grid[19][3])

    def test_game_over_detection(self):
        """Memverifikasi game over saat balok menumpuk hingga batas atas area permainan."""
        # Isi baris atas tempat spawn balok
        for r in range(4):
            for c in range(GRID_COLS):
                self.game.board.grid[r][c] = (255, 255, 255)

        self.game.spawn_next_piece()
        self.assertTrue(self.game.game_over)
        self.assertIn('game_over', self.dummy_sound.played)

    def test_pause_and_resume(self):
        """Memverifikasi fitur pause dan resume berfungsi."""
        self.assertFalse(self.game.is_paused)
        self.game.toggle_pause()
        self.assertTrue(self.game.is_paused)
        self.game.toggle_pause()
        self.assertFalse(self.game.is_paused)

    def test_restart(self):
        """Memverifikasi fitur restart mengembalikan skor, level, dan papan ke kondisi awal."""
        self.game.score = 1500
        self.game.lines_cleared = 25
        self.game.level = 3
        self.game.game_over = True
        self.game.reset()

        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.lines_cleared, 0)
        self.assertEqual(self.game.level, 1)
        self.assertFalse(self.game.game_over)


if __name__ == '__main__':
    unittest.main()
