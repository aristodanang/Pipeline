/**
 * tetromino.js - Definisi 7 bentuk balok Tetromino, warna, rotasi, dan 7-bag randomizer.
 */

const TETROMINO_COLORS = {
  I: '#00e5e5', // Cyan
  O: '#f5d72e', // Yellow
  T: '#aa32e6', // Purple
  S: '#2ed573', // Green
  Z: '#eb3b5a', // Red
  J: '#2d72d9', // Blue
  L: '#fa8231', // Orange
};

const SHAPES = {
  I: [
    [[0, 1], [1, 1], [2, 1], [3, 1]],
    [[2, 0], [2, 1], [2, 2], [2, 3]],
    [[0, 2], [1, 2], [2, 2], [3, 2]],
    [[1, 0], [1, 1], [1, 2], [1, 3]],
  ],
  O: [
    [[1, 0], [2, 0], [1, 1], [2, 1]],
    [[1, 0], [2, 0], [1, 1], [2, 1]],
    [[1, 0], [2, 0], [1, 1], [2, 1]],
    [[1, 0], [2, 0], [1, 1], [2, 1]],
  ],
  T: [
    [[1, 0], [0, 1], [1, 1], [2, 1]],
    [[1, 0], [1, 1], [2, 1], [1, 2]],
    [[0, 1], [1, 1], [2, 1], [1, 2]],
    [[1, 0], [0, 1], [1, 1], [1, 2]],
  ],
  S: [
    [[1, 0], [2, 0], [0, 1], [1, 1]],
    [[1, 0], [1, 1], [2, 1], [2, 2]],
    [[1, 1], [2, 1], [0, 2], [1, 2]],
    [[0, 0], [0, 1], [1, 1], [1, 2]],
  ],
  Z: [
    [[0, 0], [1, 0], [1, 1], [2, 1]],
    [[2, 0], [1, 1], [2, 1], [1, 2]],
    [[0, 1], [1, 1], [1, 2], [2, 2]],
    [[1, 0], [0, 1], [1, 1], [0, 2]],
  ],
  J: [
    [[0, 0], [0, 1], [1, 1], [2, 1]],
    [[1, 0], [2, 0], [1, 1], [1, 2]],
    [[0, 1], [1, 1], [2, 1], [2, 2]],
    [[1, 0], [1, 1], [0, 2], [1, 2]],
  ],
  L: [
    [[2, 0], [0, 1], [1, 1], [2, 1]],
    [[1, 0], [1, 1], [1, 2], [2, 2]],
    [[0, 1], [1, 1], [2, 1], [0, 2]],
    [[0, 0], [1, 0], [1, 1], [1, 2]],
  ],
};

class TetrominoPiece {
  constructor(type, x = 3, y = 0) {
    this.type = type;
    this.color = TETROMINO_COLORS[type];
    this.rotation = 0;
    this.x = x;
    this.y = y;
  }

  getBlocks(offsetX = 0, offsetY = 0, rotation = null) {
    const rot = rotation !== null ? rotation : this.rotation;
    const coords = SHAPES[this.type][rot];
    return coords.map(([dx, dy]) => [this.x + offsetX + dx, this.y + offsetY + dy]);
  }
}

class TetrominoBag {
  constructor() {
    this.bag = [];
  }

  _refill() {
    const types = ['I', 'O', 'T', 'S', 'Z', 'J', 'L'];
    // Fisher-Yates shuffle
    for (let i = types.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [types[i], types[j]] = [types[j], types[i]];
    }
    this.bag.push(...types);
  }

  next() {
    if (this.bag.length <= 3) {
      this._refill();
    }
    const type = this.bag.shift();
    return new TetrominoPiece(type);
  }

  peek() {
    if (this.bag.length === 0) {
      this._refill();
    }
    return new TetrominoPiece(this.bag[0]);
  }
}
