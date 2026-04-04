/**
 * UHAI DAMU - Main JavaScript File
 * Handles common functionality across all pages
 */

// ============================================
// DOM Ready Event
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🩸 Uhai Damu Platform Loaded');
    
    // Set current year in footer
    const yearSpans = document.querySelectorAll('.current-year');
    yearSpans.forEach(span => {
        span.textContent = new Date().getFullYear();
    });
    
    // Initialize mobile menu
    initMobileMenu();
    
    // Initialize form validations
    initFormValidations();
    
    // Check authentication status
    checkAuthStatus();
    
    // Load user profile if on dashboard
    loadUserProfile();
});

// ============================================
// MOBILE MENU
// ============================================
function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const sidebar = document.querySelector('.sidebar');
    
    if (hamburger && sidebar) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            sidebar.classList.toggle('active');
        });
    }
}

// ============================================
// FORM VALIDATIONS
// ============================================
function initFormValidations() {
    // Phone number validation (Kenyan format)
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateKenyanPhone(this);
        });
    });
    
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateEmail(this);
        });
    });
    
    // Password confirmation
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    if (password && confirmPassword) {
        confirmPassword.addEventListener('input', function() {
            validatePasswordMatch(password, this);
        });
    }
}

function validateKenyanPhone(input) {
    const phonePattern = /^(\+254|0)[17]\d{8}$/;
    const isValid = phonePattern.test(input.value);
    
    if (input.value && !isValid) {
        input.style.borderColor = '#dc3545';
        showFieldError(input, 'Enter valid Kenyan phone: +2547XXXXXXXX or 07XXXXXXXX');
    } else {
        input.style.borderColor = '#28a745';
        removeFieldError(input);
    }
    return isValid;
}

function validateEmail(input) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValid = emailPattern.test(input.value);
    
    if (input.value && !isValid) {
        input.style.borderColor = '#dc3545';
        showFieldError(input, 'Enter a valid email address');
    } else {
        input.style.borderColor = '#28a745';
        removeFieldError(input);
    }
    return isValid;
}

function validatePasswordMatch(password, confirm) {
    const isValid = password.value === confirm.value;
    
    if (confirm.value && !isValid) {
        confirm.style.borderColor = '#dc3545';
        showFieldError(confirm, 'Passwords do not match');
    } else {
        confirm.style.borderColor = '#28a745';
        removeFieldError(confirm);
    }
    return isValid;
}

function showFieldError(input, message) {
    let error = input.nextElementSibling;
    if (!error || !error.classList.contains('field-error')) {
        error = document.createElement('div');
        error.className = 'field-error';
        error.style.color = '#dc3545';
        error.style.fontSize = '12px';
        error.style.marginTop = '4px';
        input.parentNode.insertBefore(error, input.nextSibling);
    }
    error.textContent = message;
}

function removeFieldError(input) {
    const error = input.nextElementSibling;
    if (error && error.classList.contains('field-error')) {
        error.remove();
    }
}

// ============================================
// AUTHENTICATION
// ============================================
function checkAuthStatus() {
    const token = sessionStorage.getItem('token');
    const userType = sessionStorage.getItem('userType');
    const isLoggedIn = token || sessionStorage.getItem('donorLoggedIn') || 
                        sessionStorage.getItem('adminLoggedIn') || 
                        sessionStorage.getItem('hospitalLoggedIn');
    
    // Update UI based on login status
    const loginBtn = document.querySelector('.btn-login-sidebar');
    const donorInfo = document.querySelector('.donor-info');
    
    if (isLoggedIn && loginBtn) {
        const userName = sessionStorage.getItem('donorName') || 
                        sessionStorage.getItem('adminName') || 
                        sessionStorage.getItem('hospitalName');
        
        if (userName) {
            loginBtn.innerHTML = `👋 ${userName}`;
            loginBtn.href = '#';
            
            // Add logout option
            loginBtn.addEventListener('click', (e) => {
                e.preventDefault();
                logout();
            });
        }
    }
}

function logout() {
    fetch('/api/logout', { method: 'POST' })
        .finally(() => {
            sessionStorage.clear();
            window.location.href = 'login.html';
        });
}

// ============================================
// USER PROFILE
// ============================================
async function loadUserProfile() {
    const donorDashboard = document.querySelector('.donor-dashboard');
    if (!donorDashboard) return;
    
    try {
        const response = await fetch('/api/donor/profile', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.donor) {
                updateProfileDisplay(data.donor);
            }
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

function updateProfileDisplay(donor) {
    const nameElements = document.querySelectorAll('.donor-name');
    nameElements.forEach(el => {
        el.textContent = `${donor.firstName} ${donor.lastName}`;
    });
    
    const profileFields = {
        'full-name': `${donor.firstName} ${donor.lastName}`,
        'email': donor.email,
        'phone': donor.phone,
        'blood-type': donor.bloodType,
        'county': donor.county,
        'constituency': donor.constituency,
        'weight': donor.weight,
        'height': donor.height
    };
    
    Object.entries(profileFields).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element && value) {
            element.textContent = value;
        }
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <span>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
        <span>${message}</span>
    `;
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#e8f5e9' : type === 'error' ? '#ffebee' : '#e3f2fd'};
        color: ${type === 'success' ? '#2e7d32' : type === 'error' ? '#c62828' : '#1976d2'};
        border-radius: 8px;
        border-left: 4px solid ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 9999;
        font-size: 14px;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

// Format blood type with superscript
function formatBloodType(type) {
    if (!type) return 'N/A';
    return type.replace('+', '<sup>+</sup>').replace('-', '<sup>-</sup>');
}

// Calculate age from date of birth
function calculateAge(dob) {
    if (!dob) return null;
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    return age;
}

// Format date to local string
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
}

// Format time to local string
function formatTime(timeString) {
    if (!timeString) return 'N/A';
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ============================================
// ANIMATIONS
// ============================================
function initScrollAnimations() {
    const elements = document.querySelectorAll('.stat-card, .feature-card, .info-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    elements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.5s ease';
        observer.observe(el);
    });
}

// ============================================
// BLOOD TYPE COLORS
// ============================================
const bloodTypeColors = {
    'A+': '#c62828',
    'A-': '#880e4f',
    'B+': '#7b1fa2',
    'B-': '#4527a0',
    'AB+': '#303f9f',
    'AB-': '#1976d2',
    'O+': '#2e7d32',
    'O-': '#558b2f'
};

function getBloodTypeColor(bloodType) {
    return bloodTypeColors[bloodType] || '#666';
}

// ============================================
// EXPORT FUNCTIONS (for global use)
// ============================================
window.showAlert = showAlert;
window.formatBloodType = formatBloodType;
window.calculateAge = calculateAge;
window.formatDate = formatDate;
window.formatTime = formatTime;
window.getBloodTypeColor = getBloodTypeColor;
window.logout = logout;