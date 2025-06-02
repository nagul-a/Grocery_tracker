/**
 * Enhanced Authentication JavaScript for Smart Grocery Tracker
 * 
 * This file handles enhanced authentication features including logout modals,
 * session management, keyboard shortcuts, and security features.
 */

class EnhancedAuth {
    constructor() {
        this.sessionTimeoutWarning = null;
        this.sessionTimeoutTimer = null;
        this.sessionWarningTime = 5 * 60 * 1000; // 5 minutes before timeout
        this.sessionTimeout = 30 * 60 * 1000; // 30 minutes total
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        this.initSessionManagement();
        this.initPasswordStrength();
        console.log('✅ Enhanced Authentication system initialized');
    }
    
    setupEventListeners() {
        // Close modals when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.hideAllModals();
            }
        });
        
        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideAllModals();
            }
        });
        
        // Activity tracking for session management
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, () => this.resetSessionTimer(), { passive: true });
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+L or Cmd+L for logout
            if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
                e.preventDefault();
                this.showLogoutModal();
            }
            
            // Ctrl+Shift+P or Cmd+Shift+P for profile
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'P') {
                e.preventDefault();
                window.location.href = '/accounts/profile/';
            }
            
            // Ctrl+Shift+D or Cmd+Shift+D for dashboard
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                window.location.href = '/dashboard/';
            }
        });
    }
    
    initSessionManagement() {
        // Only initialize if user is authenticated
        if (document.querySelector('.user-dropdown')) {
            this.resetSessionTimer();
        }
    }
    
    resetSessionTimer() {
        // Clear existing timers
        if (this.sessionTimeoutWarning) {
            clearTimeout(this.sessionTimeoutWarning);
        }
        if (this.sessionTimeoutTimer) {
            clearTimeout(this.sessionTimeoutTimer);
        }
        
        // Set warning timer (5 minutes before timeout)
        this.sessionTimeoutWarning = setTimeout(() => {
            this.showSessionTimeoutWarning();
        }, this.sessionTimeout - this.sessionWarningTime);
        
        // Set actual timeout timer
        this.sessionTimeoutTimer = setTimeout(() => {
            this.forceLogout();
        }, this.sessionTimeout);
    }
    
    showSessionTimeoutWarning() {
        const modal = document.getElementById('sessionTimeoutModal');
        if (modal) {
            modal.classList.add('show');
            this.startCountdown();
        }
    }
    
    startCountdown() {
        let timeLeft = 5 * 60; // 5 minutes in seconds
        const countdownElement = document.getElementById('timeoutCountdown');
        
        const countdown = setInterval(() => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            if (countdownElement) {
                countdownElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            }
            
            timeLeft--;
            
            if (timeLeft < 0) {
                clearInterval(countdown);
                this.forceLogout();
            }
        }, 1000);
    }
    
    extendSession() {
        // Hide timeout modal
        this.hideSessionTimeoutModal();
        
        // Make AJAX request to extend session
        fetch('/accounts/api/extend-session/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.resetSessionTimer();
                this.showNotification('Session extended successfully', 'success');
            } else {
                this.showNotification('Failed to extend session', 'error');
            }
        })
        .catch(error => {
            console.error('Error extending session:', error);
            this.showNotification('Failed to extend session', 'error');
        });
    }
    
    forceLogout() {
        // Clear all timers
        if (this.sessionTimeoutWarning) {
            clearTimeout(this.sessionTimeoutWarning);
        }
        if (this.sessionTimeoutTimer) {
            clearTimeout(this.sessionTimeoutTimer);
        }
        
        // Redirect to logout
        window.location.href = '/accounts/logout/';
    }
    
    showLogoutModal() {
        const modal = document.getElementById('logoutModal');
        if (modal) {
            modal.classList.add('show');
        }
    }
    
    hideLogoutModal() {
        const modal = document.getElementById('logoutModal');
        if (modal) {
            modal.classList.remove('show');
        }
    }
    
    hideSessionTimeoutModal() {
        const modal = document.getElementById('sessionTimeoutModal');
        if (modal) {
            modal.classList.remove('show');
        }
    }
    
    hideAllModals() {
        const modals = document.querySelectorAll('.modal-overlay');
        modals.forEach(modal => {
            modal.classList.remove('show');
        });
    }
    
    confirmLogout() {
        // Submit logout form
        const logoutForm = document.querySelector('#logoutModal form');
        if (logoutForm) {
            logoutForm.submit();
        }
    }
    
    initPasswordStrength() {
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            if (input.name === 'password1' || input.name === 'new_password1') {
                this.addPasswordStrengthMeter(input);
            }
        });
    }
    
    addPasswordStrengthMeter(input) {
        const container = input.parentNode;
        const strengthDiv = document.createElement('div');
        strengthDiv.className = 'password-strength';
        strengthDiv.innerHTML = `
            <div class="strength-meter">
                <div class="strength-bar"></div>
            </div>
            <div class="strength-text">Enter password</div>
        `;
        
        container.appendChild(strengthDiv);
        
        input.addEventListener('input', (e) => {
            this.updatePasswordStrength(e.target.value, strengthDiv);
        });
    }
    
    updatePasswordStrength(password, strengthDiv) {
        const bar = strengthDiv.querySelector('.strength-bar');
        const text = strengthDiv.querySelector('.strength-text');
        
        const strength = this.calculatePasswordStrength(password);
        
        // Remove existing classes
        bar.className = 'strength-bar';
        text.className = 'strength-text';
        
        if (password.length === 0) {
            text.textContent = 'Enter password';
            return;
        }
        
        // Add strength classes
        bar.classList.add(strength.level);
        text.classList.add(strength.level);
        text.textContent = strength.text;
    }
    
    calculatePasswordStrength(password) {
        let score = 0;
        
        // Length check
        if (password.length >= 8) score += 1;
        if (password.length >= 12) score += 1;
        
        // Character variety checks
        if (/[a-z]/.test(password)) score += 1;
        if (/[A-Z]/.test(password)) score += 1;
        if (/[0-9]/.test(password)) score += 1;
        if (/[^A-Za-z0-9]/.test(password)) score += 1;
        
        // Common patterns penalty
        if (/(.)\1{2,}/.test(password)) score -= 1; // Repeated characters
        if (/123|abc|qwe/i.test(password)) score -= 1; // Sequential patterns
        
        // Determine strength level
        if (score <= 2) {
            return { level: 'weak', text: 'Weak password' };
        } else if (score <= 3) {
            return { level: 'fair', text: 'Fair password' };
        } else if (score <= 4) {
            return { level: 'good', text: 'Good password' };
        } else {
            return { level: 'strong', text: 'Strong password' };
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="bi bi-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="bi bi-x"></i>
            </button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Show with animation
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
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
    
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// Global functions for modal controls
function showLogoutModal(event) {
    event.preventDefault();
    window.enhancedAuth.showLogoutModal();
}

function hideLogoutModal() {
    window.enhancedAuth.hideLogoutModal();
}

function confirmLogout() {
    window.enhancedAuth.confirmLogout();
}

function extendSession() {
    window.enhancedAuth.extendSession();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedAuth = new EnhancedAuth();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedAuth;
}
