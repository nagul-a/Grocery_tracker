/**
 * Working Mode JavaScript for Smart Grocery Tracker
 * Ensures all functionality works properly
 */

// Global configuration
const WORKING_MODE = {
    debug: true,
    apiBaseUrl: '/api/',
    notifications: true,
    autoRefresh: true
};

// Initialize working mode
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Smart Grocery Tracker - Working Mode Initialized');
    
    // Initialize all working mode features
    initializeWorkingMode();
    
    // Add global error handling
    setupGlobalErrorHandling();
    
    // Initialize real-time features
    initializeRealTimeFeatures();
    
    // Setup periodic health checks
    setupHealthChecks();
});

function initializeWorkingMode() {
    // Ensure all critical functions are available
    ensureCriticalFunctions();
    
    // Initialize enhanced search
    initializeEnhancedSearch();
    
    // Initialize notifications system
    initializeNotificationSystem();
    
    // Initialize data validation
    initializeDataValidation();
    
    // Initialize performance monitoring
    initializePerformanceMonitoring();
}

function ensureCriticalFunctions() {
    // List of critical functions that must be available
    const criticalFunctions = [
        'getCsrfToken',
        'showNotification',
        'quickEdit',
        'markAsPurchased',
        'quickDelete',
        'addToShoppingList'
    ];
    
    criticalFunctions.forEach(funcName => {
        if (typeof window[funcName] !== 'function') {
            console.warn(`⚠️ Critical function missing: ${funcName}`);
            // Create placeholder function
            window[funcName] = function() {
                console.error(`Function ${funcName} not implemented`);
                showNotification(`Feature ${funcName} is not available`, 'error');
            };
        }
    });
}

function initializeEnhancedSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[name="search"]');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 3) {
                searchTimeout = setTimeout(() => {
                    performEnhancedSearch(query);
                }, 500);
            } else if (query.length === 0) {
                // Clear search results
                clearSearchResults();
            }
        });
    });
}

function performEnhancedSearch(query) {
    if (WORKING_MODE.debug) {
        console.log(`🔍 Performing search for: ${query}`);
    }
    
    fetch(`${WORKING_MODE.apiBaseUrl}search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displaySearchResults(data.items, query);
            } else {
                console.error('Search failed:', data.error);
            }
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function displaySearchResults(items, query) {
    // Update the items container with search results
    const container = document.getElementById('items-container');
    if (!container) return;
    
    if (items.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="bi bi-search display-1 text-muted"></i>
                    <h3 class="mt-3">No items found</h3>
                    <p class="text-muted">No items match "${query}". Try different keywords.</p>
                    <button class="btn btn-primary" onclick="clearSearchResults()">
                        <i class="bi bi-arrow-left me-1"></i>Show All Items
                    </button>
                </div>
            </div>
        `;
    } else {
        // Display search results
        let html = '';
        items.forEach(item => {
            html += createItemCard(item);
        });
        container.innerHTML = html;
        
        // Show search info
        showSearchInfo(items.length, query);
    }
}

function clearSearchResults() {
    // Reload the page to show all items
    window.location.href = window.location.pathname;
}

function showSearchInfo(count, query) {
    // Create or update search info banner
    let searchInfo = document.getElementById('search-info');
    if (!searchInfo) {
        searchInfo = document.createElement('div');
        searchInfo.id = 'search-info';
        searchInfo.className = 'alert alert-info d-flex justify-content-between align-items-center mb-3';
        
        const container = document.getElementById('items-container');
        if (container && container.parentNode) {
            container.parentNode.insertBefore(searchInfo, container);
        }
    }
    
    searchInfo.innerHTML = `
        <div>
            <i class="bi bi-search me-2"></i>
            Found ${count} item${count !== 1 ? 's' : ''} for "${query}"
        </div>
        <button class="btn btn-sm btn-outline-primary" onclick="clearSearchResults()">
            <i class="bi bi-x me-1"></i>Clear Search
        </button>
    `;
}

function createItemCard(item) {
    // Create HTML for an item card
    const expiryDate = item.expiry_date ? new Date(item.expiry_date).toLocaleDateString() : 'No expiry';
    const price = item.price ? `₹${item.price}` : 'No price';
    
    return `
        <div class="col-lg-4 col-md-6 mb-4">
            <div class="card grocery-item-card-enhanced h-100">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="card-title mb-0">${item.name}</h5>
                        <span class="badge bg-primary">${item.category}</span>
                    </div>
                    <div class="item-details mb-3">
                        <div class="detail-item">
                            <i class="bi bi-box me-1"></i>
                            <span>${item.quantity} ${item.unit}</span>
                        </div>
                        <div class="detail-item">
                            <i class="bi bi-currency-rupee me-1"></i>
                            <span>${price}</span>
                        </div>
                        <div class="detail-item">
                            <i class="bi bi-calendar me-1"></i>
                            <span>${expiryDate}</span>
                        </div>
                    </div>
                    <div class="item-actions d-flex gap-1">
                        <button class="btn btn-sm btn-outline-primary" 
                                onclick="quickEdit('${item.id}', '${item.name}', ${item.quantity})"
                                title="Quick Edit">
                            <i class="bi bi-lightning-fill"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" 
                                onclick="markAsPurchased('${item.id}', '${item.name}')"
                                title="Mark Purchased">
                            <i class="bi bi-check-circle-fill"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="quickDelete('${item.id}', '${item.name}')"
                                title="Delete">
                            <i class="bi bi-trash-fill"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function initializeNotificationSystem() {
    // Create notification container if it doesn't exist
    if (!document.getElementById('notification-container')) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
    
    // Load notifications once on page load (removed interval for performance)
    if (WORKING_MODE.notifications) {
        loadNotifications();
    }
}

function loadNotifications() {
    fetch(`${WORKING_MODE.apiBaseUrl}notifications/`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.notifications.length > 0) {
                displayNotifications(data.notifications);
            }
        })
        .catch(error => {
            if (WORKING_MODE.debug) {
                console.error('Error loading notifications:', error);
            }
        });
}

function displayNotifications(notifications) {
    notifications.forEach(notification => {
        showNotification(notification.message, notification.type, 10000);
    });
}

function initializeDataValidation() {
    // Add validation to all forms
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showNotification('Please fill in all required fields correctly', 'error');
            }
        });
    });
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

function initializePerformanceMonitoring() {
    // Monitor page performance
    if (performance && performance.timing) {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        if (WORKING_MODE.debug) {
            console.log(`📊 Page load time: ${loadTime}ms`);
        }
    }
}

function setupGlobalErrorHandling() {
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        if (WORKING_MODE.debug) {
            showNotification('An error occurred. Check console for details.', 'error');
        }
    });
    
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        if (WORKING_MODE.debug) {
            showNotification('A network error occurred.', 'error');
        }
    });
}

function initializeRealTimeFeatures() {
    // Removed auto-refresh for better performance
    // Data will refresh on user actions instead
}

function refreshPageData() {
    // Refresh dashboard stats if on dashboard page
    if (window.location.pathname.includes('dashboard')) {
        refreshDashboardStats();
    }
}

function refreshDashboardStats() {
    fetch(`${WORKING_MODE.apiBaseUrl}analytics/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateDashboardStats(data);
            }
        })
        .catch(error => {
            if (WORKING_MODE.debug) {
                console.error('Error refreshing dashboard:', error);
            }
        });
}

function updateDashboardStats(data) {
    // Update dashboard statistics
    const totalItemsElement = document.querySelector('[data-stat="total-items"]');
    if (totalItemsElement) {
        totalItemsElement.textContent = data.total_items;
    }
    
    const expiringItemsElement = document.querySelector('[data-stat="expiring-items"]');
    if (expiringItemsElement) {
        expiringItemsElement.textContent = data.expiring_week;
    }
}

function setupHealthChecks() {
    // Removed periodic health checks for better performance
    // Health check will run on user actions instead
}

function performHealthCheck() {
    fetch(`${WORKING_MODE.apiBaseUrl}analytics/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Health check failed');
            }
            return response.json();
        })
        .then(data => {
            if (WORKING_MODE.debug) {
                console.log('✅ Health check passed');
            }
        })
        .catch(error => {
            console.error('❌ Health check failed:', error);
            if (WORKING_MODE.notifications) {
                showNotification('Connection issues detected', 'warning');
            }
        });
}

// Export functions for global use
window.WORKING_MODE = WORKING_MODE;
window.performEnhancedSearch = performEnhancedSearch;
window.clearSearchResults = clearSearchResults;
window.loadNotifications = loadNotifications;
