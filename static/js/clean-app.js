/**
 * Clean JavaScript for Smart Grocery Tracker
 * Error-free, optimized, and user-friendly
 */

// ===== GLOBAL VARIABLES =====
let currentTheme = localStorage.getItem('theme') || 'light';

// ===== UTILITY FUNCTIONS =====
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) return token.value;
    
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) return metaToken.getAttribute('content');
    
    return '';
}

// ===== NOTIFICATION SYSTEM =====
function showNotification(message, type = 'info', duration = 4000) {
    const container = getNotificationContainer();
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible animate-fadeIn`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="alert-close" onclick="this.parentElement.remove()">
            <i class="bi bi-x"></i>
        </button>
    `;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }
    }, duration);
}

function getNotificationContainer() {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed top-0 right-0 z-50 p-4';
        container.style.cssText = `
            position: fixed;
            top: 100px;
            right: 1rem;
            z-index: 1000;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
    return container;
}

// ===== THEME MANAGEMENT =====
function initializeTheme() {
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon();
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    updateThemeIcon();
    showNotification(`Switched to ${currentTheme} mode`, 'info', 2000);
}

function updateThemeIcon() {
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.className = currentTheme === 'light' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
    }
}

// ===== MODERN NAVIGATION =====
function toggleMobileNav() {
    const navTabs = document.getElementById('mainNavTabs');
    if (navTabs) {
        navTabs.classList.toggle('show');
    }
}

function toggleNavDropdown(element, event) {
    event.preventDefault();
    event.stopPropagation();

    const dropdown = element.parentElement;
    const dropdownMenu = dropdown.querySelector('.nav-dropdown-menu');
    const allDropdownMenus = document.querySelectorAll('.nav-dropdown-menu');
    const allDropdowns = document.querySelectorAll('.nav-dropdown');

    // Close all other dropdown menus
    allDropdownMenus.forEach(menu => {
        if (menu !== dropdownMenu) {
            menu.classList.remove('show');
        }
    });

    // Remove active class from all dropdowns
    allDropdowns.forEach(dd => {
        if (dd !== dropdown) {
            dd.classList.remove('active');
        }
    });

    // Toggle current dropdown menu
    if (dropdownMenu) {
        dropdownMenu.classList.toggle('show');
        dropdown.classList.toggle('active');
    }
}

function toggleMegaMenu(element) {
    const dropdown = element.parentElement;
    const megaMenu = dropdown.querySelector('.mega-menu');
    const allMegaMenus = document.querySelectorAll('.mega-menu');
    const allDropdowns = document.querySelectorAll('.nav-tab-dropdown');

    // Close all other mega menus
    allMegaMenus.forEach(menu => {
        if (menu !== megaMenu) {
            menu.classList.remove('show');
        }
    });

    // Remove active class from all dropdowns
    allDropdowns.forEach(dd => {
        if (dd !== dropdown) {
            dd.classList.remove('active');
        }
    });

    // Toggle current mega menu
    if (megaMenu) {
        megaMenu.classList.toggle('show');
        dropdown.classList.toggle('active');
    }
}

// Close all dropdowns when clicking outside
document.addEventListener('click', function(e) {
    if (!e.target.closest('.nav-dropdown') && !e.target.closest('.nav-tab-dropdown')) {
        // Close navigation dropdowns
        document.querySelectorAll('.nav-dropdown-menu.show').forEach(menu => {
            menu.classList.remove('show');
        });
        document.querySelectorAll('.nav-dropdown.active').forEach(dropdown => {
            dropdown.classList.remove('active');
        });

        // Close mega menus
        document.querySelectorAll('.mega-menu.show').forEach(menu => {
            menu.classList.remove('show');
        });
        document.querySelectorAll('.nav-tab-dropdown.active').forEach(dropdown => {
            dropdown.classList.remove('active');
        });
    }
});

// Handle active tab highlighting
function setActiveTab() {
    const currentPath = window.location.pathname;
    const navTabs = document.querySelectorAll('.nav-tab');

    navTabs.forEach(tab => {
        tab.classList.remove('active');
        const href = tab.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '#') {
            tab.classList.add('active');
        }
    });

    // Set home as active if on root path
    if (currentPath === '/' || currentPath === '/home/') {
        const homeTab = document.querySelector('.nav-tab[href*="home"]');
        if (homeTab) {
            homeTab.classList.add('active');
        }
    }
}

// ===== GROCERY ITEM FUNCTIONS =====
function quickEdit(itemId, itemName, currentQuantity) {
    const newQuantity = prompt(`Update quantity for "${itemName}":`, currentQuantity);
    
    if (newQuantity !== null && newQuantity !== '' && !isNaN(newQuantity)) {
        const quantity = parseInt(newQuantity);
        if (quantity < 0) {
            showNotification('Quantity cannot be negative', 'danger');
            return;
        }
        
        makeApiCall(`/api/quick-edit/${itemId}/`, 'POST', { quantity })
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification(data.error || 'Failed to update item', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error updating item', 'danger');
            });
    }
}

function markAsPurchased(itemId, itemName) {
    if (confirm(`Mark "${itemName}" as purchased?`)) {
        makeApiCall(`/api/mark-purchased/${itemId}/`, 'POST')
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification(data.error || 'Failed to mark as purchased', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error marking item as purchased', 'danger');
            });
    }
}

function quickDelete(itemId, itemName) {
    if (confirm(`Are you sure you want to delete "${itemName}"?`)) {
        makeApiCall(`/api/quick-delete/${itemId}/`, 'DELETE')
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification(data.error || 'Failed to delete item', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error deleting item', 'danger');
            });
    }
}

function addToShoppingList(itemId, itemName) {
    makeApiCall(`/api/add-to-shopping-list/${itemId}/`, 'POST')
        .then(data => {
            if (data.success) {
                showNotification(`Added "${itemName}" to shopping list`, 'success');
            } else {
                showNotification(data.error || 'Failed to add to shopping list', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error adding to shopping list', 'danger');
        });
}

// ===== API HELPER =====
async function makeApiCall(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    return await response.json();
}

// ===== SEARCH FUNCTIONALITY =====
const performSearch = debounce(function(query) {
    if (query.length >= 3) {
        const url = new URL(window.location);
        url.searchParams.set('search', query);
        window.location.href = url.toString();
    } else if (query.length === 0) {
        const url = new URL(window.location);
        url.searchParams.delete('search');
        window.location.href = url.toString();
    }
}, 1000);

// ===== FORM VALIDATION =====
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('border-danger');
            isValid = false;
        } else {
            field.classList.remove('border-danger');
        }
    });
    
    return isValid;
}

// ===== BULK OPERATIONS =====
function toggleItemSelection(itemId) {
    const checkbox = document.querySelector(`input[data-item-id="${itemId}"]`);
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
        updateBulkActionButtons();
    }
}

function updateBulkActionButtons() {
    const selectedItems = document.querySelectorAll('input[data-item-id]:checked');
    const bulkActions = document.getElementById('bulk-actions');
    
    if (bulkActions) {
        bulkActions.style.display = selectedItems.length > 0 ? 'block' : 'none';
    }
}

function bulkMarkPurchased() {
    const selectedItems = getSelectedItems();
    if (selectedItems.length === 0) {
        showNotification('No items selected', 'warning');
        return;
    }
    
    if (confirm(`Mark ${selectedItems.length} items as purchased?`)) {
        makeApiCall('/api/bulk-actions/', 'POST', {
            action: 'mark_purchased',
            item_ids: selectedItems
        })
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showNotification('Failed to mark items as purchased', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error performing bulk action', 'danger');
        });
    }
}

function bulkDelete() {
    const selectedItems = getSelectedItems();
    if (selectedItems.length === 0) {
        showNotification('No items selected', 'warning');
        return;
    }
    
    if (confirm(`Delete ${selectedItems.length} items permanently?`)) {
        makeApiCall('/api/bulk-actions/', 'POST', {
            action: 'delete',
            item_ids: selectedItems
        })
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showNotification('Failed to delete items', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error performing bulk action', 'danger');
        });
    }
}

function getSelectedItems() {
    return Array.from(document.querySelectorAll('input[data-item-id]:checked'))
        .map(cb => cb.dataset.itemId);
}

function clearSelection() {
    document.querySelectorAll('input[data-item-id]:checked').forEach(cb => {
        cb.checked = false;
    });
    updateBulkActionButtons();
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    initializeTheme();

    // Initialize theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }

    // Initialize navigation
    setActiveTab();

    // Initialize search
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            performSearch(this.value.trim());
        });
    }

    // Initialize bulk selection
    document.querySelectorAll('input[data-item-id]').forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActionButtons);
    });

    // Initialize form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'danger');
            }
        });
    });

    // Close mobile nav when clicking nav links
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const navTabs = document.getElementById('mainNavTabs');
            if (navTabs && navTabs.classList.contains('show')) {
                navTabs.classList.remove('show');
            }
        });
    });

    console.log('✅ Clean app with modern navigation initialized successfully');
});

// ===== GLOBAL EXPORTS =====
window.quickEdit = quickEdit;
window.markAsPurchased = markAsPurchased;
window.quickDelete = quickDelete;
window.addToShoppingList = addToShoppingList;
window.toggleItemSelection = toggleItemSelection;
window.bulkMarkPurchased = bulkMarkPurchased;
window.bulkDelete = bulkDelete;
window.clearSelection = clearSelection;
window.showNotification = showNotification;
window.toggleMobileNav = toggleMobileNav;
window.toggleNavDropdown = toggleNavDropdown;
window.toggleMegaMenu = toggleMegaMenu;
window.setActiveTab = setActiveTab;
window.toggleTheme = toggleTheme;
