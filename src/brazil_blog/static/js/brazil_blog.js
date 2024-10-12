// Simple toast notification function
function showToast(message, type = 'success') {
    const toasts = document.querySelectorAll('[role="alert"]');
    console.log(toasts);
    toasts.forEach(toast => {
        const currentY = toast.style.transform.match(/translateY\(-(\d+)px\)/);
        toast.style.transform = `translateY(-${toast.offsetHeight + 10 + (currentY ? parseInt(currentY[1]) : 0)}px)`;
    });

    const toast = document.createElement('div');
    toast.setAttribute('role', 'alert');
    toast.className = `fixed z-[10000] bottom-4 right-4 px-4 py-2 rounded-md text-white ${type === 'success' ? 'bg-green-700' : 'bg-red-700'} transition duration-300 drop-shadow-lg`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}