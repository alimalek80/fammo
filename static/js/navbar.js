document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const mainNavbar = document.getElementById('main-navbar');
    let lastScrollTop = 0;

    // Toggle mobile menu on hamburger click
    mobileMenuButton.addEventListener('click', function () {
        mobileMenu.classList.toggle('hidden');
    });

    // Hide/Show Navbar on Scroll
    window.addEventListener('scroll', function () {
        const currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (currentScrollTop > lastScrollTop && currentScrollTop > 70) {
            mainNavbar.classList.add('navbar-hidden');
        } else if (currentScrollTop < lastScrollTop || currentScrollTop <= 70) {
            mainNavbar.classList.remove('navbar-hidden');
        }

        lastScrollTop = Math.max(0, currentScrollTop);
    });

    document.querySelectorAll('.pet-type-option input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function () {
            document.querySelectorAll('.pet-type-option').forEach(label => {
                label.classList.remove('border-indigo-600', 'shadow-md', 'bg-indigo-50');
            });
            this.closest('label').classList.add('border-indigo-600', 'shadow-md', 'bg-indigo-50');
        });
    });
});
