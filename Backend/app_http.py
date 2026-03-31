"""
UHAI DAMU - Blood Donation Platform
Using HTTP Requests to Supabase (No supabase library needed)
"""

from flask import Flask, send_from_directory, jsonify, request, session
from flask_cors import CORS
import os
import bcrypt
import requests
from datetime import datetime
import re
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, static_folder='../', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'uhai-damu-secret-key-2025')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

# Enable CORS
CORS(app, supports_credentials=True, origins=[
    'http://localhost:5001',
    'http://127.0.0.1:5001'
])

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================
# SUPABASE CONFIGURATION
# ============================================
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://tnrgregvmythjrutbtou.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRucmdyZWd2bXl0aGpydXRidG91Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ4ODI5MzAsImV4cCI6MjA5MDQ1ODkzMH0.RmK-IjHEvxL5O01IUHZXm40H3R6z8p_K464H7XHLkww')

def supabase_request(method, endpoint, data=None, params=None):
    """Make HTTP request to Supabase REST API"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return None
        
        if response.status_code >= 400:
            print(f"Supabase error: {response.status_code} - {response.text}")
            return None
        
        return response.json() if response.text else []
    except Exception as e:
        print(f"Supabase request error: {e}")
        return None

# ============================================
# AUTHENTICATION DECORATOR
# ============================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# SERVE HTML FILES
# ============================================

@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    if '..' in filename or filename.startswith('/'):
        return "Invalid path", 400
    try:
        return send_from_directory(BASE_DIR, filename)
    except Exception as e:
        return f"File not found: {filename}", 404

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Uhai Damu API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/test')
def test():
    return jsonify({'success': True, 'message': 'API is working!'})

# ============================================
# LOCATION DATA
# ============================================

@app.route('/api/counties')
def get_counties():
    return jsonify({
        'counties': [
            {'id': 'nairobi', 'name': 'Nairobi City County'},
            {'id': 'kiambu', 'name': 'Kiambu County'}
        ]
    })

@app.route('/api/constituencies/<county>')
def get_constituencies(county):
    constituencies = {
        'Nairobi City County': [
            'Dagoretti North', 'Dagoretti South', "Lang'ata", 'Kibra', 'Roysambu',
            'Kasarani', 'Ruaraka', 'Embakasi South', 'Embakasi North', 'Embakasi Central',
            'Embakasi East', 'Embakasi West', 'Makadara', 'Kamukunji', 'Starehe',
            'Mathare', 'Westlands'
        ],
        'Kiambu County': [
            'Kiambaa', 'Kikuyu', 'Limuru', 'Gatundu North', 'Gatundu South',
            'Juja', 'Thika Town', 'Ruiru', 'Githunguri', 'Kiambu',
            'Kabete', 'Lari'
        ]
    }
    
    if county == 'nairobi':
        county_name = 'Nairobi City County'
    elif county == 'kiambu':
        county_name = 'Kiambu County'
    else:
        county_name = county
    
    return jsonify({'constituencies': constituencies.get(county_name, [])})

@app.route('/api/blood-types')
def get_blood_types():
    return jsonify({'blood_types': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']})

# ============================================
# BLOOD STOCK
# ============================================

@app.route('/api/blood-stock/<county>/<constituency>')
def get_blood_stock(county, constituency):
    # Return sample data (you can replace with Supabase later)
    hospitals = [
        {
            'name': 'Kenyatta National Hospital',
            'contact_phone': '+254 20 271 3344',
            'contact_email': 'info@knh.or.ke',
            'stock': [
                {'blood_type': 'A+', 'units_available': 15, 'status': 'adequate'},
                {'blood_type': 'O+', 'units_available': 20, 'status': 'adequate'},
                {'blood_type': 'O-', 'units_available': 3, 'status': 'critical'}
            ]
        },
        {
            'name': 'MP Shah Hospital',
            'contact_phone': '+254 20 429 4000',
            'contact_email': 'info@mpshah.co.ke',
            'stock': [
                {'blood_type': 'A+', 'units_available': 10, 'status': 'adequate'},
                {'blood_type': 'B+', 'units_available': 5, 'status': 'low'}
            ]
        }
    ]
    return jsonify({'hospitals': hospitals})

# ============================================
# DONOR REGISTRATION (Without Database for now)
# ============================================

@app.route('/api/donor/register', methods=['POST'])
def donor_register():
    try:
        data = request.json
        
        # Validate required fields
        required = ['first_name', 'last_name', 'email', 'phone', 'blood_type', 'password']
        for field in required:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Validate email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Validate phone (Kenyan format)
        phone_pattern = r'^(\+254|0)[17]\d{8}$'
        if not re.match(phone_pattern, data['phone']):
            return jsonify({'success': False, 'error': 'Invalid phone number'}), 400
        
        # In demo mode, just return success
        return jsonify({
            'success': True,
            'message': 'Registration successful! You can now login.',
            'user_id': 'demo-user-id'
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# DONOR LOGIN (Demo)
# ============================================

@app.route('/api/donor/login', methods=['POST'])
def donor_login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        # Demo donor
        if email and password:
            # Store session
            session['user_id'] = 'demo-donor-id'
            session['user_type'] = 'donor'
            session['user_email'] = email
            session['user_name'] = 'Demo Donor'
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'donor': {
                    'id': 'demo-donor-id',
                    'firstName': 'Demo',
                    'lastName': 'Donor',
                    'email': email,
                    'phone': '+254712345678',
                    'bloodType': 'O+',
                    'county': 'Nairobi',
                    'constituency': 'Westlands',
                    'weight': 70,
                    'height': 175,
                    'donationStatus': {
                        'tattoosLast6Months': False,
                        'alcoholLast24Hours': False,
                        'medication': False,
                        'healthIssues': False
                    }
                }
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# GET DONOR PROFILE
# ============================================

@app.route('/api/donor/profile', methods=['GET'])
@login_required
def get_donor_profile():
    try:
        return jsonify({
            'success': True,
            'donor': {
                'id': session.get('user_id'),
                'firstName': 'Demo',
                'lastName': 'Donor',
                'email': session.get('user_email', 'demo@example.com'),
                'phone': '+254712345678',
                'bloodType': 'O+',
                'county': 'Nairobi',
                'constituency': 'Westlands',
                'weight': 70,
                'height': 175,
                'donationStatus': {
                    'tattoosLast6Months': False,
                    'alcoholLast24Hours': False,
                    'medication': False,
                    'healthIssues': False
                }
            }
        })
        
    except Exception as e:
        print(f"Profile error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# UPDATE DONOR STATUS
# ============================================

@app.route('/api/donor/status', methods=['PUT'])
@login_required
def update_donor_status():
    try:
        data = request.json
        # Just return success for demo
        return jsonify({'success': True, 'message': 'Donation status updated successfully'})
        
    except Exception as e:
        print(f"Status update error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# APPOINTMENT ENDPOINTS
# ============================================

@app.route('/api/appointments/create', methods=['POST'])
@login_required
def create_appointment():
    try:
        data = request.json
        
        hospital_id = data.get('hospital_id')
        appointment_date = data.get('date')
        appointment_time = data.get('time')
        
        if not hospital_id or not appointment_date or not appointment_time:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Appointment request submitted successfully',
            'appointment_id': 'demo-appointment-id'
        }), 201
        
    except Exception as e:
        print(f"Appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/appointments/my', methods=['GET'])
@login_required
def get_my_appointments():
    try:
        return jsonify({
            'success': True,
            'appointments': [
                {
                    'id': '1',
                    'hospital_name': 'Kenyatta National Hospital',
                    'appointment_date': '2025-04-05',
                    'appointment_time': '10:00 AM',
                    'status': 'pending'
                }
            ]
        })
        
    except Exception as e:
        print(f"Get appointments error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ADMIN LOGIN
# ============================================

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if email == 'admin@uhai-damu.co.ke' and password == 'Admin123':
            session['user_id'] = 'admin-id'
            session['user_type'] = 'admin'
            session['user_name'] = 'Super Admin'
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'admin': {
                    'id': 'admin-id',
                    'email': email,
                    'full_name': 'Super Admin',
                    'role': 'super_admin'
                }
            }), 200
        
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"Admin login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

# ============================================
# ADMIN APPOINTMENTS
# ============================================

@app.route('/api/admin/appointments', methods=['GET'])
@login_required
def admin_get_appointments():
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({
            'success': True,
            'appointments': [
                {
                    'id': '1',
                    'donor_name': 'Demo Donor',
                    'donor_email': 'demo@example.com',
                    'blood_type': 'O+',
                    'hospital_name': 'Kenyatta National Hospital',
                    'appointment_date': '2025-04-05',
                    'appointment_time': '10:00 AM',
                    'status': 'pending'
                }
            ],
            'count': 1
        })
        
    except Exception as e:
        print(f"Admin get appointments error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/appointments/<appointment_id>/approve', methods=['POST'])
@login_required
def admin_approve_appointment(appointment_id):
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({'success': True, 'message': 'Appointment approved successfully'}), 200
        
    except Exception as e:
        print(f"Approve appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/appointments/<appointment_id>/reject', methods=['POST'])
@login_required
def admin_reject_appointment(appointment_id):
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({'success': True, 'message': 'Appointment rejected'}), 200
        
    except Exception as e:
        print(f"Reject appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ADMIN USERS
# ============================================

@app.route('/api/admin/users', methods=['GET'])
@login_required
def admin_get_users():
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({
            'success': True,
            'users': [
                {
                    'user_id': '1',
                    'full_name': 'Demo Donor',
                    'email': 'demo@example.com',
                    'phone_number': '+254712345678',
                    'blood_type': 'O+',
                    'is_active': True,
                    'created_at': '2025-03-30'
                }
            ]
        })
        
    except Exception as e:
        print(f"Admin get users error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<user_id>', methods=['PUT'])
@login_required
def admin_update_user(user_id):
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({'success': True, 'message': 'User updated successfully'})
        
    except Exception as e:
        print(f"Admin update user error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@login_required
def admin_delete_user(user_id):
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({'success': True, 'message': 'User deleted successfully'})
        
    except Exception as e:
        print(f"Admin delete user error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ADMIN BLOOD STOCK
# ============================================

@app.route('/api/admin/blood-stock', methods=['GET'])
@login_required
def admin_get_blood_stock():
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({
            'success': True,
            'stock': [
                {'id': '1', 'hospital_name': 'Kenyatta National Hospital', 'blood_type': 'A+', 'units_available': 15, 'status': 'adequate', 'last_updated': '2025-03-31'},
                {'id': '2', 'hospital_name': 'Kenyatta National Hospital', 'blood_type': 'O+', 'units_available': 20, 'status': 'adequate', 'last_updated': '2025-03-31'},
                {'id': '3', 'hospital_name': 'Kenyatta National Hospital', 'blood_type': 'O-', 'units_available': 3, 'status': 'critical', 'last_updated': '2025-03-31'},
                {'id': '4', 'hospital_name': 'MP Shah Hospital', 'blood_type': 'A+', 'units_available': 10, 'status': 'adequate', 'last_updated': '2025-03-31'}
            ]
        })
        
    except Exception as e:
        print(f"Admin get blood stock error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/blood-stock/add', methods=['POST'])
@login_required
def admin_add_blood_stock():
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({'success': True, 'message': 'Blood stock added successfully'})
        
    except Exception as e:
        print(f"Admin add blood stock error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/blood-stock/<stock_id>', methods=['DELETE'])
@login_required
def admin_delete_blood_stock(stock_id):
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({'success': True, 'message': 'Blood stock deleted successfully'})
        
    except Exception as e:
        print(f"Admin delete blood stock error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ADMIN DASHBOARD STATS
# ============================================

@app.route('/api/admin/dashboard-stats', methods=['GET'])
@login_required
def admin_dashboard_stats():
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({
            'success': True,
            'stats': {
                'total_donors': 5,
                'total_hospitals': 2,
                'total_appointments': 3,
                'pending_appointments': 1,
                'total_blood_units': 48,
                'critical_stock': 1
            }
        })
        
    except Exception as e:
        print(f"Admin dashboard stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# HOSPITAL LOGIN
# ============================================

@app.route('/api/hospital/login', methods=['POST'])
def hospital_login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if email == 'hospital@knh.co.ke' and password == 'hospital123':
            session['user_id'] = 'hospital-id'
            session['user_type'] = 'hospital'
            session['hospital_name'] = 'Kenyatta National Hospital'
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'hospital': {'id': 1, 'name': 'Kenyatta National Hospital', 'email': email}
            }), 200
        elif email == 'hospital@mpshah.co.ke' and password == 'hospital123':
            session['user_id'] = 'hospital-id-2'
            session['user_type'] = 'hospital'
            session['hospital_name'] = 'MP Shah Hospital'
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'hospital': {'id': 2, 'name': 'MP Shah Hospital', 'email': email}
            }), 200
        
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"Hospital login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# HOSPITAL APPOINTMENTS
# ============================================

@app.route('/api/hospital/appointments', methods=['GET'])
@login_required
def hospital_get_appointments():
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({
            'success': True,
            'appointments': [
                {
                    'id': '1',
                    'donor_name': 'Demo Donor',
                    'donor_email': 'demo@example.com',
                    'donor_phone': '+254712345678',
                    'blood_type': 'O+',
                    'appointment_date': '2025-04-05',
                    'appointment_time': '10:00 AM',
                    'status': 'pending'
                }
            ]
        })
        
    except Exception as e:
        print(f"Hospital get appointments error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/appointments/<appointment_id>/approve', methods=['POST'])
@login_required
def hospital_approve_appointment(appointment_id):
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({'success': True, 'message': 'Appointment approved successfully'}), 200
        
    except Exception as e:
        print(f"Hospital approve appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/appointments/<appointment_id>/reject', methods=['POST'])
@login_required
def hospital_reject_appointment(appointment_id):
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({'success': True, 'message': 'Appointment rejected'}), 200
        
    except Exception as e:
        print(f"Hospital reject appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# HOSPITAL BLOOD STOCK
# ============================================

@app.route('/api/hospital/blood-stock', methods=['GET'])
@login_required
def hospital_get_blood_stock():
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({
            'success': True,
            'stock': [
                {'id': '1', 'blood_type': 'A+', 'units_available': 15, 'status': 'adequate', 'last_updated': '2025-03-31'},
                {'id': '2', 'blood_type': 'O+', 'units_available': 20, 'status': 'adequate', 'last_updated': '2025-03-31'},
                {'id': '3', 'blood_type': 'O-', 'units_available': 3, 'status': 'critical', 'last_updated': '2025-03-31'}
            ]
        })
        
    except Exception as e:
        print(f"Hospital get blood stock error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/blood-stock', methods=['POST'])
@login_required
def hospital_add_blood_stock():
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({'success': True, 'message': 'Blood stock added successfully'}), 200
        
    except Exception as e:
        print(f"Hospital add blood stock error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/blood-stock/<stock_id>', methods=['DELETE'])
@login_required
def hospital_delete_blood_stock(stock_id):
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({'success': True, 'message': 'Blood stock deleted successfully'}), 200
        
    except Exception as e:
        print(f"Hospital delete blood stock error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# HOSPITAL DOCTORS
# ============================================

@app.route('/api/hospital/doctors', methods=['GET'])
@login_required
def hospital_get_doctors():
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({
            'success': True,
            'doctors': [
                {'id': '1', 'name': 'Dr. Sarah Mwangi', 'email': 'sarah@knh.co.ke', 'phone': '+254712345678', 'specialization': 'Hematology'},
                {'id': '2', 'name': 'Dr. James Otieno', 'email': 'james@knh.co.ke', 'phone': '+254723456789', 'specialization': 'Transfusion Medicine'}
            ]
        })
        
    except Exception as e:
        print(f"Hospital get doctors error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/doctors', methods=['POST'])
@login_required
def hospital_add_doctor():
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({'success': True, 'message': 'Doctor added successfully'}), 201
        
    except Exception as e:
        print(f"Hospital add doctor error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/doctors/<doctor_id>', methods=['DELETE'])
@login_required
def hospital_delete_doctor(doctor_id):
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return jsonify({'success': True, 'message': 'Doctor deleted successfully'}), 200
        
    except Exception as e:
        print(f"Hospital delete doctor error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# LOGOUT
# ============================================

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    
    print("\n" + "=" * 70)
    print("🩸  UHAI DAMU - Blood Donation Platform (Demo Mode)")
    print("=" * 70)
    print(f"📅  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    print(f"🌐  Website: http://localhost:{port}")
    print(f"🔧  API Test: http://localhost:{port}/api/test")
    print(f"👑  Admin Login: http://localhost:{port}/admin-login.html")
    print(f"📝  Register: http://localhost:{port}/register.html")
    print(f"🏥  Hospital: http://localhost:{port}/hospital-dashboard.html")
    print(f"🩸  Donor: http://localhost:{port}/donor-dashboard.html")
    print("-" * 70)
    print("🔑  Demo Credentials:")
    print("    👑 Admin: admin@uhai-damu.co.ke / Admin123")
    print("    🩸 Donor: any email / any password")
    print("    🏥 Hospital: hospital@knh.co.ke / hospital123")
    print("=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)