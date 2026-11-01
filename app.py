"""
app.py - Modul backend Flask untuk Python Tetris Web Edition.

Menyediakan portal login terproteksi, autentikasi berbasis SQLite,
dan REST API untuk skor permainan Tetris.
"""

import json
import os
import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "tetris-secure-session-key-devsecops")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.json")
DB_FILE = os.path.join(BASE_DIR, "users.db")


def init_db():
    """Inisialisasi basis data SQLite dan membuat akun admin jika belum ada."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)"
    )
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'supersecret')"
    )
    conn.commit()
    conn.close()


def get_high_score() -> int:
    """Membaca skor tertinggi dari file highscore.json lokal."""
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return int(data.get("high_score", 0))
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    return 0


def save_high_score(new_score: int) -> int:
    """Menyimpan skor tertinggi baru jika melampaui skor yang ada."""
    current = get_high_score()
    if new_score > current:
        try:
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as file:
                json.dump({"high_score": new_score}, file, indent=2)
            return new_score
        except OSError:
            pass
    return current


@app.route("/")
def index():
    """Halaman utama game Tetris jika sudah login, atau redirect ke login."""
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session["user"])


@app.route("/login", methods=["GET", "POST"])
def login():
    """Menampilkan formulir portal login dan memproses autentikasi pengguna."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        query = f"SELECT username FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = user[0]
            return redirect(url_for("index"))

        return render_template(
            "login.html",
            message="Login Gagal! Kredensial tidak valid.",
            status_class="danger",
        )

    if "user" in session:
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Mengakhiri sesi pengguna dan mengalihkan kembali ke portal login."""
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/api/highscore", methods=["GET"])
def api_get_highscore():
    """Mengembalikan nilai skor tertinggi saat ini dalam format JSON."""
    return jsonify({"high_score": get_high_score()})


@app.route("/api/highscore", methods=["POST"])
def api_set_highscore():
    """Menerima dan memperbarui skor tertinggi jika pemain memecahkan rekor."""
    try:
        data = request.get_json(force=True)
        score = int(data.get("score", 0))
        saved = save_high_score(score)
        return jsonify({"status": "success", "high_score": saved})
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        return jsonify({"status": "error", "message": str(exc)}), 400


@app.route("/api/info", methods=["GET"])
def api_info():
    """Mengembalikan informasi metadata produk sesuai PRD."""
    return jsonify({
        "product_name": "Python Tetris (Web Edition)",
        "genre": "Puzzle",
        "platform": "Web Browser",
        "scoring_system": {
            "1_line": 100,
            "2_lines": 300,
            "3_lines": 500,
            "4_lines": 800
        },
        "lines_per_level": 10
    })


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)  # nosemgrep
