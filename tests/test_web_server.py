"""
tests/test_web_server.py - Unit test untuk memverifikasi endpoint server web Flask,
routing halaman utama, API highscore, dan penyajian static files.
"""

import os
import unittest
import json
from app import app, HIGHSCORE_FILE


class TestWebServer(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True
        self.orig_content = None
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                self.orig_content = f.read()

    def tearDown(self):
        if self.orig_content is not None:
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
                f.write(self.orig_content)

    def test_index_route(self):
        """Memverifikasi route '/' redirect ke login jika unauth dan return 200 saat auth."""
        # Unauthenticated: harus redirect 302 ke /login
        unauth_response = self.client.get("/")
        self.assertEqual(unauth_response.status_code, 400)
        self.assertIn("/login", unauth_response.headers.get("Location", ""))

        # Authenticated: harus mengembalikan status 200 dan halaman game
        with self.client.session_transaction() as sess:
            sess["user"] = "admin"
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"TETRIS", response.data)
        self.assertIn(b"tetris-canvas", response.data)

    def test_api_highscore_get(self):
        """Memverifikasi endpoint GET '/api/highscore' mengembalikan JSON yang valid."""
        response = self.client.get("/api/highscore")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("high_score", data)
        self.assertIsInstance(data["high_score"], int)

    def test_api_highscore_post(self):
        """Memverifikasi endpoint POST '/api/highscore' dapat memperbarui skor."""
        payload = {"score": 9999}
        response = self.client.post(
            "/api/highscore",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["high_score"], 9999)

    def test_api_info_route(self):
        """Memverifikasi endpoint GET '/api/info' mengembalikan spesifikasi PRD."""
        response = self.client.get("/api/info")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["product_name"], "Python Tetris (Web Edition)")
        self.assertEqual(data["scoring_system"]["1_line"], 100)
        self.assertEqual(data["scoring_system"]["4_lines"], 800)

    def test_static_assets_exist(self):
        """Memverifikasi seluruh file static (CSS, JS) dapat diakses dengan sukses."""
        assets = [
            "/static/css/style.css",
            "/static/js/audio.js",
            "/static/js/tetromino.js",
            "/static/js/game.js",
            "/static/js/app.js",
        ]
        for asset in assets:
            res = self.client.get(asset)
            self.assertEqual(res.status_code, 200, f"Gagal memuat asset: {asset}")
            res.close()


if __name__ == "__main__":
    unittest.main()
