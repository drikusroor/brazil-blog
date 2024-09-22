// Get the canvas and context
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Load images
const frogImage = new Image();
frogImage.src = '/static/games/images/toucan.png'; // Replace with your frog image path

const MAX_ENEMY_SPEED = 4;
const MIN_ENEMY_SPEED = 1.5;
const ENEMIES_COUNT = (canvas.height / 30) - 1;

const getRandomSpeed = () => Math.floor(Math.random() * (MAX_ENEMY_SPEED - MIN_ENEMY_SPEED + 1)) + MIN_ENEMY_SPEED;

// Car types configuration
const carTypes = [
    {
        name: 'redCar',
        imageSrc: '/static/games/images/red_car.png', // Replace with your car image path
        speed: getRandomSpeed()
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
        const y = i * height;

        const car = {
            x: Math.random() * canvas.width,
            y,
            width,
            height,
            speed,
            image: carType.image
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
        car.x += car.speed;
        if (car.x > canvas.width) car.x = -car.width;
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
        alert('You win!');
        resetGame();
    }
}

// Draw everything
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw frog
    ctx.drawImage(frogImage, frog.x, frog.y, frog.width, frog.height);

    // Draw cars
    cars.forEach(car => {
        ctx.drawImage(car.image, car.x, car.y, car.width, car.height);
    });
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