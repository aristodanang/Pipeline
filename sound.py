"""
sound.py - Generator efek suara prosedural 8-bit untuk Tetris menggunakan NumPy dan Pygame.
Tidak memerlukan file audio eksternal. Mendukung mute dan fallback jika audio tidak tersedia.
"""

import numpy as np
import pygame


class SoundManager:
    """Mengelola dan mensintesis efek suara retro untuk game Tetris."""

    def __init__(self):
        self.enabled = True
        self.muted = False
        self.sounds = {}
        self.sample_rate = 44100

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=512)
            self._generate_all_sounds()
        except Exception as e:
            # Jika audio device tidak tersedia di sistem, nonaktifkan suara secara anggun
            self.enabled = False

    def _create_stereo_sound(self, wave_mono: np.ndarray) -> pygame.mixer.Sound:
        """Mengonversi gelombang mono ke stereo format Pygame Sound."""
        audio_int16 = (wave_mono * 32767).astype(np.int16)
        audio_stereo = np.column_stack((audio_int16, audio_int16))
        return pygame.sndarray.make_sound(audio_stereo)

    def _generate_all_sounds(self):
        """Membuat ragam efek suara menggunakan sintesis gelombang sinusoidal dan modulasi frekuensi."""
        sr = self.sample_rate

        # 1. Move Sound (Blip halus cepat)
        t = np.linspace(0, 0.04, int(sr * 0.04), False)
        env = np.exp(-t * 80)
        wave = np.sin(2 * np.pi * 480 * t) * env * 0.2
        self.sounds['move'] = self._create_stereo_sound(wave)

        # 2. Rotate Sound (Nada sedikit naik)
        t = np.linspace(0, 0.06, int(sr * 0.06), False)
        freq = np.linspace(520, 780, len(t))
        env = np.exp(-t * 50)
        wave = np.sin(2 * np.pi * freq * t) * env * 0.25
        self.sounds['rotate'] = self._create_stereo_sound(wave)

        # 3. Soft / Hard Drop Sound (Thud bass empuk)
        t = np.linspace(0, 0.08, int(sr * 0.08), False)
        freq = np.linspace(200, 60, len(t))
        env = np.exp(-t * 40)
        wave = np.sin(2 * np.pi * freq * t) * env * 0.35
        self.sounds['drop'] = self._create_stereo_sound(wave)

        # 4. Line Clear Sound (Akord arpeggio 3 nada: C5 -> E5 -> G5)
        notes = [523.25, 659.25, 783.99]
        note_dur = 0.07
        combined_wave = []
        for n_freq in notes:
            t = np.linspace(0, note_dur, int(sr * note_dur), False)
            env = np.exp(-t * 15)
            w = (0.7 * np.sin(2 * np.pi * n_freq * t) + 0.3 * np.sin(4 * np.pi * n_freq * t)) * env * 0.28
            combined_wave.extend(w)
        self.sounds['clear'] = self._create_stereo_sound(np.array(combined_wave, dtype=np.float32))

        # 5. Tetris Fanfare Sound (4-line clear, arpeggio kemenangan C5 -> G5 -> C6)
        fanfare_notes = [523.25, 659.25, 783.99, 1046.50]
        f_dur = 0.09
        f_wave = []
        for n_freq in fanfare_notes:
            t = np.linspace(0, f_dur, int(sr * f_dur), False)
            env = np.exp(-t * 10)
            w = (0.75 * np.sin(2 * np.pi * n_freq * t) + 0.25 * np.sin(4 * np.pi * n_freq * t)) * env * 0.32
            f_wave.extend(w)
        self.sounds['tetris'] = self._create_stereo_sound(np.array(f_wave, dtype=np.float32))

        # 6. Game Over Sound (Nada sedih menurun)
        t = np.linspace(0, 0.45, int(sr * 0.45), False)
        freq = np.linspace(350, 90, len(t))
        env = np.exp(-t * 5)
        wave = np.sin(2 * np.pi * freq * t) * env * 0.3
        self.sounds['game_over'] = self._create_stereo_sound(wave)

    def play(self, sound_name: str):
        """Memutar suara sesuai nama, jika audio aktif dan tidak dimute."""
        if not self.enabled or self.muted:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def toggle_mute(self) -> bool:
        """Mengubah status mute, mengembalikan status baru."""
        self.muted = not self.muted
        return self.muted
