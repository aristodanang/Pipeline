"""
ui.py - Komponen User Interface (UI), perenderan grafis balok, tombol interaktif,
panel statistik, layar Menu Utama, Pause, Game Over, dan How to Play.
"""

import pygame
from typing import Tuple, List, Optional
from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BOARD_X,
    BOARD_Y,
    BOARD_WIDTH,
    BOARD_HEIGHT,
    CELL_SIZE,
    GRID_COLS,
    GRID_ROWS,
    COLOR_BG_DARK,
    COLOR_BOARD_BG,
    COLOR_GRID_LINE,
    COLOR_BORDER,
    COLOR_BORDER_ACCENT,
    COLOR_WHITE,
    COLOR_GRAY_LIGHT,
    COLOR_GRAY_MUTED,
    COLOR_GRAY_DARK,
    COLOR_BTN_NORMAL,
    COLOR_BTN_HOVER,
    COLOR_BTN_CLICK,
    COLOR_BTN_TEXT,
    COLOR_BTN_BORDER,
    TETROMINO_COLORS,
    SCORE_PER_LINES,
)
from tetromino import Tetromino, SHAPES


class Button:
    """Komponen tombol interaktif dengan efek hover, klik, dan border modern."""

    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        text: str,
        font: pygame.font.Font,
        bg_color=COLOR_BTN_NORMAL,
        hover_color=COLOR_BTN_HOVER,
        text_color=COLOR_BTN_TEXT,
        border_color=COLOR_BTN_BORDER,
        border_radius=8,
        shortcut_text: str = ""
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.shortcut_text = shortcut_text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.is_hovered = False

    def update(self, mouse_pos: Tuple[int, int]):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

    def draw(self, surface: pygame.Surface):
        # Warna background saat hover
        current_bg = self.hover_color if self.is_hovered else self.bg_color
        current_border = (130, 180, 255) if self.is_hovered else self.border_color

        # Gambar background tombol
        pygame.draw.rect(surface, current_bg, self.rect, border_radius=self.border_radius)
        # Gambar border
        pygame.draw.rect(surface, current_border, self.rect, width=2, border_radius=self.border_radius)

        # Gambar teks tombol
        label_surf = self.font.render(self.text, True, self.text_color)
        label_rect = label_surf.get_rect(center=self.rect.center)
        surface.blit(label_surf, label_rect)

        # Gambar teks shortcut jika ada
        if self.shortcut_text:
            sc_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
            sc_surf = sc_font.render(self.shortcut_text, True, COLOR_GRAY_MUTED)
            sc_rect = sc_surf.get_rect(right=self.rect.right - 10, centery=self.rect.centery)
            surface.blit(sc_surf, sc_rect)


def clamp(val, min_val=0, max_val=255):
    return max(min_val, min(max_val, int(val)))


def draw_beveled_block(
    surface: pygame.Surface,
    x: int,
    y: int,
    size: int,
    color: Tuple[int, int, int],
    is_ghost: bool = False,
    is_clearing: bool = False
):
    """
    Menggambar 1 sel balok dengan efek 3D bevel / relief arcade yang halus.
    Jika ghost, digambar sebagai wireframe / semitransparan.
    """
    rect = pygame.Rect(x, y, size, size)

    if is_clearing:
        # Efek flash putih berkilau saat baris terhapus
        pygame.draw.rect(surface, (255, 255, 255), rect)
        pygame.draw.rect(surface, (200, 240, 255), rect, width=2)
        return

    if is_ghost:
        # Ghost piece: gambar balok transparan dengan outline neon halus
        ghost_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        ghost_color = (*color, 45)
        outline_color = (*color, 160)
        pygame.draw.rect(ghost_surf, ghost_color, (0, 0, size, size), border_radius=3)
        pygame.draw.rect(ghost_surf, outline_color, (0, 0, size, size), width=2, border_radius=3)
        surface.blit(ghost_surf, (x, y))
        return

    # Balok Solid Berwarna dengan efek bevel 3D
    r, g, b = color
    light_color = (clamp(r + 55), clamp(g + 55), clamp(b + 55))
    dark_color = (clamp(r - 55), clamp(g - 55), clamp(b - 55))
    bevel = 3

    # Bagian dasar
    pygame.draw.rect(surface, color, rect, border_radius=3)

    # Bevel highlight atas dan kiri
    pygame.draw.polygon(surface, light_color, [
        (x, y), (x + size, y), (x + size - bevel, y + bevel),
        (x + bevel, y + bevel), (x + bevel, y + size - bevel), (x, y + size)
    ])

    # Bevel shadow bawah dan kanan
    pygame.draw.polygon(surface, dark_color, [
        (x + size, y), (x + size, y + size), (x, y + size),
        (x + bevel, y + size - bevel), (x + size - bevel, y + size - bevel), (x + size - bevel, y + bevel)
    ])

    # Inner core
    inner_rect = pygame.Rect(x + bevel, y + bevel, size - 2 * bevel, size - 2 * bevel)
    pygame.draw.rect(surface, color, inner_rect)


class UIRenderer:
    """Mengelola render seluruh visual interface game Tetris."""

    def __init__(self, surface: pygame.Surface):
        self.surface = surface

        # Inisialisasi font sistem modern
        self.font_title_large = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.font_title_medium = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.font_heading = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_body = pygame.font.SysFont("Segoe UI", 16)
        self.font_body_bold = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 13)
        self.font_number = pygame.font.SysFont("Consolas", 24, bold=True)

        # Inisialisasi Tombol Menu Utama
        btn_w, btn_h = 240, 50
        btn_x = (WINDOW_WIDTH - btn_w) // 2
        self.btn_play = Button((btn_x, 330, btn_w, btn_h), "PLAY GAME", self.font_heading, shortcut_text="[Enter]")
        self.btn_how_to = Button((btn_x, 400, btn_w, btn_h), "HOW TO PLAY", self.font_heading, shortcut_text="[H]")
        self.btn_exit = Button((btn_x, 470, btn_w, btn_h), "EXIT", self.font_heading, shortcut_text="[Esc]")

        # Tombol di Pause Screen
        self.btn_pause_resume = Button((btn_x, 320, btn_w, 48), "RESUME", self.font_heading, shortcut_text="[P]")
        self.btn_pause_restart = Button((btn_x, 385, btn_w, 48), "RESTART", self.font_heading, shortcut_text="[R]")
        self.btn_pause_menu = Button((btn_x, 450, btn_w, 48), "MAIN MENU", self.font_heading, shortcut_text="[Esc]")

        # Tombol di Game Over Screen
        self.btn_over_restart = Button((btn_x, 450, btn_w, 50), "PLAY AGAIN", self.font_heading, shortcut_text="[R]")
        self.btn_over_menu = Button((btn_x, 515, btn_w, 50), "MAIN MENU", self.font_heading, shortcut_text="[Esc]")

        # Tombol di How to Play Screen
        self.btn_how_back = Button(((WINDOW_WIDTH - 220) // 2, 620, 220, 48), "BACK TO MENU", self.font_heading, shortcut_text="[Esc]")

        # Tombol HUD samping (In-game)
        self.btn_hud_pause = Button((430, 600, 140, 42), "PAUSE", self.font_body_bold, shortcut_text="[P]")
        self.btn_hud_restart = Button((590, 600, 140, 42), "RESTART", self.font_body_bold, shortcut_text="[R]")

    def draw_menu(self, mouse_pos: Tuple[int, int], high_score: int):
        """Merender tampilan Menu Utama (FR-01)."""
        self.surface.fill(COLOR_BG_DARK)

        # Hiasan latar belakang geometris retro
        for i in range(0, WINDOW_WIDTH, 40):
            pygame.draw.line(self.surface, (20, 24, 38), (i, 0), (i, WINDOW_HEIGHT), 1)
        for j in range(0, WINDOW_HEIGHT, 40):
            pygame.draw.line(self.surface, (20, 24, 38), (0, j), (WINDOW_WIDTH, j), 1)

        # Kartu hiasan balok mengambang di latar
        preview_shapes = ['T', 'I', 'O', 'S', 'Z', 'L', 'J']
        decor_positions = [
            (90, 100), (660, 120), (80, 520), (670, 490),
            (140, 320), (620, 310), (380, 70)
        ]
        for shape_name, (dx, dy) in zip(preview_shapes, decor_positions):
            color = TETROMINO_COLORS[shape_name]
            cells = SHAPES[shape_name][0]
            for cx, cy in cells:
                draw_beveled_block(self.surface, dx + cx * 20, dy + cy * 20, 20, color)

        # Judul Utama
        title_surf = self.font_title_large.render("PYTHON TETRIS", True, (240, 248, 255))
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, 180))
        # Shadow judul
        shadow_surf = self.font_title_large.render("PYTHON TETRIS", True, (20, 40, 80))
        self.surface.blit(shadow_surf, (title_rect.x + 3, title_rect.y + 3))
        self.surface.blit(title_surf, title_rect)

        # Subjudul
        sub_surf = self.font_body.render("Classic Puzzle Experience Powered by Pygame", True, COLOR_GRAY_MUTED)
        sub_rect = sub_surf.get_rect(center=(WINDOW_WIDTH // 2, 230))
        self.surface.blit(sub_surf, sub_rect)

        # Skor tertinggi di menu
        hs_surf = self.font_heading.render(f"HIGH SCORE: {high_score}", True, (245, 215, 30))
        hs_rect = hs_surf.get_rect(center=(WINDOW_WIDTH // 2, 275))
        self.surface.blit(hs_surf, hs_rect)

        # Tombol Menu
        for btn in [self.btn_play, self.btn_how_to, self.btn_exit]:
            btn.update(mouse_pos)
            btn.draw(self.surface)

        # Footer info
        foot_surf = self.font_small.render("Created for Desktop (Windows & Linux) | Single Player Mode", True, (90, 100, 120))
        foot_rect = foot_surf.get_rect(center=(WINDOW_WIDTH // 2, 665))
        self.surface.blit(foot_surf, foot_rect)

    def draw_game_screen(self, game, mouse_pos: Tuple[int, int], is_muted: bool = False):
        """Merender tampilan permainan aktif termasuk papan balok dan panel informasi samping."""
        self.surface.fill(COLOR_BG_DARK)

        # 1. Gambar Area Papan Permainan (FR-02, FR-05)
        # Background papan
        board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT)
        pygame.draw.rect(self.surface, COLOR_BOARD_BG, board_rect)

        # Garis grid papan
        for c in range(1, GRID_COLS):
            x = BOARD_X + c * CELL_SIZE
            pygame.draw.line(self.surface, COLOR_GRID_LINE, (x, BOARD_Y), (x, BOARD_Y + BOARD_HEIGHT), 1)
        for r in range(1, GRID_ROWS):
            y = BOARD_Y + r * CELL_SIZE
            pygame.draw.line(self.surface, COLOR_GRID_LINE, (BOARD_X, y), (BOARD_X + BOARD_WIDTH, y), 1)

        # Gambar Balok Terkunci di Papan
        for r in range(GRID_ROWS):
            is_clearing_row = r in game.clearing_lines
            for c in range(GRID_COLS):
                cell_color = game.board.grid[r][c]
                if cell_color is not None:
                    px = BOARD_X + c * CELL_SIZE
                    py = BOARD_Y + r * CELL_SIZE
                    draw_beveled_block(self.surface, px, py, CELL_SIZE, cell_color, is_clearing=is_clearing_row)

        # Jika tidak sedang animasi flash baris, gambar ghost piece dan balok aktif
        if not game.clearing_lines and game.current_piece:
            # 2. Gambar Ghost Piece (Bayangan letak jatuhnya balok)
            ghost_y = game.board.get_ghost_y(game.current_piece)
            for gx, gy in game.current_piece.get_blocks(offset_y=ghost_y - game.current_piece.y):
                if gy >= 0:
                    px = BOARD_X + gx * CELL_SIZE
                    py = BOARD_Y + gy * CELL_SIZE
                    draw_beveled_block(self.surface, px, py, CELL_SIZE, game.current_piece.color, is_ghost=True)

            # 3. Gambar Balok Aktif (Current Piece)
            for ax, ay in game.current_piece.get_blocks():
                if ay >= 0:
                    px = BOARD_X + ax * CELL_SIZE
                    py = BOARD_Y + ay * CELL_SIZE
                    draw_beveled_block(self.surface, px, py, CELL_SIZE, game.current_piece.color)

        # Border luar papan dengan aksen glowing
        pygame.draw.rect(self.surface, COLOR_BORDER_ACCENT, board_rect, width=3, border_radius=4)

        # 4. Gambar Sidebar Panel Informasi (Kanan)
        panel_x = 410
        panel_w = 340

        # Panel NEXT BLOCK (FR-09)
        self._draw_next_block_panel(panel_x, 50, panel_w, 140, game.next_piece)

        # Panel STATS (Skor, Level, Lines, High Score) (FR-07, FR-08)
        self._draw_stats_panel(panel_x, 210, panel_w, 240, game)

        # Panel CONTROLS HINT (FR-03, FR-04, FR-10, FR-12)
        self._draw_controls_panel(panel_x, 465, panel_w, 120, is_muted)

        # Tombol aksi samping (Pause, Restart)
        self.btn_hud_pause.update(mouse_pos)
        self.btn_hud_restart.update(mouse_pos)
        self.btn_hud_pause.draw(self.surface)
        self.btn_hud_restart.draw(self.surface)

    def _draw_next_block_panel(self, x: int, y: int, w: int, h: int, next_piece: Optional[Tetromino]):
        """Menggambar kotak preview balok berikutnya."""
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.surface, (24, 30, 46), rect, border_radius=8)
        pygame.draw.rect(self.surface, COLOR_BORDER, rect, width=2, border_radius=8)

        # Judul panel
        title = self.font_heading.render("NEXT BLOCK", True, COLOR_GRAY_LIGHT)
        self.surface.blit(title, (x + 20, y + 14))

        if next_piece:
            # Hitung bounding box agar balok preview berada tepat di tengah area preview
            shape_coords = SHAPES[next_piece.shape_type][0]
            min_x = min(cx for cx, cy in shape_coords)
            max_x = max(cx for cx, cy in shape_coords)
            min_y = min(cy for cx, cy in shape_coords)
            max_y = max(cy for cx, cy in shape_coords)

            block_size = 24
            shape_pixel_w = (max_x - min_x + 1) * block_size
            shape_pixel_h = (max_y - min_y + 1) * block_size

            # Area gambar balok di sisi kanan panel
            preview_center_x = x + w - 90
            preview_center_y = y + h // 2

            start_px = preview_center_x - shape_pixel_w // 2 - min_x * block_size
            start_py = preview_center_y - shape_pixel_h // 2 - min_y * block_size

            for cx, cy in shape_coords:
                bx = start_px + cx * block_size
                by = start_py + cy * block_size
                draw_beveled_block(self.surface, bx, by, block_size, next_piece.color)

    def _draw_stats_panel(self, x: int, y: int, w: int, h: int, game):
        """Menggambar panel skor, level, dan statistik baris."""
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.surface, (24, 30, 46), rect, border_radius=8)
        pygame.draw.rect(self.surface, COLOR_BORDER, rect, width=2, border_radius=8)

        items = [
            ("SCORE", str(game.score), (255, 255, 255)),
            ("HIGH SCORE", str(game.high_score), (245, 215, 30)),
            ("LEVEL", str(game.level), (100, 200, 255)),
            ("LINES CLEARED", str(game.lines_cleared), (120, 240, 160)),
        ]

        item_h = h // len(items)
        for i, (label, val, val_color) in enumerate(items):
            iy = y + i * item_h + 8
            lbl_surf = self.font_small.render(label, True, COLOR_GRAY_MUTED)
            self.surface.blit(lbl_surf, (x + 20, iy))

            val_surf = self.font_number.render(val, True, val_color)
            val_rect = val_surf.get_rect(right=x + w - 20, top=iy + 14)
            self.surface.blit(val_surf, val_rect)

            if i < len(items) - 1:
                pygame.draw.line(self.surface, (35, 42, 60), (x + 15, iy + item_h), (x + w - 15, iy + item_h), 1)

    def _draw_controls_panel(self, x: int, y: int, w: int, h: int, is_muted: bool):
        """Menggambar panduan pintas tombol kontrol."""
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.surface, (20, 25, 38), rect, border_radius=8)
        pygame.draw.rect(self.surface, (50, 60, 85), rect, width=1, border_radius=8)

        title = self.font_small.render("KONTROL CEPAT", True, COLOR_BORDER_ACCENT)
        self.surface.blit(title, (x + 15, y + 10))

        hints_left = [
            ("Panah", "Gerak & Putar"),
            ("Spasi", "Hard Drop"),
        ]
        hints_right = [
            ("P", "Pause"),
            ("R", "Restart"),
            ("M", "Mute" if not is_muted else "Unmute"),
        ]

        # Sisi kiri
        for i, (k, desc) in enumerate(hints_left):
            txt = self.font_small.render(f"[{k}] {desc}", True, COLOR_GRAY_LIGHT)
            self.surface.blit(txt, (x + 15, y + 36 + i * 24))

        # Sisi kanan
        for i, (k, desc) in enumerate(hints_right):
            txt = self.font_small.render(f"[{k}] {desc}", True, COLOR_GRAY_LIGHT)
            self.surface.blit(txt, (x + 180, y + 36 + i * 24))

    def draw_pause_screen(self, mouse_pos: Tuple[int, int]):
        """Merender overlay layar Pause (FR-10)."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 14, 24, 210))
        self.surface.blit(overlay, (0, 0))

        box_w, box_h = 420, 320
        box_x = (WINDOW_WIDTH - box_w) // 2
        box_y = 200
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(self.surface, (22, 28, 44), box_rect, border_radius=12)
        pygame.draw.rect(self.surface, COLOR_BORDER_ACCENT, box_rect, width=2, border_radius=12)

        title = self.font_title_medium.render("GAME PAUSED", True, (245, 215, 30))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, box_y + 45))
        self.surface.blit(title, title_rect)

        sub = self.font_body.render("Permainan dihentikan sementara", True, COLOR_GRAY_MUTED)
        sub_rect = sub.get_rect(center=(WINDOW_WIDTH // 2, box_y + 80))
        self.surface.blit(sub, sub_rect)

        for btn in [self.btn_pause_resume, self.btn_pause_restart, self.btn_pause_menu]:
            btn.update(mouse_pos)
            btn.draw(self.surface)

    def draw_game_over_screen(self, game, mouse_pos: Tuple[int, int]):
        """Merender modal dialog Game Over (FR-11)."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((12, 10, 18, 220))
        self.surface.blit(overlay, (0, 0))

        box_w, box_h = 440, 480
        box_x = (WINDOW_WIDTH - box_w) // 2
        box_y = 110
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(self.surface, (26, 24, 38), box_rect, border_radius=12)
        pygame.draw.rect(self.surface, (235, 60, 70), box_rect, width=3, border_radius=12)

        # Judul Game Over
        title = self.font_title_large.render("GAME OVER", True, (245, 65, 75))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, box_y + 55))
        self.surface.blit(title, title_rect)

        # Kartu Skor Akhir
        stats_box = pygame.Rect(box_x + 30, box_y + 110, box_w - 60, 190)
        pygame.draw.rect(self.surface, (18, 18, 28), stats_box, border_radius=8)
        pygame.draw.rect(self.surface, (50, 45, 65), stats_box, width=1, border_radius=8)

        stats = [
            ("FINAL SCORE", str(game.score), (255, 255, 255)),
            ("HIGH SCORE", str(game.high_score), (245, 215, 30)),
            ("LINES CLEARED", str(game.lines_cleared), (120, 240, 160)),
            ("LEVEL REACHED", str(game.level), (100, 200, 255)),
        ]

        for i, (label, val, color) in enumerate(stats):
            iy = stats_box.y + 16 + i * 42
            lbl = self.font_body.render(label, True, COLOR_GRAY_MUTED)
            self.surface.blit(lbl, (stats_box.x + 20, iy))

            val_surf = self.font_heading.render(val, True, color)
            val_rect = val_surf.get_rect(right=stats_box.right - 20, centery=iy + 10)
            self.surface.blit(val_surf, val_rect)

        # Tombol aksi
        for btn in [self.btn_over_restart, self.btn_over_menu]:
            btn.update(mouse_pos)
            btn.draw(self.surface)

    def draw_how_to_play(self, mouse_pos: Tuple[int, int]):
        """Merender panduan bermain lengkap sesuai bagian 5 dan 7 dari PRD."""
        self.surface.fill(COLOR_BG_DARK)

        # Header
        title = self.font_title_medium.render("PANDUAN BERMAIN (HOW TO PLAY)", True, (240, 245, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 45))
        self.surface.blit(title, title_rect)

        # Kotak Kontrol
        ctrl_rect = pygame.Rect(50, 95, 330, 480)
        pygame.draw.rect(self.surface, (22, 28, 44), ctrl_rect, border_radius=8)
        pygame.draw.rect(self.surface, COLOR_BORDER, ctrl_rect, width=2, border_radius=8)

        ctrl_title = self.font_heading.render("KONTROL KEYBOARD", True, COLOR_BORDER_ACCENT)
        self.surface.blit(ctrl_title, (ctrl_rect.x + 20, ctrl_rect.y + 18))

        ctrl_list = [
            ("Panah Kiri", "Geser balok ke kiri"),
            ("Panah Kanan", "Geser balok ke kanan"),
            ("Panah Bawah", "Percepat jatuh (Soft Drop)"),
            ("Panah Atas", "Putar balok 90 derajat"),
            ("Spasi (Space)", "Jatuhkan langsung (Hard Drop)"),
            ("Tombol P", "Jeda / Lanjutkan permainan"),
            ("Tombol R", "Mengulang permainan (Restart)"),
            ("Tombol M", "Mute / Unmute suara"),
            ("Tombol Esc", "Kembali ke Menu Utama"),
        ]

        for i, (key, desc) in enumerate(ctrl_list):
            iy = ctrl_rect.y + 60 + i * 44
            k_surf = self.font_body_bold.render(f"[{key}]", True, (245, 215, 30))
            self.surface.blit(k_surf, (ctrl_rect.x + 20, iy))

            d_surf = self.font_small.render(desc, True, COLOR_GRAY_LIGHT)
            self.surface.blit(d_surf, (ctrl_rect.x + 20, iy + 18))

        # Kotak Aturan & Skor
        rules_rect = pygame.Rect(420, 95, 330, 480)
        pygame.draw.rect(self.surface, (22, 28, 44), rules_rect, border_radius=8)
        pygame.draw.rect(self.surface, COLOR_BORDER, rules_rect, width=2, border_radius=8)

        rules_title = self.font_heading.render("ATURAN & SISTEM SKOR", True, (120, 240, 160))
        self.surface.blit(rules_title, (rules_rect.x + 20, rules_rect.y + 18))

        # Penjelasan Tujuan
        obj_text = [
            "Tujuan Permainan:",
            "Susun 7 jenis balok tetromino agar membentuk",
            "garis horizontal penuh tanpa celah.",
            "",
            "Setiap baris penuh akan hilang dan",
            "memberikan poin kepada pemain.",
            "",
            "Kenaikan Level:",
            "Setiap 10 baris berhasil dihapus, level meningkat",
            "dan balok akan jatuh dengan kecepatan lebih tinggi.",
        ]

        for i, line in enumerate(obj_text):
            color = COLOR_BORDER_ACCENT if i in [0, 7] else COLOR_GRAY_LIGHT
            f = self.font_body_bold if i in [0, 7] else self.font_small
            surf = f.render(line, True, color)
            self.surface.blit(surf, (rules_rect.x + 20, rules_rect.y + 55 + i * 19))

        # Tabel Skor PRD
        score_box = pygame.Rect(rules_rect.x + 15, rules_rect.y + 275, rules_rect.width - 30, 175)
        pygame.draw.rect(self.surface, (16, 20, 32), score_box, border_radius=6)
        pygame.draw.rect(self.surface, (45, 55, 80), score_box, width=1, border_radius=6)

        st_title = self.font_body_bold.render("Ketentuan Skor (PRD 5.E):", True, (245, 215, 30))
        self.surface.blit(st_title, (score_box.x + 15, score_box.y + 12))

        score_rows = [
            ("1 Garis Horizontal", "100 Poin"),
            ("2 Garis Horizontal", "300 Poin"),
            ("3 Garis Horizontal", "500 Poin"),
            ("4 Garis (TETRIS!)", "800 Poin"),
        ]

        for i, (lines_text, points_text) in enumerate(score_rows):
            sy = score_box.y + 40 + i * 30
            lt = self.font_small.render(lines_text, True, COLOR_GRAY_LIGHT)
            self.surface.blit(lt, (score_box.x + 15, sy))

            pt = self.font_body_bold.render(points_text, True, (100, 220, 255))
            pt_rect = pt.get_rect(right=score_box.right - 15, centery=sy + 8)
            self.surface.blit(pt, pt_rect)

        # Tombol Kembali
        self.btn_how_back.update(mouse_pos)
        self.btn_how_back.draw(self.surface)
