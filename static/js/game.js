/**
 * game.js - Mesin logika game Tetris web sesuai spesifikasi PRD.
 */

const COLS = 10;
const ROWS = 20;
const CELL_SIZE = 30; // 300 x 600 px

const SCORE_TABLE = {
  1: 100,
  2: 300,
  3: 500,
  4: 800,
};

class TetrisGameEngine {
  constructor(soundManager) {
    this.sound = soundManager;
    this.board = Array.from({ length: ROWS }, () => Array(COLS).fill(null));
    this.bag = new TetrominoBag();

    this.currentPiece = null;
    this.nextPiece = null;

    this.score = 0;
    this.highScore = 0;
    this.linesCleared = 0;
    this.level = 1;

    this.gameOver = false;
    this.isPaused = false;

    this.fallTimer = 0;
    this.fallInterval = 1000;

    this.clearingLines = [];
    this.clearingTimer = 0;
    this.clearAnimDuration = 180; // ms

    this.loadHighScore();
    this.reset();
  }

  async loadHighScore() {
    try {
      const res = await fetch('/api/highscore');
      const data = await res.json();
      if (data && typeof data.high_score === 'number') {
        this.highScore = data.high_score;
      }
    } catch (err) {
      console.warn('Gagal memuat high score dari server:', err);
    }
  }

  async saveHighScore(score) {
    if (score > this.highScore) {
      this.highScore = score;
      try {
        await fetch('/api/highscore', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ score }),
        });
      } catch (err) {
        console.warn('Gagal menyimpan high score ke server:', err);
      }
    }
  }

  reset() {
    this.board = Array.from({ length: ROWS }, () => Array(COLS).fill(null));
    this.bag = new TetrominoBag();
    this.score = 0;
    this.linesCleared = 0;
    this.level = 1;
    this.gameOver = false;
    this.isPaused = false;
    this.fallTimer = 0;
    this.clearingLines = [];
    this.updateFallSpeed();

    this.nextPiece = this.bag.next();
    this.spawnPiece();
  }

  updateFallSpeed() {
    const speed = 1000 - (this.level - 1) * 75;
    this.fallInterval = Math.max(100, speed);
  }

  spawnPiece() {
    this.currentPiece = this.nextPiece;
    this.nextPiece = this.bag.next();

    // Cek Game Over: jika balok yang baru spawn langsung terhalang
    if (!this.isValidPosition(this.currentPiece)) {
      this.gameOver = true;
      this.sound.playGameOver();
      this.saveHighScore(this.score);
    }
  }

  isValidPosition(piece, offsetX = 0, offsetY = 0, rotation = null) {
    const blocks = piece.getBlocks(offsetX, offsetY, rotation);
    for (const [x, y] of blocks) {
      if (x < 0 || x >= COLS || y >= ROWS) return false;
      if (y >= 0 && this.board[y][x] !== null) return false;
    }
    return true;
  }

  tryRotate() {
    if (this.gameOver || this.isPaused || this.clearingLines.length > 0) return false;
    const newRot = (this.currentPiece.rotation + 1) % 4;
    const wallKicks = [[0, 0], [-1, 0], [1, 0], [-2, 0], [2, 0], [0, -1]];

    for (const [dx, dy] of wallKicks) {
      if (this.isValidPosition(this.currentPiece, dx, dy, newRot)) {
        this.currentPiece.x += dx;
        this.currentPiece.y += dy;
        this.currentPiece.rotation = newRot;
        this.sound.playRotate();
        return true;
      }
    }
    return false;
  }

  moveLeft() {
    if (this.gameOver || this.isPaused || this.clearingLines.length > 0) return false;
    if (this.isValidPosition(this.currentPiece, -1, 0)) {
      this.currentPiece.x -= 1;
      this.sound.playMove();
      return true;
    }
    return false;
  }

  moveRight() {
    if (this.gameOver || this.isPaused || this.clearingLines.length > 0) return false;
    if (this.isValidPosition(this.currentPiece, 1, 0)) {
      this.currentPiece.x += 1;
      this.sound.playMove();
      return true;
    }
    return false;
  }

  softDrop() {
    if (this.gameOver || this.isPaused || this.clearingLines.length > 0) return false;
    if (this.isValidPosition(this.currentPiece, 0, 1)) {
      this.currentPiece.y += 1;
      return true;
    } else {
      this.lockPiece();
      return false;
    }
  }

  getGhostY() {
    let dy = 0;
    while (this.isValidPosition(this.currentPiece, 0, dy + 1)) {
      dy += 1;
    }
    return this.currentPiece.y + dy;
  }

  hardDrop() {
    if (this.gameOver || this.isPaused || this.clearingLines.length > 0) return;
    this.currentPiece.y = this.getGhostY();
    this.sound.playDrop();
    this.lockPiece();
  }

  lockPiece() {
    if (!this.currentPiece) return;
    const blocks = this.currentPiece.getBlocks();
    for (const [x, y] of blocks) {
      if (y >= 0 && y < ROWS && x >= 0 && x < COLS) {
        this.board[y][x] = this.currentPiece.color;
      }
    }

    const fullRows = [];
    for (let r = 0; r < ROWS; r++) {
      if (this.board[r].every((cell) => cell !== null)) {
        fullRows.push(r);
      }
    }

    if (fullRows.length > 0) {
      this.clearingLines = fullRows;
      this.clearingTimer = this.clearAnimDuration;

      const count = fullRows.length;
      if (count === 4) {
        this.sound.playTetris();
      } else {
        this.sound.playClear();
      }

      const earned = SCORE_TABLE[count] || count * 200;
      this.score += earned;
      this.linesCleared += count;
      this.saveHighScore(this.score);

      const newLevel = 1 + Math.floor(this.linesCleared / 10);
      if (newLevel !== this.level) {
        this.level = newLevel;
        this.updateFallSpeed();
      }
    } else {
      this.sound.playDrop();
      this.spawnPiece();
    }
  }

  update(dt) {
    if (this.gameOver || this.isPaused) return;

    if (this.clearingLines.length > 0) {
      this.clearingTimer -= dt;
      if (this.clearingTimer <= 0) {
        // Hapus baris yang penuh dan turunkan baris di atasnya
        for (const r of this.clearingLines.sort((a, b) => a - b)) {
          this.board.splice(r, 1);
          this.board.unshift(Array(COLS).fill(null));
        }
        this.clearingLines = [];
        this.spawnPiece();
      }
      return;
    }

    this.fallTimer += dt;
    if (this.fallTimer >= this.fallInterval) {
      this.fallTimer = 0;
      this.softDrop();
    }
  }

  togglePause() {
    if (!this.gameOver) {
      this.isPaused = !this.isPaused;
    }
    return this.isPaused;
  }
}
