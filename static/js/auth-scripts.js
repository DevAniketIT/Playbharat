/**
 * PlayBharat Authentication Pages - Enhanced User Experience
 * Modern JavaScript for form validation, interactions, and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all authentication page features
    initializeAuthenticationFeatures();
});

function initializeAuthenticationFeatures() {
    // Form validation
    initializeFormValidation();
    
    // Password strength indicator
    initializePasswordStrength();
    
    // Form interactions
    initializeFormInteractions();
    
    // Loading states
    initializeLoadingStates();
    
    // Smooth animations
    initializeSmoothAnimations();
    
    // Mobile optimizations
    initializeMobileOptimizations();
}

/**
 * Real-time Form Validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('.auth-form-input');
        
        inputs.forEach(input => {
            // Real-time validation on input
            input.addEventListener('input', function() {
                validateField(this);
            });
            
            // Validation on blur
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            // Remove error styling on focus
            input.addEventListener('focus', function() {
                clearFieldError(this);
            });
        });
        
        // Form submission validation
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showFormError('Please fix the errors above before submitting.');
            } else {
                showLoadingState(this);
            }
        });
    });
}

function validateField(field) {
    const fieldName = field.name;
    const fieldValue = field.value.trim();
    const fieldGroup = field.closest('.auth-form-group');
    
    // Clear previous errors
    clearFieldError(field);
    
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.required && !fieldValue) {
        isValid = false;
        errorMessage = 'This field is required.';
    }
    
    // Email validation
    else if (fieldName === 'email' && fieldValue) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(fieldValue)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address.';
        }
    }
    
    // Username validation
    else if (fieldName === 'username' && fieldValue) {
        if (fieldValue.length < 3) {
            isValid = false;
            errorMessage = 'Username must be at least 3 characters long.';
        } else if (!/^[a-zA-Z0-9_]+$/.test(fieldValue)) {
            isValid = false;
            errorMessage = 'Username can only contain letters, numbers, and underscores.';
        }
    }
    
    // Password validation
    else if (fieldName === 'password1' && fieldValue) {
        if (fieldValue.length < 8) {
            isValid = false;
            errorMessage = 'Password must be at least 8 characters long.';
        }
    }
    
    // Password confirmation validation
    else if (fieldName === 'password2' && fieldValue) {
        const password1 = document.querySelector('input[name="password1"]');
        if (password1 && fieldValue !== password1.value) {
            isValid = false;
            errorMessage = 'Passwords do not match.';
        }
    }
    
    // Show validation result
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        showFieldSuccess(field);
    }
    
    return isValid;
}

function validateForm(form) {
    const inputs = form.querySelectorAll('.auth-form-input[required]');
    let isFormValid = true;
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isFormValid = false;
        }
    });
    
    // Terms agreement validation
    const termsCheckbox = form.querySelector('#terms_agreement');
    if (termsCheckbox && !termsCheckbox.checked) {
        showFormError('Please agree to the Terms of Service and Privacy Policy.');
        isFormValid = false;
    }
    
    return isFormValid;
}

function showFieldError(field, message) {
    field.classList.add('auth-form-error');
    
    const fieldGroup = field.closest('.auth-form-group');
    let errorElement = fieldGroup.querySelector('.auth-error-message');
    
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'auth-error-message';
        fieldGroup.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    // Add shake animation
    field.style.animation = 'shake 0.5s ease-in-out';
    setTimeout(() => {
        field.style.animation = '';
    }, 500);
}

function showFieldSuccess(field) {
    field.classList.remove('auth-form-error');
    field.classList.add('auth-form-success');
}

function clearFieldError(field) {
    field.classList.remove('auth-form-error');
    field.classList.remove('auth-form-success');
    
    const fieldGroup = field.closest('.auth-form-group');
    const errorElement = fieldGroup.querySelector('.auth-error-message');
    
    if (errorElement && !errorElement.textContent.includes('This field is required')) {
        errorElement.style.display = 'none';
    }
}

function showFormError(message) {
    // Create or update form error message
    let errorDiv = document.querySelector('.form-error-message');
    
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'auth-error-message text-center mt-3 form-error-message';
        
        const form = document.querySelector('.auth-form');
        form.appendChild(errorDiv);
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

/**
 * Password Strength Indicator
 */
function initializePasswordStrength() {
    const passwordField = document.querySelector('input[name="password1"]');
    
    if (passwordField) {
        // Create strength indicator
        const strengthIndicator = createPasswordStrengthIndicator();
        const fieldGroup = passwordField.closest('.auth-form-group');
        fieldGroup.appendChild(strengthIndicator);
        
        passwordField.addEventListener('input', function() {
            updatePasswordStrength(this.value, strengthIndicator);
        });
    }
}

function createPasswordStrengthIndicator() {
    const container = document.createElement('div');
    container.className = 'password-strength-indicator mt-2';
    container.style.display = 'none';
    
    const progressBar = document.createElement('div');
    progressBar.className = 'strength-progress-bar';
    progressBar.innerHTML = `
        <div class="strength-bar">
            <div class="strength-fill"></div>
        </div>
        <div class="strength-text">Password strength: <span class="strength-level">Weak</span></div>
    `;
    
    container.appendChild(progressBar);
    
    // Add CSS for strength indicator
    if (!document.querySelector('#password-strength-styles')) {
        const styles = document.createElement('style');
        styles.id = 'password-strength-styles';
        styles.textContent = `
            .password-strength-indicator {
                margin-top: 0.5rem;
            }
            .strength-bar {
                height: 4px;
                background: #e2e8f0;
                border-radius: 2px;
                overflow: hidden;
                margin-bottom: 0.5rem;
            }
            .strength-fill {
                height: 100%;
                border-radius: 2px;
                transition: all 0.3s ease;
                width: 0%;
            }
            .strength-text {
                font-size: 0.75rem;
                color: #64748b;
            }
            .strength-level {
                font-weight: 600;
            }
            .strength-weak .strength-fill { width: 25%; background: #ef4444; }
            .strength-fair .strength-fill { width: 50%; background: #f97316; }
            .strength-good .strength-fill { width: 75%; background: #eab308; }
            .strength-strong .strength-fill { width: 100%; background: #16a34a; }
        `;
        document.head.appendChild(styles);
    }
    
    return container;
}

function updatePasswordStrength(password, indicator) {
    if (!password) {
        indicator.style.display = 'none';
        return;
    }
    
    indicator.style.display = 'block';
    
    let strength = 0;
    let strengthText = 'Weak';
    let strengthClass = 'strength-weak';
    
    // Length check
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    
    // Character variety checks
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) strength++;
    
    // Determine strength level
    if (strength >= 5) {
        strengthText = 'Strong';
        strengthClass = 'strength-strong';
    } else if (strength >= 4) {
        strengthText = 'Good';
        strengthClass = 'strength-good';
    } else if (strength >= 2) {
        strengthText = 'Fair';
        strengthClass = 'strength-fair';
    }
    
    // Update indicator
    indicator.className = `password-strength-indicator ${strengthClass}`;
    indicator.querySelector('.strength-level').textContent = strengthText;
}

/**
 * Form Interactions and Animations
 */
function initializeFormInteractions() {
    // Social login button interactions
    const socialButtons = document.querySelectorAll('.auth-social-button');
    socialButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            // Add loading state to clicked social button
            this.style.opacity = '0.6';
            this.style.pointerEvents = 'none';
            
            // Reset after 3 seconds (replace with actual OAuth flow)
            setTimeout(() => {
                this.style.opacity = '';
                this.style.pointerEvents = '';
            }, 3000);
        });
    });
    
    // Input focus animations
    const inputs = document.querySelectorAll('.auth-form-input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
}

/**
 * Loading States
 */
function initializeLoadingStates() {
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('.auth-form-button');
            showLoadingState(this);
        });
    });
}

function showLoadingState(form) {
    const submitButton = form.querySelector('.auth-form-button');
    
    if (submitButton && !submitButton.classList.contains('loading')) {
        submitButton.classList.add('loading');
        submitButton.disabled = true;
        
        // Store original text
        if (!submitButton.dataset.originalText) {
            submitButton.dataset.originalText = submitButton.textContent;
        }
    }
}

function hideLoadingState(form) {
    const submitButton = form.querySelector('.auth-form-button');
    
    if (submitButton && submitButton.classList.contains('loading')) {
        submitButton.classList.remove('loading');
        submitButton.disabled = false;
        
        if (submitButton.dataset.originalText) {
            submitButton.innerHTML = submitButton.dataset.originalText;
        }
    }
}

/**
 * Smooth Animations
 */
function initializeSmoothAnimations() {
    // Add page transition animation
    document.body.style.opacity = '0';
    document.body.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        document.body.style.transition = 'all 0.5s ease';
        document.body.style.opacity = '1';
        document.body.style.transform = 'translateY(0)';
    }, 100);
    
    // Staggered animation for form elements
    const formElements = document.querySelectorAll('.auth-form-group, .auth-social-buttons, .auth-form-header');
    formElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.6s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 200 + (index * 100));
    });
}

/**
 * Mobile Optimizations
 */
function initializeMobileOptimizations() {
    // Handle mobile viewport issues
    const viewportMeta = document.querySelector('meta[name="viewport"]');
    if (!viewportMeta) {
        const meta = document.createElement('meta');
        meta.name = 'viewport';
        meta.content = 'width=device-width, initial-scale=1, user-scalable=no';
        document.head.appendChild(meta);
    }
    
    // Mobile keyboard handling
    const inputs = document.querySelectorAll('.auth-form-input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            // Prevent zoom on iOS
            if (/iPhone|iPad|iPod/.test(navigator.userAgent)) {
                this.style.fontSize = '16px';
            }
        });
    });
    
    // Handle mobile menu toggle if needed
    if (window.innerWidth <= 768) {
        document.body.classList.add('mobile');
        
        // Adjust floating icons for mobile
        const floatingIcons = document.querySelectorAll('.floating-icon');
        floatingIcons.forEach(icon => {
            icon.style.display = 'none';
        });
    }
}

/**
 * Utility Functions
 */

// Add CSS animation keyframes dynamically
function addAnimationKeyframes() {
    if (!document.querySelector('#auth-animations')) {
        const styles = document.createElement('style');
        styles.id = 'auth-animations';
        styles.textContent = `
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-5px); }
                75% { transform: translateX(5px); }
            }
            
            .focused .auth-input-icon {
                color: var(--primary-blue) !important;
                transform: translateY(-50%) scale(1.1);
            }
            
            .auth-form-input:focus {
                transform: translateY(-2px);
            }
        `;
        document.head.appendChild(styles);
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.textContent = message;
    
    // Toast styles
    if (!document.querySelector('#toast-styles')) {
        const styles = document.createElement('style');
        styles.id = 'toast-styles';
        styles.textContent = `
            .toast-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 0.5rem;
                color: white;
                font-weight: 600;
                z-index: 9999;
                transform: translateX(100%);
                transition: transform 0.3s ease;
            }
            .toast-info { background: #3b82f6; }
            .toast-success { background: #16a34a; }
            .toast-error { background: #ef4444; }
            .toast-warning { background: #f97316; }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Initialize animations and helper functions
addAnimationKeyframes();

// Export functions for potential use in other scripts
window.AuthScripts = {
    showToast,
    showLoadingState,
    hideLoadingState,
    validateForm,
    validateField
};