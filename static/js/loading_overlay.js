document.addEventListener('DOMContentLoaded', function () {
    const overlay = document.getElementById('pet-loading-overlay');
    // Select all AI Meal and AI Health buttons
    const aiButtons = document.querySelectorAll('a[href*="generate_meal"], a[href*="generate_health"]');
    aiButtons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            overlay.classList.remove('hidden');
            // Delay navigation so overlay is visible
            setTimeout(() => {
                window.location = btn.href;
            }, 150);
            e.preventDefault();
        });
    });
});