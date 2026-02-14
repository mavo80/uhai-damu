/**
 * UHAI DAMU - API Service
 * Complete backend integration with Flask
 */

const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000/api'
    : 'https://uhai-damu.onrender.com/api'; // Update with your deployment URL

class ApiService {
    constructor() {
        this.token = localStorage.getItem('auth_token');
        this.userData = JSON.parse(localStorage.getItem('userData') || 'null');
    }

    // ===== HTTP REQUEST METHODS =====
    async request(endpoint, method = 'GET', data = null, requiresAuth = true) {
        const url = `${API_BASE_URL}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
        
        if (requiresAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        const config = {
            method,
            headers,
            mode: 'cors',
            cache: 'no-cache'
        };
        
        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            config.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, config);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || result.message || 'API request failed');
            }
            
            return result;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // ===== AUTHENTICATION =====
    async login(phone, password, userType) {
        const data = { phone, password, user_type: userType };
        const result = await this.request('/donor/login', 'POST', data, false);
        
        if (result.token || result.access_token) {
            this.token = result.token || result.access_token;
            this.userData = result.donor || result.user;
            
            localStorage.setItem('auth_token', this.token);
            localStorage.setItem('userData', JSON.stringify(this.userData));
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('userType', userType);
        }
        
        return result;
    }

    async register(donorData) {
        return await this.request('/donor/register', 'POST', donorData, false);
    }

    async logout() {
        try {
            await this.request('/donor/logout', 'POST');
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.token = null;
            this.userData = null;
            localStorage.clear();
            window.location.href = '/login.html';
        }
    }

    async getCurrentUser() {
        if (!this.token) return null;
        try {
            return await this.request('/donor/profile', 'GET');
        } catch (error) {
            this.logout();
            return null;
        }
    }

    // ===== BLOOD STOCK =====
    async getBloodStock(county, constituency) {
        const endpoint = `/blood-stock/${encodeURIComponent(county)}/${encodeURIComponent(constituency)}`;
        return await this.request(endpoint, 'GET', null, false);
    }

    async getBloodAvailability(filters = {}) {
        let endpoint = '/blood-stock';
        const params = new URLSearchParams();
        
        if (filters.county) params.append('county', filters.county);
        if (filters.constituency) params.append('constituency', filters.constituency);
        if (filters.blood_type) params.append('blood_type', filters.blood_type);
        
        const queryString = params.toString();
        if (queryString) endpoint += `?${queryString}`;
        
        return await this.request(endpoint, 'GET', null, false);
    }

    // ===== DONORS =====
    async getNearbyDonors(county, bloodType, constituency = '') {
        let endpoint = `/donors/nearby?county=${encodeURIComponent(county)}&blood_type=${encodeURIComponent(bloodType)}`;
        if (constituency) {
            endpoint += `&constituency=${encodeURIComponent(constituency)}`;
        }
        return await this.request(endpoint, 'GET', null, true);
    }

    async updateDonorAvailability(isAvailable) {
        return await this.request('/donor/availability', 'PUT', { is_available: isAvailable }, true);
    }

    // ===== BLOOD REQUESTS =====
    async createBloodRequest(requestData) {
        return await this.request('/blood-request', 'POST', requestData, true);
    }

    // ===== LOCATIONS =====
    async getCounties() {
        return await this.request('/counties', 'GET', null, false);
    }

    async getConstituencies(county) {
        return await this.request(`/constituencies/${encodeURIComponent(county)}`, 'GET', null, false);
    }

    // ===== BLOOD TYPES =====
    async getBloodTypes() {
        return await this.request('/blood-types', 'GET', null, false);
    }

    // ===== INITIALIZE DATABASE =====
    async initDatabase() {
        return await this.request('/init', 'POST', null, false);
    }
}

// Create global instance
window.api = new ApiService();

// Check login status on page load
document.addEventListener('DOMContentLoaded', () => {
    // Update UI based on login status
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const userData = JSON.parse(localStorage.getItem('userData') || 'null');
    
    if (isLoggedIn && userData) {
        // Update sidebar login button
        const loginBtn = document.querySelector('.btn-login-sidebar');
        if (loginBtn) {
            loginBtn.innerHTML = `👋 ${userData.name || userData.first_name || 'Donor'}`;
            loginBtn.href = 'dashboard.html';
        }
        
        // Add logout option
        const sidebarFooter = document.querySelector('.sidebar-footer');
        if (sidebarFooter) {
            const logoutBtn = document.createElement('a');
            logoutBtn.href = '#';
            logoutBtn.className = 'btn-logout';
            logoutBtn.style.cssText = `
                display: block;
                padding: 12px;
                margin-top: 10px;
                background: transparent;
                color: var(--danger);
                border: 2px solid var(--danger);
                border-radius: 8px;
                text-align: center;
                font-weight: 600;
                transition: all 0.3s;
            `;
            logoutBtn.innerHTML = '🚪 Logout';
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                window.api.logout();
            });
            sidebarFooter.appendChild(logoutBtn);
        }
    }
});