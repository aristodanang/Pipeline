/**
 * app.js - Controller UI, canvas renderer, event listener keyboard dan touch.
 */

document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('tetris-canvas');
  const ctx = canvas.getContext('2d');

  const nextCanvas = document.getElementById('next-canvas');
  const nextCtx = nextCanvas.getContext('2d');

  const sound = new SoundEffects();
  const game = new TetrisGameEngine(sound);

  // Elemen UI
  const scoreElem = document.getElementById('val-score');
  const highScoreElem = document.getElementById('val-high-score');
  const levelElem = document.getElementById('val-level');
  const linesElem = document.getElementById('val-lines');

  // Modals
  const menuModal = document.getElementById('modal-menu');
  const pauseModal = document.getElementById('modal-pause');
  const gameOverModal = document.getElementById('modal-gameover');
  const howToModal = document.getElementById('modal-howto');

  // Tombol
  const btnStartGame = document.getElementById('btn-start-game');
  const btnMenuHowTo = document.getElementById('btn-menu-howto');
  const btnHowToBack = document.getElementById('btn-howto-back');

  const btnHudPause = document.getElementById('btn-hud-pause');
  const btnHudRestart = document.getElementById('btn-hud-restart');
  const btnHudMute = document.getElementById('btn-hud-mute');

  const btnPauseResume = document.getElementById('btn-pause-resume');
  const btnPauseRestart = document.getElementById('btn-pause-restart');
  const btnPauseMenu = document.getElementById('btn-pause-menu');

  const btnOverRestart = document.getElementById('btn-over-restart');
  const btnOverMenu = document.getElementById('btn-over-menu');

  // Stats Game Over Modal
  const overScoreElem = document.getElementById('over-score');
  const overHighScoreElem = document.getElementById('over-high-score');
  const overLinesElem = document.getElementById('over-lines');
  const overLevelElem = document.getElementById('over-level');

  let state = 'MENU'; // 'MENU' | 'PLAYING' | 'PAUSED' | 'GAME_OVER' | 'HOW_TO'
  let lastTime = 0;

  // Keyboard DAS (Delayed Auto Shift) State
  const keyState = {
    left: false,
    right: false,
    down: false,
  };
  const keyTimers = {
    left: 0,
    right: 0,
    down: 0,
  };
  const DAS_DELAY = 170; // ms
  const DAS_REPEAT = 50; // ms
  const SOFT_DROP_REPEAT = 40; // ms

  function updateHUD() {
    scoreElem.textContent = game.score;
    highScoreElem.textContent = game.highScore;
    levelElem.textContent = game.level;
    linesElem.textContent = game.linesCleared;
  }

  function adjustColor(hex, amt) {
    let col = hex.replace('#', '');
    if (col.length === 3) {
      col = col.split('').map((c) => c + c).join('');
    }
    const num = parseInt(col, 16);
    let r = (num >> 16) + amt;
    let g = ((num >> 8) & 0x00ff) + amt;
    let b = (num & 0x0000ff) + amt;

    r = Math.min(255, Math.max(0, r));
    g = Math.min(255, Math.max(0, g));
    b = Math.min(255, Math.max(0, b));

    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
  }

  function drawBlock(context, x, y, size, color, isGhost = false, isClearing = false) {
    if (isClearing) {
      context.fillStyle = '#ffffff';
      context.fillRect(x, y, size, size);
      context.strokeStyle = '#60a5fa';
      context.lineWidth = 2;
      context.strokeRect(x, y, size, size);
      return;
    }

    if (isGhost) {
      context.save();
      context.globalAlpha = 0.25;
      context.fillStyle = color;
      context.fillRect(x, y, size, size);
      context.globalAlpha = 0.7;
      context.strokeStyle = color;
      context.lineWidth = 2;
      context.strokeRect(x + 1, y + 1, size - 2, size - 2);
      context.restore();
      return;
    }

    const bevel = 3;
    const light = adjustColor(color, 50);
    const dark = adjustColor(color, -50);

    // Main fill
    context.fillStyle = color;
    context.fillRect(x, y, size, size);

    // Top-left highlight
    context.fillStyle = light;
    context.beginPath();
    context.moveTo(x, y);
    context.lineTo(x + size, y);
    context.lineTo(x + size - bevel, y + bevel);
    context.lineTo(x + bevel, y + bevel);
    context.lineTo(x + bevel, y + size - bevel);
    context.lineTo(x, y + size);
    context.closePath();
    context.fill();

    // Bottom-right shadow
    context.fillStyle = dark;
    context.beginPath();
    context.moveTo(x + size, y);
    context.lineTo(x + size, y + size);
    context.lineTo(x, y + size);
    context.lineTo(x + bevel, y + size - bevel);
    context.lineTo(x + size - bevel, y + size - bevel);
    context.lineTo(x + size - bevel, y + bevel);
    context.closePath();
    context.fill();

    // Inner core
    context.fillStyle = color;
    context.fillRect(x + bevel, y + bevel, size - 2 * bevel, size - 2 * bevel);
  }

  function renderBoard() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Garis grid halus
    ctx.strokeStyle = '#1a2236';
    ctx.lineWidth = 1;
    for (let c = 1; c < COLS; c++) {
      ctx.beginPath();
      ctx.moveTo(c * CELL_SIZE, 0);
      ctx.lineTo(c * CELL_SIZE, canvas.height);
      ctx.stroke();
    }
    for (let r = 1; r < ROWS; r++) {
      ctx.beginPath();
      ctx.moveTo(0, r * CELL_SIZE);
      ctx.lineTo(canvas.width, r * CELL_SIZE);
      ctx.stroke();
    }

    // Gambar balok yang sudah terkunci di papan
    for (let r = 0; r < ROWS; r++) {
      const isClearingRow = game.clearingLines.includes(r);
      for (let c = 0; c < COLS; c++) {
        const color = game.board[r][c];
        if (color) {
          drawBlock(ctx, c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, color, false, isClearingRow);
        }
      }
    }

    // Gambar ghost piece & balok aktif
    if (game.currentPiece && game.clearingLines.length === 0) {
      // Ghost Piece
      const ghostY = game.getGhostY();
      const ghostBlocks = game.currentPiece.getBlocks(0, ghostY - game.currentPiece.y);
      for (const [gx, gy] of ghostBlocks) {
        if (gy >= 0) {
          drawBlock(ctx, gx * CELL_SIZE, gy * CELL_SIZE, CELL_SIZE, game.currentPiece.color, true);
        }
      }

      // Active Piece
      const blocks = game.currentPiece.getBlocks();
      for (const [x, y] of blocks) {
        if (y >= 0) {
          drawBlock(ctx, x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, game.currentPiece.color);
        }
      }
    }
  }

  function renderNextPiece() {
    nextCtx.clearRect(0, 0, nextCanvas.width, nextCanvas.height);
    if (!game.nextPiece) return;

    const coords = SHAPES[game.nextPiece.type][0];
    const minX = Math.min(...coords.map(([cx]) => cx));
    const maxX = Math.max(...coords.map(([cx]) => cx));
    const minY = Math.min(...coords.map(([, cy]) => cy));
    const maxY = Math.max(...coords.map(([, cy]) => cy));

    const blockSize = 20;
    const pieceW = (maxX - minX + 1) * blockSize;
    const pieceH = (maxY - minY + 1) * blockSize;

    const startX = (nextCanvas.width - pieceW) / 2 - minX * blockSize;
    const startY = (nextCanvas.height - pieceH) / 2 - minY * blockSize;

    for (const [cx, cy] of coords) {
      drawBlock(nextCtx, startX + cx * blockSize, startY + cy * blockSize, blockSize, game.nextPiece.color);
    }
  }

  function setGameState(newState) {
    state = newState;
    menuModal.classList.remove('active');
    pauseModal.classList.remove('active');
    gameOverModal.classList.remove('active');
    howToModal.classList.remove('active');

    if (state === 'MENU') {
      menuModal.classList.add('active');
    } else if (state === 'PAUSED') {
      pauseModal.classList.add('active');
    } else if (state === 'GAME_OVER') {
      overScoreElem.textContent = game.score;
      overHighScoreElem.textContent = game.highScore;
      overLinesElem.textContent = game.linesCleared;
      overLevelElem.textContent = game.level;
      gameOverModal.classList.add('active');
    } else if (state === 'HOW_TO') {
      howToModal.classList.add('active');
    }
  }

  // Event Listeners Tombol Menu & Modal
  btnStartGame.addEventListener('click', () => {
    game.reset();
    setGameState('PLAYING');
  });

  btnMenuHowTo.addEventListener('click', () => {
    setGameState('HOW_TO');
  });

  btnHowToBack.addEventListener('click', () => {
    setGameState('MENU');
  });

  btnHudPause.addEventListener('click', () => {
    if (state === 'PLAYING') {
      game.togglePause();
      setGameState('PAUSED');
    }
  });

  btnHudRestart.addEventListener('click', () => {
    game.reset();
    setGameState('PLAYING');
  });

  btnHudMute.addEventListener('click', () => {
    const isMuted = sound.toggleMute();
    btnHudMute.textContent = isMuted ? '🔇 UNMUTE' : '🔊 MUTE';
  });

  btnPauseResume.addEventListener('click', () => {
    game.togglePause();
    setGameState('PLAYING');
  });

  btnPauseRestart.addEventListener('click', () => {
    game.reset();
    setGameState('PLAYING');
  });

  btnPauseMenu.addEventListener('click', () => {
    setGameState('MENU');
  });

  btnOverRestart.addEventListener('click', () => {
    game.reset();
    setGameState('PLAYING');
  });

  btnOverMenu.addEventListener('click', () => {
    setGameState('MENU');
  });

  // Touch Virtual Controls
  document.getElementById('touch-left')?.addEventListener('touchstart', (e) => {
    e.preventDefault();
    if (state === 'PLAYING') game.moveLeft();
  });
  document.getElementById('touch-right')?.addEventListener('touchstart', (e) => {
    e.preventDefault();
    if (state === 'PLAYING') game.moveRight();
  });
  document.getElementById('touch-down')?.addEventListener('touchstart', (e) => {
    e.preventDefault();
    if (state === 'PLAYING') game.softDrop();
  });
  document.getElementById('touch-rotate')?.addEventListener('touchstart', (e) => {
    e.preventDefault();
    if (state === 'PLAYING') game.tryRotate();
  });
  document.getElementById('touch-drop')?.addEventListener('touchstart', (e) => {
    e.preventDefault();
    if (state === 'PLAYING') game.hardDrop();
  });

  // Keyboard Event Handlers
  window.addEventListener('keydown', (e) => {
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
      e.preventDefault();
    }

    if (state === 'MENU') {
      if (e.key === 'Enter' || e.key === ' ') {
        game.reset();
        setGameState('PLAYING');
      } else if (e.key.toLowerCase() === 'h') {
        setGameState('HOW_TO');
      }
      return;
    }

    if (state === 'HOW_TO') {
      if (e.key === 'Escape' || e.key === 'Enter') {
        setGameState('MENU');
      }
      return;
    }

    if (state === 'PAUSED') {
      if (e.key.toLowerCase() === 'p') {
        game.togglePause();
        setGameState('PLAYING');
      } else if (e.key.toLowerCase() === 'r') {
        game.reset();
        setGameState('PLAYING');
      } else if (e.key === 'Escape') {
        setGameState('MENU');
      }
      return;
    }

    if (state === 'GAME_OVER') {
      if (e.key.toLowerCase() === 'r') {
        game.reset();
        setGameState('PLAYING');
      } else if (e.key === 'Escape') {
        setGameState('MENU');
      }
      return;
    }

    if (state === 'PLAYING') {
      if (e.key === 'ArrowLeft') {
        if (!keyState.left) {
          keyState.left = true;
          keyState.right = false;
          keyTimers.left = -DAS_DELAY;
          game.moveLeft();
        }
      } else if (e.key === 'ArrowRight') {
        if (!keyState.right) {
          keyState.right = true;
          keyState.left = false;
          keyTimers.right = -DAS_DELAY;
          game.moveRight();
        }
      } else if (e.key === 'ArrowDown') {
        if (!keyState.down) {
          keyState.down = true;
          keyTimers.down = 0;
          game.softDrop();
        }
      } else if (e.key === 'ArrowUp') {
        game.tryRotate();
      } else if (e.key === ' ') {
        game.hardDrop();
      } else if (e.key.toLowerCase() === 'p') {
        game.togglePause();
        setGameState('PAUSED');
      } else if (e.key.toLowerCase() === 'r') {
        game.reset();
      } else if (e.key.toLowerCase() === 'm') {
        const isMuted = sound.toggleMute();
        btnHudMute.textContent = isMuted ? '🔇 UNMUTE' : '🔊 MUTE';
      } else if (e.key === 'Escape') {
        game.togglePause();
        setGameState('PAUSED');
      }
    }
  });

  window.addEventListener('keyup', (e) => {
    if (e.key === 'ArrowLeft') keyState.left = false;
    if (e.key === 'ArrowRight') keyState.right = false;
    if (e.key === 'ArrowDown') keyState.down = false;
  });

  // Game Loop
  function gameLoop(timestamp) {
    if (!lastTime) lastTime = timestamp;
    const dt = timestamp - lastTime;
    lastTime = timestamp;

    if (state === 'PLAYING') {
      // Delayed Auto Shift (DAS) handling
      if (keyState.left) {
        keyTimers.left += dt;
        if (keyTimers.left >= DAS_REPEAT) {
          keyTimers.left = 0;
          game.moveLeft();
        }
      }
      if (keyState.right) {
        keyTimers.right += dt;
        if (keyTimers.right >= DAS_REPEAT) {
          keyTimers.right = 0;
          game.moveRight();
        }
      }
      if (keyState.down) {
        keyTimers.down += dt;
        if (keyTimers.down >= SOFT_DROP_REPEAT) {
          keyTimers.down = 0;
          game.softDrop();
        }
      }

      game.update(dt);
      updateHUD();

      if (game.gameOver) {
        setGameState('GAME_OVER');
      }
    }

    renderBoard();
    renderNextPiece();

    requestAnimationFrame(gameLoop);
  }

  // Jalankan Game Loop
  setGameState('MENU');
  requestAnimationFrame(gameLoop);
});
