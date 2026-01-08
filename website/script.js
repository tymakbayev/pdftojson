// Game Variables
const canvas = document.getElementById('gameCanvas');
const ctx = canvas ? canvas.getContext('2d') : null;

// Set canvas size
function resizeCanvas() {
    if (canvas) {
        canvas.width = canvas.offsetWidth;
        canvas.height = 500;
    }
}

window.addEventListener('resize', resizeCanvas);
if (canvas) {
    resizeCanvas();
}

// Game State
let gameState = {
    isRunning: false,
    isPaused: false,
    score: 0,
    lives: 3,
    gameSpeed: 2
};

// Player (Rocket)
const player = {
    x: 0,
    y: 0,
    width: 40,
    height: 60,
    speed: 5,
    color: '#00d4ff'
};

// Initialize player position
function initPlayer() {
    player.x = canvas ? canvas.width / 2 - player.width / 2 : 0;
    player.y = canvas ? canvas.height - player.height - 20 : 0;
}

// Arrays for game objects
let asteroids = [];
let stars = [];
let particles = [];

// Input handling
const keys = {};

window.addEventListener('keydown', (e) => {
    keys[e.key.toLowerCase()] = true;
});

window.addEventListener('keyup', (e) => {
    keys[e.key.toLowerCase()] = false;
});

// Button event listeners
document.getElementById('startBtn')?.addEventListener('click', startGame);
document.getElementById('pauseBtn')?.addEventListener('click', togglePause);
document.getElementById('restartBtn')?.addEventListener('click', restartGame);
document.getElementById('playAgainBtn')?.addEventListener('click', restartGame);

// Smooth scrolling for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Game Functions
function startGame() {
    if (!canvas || !ctx) return;

    gameState.isRunning = true;
    gameState.isPaused = false;
    gameState.score = 0;
    gameState.lives = 3;
    gameState.gameSpeed = 2;

    asteroids = [];
    stars = [];
    particles = [];

    initPlayer();

    document.getElementById('startBtn').disabled = true;
    document.getElementById('pauseBtn').disabled = false;
    document.getElementById('gameOver')?.classList.add('hidden');

    updateUI();
    gameLoop();
}

function togglePause() {
    if (gameState.isRunning) {
        gameState.isPaused = !gameState.isPaused;
        document.getElementById('pauseBtn').textContent = gameState.isPaused ? 'Resume' : 'Pause';
        if (!gameState.isPaused) {
            gameLoop();
        }
    }
}

function restartGame() {
    startGame();
}

function gameOver() {
    gameState.isRunning = false;
    document.getElementById('startBtn').disabled = false;
    document.getElementById('pauseBtn').disabled = true;
    document.getElementById('finalScore').textContent = gameState.score;
    document.getElementById('gameOver')?.classList.remove('hidden');
}

function updateUI() {
    document.getElementById('score').textContent = gameState.score;
    const heartsDisplay = '❤️'.repeat(Math.max(0, gameState.lives));
    document.getElementById('lives').textContent = heartsDisplay || '💀';
}

// Player Movement
function movePlayer() {
    if (!canvas) return;

    // Horizontal movement
    if ((keys['arrowleft'] || keys['a']) && player.x > 0) {
        player.x -= player.speed;
    }
    if ((keys['arrowright'] || keys['d']) && player.x < canvas.width - player.width) {
        player.x += player.speed;
    }

    // Vertical movement
    if ((keys['arrowup'] || keys['w']) && player.y > 0) {
        player.y -= player.speed;
    }
    if ((keys['arrowdown'] || keys['s']) && player.y < canvas.height - player.height) {
        player.y += player.speed;
    }
}

// Draw Player (Rocket)
function drawPlayer() {
    if (!ctx) return;

    // Rocket body
    ctx.fillStyle = player.color;
    ctx.beginPath();
    ctx.moveTo(player.x + player.width / 2, player.y);
    ctx.lineTo(player.x, player.y + player.height);
    ctx.lineTo(player.x + player.width, player.y + player.height);
    ctx.closePath();
    ctx.fill();

    // Rocket window
    ctx.fillStyle = '#ffd700';
    ctx.beginPath();
    ctx.arc(player.x + player.width / 2, player.y + 20, 8, 0, Math.PI * 2);
    ctx.fill();

    // Rocket flames
    const flameHeight = Math.random() * 15 + 10;
    ctx.fillStyle = '#ff6600';
    ctx.beginPath();
    ctx.moveTo(player.x + 5, player.y + player.height);
    ctx.lineTo(player.x + player.width / 2, player.y + player.height + flameHeight);
    ctx.lineTo(player.x + player.width - 5, player.y + player.height);
    ctx.closePath();
    ctx.fill();

    ctx.fillStyle = '#ffff00';
    ctx.beginPath();
    ctx.moveTo(player.x + 10, player.y + player.height);
    ctx.lineTo(player.x + player.width / 2, player.y + player.height + flameHeight - 5);
    ctx.lineTo(player.x + player.width - 10, player.y + player.height);
    ctx.closePath();
    ctx.fill();
}

// Asteroids
function createAsteroid() {
    if (!canvas) return;

    const size = Math.random() * 30 + 20;
    asteroids.push({
        x: Math.random() * (canvas.width - size),
        y: -size,
        width: size,
        height: size,
        speed: Math.random() * 2 + gameState.gameSpeed,
        rotation: Math.random() * Math.PI * 2,
        rotationSpeed: (Math.random() - 0.5) * 0.1
    });
}

function updateAsteroids() {
    if (!canvas) return;

    asteroids.forEach((asteroid, index) => {
        asteroid.y += asteroid.speed;
        asteroid.rotation += asteroid.rotationSpeed;

        // Remove asteroids that are off screen
        if (asteroid.y > canvas.height) {
            asteroids.splice(index, 1);
        }

        // Check collision with player
        if (checkCollision(player, asteroid)) {
            asteroids.splice(index, 1);
            gameState.lives--;
            updateUI();
            createExplosion(asteroid.x, asteroid.y);

            if (gameState.lives <= 0) {
                gameOver();
            }
        }
    });
}

function drawAsteroids() {
    if (!ctx) return;

    asteroids.forEach(asteroid => {
        ctx.save();
        ctx.translate(asteroid.x + asteroid.width / 2, asteroid.y + asteroid.height / 2);
        ctx.rotate(asteroid.rotation);

        // Draw asteroid shape
        ctx.fillStyle = '#8b4513';
        ctx.beginPath();
        for (let i = 0; i < 8; i++) {
            const angle = (i / 8) * Math.PI * 2;
            const radius = asteroid.width / 2 + (Math.random() - 0.5) * 5;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = '#654321';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.restore();
    });
}

// Stars (collectibles)
function createStar() {
    if (!canvas) return;

    stars.push({
        x: Math.random() * (canvas.width - 20),
        y: -20,
        width: 20,
        height: 20,
        speed: Math.random() + 1.5,
        rotation: 0
    });
}

function updateStars() {
    if (!canvas) return;

    stars.forEach((star, index) => {
        star.y += star.speed;
        star.rotation += 0.05;

        // Remove stars that are off screen
        if (star.y > canvas.height) {
            stars.splice(index, 1);
        }

        // Check collision with player
        if (checkCollision(player, star)) {
            stars.splice(index, 1);
            gameState.score += 10;
            updateUI();
            createSparkles(star.x, star.y);
        }
    });
}

function drawStars() {
    if (!ctx) return;

    stars.forEach(star => {
        ctx.save();
        ctx.translate(star.x + star.width / 2, star.y + star.height / 2);
        ctx.rotate(star.rotation);

        // Draw star shape
        ctx.fillStyle = '#ffd700';
        ctx.beginPath();
        for (let i = 0; i < 5; i++) {
            const angle = (i / 5) * Math.PI * 2 - Math.PI / 2;
            const x = Math.cos(angle) * star.width / 2;
            const y = Math.sin(angle) * star.height / 2;
            ctx.lineTo(x, y);

            const innerAngle = angle + Math.PI / 5;
            const innerX = Math.cos(innerAngle) * star.width / 4;
            const innerY = Math.sin(innerAngle) * star.height / 4;
            ctx.lineTo(innerX, innerY);
        }
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = '#ffea00';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.restore();
    });
}

// Particles for effects
function createExplosion(x, y) {
    for (let i = 0; i < 15; i++) {
        particles.push({
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 6,
            vy: (Math.random() - 0.5) * 6,
            life: 30,
            color: '#ff6600'
        });
    }
}

function createSparkles(x, y) {
    for (let i = 0; i < 10; i++) {
        particles.push({
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 4,
            vy: (Math.random() - 0.5) * 4,
            life: 20,
            color: '#ffd700'
        });
    }
}

function updateParticles() {
    particles.forEach((particle, index) => {
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.life--;

        if (particle.life <= 0) {
            particles.splice(index, 1);
        }
    });
}

function drawParticles() {
    if (!ctx) return;

    particles.forEach(particle => {
        ctx.fillStyle = particle.color;
        ctx.globalAlpha = particle.life / 30;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
    });
}

// Collision Detection
function checkCollision(obj1, obj2) {
    return obj1.x < obj2.x + obj2.width &&
           obj1.x + obj1.width > obj2.x &&
           obj1.y < obj2.y + obj2.height &&
           obj1.y + obj1.height > obj2.y;
}

// Background Stars
function drawBackground() {
    if (!ctx || !canvas) return;

    // Gradient background
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#000428');
    gradient.addColorStop(1, '#004e92');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Random stars in background
    ctx.fillStyle = 'white';
    for (let i = 0; i < 50; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        const size = Math.random() * 2;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Spawn Management
let asteroidSpawnTimer = 0;
let starSpawnTimer = 0;

function spawnObjects() {
    asteroidSpawnTimer++;
    starSpawnTimer++;

    if (asteroidSpawnTimer > 60) {
        createAsteroid();
        asteroidSpawnTimer = 0;
    }

    if (starSpawnTimer > 120) {
        createStar();
        starSpawnTimer = 0;
    }

    // Increase difficulty over time
    if (gameState.score > 0 && gameState.score % 100 === 0) {
        gameState.gameSpeed += 0.1;
    }
}

// Main Game Loop
function gameLoop() {
    if (!gameState.isRunning || gameState.isPaused || !ctx || !canvas) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background
    drawBackground();

    // Update game objects
    movePlayer();
    updateAsteroids();
    updateStars();
    updateParticles();
    spawnObjects();

    // Draw game objects
    drawParticles();
    drawPlayer();
    drawAsteroids();
    drawStars();

    // Continue game loop
    requestAnimationFrame(gameLoop);
}

// Initialize
window.addEventListener('load', () => {
    if (canvas) {
        resizeCanvas();
        initPlayer();
    }
});
