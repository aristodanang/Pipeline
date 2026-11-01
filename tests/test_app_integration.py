"""
tests/test_app_integration.py - Integration test untuk memverifikasi TetrisApp,
event loop, transisi state (Menu, How To Play, Playing, Pause, Game Over),
dan rendering berjalan tanpa error dalam mode headless.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
import pygame
from constants import GameState
from main import TetrisApp


class TestTetrisAppIntegration(unittest.TestCase):
    def setUp(self):
        self.app = TetrisApp()

    def tearDown(self):
        pygame.quit()

    def test_app_initial_state(self):
        """Memverifikasi inisialisasi awal aplikasi berada di Menu Utama."""
        self.assertEqual(self.app.state, GameState.MENU)
        self.assertTrue(self.app.running)

    def test_state_transitions(self):
        """Memverifikasi transisi state aplikasi antara Menu, Playing, Pause, dan How to Play."""
        # Navigasi ke How to Play via keyboard 'H'
        event_h = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h)
        pygame.event.post(event_h)
        self.app.handle_events()
        self.assertEqual(self.app.state, GameState.HOW_TO_PLAY)

        # Kembali ke Menu via Esc
        event_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        pygame.event.post(event_esc)
        self.app.handle_events()
        self.assertEqual(self.app.state, GameState.MENU)

        # Masuk ke game via Enter
        event_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        pygame.event.post(event_enter)
        self.app.handle_events()
        self.assertEqual(self.app.state, GameState.PLAYING)

        # Pause via 'P'
        event_p = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)
        pygame.event.post(event_p)
        self.app.handle_events()
        self.assertEqual(self.app.state, GameState.PAUSED)

        # Resume via 'P'
        pygame.event.post(event_p)
        self.app.handle_events()
        self.assertEqual(self.app.state, GameState.PLAYING)

    def test_gameplay_inputs(self):
        """Memverifikasi penanganan input gerak kiri, kanan, bawah, spasi, dan putar saat bermain."""
        self.app.state = GameState.PLAYING
        initial_x = self.app.game.current_piece.x

        # Panah Kiri
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
        self.app.handle_events()
        self.assertEqual(self.app.game.current_piece.x, initial_x - 1)

        # Panah Kanan
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
        self.app.handle_events()
        self.assertEqual(self.app.game.current_piece.x, initial_x)

        # Panah Atas (Rotate)
        initial_rot = self.app.game.current_piece.rotation_index
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
        self.app.handle_events()
        # Rotation index should advance (or remain if O-piece)
        if self.app.game.current_piece.shape_type != 'O':
            self.assertNotEqual(self.app.game.current_piece.rotation_index, initial_rot)

        # Spasi (Hard drop)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        self.app.handle_events()
        # Setelah hard drop balok terkunci dan piece baru terbentuk
        self.assertIsNotNone(self.app.game.current_piece)

    def test_render_all_screens(self):
        """Memverifikasi fungsi render untuk seluruh kemungkinan layar tidak melempar exception."""
        states = [
            GameState.MENU,
            GameState.PLAYING,
            GameState.PAUSED,
            GameState.GAME_OVER,
            GameState.HOW_TO_PLAY,
        ]
        mouse_pos = (400, 350)
        for state in states:
            self.app.state = state
            # Render frame
            self.app.render(mouse_pos)
            self.app.update(16.6)


if __name__ == '__main__':
    unittest.main()
