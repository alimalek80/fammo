document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const userDropdownToggle = document.getElementById('user-dropdown-toggle');
    const userDropdownMenu = document.getElementById('user-dropdown-menu');
    const howItWorksToggle = document.getElementById('how-it-works-toggle');
    const howItWorksMenu = document.getElementById('how-it-works-menu');
    const mainNavbar = document.getElementById('main-navbar');
    let lastScrollTop = 0;

    // Toggle mobile menu on hamburger click
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            mobileMenu.classList.toggle('hidden');
            console.log('Mobile menu toggled, hidden class:', mobileMenu.classList.contains('hidden'));
        });
    } else {
        console.error('Mobile menu elements not found:', {
            button: !!mobileMenuButton,
            menu: !!mobileMenu
        });
    }

    // User dropdown toggle
    if (userDropdownToggle && userDropdownMenu) {
        userDropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            userDropdownMenu.classList.toggle('show');
            // Close how it works dropdown if open
            if (howItWorksMenu) {
                howItWorksMenu.classList.remove('show');
            }
            console.log('User dropdown toggled, show class:', userDropdownMenu.classList.contains('show'));
        });
    }

    // How it Works dropdown toggle
    if (howItWorksToggle && howItWorksMenu) {
        howItWorksToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            howItWorksMenu.classList.toggle('show');
            // Close user dropdown if open
            if (userDropdownMenu) {
                userDropdownMenu.classList.remove('show');
            }
            console.log('How it Works dropdown toggled, show class:', howItWorksMenu.classList.contains('show'));
        });
    }

    // Single global click handler to close all dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        // Close mobile menu if clicking outside
        if (mobileMenuButton && mobileMenu) {
            if (!mobileMenu.contains(e.target) && !mobileMenuButton.contains(e.target)) {
                if (!mobileMenu.classList.contains('hidden')) {
                    mobileMenu.classList.add('hidden');
                }
            }
        }

        // Close user dropdown if clicking outside
        if (userDropdownToggle && userDropdownMenu) {
            if (!userDropdownToggle.contains(e.target) && !userDropdownMenu.contains(e.target)) {
                userDropdownMenu.classList.remove('show');
            }
        }

        // Close how it works dropdown if clicking outside
        if (howItWorksToggle && howItWorksMenu) {
            if (!howItWorksToggle.contains(e.target) && !howItWorksMenu.contains(e.target)) {
                howItWorksMenu.classList.remove('show');
            }
        }
    });

    // Hide/Show Navbar on Scroll
    if (mainNavbar) {
        window.addEventListener('scroll', function () {
            const currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;

            if (currentScrollTop > lastScrollTop && currentScrollTop > 70) {
                mainNavbar.classList.add('navbar-hidden');
            } else if (currentScrollTop < lastScrollTop || currentScrollTop <= 70) {
                mainNavbar.classList.remove('navbar-hidden');
            }

            lastScrollTop = Math.max(0, currentScrollTop);
        });
    }

    // Pet type option selection
    const petTypeOptions = document.querySelectorAll('.pet-type-option input[type="radio"]');
    if (petTypeOptions.length > 0) {
        petTypeOptions.forEach(radio => {
            radio.addEventListener('change', function () {
                document.querySelectorAll('.pet-type-option').forEach(label => {
                    label.classList.remove('border-indigo-600', 'shadow-md', 'bg-indigo-50');
                });
                this.closest('label').classList.add('border-indigo-600', 'shadow-md', 'bg-indigo-50');
            });
        });
    }
});
