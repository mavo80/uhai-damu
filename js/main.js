/**
 * UHAI DAMU - Main JavaScript
 * Handles all UI interactions and page-specific logic
 */

// ===== PAGE INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    console.log('🩸 Uhai Damu - Blood Donation Platform Loaded');
    
    // Initialize components
    initNavigation();
    initMobileMenu();
    initScrollEffects();
    
    // Initialize page-specific functions
    if (document.getElementById('bloodSearchForm')) initLiveStatusPage();
    if (document.querySelector('.user-type-btn')) initLoginPage();
    if (document.querySelector('.stats-container')) initStatsCounter();
    if (document.querySelector('.register-form')) initRegistrationForm();
    
    // Initialize blood stock display if on live-status page
    if (window.location.pathname.includes('live-status')) {
        initBloodStockDisplay();
    }
    
    // Set current year in footer
    const yearElements = document.querySelectorAll('.current-year');
    yearElements.forEach(el => {
        el.textContent = new Date().getFullYear();
    });
});

// ===== NAVIGATION =====
function initNavigation() {
    // Highlight current page in sidebar
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    const sidebarLinks = document.querySelectorAll('.sidebar-menu a');
    
    sidebarLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Highlight current page in top navigation
    const topNavLinks = document.querySelectorAll('.upper-nav-links a');
    topNavLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        }
    });
}

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

function initScrollEffects() {
    window.addEventListener('scroll', () => {
        const header = document.querySelector('.top-nav');
        if (header) {
            if (window.scrollY > 50) {
                header.style.boxShadow = '0 4px 20px rgba(0,0,0,0.15)';
            } else {
                header.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
            }
        }
    });
}

// ===== STATS COUNTER =====
function initStatsCounter() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const target = parseInt(element.getAttribute('data-target') || element.textContent.replace(/[+,]/g, ''), 10);
                
                if (!isNaN(target)) {
                    animateNumber(element, target);
                }
                
                observer.unobserve(element);
            }
        });
    }, { threshold: 0.5 });
    
    statNumbers.forEach(num => observer.observe(num));
}

function animateNumber(element, target) {
    let current = 0;
    const increment = Math.ceil(target / 100);
    const duration = 2000;
    const stepTime = Math.floor(duration / (target / increment));
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = formatNumber(target);
            clearInterval(timer);
        } else {
            element.textContent = formatNumber(current);
        }
    }, stepTime);
}

function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M+';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K+';
    return num + '+';
}

// ===== LIVE STATUS PAGE =====
async function initLiveStatusPage() {
    const regionSelect = document.getElementById('regionSelect');
    const constituencySelect = document.getElementById('constituencySelect');
    const searchForm = document.getElementById('bloodSearchForm');
    
    // Load counties
    try {
        const counties = ['Nairobi City County', 'Kiambu County'];
        
        regionSelect.innerHTML = '<option value="">Select County</option>';
        counties.forEach(county => {
            const option = document.createElement('option');
            option.value = county;
            option.textContent = county;
            regionSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load counties:', error);
    }
    
    // Handle county change
    regionSelect.addEventListener('change', async function() {
        const county = this.value;
        constituencySelect.innerHTML = '<option value="">Select Constituency</option>';
        constituencySelect.disabled = !county;
        
        if (!county) return;
        
        try {
            // Nairobi constituencies
            if (county === 'Nairobi City County') {
                const nairobiConstituencies = [
                    'Dagoretti North', 'Dagoretti South', 'Lang\'ata', 'Kibra', 'Roysambu',
                    'Kasarani', 'Ruaraka', 'Embakasi South', 'Embakasi North', 'Embakasi Central',
                    'Embakasi East', 'Embakasi West', 'Makadara', 'Kamukunji', 'Starehe',
                    'Mathare', 'Westlands'
                ];
                
                nairobiConstituencies.forEach(constituency => {
                    const option = document.createElement('option');
                    option.value = constituency;
                    option.textContent = constituency;
                    constituencySelect.appendChild(option);
                });
            }
            
            // Kiambu constituencies
            if (county === 'Kiambu County') {
                const kiambuConstituencies = [
                    'Kiambaa', 'Kikuyu', 'Limuru', 'Gatundu North', 'Gatundu South',
                    'Juja', 'Thika Town', 'Ruiru', 'Githunguri', 'Kiambu',
                    'Kabete', 'Lari'
                ];
                
                kiambuConstituencies.forEach(constituency => {
                    const option = document.createElement('option');
                    option.value = constituency;
                    option.textContent = constituency;
                    constituencySelect.appendChild(option);
                });
            }
            
        } catch (error) {
            console.error('Failed to load constituencies:', error);
        }
    });
    
    // Handle search form
    searchForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        await searchBloodStock();
    });
}

async function searchBloodStock() {
    const county = document.getElementById('regionSelect').value;
    const constituency = document.getElementById('constituencySelect').value;
    const bloodType = document.getElementById('bloodTypeSelect').value;
    
    if (!county || !constituency) {
        showAlert('Please select both County and Constituency', 'warning');
        return;
    }
    
    const resultsDiv = document.getElementById('stockResults');
    resultsDiv.innerHTML = '<div class="spinner"></div><p class="text-center">Searching blood availability...</p>';
    
    try {
        // Simulate API call with sample data
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const sampleData = generateSampleBloodData(county, constituency, bloodType);
        displayBloodStock(sampleData);
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-error">Failed to load blood stock: ${error.message}</div>`;
    }
}

function generateSampleBloodData(county, constituency, bloodTypeFilter = '') {
    const bloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
    const hospitals = {
        'Nairobi City County': [
            { name: 'Kenyatta National Hospital', phone: '+254 20 271 3344' },
            { name: 'MP Shah Hospital', phone: '+254 20 429 4000' },
            { name: 'Aga Khan University Hospital', phone: '+254 20 366 0000' }
        ],
        'Kiambu County': [
            { name: 'Thika Level 5 Hospital', phone: '+254 67 222 021' },
            { name: 'Kiambu County Referral Hospital', phone: '+254 67 222 000' },
            { name: 'Ruiru Sub-County Hospital', phone: '+254 67 222 111' }
        ]
    };
    
    const countyHospitals = hospitals[county] || hospitals['Nairobi City County'];
    
    return countyHospitals.map(hospital => {
        const stock = bloodTypes
            .filter(bt => !bloodTypeFilter || bt === bloodTypeFilter)
            .map(bt => {
                const units = Math.floor(Math.random() * 20) + 1;
                return {
                    blood_type: bt,
                    units_available: units,
                    status: units <= 3 ? 'critical' : units <= 8 ? 'low' : 'adequate',
                    last_updated: new Date().toISOString()
                };
            });
        
        return {
            name: hospital.name,
            contact_phone: hospital.phone,
            contact_email: `${hospital.name.toLowerCase().replace(/\s+/g, '.')}@health.go.ke`,
            stock: stock
        };
    });
}

function displayBloodStock(hospitals) {
    const resultsDiv = document.getElementById('stockResults');
    
    if (!hospitals || hospitals.length === 0) {
        resultsDiv.innerHTML = '<div class="alert alert-warning">No blood stock found for the selected location.</div>';
        return;
    }
    
    let html = '';
    
    hospitals.forEach(hospital => {
        html += `
            <div class="hospital-card">
                <h3>🏥 ${hospital.name}</h3>
                <div class="hospital-contact">
                    <span>📞 ${hospital.contact_phone}</span>
                    <span>📧 ${hospital.contact_email}</span>
                </div>
                <div class="stock-container">
        `;
        
        hospital.stock.forEach(item => {
            const statusClass = `status-${item.status}`;
            const statusText = item.status === 'adequate' ? 'Adequate' : 
                             item.status === 'low' ? 'Low' : 'Critical';
            
            html += `
                <div class="blood-card">
                    <div class="blood-type">${item.blood_type}</div>
                    <div class="blood-units">${item.units_available}</div>
                    <span class="blood-status ${statusClass}">${statusText}</span>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    resultsDiv.innerHTML = html;
}

// ===== LOGIN PAGE =====
function initLoginPage() {
    const userTypeBtns = document.querySelectorAll('.user-type-btn');
    const usernameInput = document.getElementById('username');
    const userTypeHidden = document.getElementById('selectedUserType');
    
    userTypeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            userTypeBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const userType = this.dataset.type;
            if (userTypeHidden) userTypeHidden.value = userType;
            
            // Update placeholder based on user type
            if (usernameInput) {
                if (userType === 'donor') {
                    usernameInput.placeholder = 'Phone Number (+254...)';
                    usernameInput.pattern = '(\\+254|0)[17]\\d{8}';
                } else if (userType === 'doctor') {
                    usernameInput.placeholder = 'License Number';
                } else if (userType === 'admin') {
                    usernameInput.placeholder = 'Admin ID / Email';
                }
            }
        });
    });
    
    // Initialize chart
    initBloodAvailabilityChart();
}

function initBloodAvailabilityChart() {
    const chartContainer = document.getElementById('customBarChart');
    if (!chartContainer) return;
    
    const constituencies = ['Westlands', 'Starehe', 'Kasarani', 'Thika', 'Ruiru'];
    const bloodUnits = [85, 72, 68, 65, 58];
    
    let html = '<div class="bar-chart">';
    
    constituencies.forEach((name, index) => {
        const height = (bloodUnits[index] / 100) * 180;
        html += `
            <div class="bar-container">
                <div class="bar" style="height: ${height}px;">
                    <span class="bar-value">${bloodUnits[index]}</span>
                </div>
                <span class="bar-label">${name}</span>
            </div>
        `;
    });
    
    html += '</div>';
    chartContainer.innerHTML = html;
    
    // Add CSS for bar chart
    const style = document.createElement('style');
    style.textContent = `
        .bar-chart {
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            height: 200px;
            margin-top: 30px;
            gap: 15px;
        }
        .bar-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .bar {
            width: 100%;
            background: linear-gradient(to top, #fff, rgba(255,255,255,0.8));
            border-radius: 8px 8px 0 0;
            position: relative;
            min-height: 20px;
            transition: height 0.5s;
        }
        .bar-value {
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            font-weight: bold;
        }
        .bar-label {
            margin-top: 10px;
            font-size: 12px;
            color: white;
            text-align: center;
        }
    `;
    document.head.appendChild(style);
}

// ===== REGISTRATION FORM =====
function initRegistrationForm() {
    const form = document.querySelector('.register-form');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const password = document.getElementById('regPassword').value;
        const confirmPassword = document.getElementById('regConfirmPassword').value;
        
        if (password !== confirmPassword) {
            showAlert('Passwords do not match!', 'error');
            return;
        }
        
        const formData = {
            phone: document.getElementById('regPhone').value,
            first_name: document.getElementById('regFirstName').value,
            last_name: document.getElementById('regLastName').value,
            email: document.getElementById('regEmail').value,
            blood_type: document.getElementById('regBloodType').value,
            county: document.getElementById('regCounty').value,
            constituency: document.getElementById('regConstituency').value,
            date_of_birth: document.getElementById('regDOB').value,
            gender: document.getElementById('regGender').value,
            password: password
        };
        
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '⏳ Registering...';
        
        try {
            // Simulate registration
            await new Promise(resolve => setTimeout(resolve, 1500));
            showAlert('Registration successful! You can now login.', 'success');
            form.reset();
            
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } catch (error) {
            showAlert('Registration failed: ' + error.message, 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '✅ Register';
        }
    });
}

// ===== ALERT SYSTEM =====
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = message;
    
    const contentArea = document.querySelector('.content-area');
    if (contentArea) {
        contentArea.insertBefore(alertDiv, contentArea.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// ===== BLOOD TYPE FORMATTING =====
function formatBloodType(type) {
    return type.replace('+', '<sup>+</sup>').replace('-', '<sup>-</sup>');
}

// ===== BLOOD STOCK DISPLAY INITIALIZATION =====
function initBloodStockDisplay() {
    const resultsDiv = document.getElementById('stockResults');
    if (resultsDiv) {
        resultsDiv.innerHTML = `
            <div class="text-center" style="padding: 60px 20px; color: var(--text-gray);">
                <div style="font-size: 64px; margin-bottom: 20px;">🩸</div>
                <h3 style="margin-bottom: 15px;">Select Your Location</h3>
                <p>Choose your county and constituency above to view real-time blood availability</p>
            </div>
        `;
    }
}

// ===== EXPORT FUNCTIONS FOR GLOBAL USE =====
window.searchBloodStock = searchBloodStock;
window.showAlert = showAlert;
window.formatBloodType = formatBloodType;