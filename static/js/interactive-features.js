/**
 * Interactive Features for Smart Grocery Tracker
 * Makes all buttons and features fully functional
 */

class GroceryTracker {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        this.setupRealTimeSearch();
        this.setupNotifications();
    }

    init() {
        console.log('🚀 Smart Grocery Tracker initialized');
        this.csrfToken = this.getCsrfToken();
        this.setupTooltips();
        this.setupModals();
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }

    setupEventListeners() {
        // Quick Edit functionality
        document.addEventListener('click', (e) => {
            if (e.target.closest('.quick-edit-btn')) {
                this.handleQuickEdit(e);
            }

            if (e.target.closest('.quick-delete-btn')) {
                this.handleQuickDelete(e);
            }

            if (e.target.closest('.add-to-shopping-list-btn')) {
                this.handleAddToShoppingList(e);
            }

            if (e.target.closest('.mark-purchased-btn')) {
                this.handleMarkPurchased(e);
            }
        });

        // Bulk operations
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('item-checkbox')) {
                this.updateBulkActions();
            }
        });

        // Filter changes
        document.addEventListener('change', (e) => {
            if (e.target.id === 'category' || e.target.id === 'expiring') {
                this.handleFilterChange();
            }
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {


            // Ctrl+N for new item
            if (e.ctrlKey && e.key === 'n') {
                e.preventDefault();
                window.location.href = '/add/';
            }

            // Escape to close modals
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    setupRealTimeSearch() {
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });
        }
    }

    setupNotifications() {
        // Check for expiring items
        this.checkExpiringItems();

        // Check for low stock
        this.checkLowStock();
    }

    setupTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    setupModals() {
        // Initialize modals
        this.quickEditModal = new bootstrap.Modal(document.getElementById('quickEditModal') || this.createQuickEditModal());
        this.bulkActionsModal = new bootstrap.Modal(document.getElementById('bulkActionsModal') || this.createBulkActionsModal());
    }

    // Quick Edit functionality
    handleQuickEdit(e) {
        const button = e.target.closest('.quick-edit-btn');
        const itemId = button.dataset.itemId;
        const itemName = button.dataset.itemName;
        const currentQuantity = button.dataset.quantity;

        this.showQuickEditModal(itemId, itemName, currentQuantity);
    }

    showQuickEditModal(itemId, itemName, currentQuantity) {
        const modal = document.getElementById('quickEditModal');
        if (!modal) {
            this.createQuickEditModal();
        }

        document.getElementById('quickEditItemName').textContent = itemName;
        document.getElementById('quickEditQuantity').value = currentQuantity;
        document.getElementById('quickEditForm').dataset.itemId = itemId;

        this.quickEditModal.show();
    }

    createQuickEditModal() {
        const modalHtml = `
            <div class="modal fade" id="quickEditModal" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content" style="border-radius: 20px;">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-lightning-fill me-2"></i>Quick Edit
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="quickEditForm">
                                <div class="mb-3">
                                    <label class="form-label fw-bold">Item:</label>
                                    <p id="quickEditItemName" class="text-primary"></p>
                                </div>
                                <div class="mb-3">
                                    <label for="quickEditQuantity" class="form-label">Quantity:</label>
                                    <input type="number" class="form-control" id="quickEditQuantity" min="0" step="0.1">
                                </div>
                                <div class="mb-3">
                                    <label for="quickEditNotes" class="form-label">Notes (optional):</label>
                                    <textarea class="form-control" id="quickEditNotes" rows="2"></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="groceryTracker.saveQuickEdit()">
                                <i class="bi bi-check-circle me-1"></i>Save Changes
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        return document.getElementById('quickEditModal');
    }

    async saveQuickEdit() {
        const form = document.getElementById('quickEditForm');
        const itemId = form.dataset.itemId;
        const quantity = document.getElementById('quickEditQuantity').value;
        const notes = document.getElementById('quickEditNotes').value;

        try {
            const response = await fetch(`/api/quick-edit/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    quantity: parseFloat(quantity),
                    notes: notes
                })
            });

            if (response.ok) {
                this.showNotification('Item updated successfully!', 'success');
                this.quickEditModal.hide();
                setTimeout(() => window.location.reload(), 1000);
            } else {
                throw new Error('Failed to update item');
            }
        } catch (error) {
            this.showNotification('Error updating item', 'error');
        }
    }

    // Search functionality
    async performSearch(query) {
        if (query.length < 2) return;

        try {
            const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.success) {
                this.updateSearchResults(data.items);
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    updateSearchResults(items) {
        const container = document.getElementById('items-container');
        if (!container) return;

        // Update the items display
        container.innerHTML = this.renderItems(items);
        this.setupItemEventListeners();
    }

    renderItems(items) {
        if (items.length === 0) {
            return `
                <div class="col-12">
                    <div class="text-center py-5">
                        <i class="bi bi-search display-1 text-muted"></i>
                        <h3 class="mt-3">No items found</h3>
                        <p class="text-muted">Try adjusting your search terms.</p>
                    </div>
                </div>
            `;
        }

        return items.map(item => this.renderItemCard(item)).join('');
    }

    renderItemCard(item) {
        return `
            <div class="col-xl-4 col-lg-6 col-md-6">
                <div class="grocery-item-card-enhanced">
                    <div class="item-header">
                        <div class="d-flex justify-content-between align-items-start">
                            <h5 class="item-title">${item.name}</h5>
                            <div class="action-dropdown">
                                <button class="dropdown-toggle-enhanced" type="button" data-bs-toggle="dropdown">
                                    <i class="bi bi-three-dots-vertical"></i>
                                </button>
                                <ul class="dropdown-menu">
                                    <li><a class="dropdown-item quick-edit-btn" href="#"
                                           data-item-id="${item._id}" data-item-name="${item.name}" data-quantity="${item.quantity}">
                                        <i class="bi bi-lightning-fill me-2"></i>Quick Edit
                                    </a></li>
                                    <li><a class="dropdown-item" href="/edit/${item._id}/">
                                        <i class="bi bi-pencil-fill me-2"></i>Full Edit
                                    </a></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item text-danger quick-delete-btn" href="#"
                                           data-item-id="${item._id}" data-item-name="${item.name}">
                                        <i class="bi bi-trash-fill me-2"></i>Delete
                                    </a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="item-body">
                        <div class="mb-3">
                            <span class="category-badge">
                                <i class="bi bi-tag-fill"></i>${item.category}
                            </span>
                        </div>
                        <div class="mb-3">
                            <div class="quantity-display">
                                <i class="bi bi-123"></i>
                                <span>${item.quantity} ${item.unit}</span>
                            </div>
                        </div>
                        ${item.price ? `
                            <div class="mb-3">
                                <div class="price-display">
                                    <i class="bi bi-currency-rupee me-1"></i>₹${item.price}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    // Notification system
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; border-radius: 15px;';
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-${this.getNotificationIcon(type)} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
            </div>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle-fill',
            error: 'exclamation-triangle-fill',
            warning: 'exclamation-circle-fill',
            info: 'info-circle-fill'
        };
        return icons[type] || icons.info;
    }



    closeAllModals() {
        document.querySelectorAll('.modal.show').forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.groceryTracker = new GroceryTracker();
});
