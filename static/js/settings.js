/**
 * Settings JavaScript for Smart Grocery Tracker
 * Handles settings interactions, quick settings, and AJAX updates
 */

class SettingsManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupQuickSettings();
        this.setupFormValidation();
        this.setupTooltips();
    }

    setupEventListeners() {
        // Quick settings modal
        const quickSettingsBtn = document.querySelector('[onclick="showQuickSettings()"]');
        if (quickSettingsBtn) {
            quickSettingsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showQuickSettings();
            });
        }

        // Export settings button
        const exportBtn = document.querySelector('[onclick="exportSettings()"]');
        if (exportBtn) {
            exportBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.exportSettings();
            });
        }

        // Save quick settings button
        const saveQuickBtn = document.querySelector('[onclick="saveQuickSettings()"]');
        if (saveQuickBtn) {
            saveQuickBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.saveQuickSettings();
            });
        }

        // Form auto-save for certain settings
        this.setupAutoSave();
    }

    setupQuickSettings() {
        // Initialize quick settings with current values
        const quickTheme = document.getElementById('quickTheme');
        const quickNotifications = document.getElementById('quickNotifications');

        if (quickTheme) {
            quickTheme.addEventListener('change', () => {
                this.updateQuickSetting('theme', quickTheme.value);
            });
        }

        if (quickNotifications) {
            quickNotifications.addEventListener('change', () => {
                this.updateQuickSetting('notifications', quickNotifications.checked);
            });
        }
    }

    setupFormValidation() {
        // Add real-time validation for settings forms
        const forms = document.querySelectorAll('.settings-form form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
            });
        });
    }

    setupTooltips() {
        // Initialize Bootstrap tooltips for settings
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    setupAutoSave() {
        // Auto-save for certain settings after a delay
        const autoSaveInputs = document.querySelectorAll('[data-auto-save="true"]');
        autoSaveInputs.forEach(input => {
            let timeout;
            input.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    this.autoSaveSetting(input);
                }, 1000); // Save after 1 second of inactivity
            });
        });
    }

    showQuickSettings() {
        const modal = new bootstrap.Modal(document.getElementById('quickSettingsModal'));
        modal.show();
    }

    async updateQuickSetting(type, value) {
        try {
            const response = await fetch('/accounts/api/quick-settings/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    type: type,
                    value: value
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification(data.message, 'success');
                
                // Apply theme change immediately if it's a theme update
                if (type === 'theme') {
                    this.applyTheme(value);
                }
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error updating quick setting:', error);
            this.showNotification('Failed to update setting', 'error');
        }
    }

    async saveQuickSettings() {
        const quickTheme = document.getElementById('quickTheme');
        const quickNotifications = document.getElementById('quickNotifications');

        const updates = [];

        if (quickTheme) {
            updates.push(this.updateQuickSetting('theme', quickTheme.value));
        }

        if (quickNotifications) {
            updates.push(this.updateQuickSetting('notifications', quickNotifications.checked));
        }

        try {
            await Promise.all(updates);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('quickSettingsModal'));
            modal.hide();
            
            this.showNotification('Quick settings saved successfully!', 'success');
        } catch (error) {
            this.showNotification('Failed to save some settings', 'error');
        }
    }

    async autoSaveSetting(input) {
        const settingName = input.name;
        const settingValue = input.type === 'checkbox' ? input.checked : input.value;

        try {
            const response = await fetch('/accounts/api/quick-settings/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    type: settingName,
                    value: settingValue
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Show subtle save indicator
                this.showSaveIndicator(input);
            }
        } catch (error) {
            console.error('Auto-save failed:', error);
        }
    }

    validateField(input) {
        const value = input.value.trim();
        const fieldName = input.name;
        let isValid = true;
        let errorMessage = '';

        // Custom validation rules
        switch (fieldName) {
            case 'low_stock_threshold':
                if (value < 1 || value > 100) {
                    isValid = false;
                    errorMessage = 'Threshold must be between 1 and 100';
                }
                break;
            case 'expiry_warning_days':
                if (value < 1 || value > 30) {
                    isValid = false;
                    errorMessage = 'Warning days must be between 1 and 30';
                }
                break;
            case 'session_timeout':
                if (value < 5 || value > 480) {
                    isValid = false;
                    errorMessage = 'Session timeout must be between 5 and 480 minutes';
                }
                break;
        }

        this.showFieldValidation(input, isValid, errorMessage);
        return isValid;
    }

    showFieldValidation(input, isValid, errorMessage) {
        // Remove existing validation classes
        input.classList.remove('is-valid', 'is-invalid');
        
        // Remove existing error message
        const existingError = input.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        if (isValid) {
            input.classList.add('is-valid');
        } else {
            input.classList.add('is-invalid');
            
            // Add error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = errorMessage;
            input.parentNode.appendChild(errorDiv);
        }
    }

    showSaveIndicator(input) {
        // Create and show save indicator
        const indicator = document.createElement('div');
        indicator.className = 'save-indicator';
        indicator.innerHTML = '<i class="bi bi-check-circle-fill"></i> Saved';
        indicator.style.cssText = `
            position: absolute;
            top: -30px;
            right: 0;
            background: var(--bs-success);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 1000;
        `;

        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(indicator);

        // Animate in
        setTimeout(() => {
            indicator.style.opacity = '1';
        }, 10);

        // Remove after 2 seconds
        setTimeout(() => {
            indicator.style.opacity = '0';
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.parentNode.removeChild(indicator);
                }
            }, 300);
        }, 2000);
    }

    exportSettings() {
        // Create settings export
        const settingsData = {
            timestamp: new Date().toISOString(),
            user: document.querySelector('[data-username]')?.dataset.username || 'unknown',
            settings: this.gatherCurrentSettings()
        };

        // Create and download file
        const blob = new Blob([JSON.stringify(settingsData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `grocery-tracker-settings-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('Settings exported successfully!', 'success');
    }

    gatherCurrentSettings() {
        const settings = {};
        
        // Gather all form inputs
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.name) {
                settings[input.name] = input.type === 'checkbox' ? input.checked : input.value;
            }
        });

        return settings;
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update theme icons
        const themeIcons = document.querySelectorAll('[id*="theme" i] i, [id*="Theme" i] i');
        themeIcons.forEach(icon => {
            if (theme === 'dark') {
                icon.className = 'bi bi-sun-fill';
            } else {
                icon.className = 'bi bi-moon-fill';
            }
        });
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 150);
            }
        }, 5000);
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
}

// Initialize settings manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager = new SettingsManager();
});

// Global functions for backward compatibility
function showQuickSettings() {
    if (window.settingsManager) {
        window.settingsManager.showQuickSettings();
    }
}

function exportSettings() {
    if (window.settingsManager) {
        window.settingsManager.exportSettings();
    }
}

function saveQuickSettings() {
    if (window.settingsManager) {
        window.settingsManager.saveQuickSettings();
    }
}
