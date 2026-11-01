"""
main.py - Titik masuk utama (entry point) aplikasi game desktop Python Tetris.
Mengelola inisialisasi Pygame, event loop, navigasi state layar, dan perenderan grafis.
"""

import sys
import pygame
from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    GameState,
    DAS_INITIAL_DELAY_MS,
    DAS_REPEAT_INTERVAL_MS,
    SOFT_DROP_INTERVAL_MS,
)
from sound import SoundManager
from game import TetrisGame
from ui import UIRenderer, draw_beveled_block


def create_window_icon() -> pygame.Surface:
    """Membuat ikon jendela bertema balok Tetris 32x32."""
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Gambar bentuk balok 'T' warna ungu
    cells = [(0, 1), (1, 1), (2, 1), (1, 0)]
    for cx, cy in cells:
        draw_beveled_block(icon, 4 + cx * 8, 8 + cy * 8, 8, (170, 50, 230))
    return icon


class TetrisApp:
    """Kelas utama pengelola aplikasi dan alur permainan Tetris."""

    def __init__(self):
        pygame.init()
        pygame.font.init()

        # Konfigurasi jendela
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Python Tetris")
        pygame.display.set_icon(create_window_icon())

        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.game = TetrisGame(sound_manager=self.sound_manager)
        self.ui = UIRenderer(self.screen)

        self.state = GameState.MENU
        self.running = True

        # Status kontrol tombol untuk Delayed Auto Shift (DAS)
        self.key_left_held = False
        self.key_right_held = False
        self.key_down_held = False

        self.das_left_timer = 0.0
        self.das_right_timer = 0.0
        self.soft_drop_timer = 0.0

    def run(self):
        """Loop utama aplikasi."""
        while self.running:
            dt_ms = self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()

            self.handle_events()
            self.update(dt_ms)
            self.render(mouse_pos)

        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Memproses event mouse dan keyboard sesuai dengan GameState saat ini."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.state == GameState.MENU:
                self._handle_menu_events(event)
            elif self.state == GameState.PLAYING:
                self._handle_playing_events(event)
            elif self.state == GameState.PAUSED:
                self._handle_paused_events(event)
            elif self.state == GameState.GAME_OVER:
                self._handle_game_over_events(event)
            elif self.state == GameState.HOW_TO_PLAY:
                self._handle_how_to_play_events(event)

    def _handle_menu_events(self, event: pygame.event.Event):
        """Menangani input pada Menu Utama (FR-01, FR-02)."""
        if self.ui.btn_play.is_clicked(event):
            self.game.reset()
            self.state = GameState.PLAYING
        elif self.ui.btn_how_to.is_clicked(event):
            self.state = GameState.HOW_TO_PLAY
        elif self.ui.btn_exit.is_clicked(event):
            self.running = False

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE]:
                self.game.reset()
                self.state = GameState.PLAYING
            elif event.key == pygame.K_h:
                self.state = GameState.HOW_TO_PLAY
            elif event.key == pygame.K_ESCAPE:
                self.running = False

    def _handle_playing_events(self, event: pygame.event.Event):
        """Menangani kontrol balok dan aksi selama permainan berlangsung (FR-03, FR-04, FR-10, FR-12)."""
        # Klik tombol HUD samping
        if self.ui.btn_hud_pause.is_clicked(event):
            self.game.toggle_pause()
            self.state = GameState.PAUSED
            return
        elif self.ui.btn_hud_restart.is_clicked(event):
            self.game.reset()
            return

        if event.type == pygame.KEYDOWN:
            # Panah Kiri - Gerak ke kiri
            if event.key == pygame.K_LEFT:
                self.key_left_held = True
                self.key_right_held = False
                self.das_left_timer = -DAS_INITIAL_DELAY_MS
                self.game.move_left()

            # Panah Kanan - Gerak ke kanan
            elif event.key == pygame.K_RIGHT:
                self.key_right_held = True
                self.key_left_held = False
                self.das_right_timer = -DAS_INITIAL_DELAY_MS
                self.game.move_right()

            # Panah Bawah - Soft Drop
            elif event.key == pygame.K_DOWN:
                self.key_down_held = True
                self.soft_drop_timer = 0.0
                self.game.soft_drop()

            # Panah Atas - Putar Balok (Rotate)
            elif event.key == pygame.K_UP:
                self.game.rotate()

            # Spasi - Jatuhkan Langsung (Hard Drop)
            elif event.key == pygame.K_SPACE:
                self.game.hard_drop()

            # Tombol P - Jeda Permainan (Pause)
            elif event.key == pygame.K_p:
                self.game.toggle_pause()
                self.state = GameState.PAUSED

            # Tombol R - Mulai Ulang Permainan (Restart)
            elif event.key == pygame.K_r:
                self.game.reset()

            # Tombol M - Toggle Mute Suara
            elif event.key == pygame.K_m:
                self.sound_manager.toggle_mute()

            # Tombol Esc - Jeda permainan
            elif event.key == pygame.K_ESCAPE:
                self.game.toggle_pause()
                self.state = GameState.PAUSED

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.key_left_held = False
            elif event.key == pygame.K_RIGHT:
                self.key_right_held = False
            elif event.key == pygame.K_DOWN:
                self.key_down_held = False

    def _handle_paused_events(self, event: pygame.event.Event):
        """Menangani input saat permainan di-pause (FR-10)."""
        if self.ui.btn_pause_resume.is_clicked(event):
            self.game.toggle_pause()
            self.state = GameState.PLAYING
        elif self.ui.btn_pause_restart.is_clicked(event):
            self.game.reset()
            self.state = GameState.PLAYING
        elif self.ui.btn_pause_menu.is_clicked(event):
            self.state = GameState.MENU

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.game.toggle_pause()
                self.state = GameState.PLAYING
            elif event.key == pygame.K_r:
                self.game.reset()
                self.state = GameState.PLAYING
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU

    def _handle_game_over_events(self, event: pygame.event.Event):
        """Menangani input saat layar Game Over aktif (FR-11)."""
        if self.ui.btn_over_restart.is_clicked(event):
            self.game.reset()
            self.state = GameState.PLAYING
        elif self.ui.btn_over_menu.is_clicked(event):
            self.state = GameState.MENU

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.game.reset()
                self.state = GameState.PLAYING
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU

    def _handle_how_to_play_events(self, event: pygame.event.Event):
        """Menangani input pada layar panduan bermain."""
        if self.ui.btn_how_back.is_clicked(event):
            self.state = GameState.MENU

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_h]:
                self.state = GameState.MENU

    def update(self, dt_ms: float):
        """Memperbarui status permainan dan timer penahanan tombol DAS."""
        if self.state == GameState.PLAYING:
            # Perbarui penahanan tombol panah kiri / kanan (Delayed Auto Shift)
            if self.key_left_held:
                self.das_left_timer += dt_ms
                if self.das_left_timer >= DAS_REPEAT_INTERVAL_MS:
                    self.das_left_timer = 0.0
                    self.game.move_left()

            if self.key_right_held:
                self.das_right_timer += dt_ms
                if self.das_right_timer >= DAS_REPEAT_INTERVAL_MS:
                    self.das_right_timer = 0.0
                    self.game.move_right()

            # Perbarui penahanan tombol panah bawah (Soft Drop repeat)
            if self.key_down_held:
                self.soft_drop_timer += dt_ms
                if self.soft_drop_timer >= SOFT_DROP_INTERVAL_MS:
                    self.soft_drop_timer = 0.0
                    self.game.soft_drop()

            # Perbarui logika jatuh dan animasi baris
            self.game.update(dt_ms)

            # Cek Game Over
            if self.game.game_over:
                self.state = GameState.GAME_OVER

    def render(self, mouse_pos):
        """Merender tampilan sesuai dengan GameState saat ini."""
        if self.state == GameState.MENU:
            self.ui.draw_menu(mouse_pos, self.game.high_score)
        elif self.state == GameState.PLAYING:
            self.ui.draw_game_screen(self.game, mouse_pos, self.sound_manager.muted)
        elif self.state == GameState.PAUSED:
            self.ui.draw_game_screen(self.game, mouse_pos, self.sound_manager.muted)
            self.ui.draw_pause_screen(mouse_pos)
        elif self.state == GameState.GAME_OVER:
            self.ui.draw_game_screen(self.game, mouse_pos, self.sound_manager.muted)
            self.ui.draw_game_over_screen(self.game, mouse_pos)
        elif self.state == GameState.HOW_TO_PLAY:
            self.ui.draw_how_to_play(mouse_pos)

        pygame.display.flip()


def main():
    app = TetrisApp()
    app.run()


if __name__ == "__main__":
    main()
