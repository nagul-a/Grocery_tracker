// Smart Grocery Tracker Enhanced JavaScript

// Global variables
let currentTheme = localStorage.getItem('theme') || 'light';


// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize theme
    initializeTheme();

    // Initialize tooltips and popovers
    initializeBootstrapComponents();

    // Initialize search functionality
    initializeSearch();



    // Initialize interactive elements
    initializeInteractiveElements();

    // Initialize form validation
    initializeFormValidation();

    // Initialize charts
    initializeCharts();

    // Initialize notifications
    initializeNotifications();
}

// Theme Management
function initializeTheme() {
    // Apply saved theme
    document.documentElement.setAttribute('data-theme', currentTheme);

    // Create theme toggle button
    createThemeToggle();

    // Update theme toggle icon
    updateThemeToggleIcon();
}

function createThemeToggle() {
    // Check if theme toggle already exists
    if (document.querySelector('.theme-toggle')) return;

    const themeToggle = document.createElement('button');
    themeToggle.className = 'theme-toggle';
    themeToggle.setAttribute('aria-label', 'Toggle theme');
    themeToggle.setAttribute('title', 'Toggle dark/light mode');
    themeToggle.innerHTML = '<i class="bi bi-sun-fill"></i>';

    themeToggle.addEventListener('click', toggleTheme);

    document.body.appendChild(themeToggle);
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    updateThemeToggleIcon();

    // Add smooth transition effect
    document.body.style.transition = 'all 0.3s ease';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 300);

    // Show notification
    showNotification(`Switched to ${currentTheme} mode`, 'info');
}

function updateThemeToggleIcon() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (currentTheme === 'dark') {
            icon.className = 'bi bi-moon-fill';
        } else {
            icon.className = 'bi bi-sun-fill';
        }
    }
}

// Bootstrap Components
function initializeBootstrapComponents() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}





// Utility Functions
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 80px;
        right: 20px;
        z-index: 1060;
        min-width: 300px;
        max-width: 400px;
    `;

    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            const alert = new bootstrap.Alert(notification);
            alert.close();
        }
    }, 5000);
}

// Enhanced Search
function initializeSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 2 || this.value.length === 0) {
                    performSearch(this.value);
                }
            }, 300);
        });
    }
}

function performSearch(query) {
    console.log('Searching for:', query);

    if (query) {
        const url = new URL(window.location);
        url.searchParams.set('search', query);
        window.history.pushState({}, '', url);
        // Optionally reload or update content via AJAX
    }
}

// Interactive Elements
function initializeInteractiveElements() {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add click animations to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            `;

            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');

    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        });
    });
}

// Charts (placeholder)
function initializeCharts() {
    // Charts will be initialized by individual page scripts
    console.log('Charts initialization ready');
}

// Notifications
function initializeNotifications() {
    // Auto-hide existing alerts
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            if (alert.parentNode) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 5000);
}

// Add CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }


`;
document.head.appendChild(style);

// Export enhanced functions
window.GroceryTrackerEnhanced = {
    toggleTheme,
    showNotification,
    initializeApp
};
