// Get the canvas and context
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Load images
const frogImage = new Image();
frogImage.src = '/static/games/images/toucan.png'; // Replace with your frog image path

let score = 0;
const MAX_ENEMY_SPEED = 4;
const MIN_ENEMY_SPEED = 1.5;
const ENEMIES_COUNT = (canvas.height / 30) - 2;

const getRandomSpeed = () => Math.floor(Math.random() * (MAX_ENEMY_SPEED - MIN_ENEMY_SPEED + 1)) + MIN_ENEMY_SPEED;

// Car types configuration
const carTypes = [
    {
        name: 'redCar',
        imageSrc: '/static/games/images/red_car.png', // Replace with your car image path
        speed: getRandomSpeed(),
    },
];

// Load car images
carTypes.forEach(carType => {
    carType.image = new Image();
    carType.image.src = carType.imageSrc;
});

// Game variables
let frog = { x: canvas.width / 2 - 15, y: canvas.height - 30, width: 30, height: 30 };
let cars = [];
let keys = {};

// Listen for key presses
document.addEventListener('keydown', function (e) {
    keys[e.key] = true;
});
document.addEventListener('keyup', function (e) {
    keys[e.key] = false;
});

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
}

// Update game objects
function update() {
    // Move frog
    if (keys['ArrowUp']) frog.y -= 5;
    if (keys['ArrowDown']) frog.y += 5;
    if (keys['ArrowLeft']) frog.x -= 5;
    if (keys['ArrowRight']) frog.x += 5;

    // Keep frog within canvas
    frog.x = Math.max(0, Math.min(canvas.width - frog.width, frog.x));
    frog.y = Math.max(0, Math.min(canvas.height - frog.height, frog.y));

    // Move cars
    cars.forEach(car => {
        car.x += car.flipX ? car.speed : -car.speed;
        if (car.x > canvas.width) car.x = -car.width;
        if (car.x < -car.width) car.x = canvas.width;
    });

    // Check collisions
    cars.forEach(car => {
        if (
            frog.x < car.x + car.width &&
            frog.x + frog.width > car.x &&
            frog.y < car.y + car.height &&
            frog.y + frog.height > car.y
        ) {
            resetGame();
        }
    });

    // Check win condition
    if (frog.y <= 0) {
        score += 1;
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

    // Draw frog
    ctx.drawImage(frogImage, frog.x, frog.y, frog.width, frog.height);

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
    requestAnimationFrame(gameLoop);
}

// Reset game
function resetGame() {
    frog.x = canvas.width / 2 - 15;
    frog.y = canvas.height - 30;
}

// Start the game
spawnCars();
gameLoop();