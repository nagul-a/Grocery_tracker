// Smart Grocery Tracker JavaScript

document.addEventListener('DOMContentLoaded', function() {
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

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Search functionality
    initializeSearch();



    // Analytics charts
    initializeCharts();

    // Form validation
    initializeFormValidation();
});

// Search functionality
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
    // This would typically make an AJAX request to search endpoint
    console.log('Searching for:', query);

    // For now, we'll just update the URL and reload
    if (query) {
        const url = new URL(window.location);
        url.searchParams.set('search', query);
        window.history.pushState({}, '', url);
    }
}



// Charts initialization
function initializeCharts() {
    // Category distribution chart
    const categoryChartCanvas = document.getElementById('categoryChart');
    if (categoryChartCanvas) {
        createCategoryChart(categoryChartCanvas);
    }

    // Spending trend chart
    const spendingChartCanvas = document.getElementById('spendingChart');
    if (spendingChartCanvas) {
        createSpendingChart(spendingChartCanvas);
    }

    // Expiry timeline chart
    const expiryChartCanvas = document.getElementById('expiryChart');
    if (expiryChartCanvas) {
        createExpiryChart(expiryChartCanvas);
    }
}

function createCategoryChart(canvas) {
    // This would typically get data from the backend
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Fruits & Vegetables', 'Dairy & Eggs', 'Meat & Seafood', 'Pantry Staples', 'Other'],
            datasets: [{
                data: [30, 20, 15, 25, 10],
                backgroundColor: [
                    '#198754',
                    '#ffc107',
                    '#dc3545',
                    '#0dcaf0',
                    '#6c757d'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function createSpendingChart(canvas) {
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [{
                label: 'Weekly Spending',
                data: [120, 150, 100, 180],
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value;
                        }
                    }
                }
            }
        }
    });
}

function createExpiryChart(canvas) {
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Today', 'Tomorrow', 'This Week', 'Next Week', 'Later'],
            datasets: [{
                label: 'Items Expiring',
                data: [2, 3, 8, 12, 25],
                backgroundColor: [
                    '#dc3545',
                    '#fd7e14',
                    '#ffc107',
                    '#20c997',
                    '#198754'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Form validation
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

// Utility functions
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertContainer, container.firstChild);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        const alert = new bootstrap.Alert(alertContainer);
        alert.close();
    }, 5000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function calculateDaysUntilExpiry(expiryDate) {
    const today = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

// API helper functions
function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    };

    return fetch(endpoint, { ...defaultOptions, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Export functions for use in other scripts
window.GroceryTracker = {
    showAlert,
    formatCurrency,
    formatDate,
    calculateDaysUntilExpiry,
    apiCall,

};
