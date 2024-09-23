// Get the canvas and context
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Audio context
let audioContext;

// Load images
const frogImage = new Image();
frogImage.src = '/static/games/images/toucan.png';

// Load audio
const loadAudio = async (url) => {
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    return await audioContext.decodeAudioData(arrayBuffer);
};

let walkSound, carSound, hitSound, scoreSound;

// Game variables
let score = 0;
const MAX_ENEMY_SPEED = 4;
const MIN_ENEMY_SPEED = 1.5;
const ENEMIES_COUNT = (canvas.height / 30) - 2;

const getRandomSpeed = () => Math.floor(Math.random() * (MAX_ENEMY_SPEED - MIN_ENEMY_SPEED + 1)) + MIN_ENEMY_SPEED;

// Car types configuration
const carTypes = [
    {
        name: 'redCar',
        imageSrc: '/static/games/images/red_car.png',
        speed: getRandomSpeed(),
    },
    {
        name: 'capybara',
        imageSrc: '/static/games/images/capybara.png',
        speed: getRandomSpeed(),
    },
];

// Load car images
carTypes.forEach(carType => {
    carType.image = new Image();
    carType.image.src = carType.imageSrc;
});

let frog = { x: canvas.width / 2 - 15, y: canvas.height - 30, width: 30, height: 30, facingLeft: false };
let cars = [];
let keys = {};
let walkingSoundInstance = null;
let carSoundPlayer;
let gameLoopId;

// Create start button
const startButton = document.createElement('button');
startButton.textContent = 'Start Game';
startButton.style.position = 'absolute';
startButton.style.left = '50%';
startButton.style.top = '50%';
startButton.style.transform = 'translate(-50%, -50%)';
startButton.style.padding = '10px 20px';
startButton.style.fontSize = '20px';
startButton.style.cursor = 'pointer';
startButton.style.fontFamily = 'monospace';
startButton.style.backgroundColor = '#333';
startButton.style.color = '#fff';
document.body.appendChild(startButton);

// Start game function
async function startGame() {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    startButton.style.display = 'none';
    canvas.style.display = 'block';

    // Load audio files
    [walkSound, carSound, hitSound, scoreSound] = await Promise.all([
        loadAudio('/static/games/sounds/walk.wav'),
        loadAudio('/static/games/sounds/car.wav'),
        loadAudio('/static/games/sounds/hit.wav'),
        loadAudio('/static/games/sounds/score.wav')
    ]);

    // Initialize game
    spawnCars();
    gameLoopId = requestAnimationFrame(gameLoop);

    // Add event listeners
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
}

// Event listener for start button
startButton.addEventListener('click', startGame);

// Play sound function
function playSound(buffer, loop = false, volume = 1) {
    const source = audioContext.createBufferSource();
    const gainNode = audioContext.createGain();
    source.buffer = buffer;
    source.loop = loop;
    source.connect(gainNode);
    gainNode.connect(audioContext.destination);
    gainNode.gain.setValueAtTime(volume, audioContext.currentTime);
    source.start();
    return { source, gainNode };
}

// Key event handlers
function handleKeyDown(e) {
    keys[e.key] = true;
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key) && !walkingSoundInstance) {
        walkingSoundInstance = playSound(walkSound, true, 0.5);
    }
}

function handleKeyUp(e) {
    keys[e.key] = false;
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        if (walkingSoundInstance) {
            walkingSoundInstance.source.stop();
            walkingSoundInstance = null;
        }
    }
}

// Spawn cars
function spawnCars() {
    cars = Array.from({ length: ENEMIES_COUNT }).reduce((cars, _, i) => {
        const carType = carTypes[Math.floor(Math.random() * carTypes.length)];

        const width = 50;
        const height = 30;
        const speed = getRandomSpeed();
        const y = (i + 1) * height;

        const { image } = carType;

        const flipX = Math.random() > 0.5;

        const car = {
            x: Math.random() * canvas.width,
            y,
            width,
            height,
            speed,
            image,
            flipX,
        };
        return [...cars, car];
    }, []);

    carSoundPlayer = playSound(carSound, true);
}

// Update game objects
function update() {
    // Move frog
    if (keys['ArrowUp']) frog.y -= 5;
    if (keys['ArrowDown']) frog.y += 5;
    if (keys['ArrowLeft']) { 
        frog.x -= 5; 
        frog.facingLeft = true;
        moved = true;
    }
    if (keys['ArrowRight']) { 
        frog.x += 5; 
        frog.facingLeft = false;
        moved = true;
    }

    // Keep frog within canvas
    frog.x = Math.max(0, Math.min(canvas.width - frog.width, frog.x));
    frog.y = Math.max(0, Math.min(canvas.height - frog.height, frog.y));

    // Move cars
    cars.forEach(car => {
        car.x += car.flipX ? car.speed : -car.speed;
        if (car.x > canvas.width) car.x = -car.width;
        if (car.x < -car.width) car.x = canvas.width;
    });

    // Update car sound
    const averageCarX = cars.reduce((sum, car) => sum + car.x, 0) / cars.length;
    const desiredCarVolume = 1 - Math.abs(averageCarX - canvas.width / 2) / (canvas.width / 2);
    carSoundPlayer.gainNode.gain.setValueAtTime(desiredCarVolume * .2, audioContext.currentTime);
    
    const pan = (averageCarX / canvas.width) * 2 - 1;
    const panNode = audioContext.createStereoPanner();
    panNode.pan.setValueAtTime(pan, audioContext.currentTime);
    carSoundPlayer.source.disconnect();
    carSoundPlayer.source.connect(panNode);
    panNode.connect(carSoundPlayer.gainNode);

    // Check collisions
    cars.forEach(car => {
        if (
            frog.x < car.x + car.width &&
            frog.x + frog.width > car.x &&
            frog.y < car.y + car.height &&
            frog.y + frog.height > car.y
        ) {
            playSound(hitSound);
            resetGame();
        }
    });

    // Check win condition
    if (frog.y <= 0) {
        score += 1;
        playSound(scoreSound);
        resetGame();
    }
}

// Draw everything
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw road
    ctx.fillStyle = '#292929';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw road lines  
    ctx.fillStyle = '#9e5';
    ctx.fillRect(0, 0, canvas.width, 30);
    ctx.fillRect(0, canvas.height - 30, canvas.width, 30);

    // Draw frog (toucan)
    ctx.save();
    if (frog.facingLeft) {
        ctx.scale(-1, 1);
        ctx.drawImage(frogImage, -frog.x - frog.width, frog.y, frog.width, frog.height);
    } else {
        ctx.drawImage(frogImage, frog.x, frog.y, frog.width, frog.height);
    }
    ctx.restore();

    // Draw cars
    cars.forEach(car => {
        if (car.flipX) {
            ctx.save();
            ctx.scale(-1, 1);
            ctx.drawImage(car.image, -car.x - car.width, car.y, car.width, car.height);
            ctx.restore();
            return;
        }
        ctx.drawImage(car.image, car.x, car.y, car.width, car.height); 
    });

    // Draw score
    ctx.fillStyle = '#333';
    ctx.font = '20px monospace';
    ctx.fillText(`SCORE: ${score}`, 10, 20);
}

// Game loop
function gameLoop() {
    update();
    draw();
    gameLoopId = requestAnimationFrame(gameLoop);
}

// Reset game
function resetGame() {
    frog.x = canvas.width / 2 - 15;
    frog.y = canvas.height - 30;
    frog.facingLeft = false;
}

// Initially hide the canvas
canvas.style.display = 'none';
