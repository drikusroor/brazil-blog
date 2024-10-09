document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.drink-add-btn');
    buttons.forEach(button => {

        const initialInnerHTML = button.innerHTML;

        button.addEventListener('click', async function() {
            const drinkTypeId = this.dataset.drinkType;

            button.disabled = true;
            button.classList.add('opacity-50', 'cursor-not-allowed');

            let location = '';

            try {
                const position = await getCurrentLocation();
                location = `${position.coords.latitude},${position.coords.longitude}`;
            } catch (error) {
                console.error('Error getting location:', error);
            }

            fetch('/drinks/api/drinks/quick_add_drink/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    drink_type: drinkTypeId,
                    location,
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Drink added:', data);
                // You can add some feedback here, like a toast notification
                showToast('Drink added successfully!');
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Failed to add drink.', 'error');
            })
            .finally(() => {
                // Wait for 1 second before enabling the button again
                // This is to prevent multiple clicks
                setTimeout(() => {
                    button.disabled = false;
                    button.classList.remove('opacity-50', 'cursor-not-allowed');
                }, 1000);
            });
        });
    });
});

// Get location through the browser's geolocation API as a promise
async function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject('Geolocation is not supported by your browser');
        } else {
            navigator.geolocation.getCurrentPosition(
                position => resolve(position),
                error => reject(error)
            );
        }
    });
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

// Simple toast notification function
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed z-[10000] bottom-4 right-4 px-4 py-2 rounded-md text-white ${type === 'success' ? 'bg-green-700' : 'bg-red-700'} transition-opacity duration-300 drop-shadow-lg`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}