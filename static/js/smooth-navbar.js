/**
 * Smooth Navbar JavaScript
 * Handles sliding underline animation and smooth interactions
 */

class SmoothNavbar {
    constructor() {
        this.navbar = document.querySelector('.smooth-navbar');
        this.navList = document.querySelector('.nav-list');
        this.navLinks = document.querySelectorAll('.nav-link');
        this.underline = document.querySelector('.nav-underline');
        this.mobileToggle = document.getElementById('mobileToggle');
        this.navbarNav = document.querySelector('.navbar-nav');
        this.mobileOverlay = document.getElementById('mobileMenuOverlay');
        this.dropdowns = document.querySelectorAll('.nav-dropdown');
        this.quickThemeToggle = document.getElementById('quickThemeToggle');
        this.notificationToggle = document.getElementById('notificationToggle');

        this.isMenuOpen = false;
        this.currentPath = window.location.pathname;

        this.init();
    }
    
    init() {
        this.setupUnderlineAnimation();
        this.setupMobileToggle();
        this.setupDropdowns();
        this.setupActiveTab();
        this.setupScrollEffect();
        this.setupClickOutside();
        this.setupKeyboardNavigation();
        this.setupQuickSettings();
        this.setupActivePageHighlighting();
        this.setupDropdownThemeToggle();
        this.setupFloatingLogout();
        this.setupSettingsNavigation();

        // Set initial active tab
        this.setActiveTab();

        console.log('✅ Enhanced smooth navbar initialized');
    }
    
    setupUnderlineAnimation() {
        if (!this.underline || !this.navLinks.length) return;
        
        // Add underline to nav list if not exists
        if (!this.underline.parentElement) {
            this.navList.appendChild(this.underline);
        }
        
        // Handle nav link clicks
        this.navLinks.forEach((link, index) => {
            link.addEventListener('click', (e) => {
                // Don't prevent default for dropdown toggles
                if (!link.classList.contains('dropdown-toggle')) {
                    this.setActiveLink(link);
                }
            });
            
            // Handle hover effects
            link.addEventListener('mouseenter', () => {
                this.moveUnderline(link, true);
            });
        });
        
        // Handle mouse leave from nav list
        this.navList.addEventListener('mouseleave', () => {
            const activeLink = this.navList.querySelector('.nav-link.active');
            if (activeLink) {
                this.moveUnderline(activeLink, false);
            } else {
                this.hideUnderline();
            }
        });
    }
    
    setActiveLink(link) {
        // Remove active class from all links
        this.navLinks.forEach(l => l.classList.remove('active'));
        
        // Add active class to clicked link
        link.classList.add('active');
        
        // Move underline to active link
        this.moveUnderline(link, false);
        
        // Store active tab in localStorage
        const href = link.getAttribute('href');
        if (href) {
            localStorage.setItem('activeTab', href);
        }
    }
    
    moveUnderline(targetLink, isHover = false) {
        if (!this.underline || !targetLink) return;
        
        const linkRect = targetLink.getBoundingClientRect();
        const navRect = this.navList.getBoundingClientRect();
        
        const left = linkRect.left - navRect.left;
        const width = linkRect.width;
        
        // Apply transform for smooth animation
        this.underline.style.transform = `translateX(${left}px)`;
        this.underline.style.width = `${width}px`;
        this.underline.classList.add('active');
        
        // Add subtle scale effect on hover
        if (isHover) {
            this.underline.style.transform += ' scaleY(1.2)';
        }
    }
    
    hideUnderline() {
        if (this.underline) {
            this.underline.classList.remove('active');
        }
    }
    
    setActiveTab() {
        const currentPath = window.location.pathname;
        const storedTab = localStorage.getItem('activeTab');
        
        // Find matching link based on current path
        let activeLink = null;
        
        this.navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && (currentPath.includes(href) || href === storedTab)) {
                activeLink = link;
            }
        });
        
        // Default to first link if no match found
        if (!activeLink && this.navLinks.length > 0) {
            activeLink = this.navLinks[0];
        }
        
        if (activeLink) {
            this.setActiveLink(activeLink);
        }
    }
    
    setupMobileToggle() {
        if (!this.mobileToggle || !this.navbarNav) return;

        this.mobileToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleMobileMenu();
        });

        // Close menu when clicking overlay
        if (this.mobileOverlay) {
            this.mobileOverlay.addEventListener('click', () => {
                this.closeMobileMenu();
            });
        }

        // Close menu on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isMenuOpen) {
                this.closeMobileMenu();
            }
        });
    }

    toggleMobileMenu() {
        if (this.isMenuOpen) {
            this.closeMobileMenu();
        } else {
            this.openMobileMenu();
        }
    }

    openMobileMenu() {
        this.isMenuOpen = true;
        this.mobileToggle.classList.add('active');
        this.navbarNav.classList.add('show');

        if (this.mobileOverlay) {
            this.mobileOverlay.classList.add('show');
        }

        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        // Close any open dropdowns
        this.closeAllDropdowns();

        // Focus first nav link for accessibility
        const firstNavLink = this.navbarNav.querySelector('.nav-link');
        if (firstNavLink) {
            setTimeout(() => firstNavLink.focus(), 300);
        }
    }

    closeMobileMenu() {
        this.isMenuOpen = false;
        this.mobileToggle.classList.remove('active');
        this.navbarNav.classList.remove('show');

        if (this.mobileOverlay) {
            this.mobileOverlay.classList.remove('show');
        }

        // Restore body scroll
        document.body.style.overflow = '';

        // Close any open dropdowns
        this.closeAllDropdowns();
    }
    
    setupDropdowns() {
        this.dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const menu = dropdown.querySelector('.dropdown-menu');

            if (toggle && menu) {
                // Click handler for mobile
                toggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleDropdown(dropdown);
                });

                // Hover handlers for desktop
                if (window.innerWidth > 768) {
                    dropdown.addEventListener('mouseenter', () => {
                        this.showDropdown(dropdown);
                    });

                    dropdown.addEventListener('mouseleave', () => {
                        this.hideDropdown(dropdown);
                    });
                }
            }
        });
    }
    
    toggleDropdown(targetDropdown) {
        const menu = targetDropdown.querySelector('.dropdown-menu');
        const isOpen = menu.classList.contains('show');
        
        // Close all other dropdowns
        this.closeAllDropdowns();
        
        // Toggle target dropdown
        if (!isOpen) {
            targetDropdown.classList.add('active');
            menu.classList.add('show');
        }
    }
    
    showDropdown(dropdown) {
        // Close other dropdowns first
        this.closeAllDropdowns();

        dropdown.classList.add('active');
        const menu = dropdown.querySelector('.dropdown-menu');
        if (menu) {
            menu.classList.add('show');
        }
    }

    hideDropdown(dropdown) {
        dropdown.classList.remove('active');
        const menu = dropdown.querySelector('.dropdown-menu');
        if (menu) {
            menu.classList.remove('show');
        }
    }

    closeAllDropdowns() {
        this.dropdowns.forEach(dropdown => {
            dropdown.classList.remove('active');
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu) {
                menu.classList.remove('show');
            }
        });
    }
    
    setupClickOutside() {
        document.addEventListener('click', (e) => {
            // Close mobile menu if clicking outside
            if (!this.navbar.contains(e.target) && this.isMenuOpen) {
                this.closeMobileMenu();
            }

            // Close dropdowns if clicking outside
            if (!e.target.closest('.nav-dropdown')) {
                this.closeAllDropdowns();
            }
        });
    }

    setupKeyboardNavigation() {
        // Tab navigation through nav links
        this.navLinks.forEach((link, index) => {
            link.addEventListener('keydown', (e) => {
                switch (e.key) {
                    case 'Enter':
                    case ' ':
                        e.preventDefault();
                        link.click();
                        break;
                    case 'ArrowRight':
                    case 'ArrowDown':
                        e.preventDefault();
                        this.focusNextLink(index);
                        break;
                    case 'ArrowLeft':
                    case 'ArrowUp':
                        e.preventDefault();
                        this.focusPrevLink(index);
                        break;
                    case 'Escape':
                        if (this.isMenuOpen) {
                            this.closeMobileMenu();
                        }
                        break;
                }
            });
        });

        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Alt + M for mobile menu toggle
            if (e.altKey && e.key === 'm') {
                e.preventDefault();
                if (window.innerWidth <= 768) {
                    this.toggleMobileMenu();
                }
            }
        });
    }

    focusNextLink(currentIndex) {
        const nextIndex = (currentIndex + 1) % this.navLinks.length;
        this.navLinks[nextIndex].focus();
    }

    focusPrevLink(currentIndex) {
        const prevIndex = currentIndex === 0 ? this.navLinks.length - 1 : currentIndex - 1;
        this.navLinks[prevIndex].focus();
    }

    setupQuickSettings() {
        // Quick theme toggle
        if (this.quickThemeToggle) {
            this.quickThemeToggle.addEventListener('click', () => {
                this.toggleQuickTheme();
            });
        }

        // Notification toggle
        if (this.notificationToggle) {
            this.notificationToggle.addEventListener('click', () => {
                this.toggleNotifications();
            });
        }
    }

    toggleQuickTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        // Update theme
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        // Update icon
        const icon = this.quickThemeToggle.querySelector('i');
        if (icon) {
            icon.className = newTheme === 'light' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
        }

        // Show feedback
        this.showQuickFeedback(this.quickThemeToggle, `${newTheme} mode`);
    }

    toggleNotifications() {
        const isEnabled = this.notificationToggle.classList.toggle('active');

        // Update icon
        const icon = this.notificationToggle.querySelector('i');
        if (icon) {
            icon.className = isEnabled ? 'bi bi-bell-fill' : 'bi bi-bell-slash-fill';
        }

        // Show feedback
        this.showQuickFeedback(this.notificationToggle,
            isEnabled ? 'Notifications on' : 'Notifications off');
    }

    showQuickFeedback(button, message) {
        const feedback = document.createElement('div');
        feedback.className = 'quick-feedback';
        feedback.textContent = message;
        feedback.style.cssText = `
            position: absolute;
            top: calc(100% + 8px);
            left: 50%;
            transform: translateX(-50%);
            background: var(--nav-bg);
            border: 1px solid var(--nav-border);
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            font-size: 0.75rem;
            white-space: nowrap;
            z-index: 1002;
            opacity: 0;
            transition: opacity 0.2s ease;
            pointer-events: none;
        `;

        button.style.position = 'relative';
        button.appendChild(feedback);

        // Animate in
        setTimeout(() => feedback.style.opacity = '1', 10);

        // Remove after delay
        setTimeout(() => {
            feedback.style.opacity = '0';
            setTimeout(() => feedback.remove(), 200);
        }, 2000);
    }

    setupActivePageHighlighting() {
        // Highlight current page in navigation
        this.navLinks.forEach(link => {
            const href = link.getAttribute('href');

            // Special handling for settings pages
            if (href && href.includes('settings') && this.currentPath.includes('settings')) {
                link.classList.add('active');
                this.moveUnderline(link, false);
                return;
            }

            // Regular page highlighting
            if (href && this.currentPath.includes(href) && href !== '/') {
                link.classList.add('active');
                this.moveUnderline(link, false);
            } else if (href === '/' && this.currentPath === '/') {
                link.classList.add('active');
                this.moveUnderline(link, false);
            }
        });
    }

    // Enhanced dropdown theme toggle
    setupDropdownThemeToggle() {
        const dropdownThemeSwitch = document.getElementById('dropdownThemeSwitch');
        const dropdownThemeIcon = document.getElementById('dropdownThemeIcon');
        const dropdownThemeText = document.getElementById('dropdownThemeText');

        if (dropdownThemeSwitch && dropdownThemeIcon && dropdownThemeText) {
            // Set initial state
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            dropdownThemeSwitch.checked = currentTheme === 'dark';
            this.updateDropdownThemeDisplay(currentTheme, dropdownThemeIcon, dropdownThemeText);

            // Add event listener
            dropdownThemeSwitch.addEventListener('change', () => {
                const newTheme = dropdownThemeSwitch.checked ? 'dark' : 'light';
                this.applyTheme(newTheme);
                this.updateDropdownThemeDisplay(newTheme, dropdownThemeIcon, dropdownThemeText);
            });
        }
    }

    updateDropdownThemeDisplay(theme, icon, text) {
        if (theme === 'dark') {
            icon.className = 'bi bi-sun-fill';
            text.textContent = 'Light Mode';
        } else {
            icon.className = 'bi bi-moon-fill';
            text.textContent = 'Dark Mode';
        }
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);

        // Update main theme toggle if it exists
        const mainThemeToggle = document.getElementById('themeToggle');
        const mainThemeIcon = document.getElementById('themeIcon');
        if (mainThemeToggle && mainThemeIcon) {
            mainThemeIcon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
        }

        // Update quick theme toggle if it exists
        const quickThemeToggle = document.getElementById('quickThemeToggle');
        const quickThemeIcon = document.getElementById('quickThemeIcon');
        if (quickThemeToggle && quickThemeIcon) {
            quickThemeIcon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
        }
    }

    setupFloatingLogout() {
        const floatingLogout = document.getElementById('floatingLogout');
        if (!floatingLogout) return;

        let scrollTimeout;
        let isVisible = false;

        // Show/hide floating logout based on scroll
        window.addEventListener('scroll', () => {
            const scrollY = window.scrollY;
            const shouldShow = scrollY > 300; // Show after scrolling 300px

            if (shouldShow && !isVisible) {
                floatingLogout.classList.add('show');
                isVisible = true;
            } else if (!shouldShow && isVisible) {
                floatingLogout.classList.remove('show');
                isVisible = false;
            }

            // Auto-hide after 3 seconds of no scrolling
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                if (isVisible && scrollY > 300) {
                    floatingLogout.classList.remove('show');
                    isVisible = false;
                }
            }, 3000);
        });

        // Show on mouse movement near bottom-right corner
        document.addEventListener('mousemove', (e) => {
            const windowWidth = window.innerWidth;
            const windowHeight = window.innerHeight;
            const mouseX = e.clientX;
            const mouseY = e.clientY;

            // Show if mouse is in bottom-right 200x200px area
            const isInCorner = mouseX > windowWidth - 200 && mouseY > windowHeight - 200;

            if (isInCorner && window.scrollY > 100 && !isVisible) {
                floatingLogout.classList.add('show');
                isVisible = true;

                // Auto-hide after 2 seconds
                setTimeout(() => {
                    if (isVisible) {
                        floatingLogout.classList.remove('show');
                        isVisible = false;
                    }
                }, 2000);
            }
        });

        // Hide when clicking elsewhere
        document.addEventListener('click', (e) => {
            if (!floatingLogout.contains(e.target) && isVisible) {
                floatingLogout.classList.remove('show');
                isVisible = false;
            }
        });
    }
    
    setupScrollEffect() {
        let lastScrollY = window.scrollY;
        
        window.addEventListener('scroll', () => {
            const currentScrollY = window.scrollY;
            
            // Add/remove scrolled class for styling
            if (currentScrollY > 50) {
                this.navbar.classList.add('scrolled');
            } else {
                this.navbar.classList.remove('scrolled');
            }
            
            // Hide navbar on scroll down, show on scroll up
            if (currentScrollY > lastScrollY && currentScrollY > 100) {
                this.navbar.style.transform = 'translateY(-100%)';
            } else {
                this.navbar.style.transform = 'translateY(0)';
            }
            
            lastScrollY = currentScrollY;
        });
    }
    
    // Public methods for external use
    highlightTab(href) {
        const link = this.navList.querySelector(`[href="${href}"]`);
        if (link) {
            this.setActiveLink(link);
        }
    }
    
    updateUnderline() {
        const activeLink = this.navList.querySelector('.nav-link.active');
        if (activeLink) {
            // Delay to ensure layout is complete
            setTimeout(() => {
                this.moveUnderline(activeLink, false);
            }, 100);
        }
    }
    
    setupSettingsNavigation() {
        const settingsLink = document.querySelector('.nav-link[href*="settings"]');
        if (!settingsLink) return;

        // Add special hover effects for settings button
        settingsLink.addEventListener('mouseenter', () => {
            const icon = settingsLink.querySelector('.nav-icon');
            if (icon) {
                icon.style.transform = 'rotate(90deg) scale(1.1)';
                icon.style.filter = 'drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3))';
            }
        });

        settingsLink.addEventListener('mouseleave', () => {
            const icon = settingsLink.querySelector('.nav-icon');
            if (icon && !settingsLink.classList.contains('active')) {
                icon.style.transform = '';
                icon.style.filter = '';
            }
        });

        // Add click analytics and visual feedback
        settingsLink.addEventListener('click', () => {
            console.log('🔧 Settings navigation clicked');

            // Add temporary visual feedback
            const icon = settingsLink.querySelector('.nav-icon');
            if (icon) {
                icon.style.transform = 'rotate(180deg) scale(0.9)';
                setTimeout(() => {
                    icon.style.transform = 'rotate(90deg) scale(1.1)';
                }, 150);
            }
        });

        // Handle keyboard navigation
        settingsLink.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                settingsLink.click();
            }
        });

        // Add notification badge functionality (for future use)
        this.setupSettingsNotifications(settingsLink);
    }

    setupSettingsNotifications(settingsLink) {
        // Check for settings updates or notifications
        const checkForUpdates = () => {
            // This could be connected to an API endpoint in the future
            const hasUpdates = localStorage.getItem('settings-has-updates') === 'true';

            if (hasUpdates) {
                settingsLink.classList.add('has-updates');

                // Create notification badge if it doesn't exist
                if (!settingsLink.querySelector('.notification-badge')) {
                    const badge = document.createElement('span');
                    badge.className = 'notification-badge';
                    settingsLink.appendChild(badge);
                }
            } else {
                settingsLink.classList.remove('has-updates');
                const badge = settingsLink.querySelector('.notification-badge');
                if (badge) {
                    badge.remove();
                }
            }
        };

        // Check on initialization
        checkForUpdates();

        // Check periodically (every 5 minutes)
        setInterval(checkForUpdates, 300000);

        // Listen for storage changes
        window.addEventListener('storage', (e) => {
            if (e.key === 'settings-has-updates') {
                checkForUpdates();
            }
        });
    }

    destroy() {
        // Clean up event listeners if needed
        this.navLinks.forEach(link => {
            link.replaceWith(link.cloneNode(true));
        });

        if (this.mobileToggle) {
            this.mobileToggle.replaceWith(this.mobileToggle.cloneNode(true));
        }
    }
}

// Utility functions for smooth interactions
const SmoothNavUtils = {
    // Smooth scroll to section
    scrollToSection(targetId) {
        const target = document.getElementById(targetId);
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    },
    
    // Add loading state to nav link
    setLoadingState(link, isLoading = true) {
        if (isLoading) {
            link.classList.add('loading');
            link.style.pointerEvents = 'none';
        } else {
            link.classList.remove('loading');
            link.style.pointerEvents = 'auto';
        }
    },
    
    // Update badge count with animation
    updateBadgeCount(badgeElement, newCount) {
        if (!badgeElement) return;
        
        badgeElement.style.transform = 'scale(1.2)';
        setTimeout(() => {
            badgeElement.textContent = newCount;
            badgeElement.style.transform = 'scale(1)';
        }, 150);
    },
    
    // Show notification in navbar
    showNavNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `nav-notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 1rem;
            background: var(--nav-bg);
            border: 1px solid var(--nav-border);
            border-radius: var(--nav-radius);
            padding: 0.75rem 1rem;
            box-shadow: var(--nav-shadow);
            z-index: 1002;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after delay
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.smoothNavbar = new SmoothNavbar();
});

// Handle window resize
window.addEventListener('resize', () => {
    if (window.smoothNavbar) {
        window.smoothNavbar.updateUnderline();
    }
});

// Export for global use
window.SmoothNavUtils = SmoothNavUtils;

// Global function for dropdown theme toggle
function toggleThemeFromDropdown() {
    if (window.smoothNavbar) {
        const dropdownThemeSwitch = document.getElementById('dropdownThemeSwitch');
        if (dropdownThemeSwitch) {
            dropdownThemeSwitch.checked = !dropdownThemeSwitch.checked;
            dropdownThemeSwitch.dispatchEvent(new Event('change'));
        }
    }
}
