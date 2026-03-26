/**
 * UHAI DAMU - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Uhai Damu Platform Loaded');
    
    // Set current year in footer
    const yearSpan = document.querySelector('.current-year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }
    
    // Handle login form if on login page
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (email === 'admin@uhai-damu.co.ke' && password === 'Admin123') {
                window.location.href = 'admin-dashboard.html';
            } else {
                alert('Invalid credentials. Use admin@uhai-damu.co.ke / Admin123 for admin access.');
            }
        });
    }
    
    // Handle registration form if on register page
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Registration successful! You can now login.');
            window.location.href = 'login.html';
        });
    }
});
