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

let musics = [
    '/static/games/sounds/frogalicious.mp3',
    '/static/games/sounds/toucanchamon.mp3',
]

// Background music variables
let backgroundMusic = [];
let currentMusicIndex = 0;
let musicSource;

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
    {
        name: 'jaguar',
        imageSrc: '/static/games/images/jaguar.png',
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
let isPaused = false;

const buttonArea = document.querySelector('#buttonArea');

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
buttonArea.appendChild(startButton);

// Create pause menu
const pauseMenu = document.createElement('div');
pauseMenu.style.position = 'absolute';
pauseMenu.style.left = '50%';
pauseMenu.style.top = '50%';
pauseMenu.style.transform = 'translate(-50%, -50%)';
pauseMenu.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
pauseMenu.style.padding = '20px';
pauseMenu.style.borderRadius = '10px';
pauseMenu.style.display = 'none';
buttonArea.appendChild(pauseMenu);

const continueButton = document.createElement('button');
continueButton.textContent = 'Continue';
continueButton.style.display = 'block';
continueButton.style.marginBottom = '10px';
continueButton.style.padding = '10px 20px';
continueButton.style.fontSize = '16px';
continueButton.style.cursor = 'pointer';
continueButton.style.color = '#fff';
pauseMenu.appendChild(continueButton);

const forfeitButton = document.createElement('button');
forfeitButton.textContent = 'Forfeit';
forfeitButton.style.display = 'block';
forfeitButton.style.padding = '10px 20px';
forfeitButton.style.fontSize = '16px';
forfeitButton.style.cursor = 'pointer';
forfeitButton.style.color = '#fff';
pauseMenu.appendChild(forfeitButton);

// Start game function
async function startGame() {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    startButton.style.display = 'none';
    canvas.style.display = 'block';

    // Load audio files
    [walkSound, carSound, hitSound, scoreSound, ...backgroundMusic] = await Promise.all([
        loadAudio('/static/games/sounds/walk.wav'),
        loadAudio('/static/games/sounds/car.wav'),
        loadAudio('/static/games/sounds/hit.wav'),
        loadAudio('/static/games/sounds/score.wav'),
        ...musics.map(loadAudio),
    ]);

    // Initialize game
    resetGame();
    spawnCars();
    playBackgroundMusic();
    gameLoopId = requestAnimationFrame(gameLoop);

    // Add event listeners
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
}

// Event listener for start button
startButton.addEventListener('click', startGame);

// Event listeners for pause menu buttons
continueButton.addEventListener('click', () => {
    isPaused = false;
    pauseMenu.style.display = 'none';
    gameLoopId = requestAnimationFrame(gameLoop);
});

forfeitButton.addEventListener('click', () => {
    isPaused = false;
    pauseMenu.style.display = 'none';
    canvas.style.opacity = 0.1;
    startButton.style.display = 'block';
    
    // Stop all sounds
    if (walkingSoundInstance) {
        walkingSoundInstance.source.stop();
        walkingSoundInstance = null;
    }
    if (carSoundPlayer) {
        carSoundPlayer.source.stop();
        carSoundPlayer = null;
    }
    stopBackgroundMusic();
    
    // Reset game state
    score = 0;
    frog = { x: canvas.width / 2 - 15, y: canvas.height - 30, width: 30, height: 30, facingLeft: false };
    cars = [];
    keys = {};
    
    // Cancel the game loop
    cancelAnimationFrame(gameLoopId);
});

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

// Play background music function
function playBackgroundMusic() {
    if (musicSource) {
        musicSource.stop();
    }
    musicSource = audioContext.createBufferSource();
    musicSource.buffer = backgroundMusic[currentMusicIndex];
    musicSource.connect(audioContext.destination);
    musicSource.loop = false;
    musicSource.start();
    musicSource.onended = () => {
        currentMusicIndex = (currentMusicIndex + 1) % backgroundMusic.length;
        playBackgroundMusic();
    };
}

// Stop background music function
function stopBackgroundMusic() {
    if (musicSource) {
        musicSource.stop();
        musicSource = null;
    }
    currentMusicIndex = 0;
}

// Key event handlers
function handleKeyDown(e) {
    keys[e.key.toLowerCase()] = true;
    if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', 'w', 'a', 's', 'd'].includes(e.key.toLowerCase()) && !walkingSoundInstance) {
        walkingSoundInstance = playSound(walkSound, true, 0.5);
    }
    if (e.key.toLowerCase() === 'escape') {
        togglePause();
    }
}

function handleKeyUp(e) {
    keys[e.key.toLowerCase()] = false;
    if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', 'w', 'a', 's', 'd'].includes(e.key.toLowerCase())) {
        if (!keys['arrowup'] && !keys['arrowdown'] && !keys['arrowleft'] && !keys['arrowright'] &&
            !keys['w'] && !keys['a'] && !keys['s'] && !keys['d'] && walkingSoundInstance) {
            walkingSoundInstance.source.stop();
            walkingSoundInstance = null;
        }
    }
}

// Toggle pause function
function togglePause() {
    isPaused = !isPaused;
    if (isPaused) {
        cancelAnimationFrame(gameLoopId);
        pauseMenu.style.display = 'block';
    } else {
        pauseMenu.style.display = 'none';
        gameLoopId = requestAnimationFrame(gameLoop);
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
    if (keys['arrowup'] || keys['w']) frog.y -= 5;
    if (keys['arrowdown'] || keys['s']) frog.y += 5;
    if (keys['arrowleft'] || keys['a']) { 
        frog.x -= 5; 
        frog.facingLeft = true;
    }
    if (keys['arrowright'] || keys['d']) { 
        frog.x += 5; 
        frog.facingLeft = false;
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
    const averageCarX = cars.length ? cars.reduce((sum, car) => sum + car.x, 0) / cars.length : 0;
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
            if (score > 0) {
                submitFetchAndDisplayHighScore(score);
            }
            score = 0;
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
    if (!isPaused) {
        update();
        draw();
        gameLoopId = requestAnimationFrame(gameLoop);
    }
}

// Add this function to submit the score
function submitScore(score) {
    return fetch('/games/submit-score/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `score=${score}`
    })
    .then(response => response.json())
}



// Fetch high score
async function fetchHighScore() {
    return fetch('/games/high-score/').then(response => response.json());
}

async function fetchAndDisplayHighScore() {

    const highScoreList = document.getElementById('highScoreList');
    
    // add shimmer
    highScoreList.innerHTML = '<div class="bg-slate-400 animate-pulse rounded-lg p-2 h-96 w-full"></div>';

    fetchHighScore().then((data) => {
        if (data?.length) {
            highScoreList.innerHTML = '';

            data.forEach((scoreEntry, index) => {
                const listItem = document.createElement('li');
                listItem.classList.add('flex', 'items-center', 'justify-start', 'p-2', 'bg-slate-100', 'rounded-lg', 'mb-2');

                const listItemContainer = document.createElement('div');
                listItemContainer.classList.add('flex-1', 'flex', 'items-center', 'justify-start', 'gap-4');
                
                const { player, score } = scoreEntry;
                const { display_name, avatar } = player;

                const numberEl = document.createElement('span');
                numberEl.textContent = index + 1;
                if (index === 0) {
                    numberEl.classList.add('text-center', 'rounded-full', 'w-8', 'h-8', 'p-0.5', 'text-xl', 'font-bold', 'bg-yellow-500', 'text-white');
                } else if (index === 1) {
                    numberEl.classList.add('text-center', 'rounded-full', 'w-8', 'h-8', 'p-0.5', 'text-xl', 'font-bold', 'bg-gray-500', 'text-white');
                } else if (index === 2) {
                    numberEl.classList.add('text-center', 'rounded-full', 'w-8', 'h-8', 'p-0.5', 'text-xl', 'font-bold', 'bg-yellow-900', 'text-white');
                } else {
                    numberEl.classList.add('text-center', 'rounded-full', 'w-8', 'h-8', 'p-0.5', 'text-xl', 'font-bold', 'bg-gray-300');
                }

                const avatarEl = document.createElement('img');
                avatarEl.classList.add('w-8', 'h-8', 'rounded-full');
                avatarEl.src = avatar;

                const nameEl = document.createElement('span');
                nameEl.textContent = display_name;

                const scoreEl = document.createElement('span');
                scoreEl.classList.add('text-lg', 'text-right', 'ml-auto', 'font-semibold', 'bg-green-700', 'text-white', 'px-2', 'rounded', 'min-w-16');
                scoreEl.textContent = score;

                listItemContainer.appendChild(numberEl);
                listItemContainer.appendChild(avatarEl);
                listItemContainer.appendChild(nameEl);
                listItemContainer.appendChild(scoreEl);

                listItem.appendChild(listItemContainer);

                highScoreList.appendChild(listItem);
            });

        } else {
            console.error('Error fetching high score:', data.message);
            highScoreList.innerHTML = 'There are no high scores yet';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        highScoreList.innerHTML = 'Failed to fetch high scores';
    });
}

async function submitFetchAndDisplayHighScore(score) {
    return submitScore(score).then(fetchAndDisplayHighScore);
}

// Function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Modify the resetGame function
function resetGame() {
    canvas.style.opacity = 1;
    frog.x = canvas.width / 2 - 15;
    frog.y = canvas.height - 30;
    frog.facingLeft = false;
}

// Initially hide the canvas
canvas.style.opacity = 0.1;

// Fetch high score
fetchAndDisplayHighScore();
