/**
 * Optimized JavaScript for Smart Grocery Tracker
 * Lightweight and performance-focused
 */

// Debounce function for performance
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

// Optimized CSRF token function
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) return token.value;
    
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) return metaToken.getAttribute('content');
    
    return '';
}

// Lightweight notification system
function showNotification(message, type = 'info', duration = 3000) {
    const container = document.getElementById('notification-container') || createNotificationContainer();
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.cssText = 'margin-bottom: 0.5rem; animation: slideInRight 0.3s ease;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, duration);
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        max-width: 350px;
    `;
    document.body.appendChild(container);
    return container;
}

// Optimized quick edit function
function quickEdit(itemId, itemName, currentQuantity) {
    const newQuantity = prompt(`Update quantity for "${itemName}":`, currentQuantity);
    
    if (newQuantity !== null && newQuantity !== '' && !isNaN(newQuantity)) {
        fetch(`/api/quick-edit/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ quantity: parseInt(newQuantity) })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => location.reload(), 1000);
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

// Optimized mark as purchased function
function markAsPurchased(itemId, itemName) {
    if (confirm(`Mark "${itemName}" as purchased?`)) {
        fetch(`/api/mark-purchased/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => location.reload(), 1000);
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

// Optimized quick delete function
function quickDelete(itemId, itemName) {
    if (confirm(`Are you sure you want to delete "${itemName}"?`)) {
        fetch(`/api/quick-delete/${itemId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => location.reload(), 1000);
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

// Optimized search function
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
}, 800);

// Optimized bulk operations
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
    const selectedItems = Array.from(document.querySelectorAll('input[data-item-id]:checked'))
        .map(cb => cb.dataset.itemId);
    
    if (selectedItems.length === 0) {
        showNotification('No items selected', 'warning');
        return;
    }
    
    if (confirm(`Mark ${selectedItems.length} items as purchased?`)) {
        fetch('/api/bulk-actions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                action: 'mark_purchased',
                item_ids: selectedItems
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => location.reload(), 1000);
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
    const selectedItems = Array.from(document.querySelectorAll('input[data-item-id]:checked'))
        .map(cb => cb.dataset.itemId);
    
    if (selectedItems.length === 0) {
        showNotification('No items selected', 'warning');
        return;
    }
    
    if (confirm(`Delete ${selectedItems.length} items permanently?`)) {
        fetch('/api/bulk-actions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                action: 'delete',
                item_ids: selectedItems
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => location.reload(), 1000);
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

function clearSelection() {
    document.querySelectorAll('input[data-item-id]:checked').forEach(cb => {
        cb.checked = false;
    });
    updateBulkActionButtons();
}

// Initialize optimized features
document.addEventListener('DOMContentLoaded', function() {
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
    
    // Initialize category filter
    const categorySelect = document.getElementById('category');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            const url = new URL(window.location);
            if (this.value) {
                url.searchParams.set('category', this.value);
            } else {
                url.searchParams.delete('category');
            }
            window.location.href = url.toString();
        });
    }
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    console.log('✅ Optimized app initialized');
});

// Export functions for global use
window.quickEdit = quickEdit;
window.markAsPurchased = markAsPurchased;
window.quickDelete = quickDelete;
window.toggleItemSelection = toggleItemSelection;
window.bulkMarkPurchased = bulkMarkPurchased;
window.bulkDelete = bulkDelete;
window.clearSelection = clearSelection;
window.showNotification = showNotification;
window.getCsrfToken = getCsrfToken;
