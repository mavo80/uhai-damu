"""
UHAI DAMU - Blood Donation Platform
Complete Flask Application for PythonAnywhere Deployment
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
import uuid
import traceback
import sys

# ============================================
# PYTHONANYWHERE COMPATIBILITY SETUP
# ============================================
print(f"🐍 Python version: {sys.version}")
print(f"📍 Running on PythonAnywhere: {'pythonanywhere' in sys.prefix}")

# Load environment variables (optional - for local development)
load_dotenv()

# Create Flask app
app = Flask(__name__, static_folder='.', static_url_path='')

# Session configuration for PythonAnywhere
app.secret_key = os.environ.get('SECRET_KEY', 'uhai-damu-secret-key-2025')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
app.config['SESSION_TYPE'] = 'filesystem'

# Enable CORS (PythonAnywhere compatible)
CORS(app, supports_credentials=True, origins=[
    'http://localhost:5001',
    'http://127.0.0.1:5001',
    'https://*.pythonanywhere.com',
    'https://*.pythonanywhere.com/',
    '*'
])

# Base directory for serving files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"📁 Serving files from: {BASE_DIR}")

# ============================================
# SUPABASE CONFIGURATION
# ============================================
SUPABASE_URL = "https://tnrgregvmythjrutbtou.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRucmdyZWd2bXl0aGpydXRidG91Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ4ODI5MzAsImV4cCI6MjA5MDQ1ODkzMH0.RmK-IjHEvxL5O01IUHZXm40H3R6z8p_K464H7XHLkww"

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
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=30)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=30)
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
    """Serve homepage"""
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    """Serve any HTML/CSS/JS file"""
    # Security: prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        return "Invalid path", 400
    
    # Allowed file extensions
    allowed_extensions = ['.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.json', '.txt']
    
    try:
        # Check if file has allowed extension
        if any(filename.endswith(ext) for ext in allowed_extensions):
            return send_from_directory(BASE_DIR, filename)
        else:
            return send_from_directory(BASE_DIR, filename)
    except Exception as e:
        print(f"File not found: {filename} - {e}")
        return f"File not found: {filename}", 404

# ============================================
# API ENDPOINTS
# ============================================
@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Uhai Damu API is running',
        'timestamp': datetime.now().isoformat(),
        'server': 'PythonAnywhere'
    })

@app.route('/api/test')
def test():
    """Test endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

# ============================================
# LOCATION DATA
# ============================================
@app.route('/api/counties')
def get_counties():
    """Get list of counties"""
    return jsonify({
        'success': True,
        'counties': [
            {'id': 'nairobi', 'name': 'Nairobi City County'},
            {'id': 'kiambu', 'name': 'Kiambu County'}
        ]
    })

@app.route('/api/constituencies/<county>')
def get_constituencies(county):
    """Get constituencies for a specific county"""
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
    
    return jsonify({
        'success': True,
        'constituencies': constituencies.get(county_name, [])
    })

@app.route('/api/blood-types')
def get_blood_types():
    """Get list of blood types"""
    return jsonify({
        'success': True,
        'blood_types': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    })

# ============================================
# HOSPITALS LIST
# ============================================
@app.route('/api/hospitals/list', methods=['GET'])
def get_hospitals_list():
    """Get list of all verified hospitals"""
    try:
        hospitals = supabase_request('GET', 'hospitals?select=id,hospital_name&is_verified=eq.true')
        
        if not hospitals:
            return jsonify({'success': True, 'hospitals': []})
        
        result = [{'id': h['id'], 'name': h['hospital_name']} for h in hospitals]
        
        return jsonify({'success': True, 'hospitals': result})
        
    except Exception as e:
        print(f"Get hospitals list error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# BLOOD STOCK (Public View)
# ============================================
@app.route('/api/blood-stock/<county>/<constituency>')
def get_blood_stock(county, constituency):
    """Get blood stock for a specific location"""
    try:
        hospitals = supabase_request('GET', f'hospitals?select=*,users!inner(*)&users.county=eq.{county}')
        
        if not hospitals:
            return jsonify({'hospitals': []})
        
        result = []
        for hospital in hospitals:
            stock = supabase_request('GET', f'blood_stock?select=*&hospital_id=eq.{hospital["id"]}')
            result.append({
                'id': hospital['id'],
                'name': hospital['hospital_name'],
                'contact_phone': hospital.get('contact_phone', 'N/A'),
                'address': hospital.get('address', 'N/A'),
                'stock': stock or []
            })
        
        return jsonify({'success': True, 'hospitals': result})
        
    except Exception as e:
        print(f"Blood stock error: {e}")
        return jsonify({'hospitals': []})

# ============================================
# DONOR REGISTRATION
# ============================================
@app.route('/api/donor/register', methods=['POST'])
def donor_register():
    """Register a new donor"""
    try:
        data = request.json
        
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
            return jsonify({'success': False, 'error': 'Invalid phone number. Use +2547XXXXXXXX or 07XXXXXXXX'}), 400
        
        # Check if user exists
        existing = supabase_request('GET', f'users?email=eq.{data["email"]}')
        if existing and len(existing) > 0:
            return jsonify({'success': False, 'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        full_name = f"{data['first_name']} {data['last_name']}"
        
        user_id = str(uuid.uuid4())
        
        # Create user
        user_result = supabase_request('POST', 'users', {
            'id': user_id,
            'email': data['email'],
            'password_hash': password_hash,
            'full_name': full_name,
            'phone': data['phone'],
            'user_type': 'donor',
            'county': data.get('county'),
            'created_at': datetime.now().isoformat()
        })
        
        if not user_result:
            return jsonify({'success': False, 'error': 'Failed to create user'}), 500
        
        # Create donor profile
        donor_result = supabase_request('POST', 'donors', {
            'id': user_id,
            'blood_type': data['blood_type'],
            'constituency': data.get('constituency'),
            'weight': data.get('weight'),
            'height': data.get('height'),
            'date_of_birth': data.get('date_of_birth'),
            'is_active': True
        })
        
        if not donor_result:
            supabase_request('DELETE', f'users?id=eq.{user_id}')
            return jsonify({'success': False, 'error': 'Failed to create donor profile'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Registration successful! You can now login.',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# DONOR LOGIN
# ============================================
@app.route('/api/donor/login', methods=['POST'])
def donor_login():
    """Login donor - returns donor profile data"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        # Get donor from database
        user = supabase_request('GET', f'users?email=eq.{email}&user_type=eq.donor')
        
        if not user or len(user) == 0:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        user = user[0]
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Get donor details
        donor = supabase_request('GET', f'donors?id=eq.{user["id"]}')
        donor_data = donor[0] if donor else {}
        
        # Format name
        name_parts = user['full_name'].split()
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[-1] if len(name_parts) > 1 else ''
        
        # Set session
        session['user_id'] = user['id']
        session['user_type'] = 'donor'
        session['user_email'] = user['email']
        session['user_name'] = user['full_name']
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'donor': {
                'id': user['id'],
                'firstName': first_name,
                'lastName': last_name,
                'email': user['email'],
                'phone': user['phone'],
                'bloodType': donor_data.get('blood_type'),
                'county': user.get('county'),
                'constituency': donor_data.get('constituency'),
                'weight': donor_data.get('weight'),
                'height': donor_data.get('height'),
                'registrationDate': user.get('created_at'),
                'donationStatus': {
                    'tattoosLast6Months': donor_data.get('tattoos_last_6months', False),
                    'alcoholLast24Hours': donor_data.get('alcohol_last_24hours', False),
                    'medication': donor_data.get('on_medication', False),
                    'healthIssues': donor_data.get('health_issues', False)
                }
            }
        }), 200
            
    except Exception as e:
        print(f"Login error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# GET DONOR PROFILE
# ============================================
@app.route('/api/donor/profile', methods=['GET'])
@login_required
def get_donor_profile():
    """Get current donor profile from session"""
    try:
        user_id = session.get('user_id')
        
        user = supabase_request('GET', f'users?id=eq.{user_id}')
        if not user or len(user) == 0:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user = user[0]
        donor = supabase_request('GET', f'donors?id=eq.{user_id}')
        donor_data = donor[0] if donor else {}
        
        name_parts = user['full_name'].split()
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[-1] if len(name_parts) > 1 else ''
        
        return jsonify({
            'success': True,
            'donor': {
                'id': user['id'],
                'firstName': first_name,
                'lastName': last_name,
                'email': user['email'],
                'phone': user['phone'],
                'bloodType': donor_data.get('blood_type'),
                'county': user.get('county'),
                'constituency': donor_data.get('constituency'),
                'weight': donor_data.get('weight'),
                'height': donor_data.get('height'),
                'registrationDate': user.get('created_at'),
                'donationStatus': {
                    'tattoosLast6Months': donor_data.get('tattoos_last_6months', False),
                    'alcoholLast24Hours': donor_data.get('alcohol_last_24hours', False),
                    'medication': donor_data.get('on_medication', False),
                    'healthIssues': donor_data.get('health_issues', False)
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
    """Update donor donation status"""
    try:
        user_id = session.get('user_id')
        data = request.json
        
        supabase_request('PATCH', f'donors?id=eq.{user_id}', {
            'tattoos_last_6months': data.get('tattoosLast6Months', False),
            'alcohol_last_24hours': data.get('alcoholLast24Hours', False),
            'on_medication': data.get('medication', False),
            'health_issues': data.get('healthIssues', False),
            'weight': data.get('weight'),
            'height': data.get('height')
        })
        
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
    """Create a new appointment request"""
    try:
        donor_id = session.get('user_id')
        data = request.json
        
        hospital_name = data.get('hospital_id')
        appointment_date = data.get('date')
        appointment_time = data.get('time')
        notes = data.get('notes', '')
        
        if not hospital_name or not appointment_date or not appointment_time:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get donor details
        donor = supabase_request('GET', f'donors?id=eq.{donor_id}')
        if not donor or len(donor) == 0:
            return jsonify({'success': False, 'error': 'Donor not found'}), 404
        
        donor_user = supabase_request('GET', f'users?id=eq.{donor_id}')
        blood_type = donor[0]['blood_type']
        
        # Get hospital ID from name
        hospitals = supabase_request('GET', f'hospitals?select=id&hospital_name=eq.{hospital_name}')
        if hospitals and len(hospitals) > 0:
            actual_hospital_id = hospitals[0]['id']
        else:
            actual_hospital_id = hospital_name
        
        appointment_id = str(uuid.uuid4())
        
        # Create appointment
        result = supabase_request('POST', 'appointments', {
            'id': appointment_id,
            'donor_id': donor_id,
            'hospital_id': actual_hospital_id,
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'notes': notes,
            'blood_type': blood_type,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        })
        
        if not result:
            return jsonify({'success': False, 'error': 'Failed to create appointment'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Appointment request submitted successfully',
            'appointment_id': appointment_id
        }), 201
        
    except Exception as e:
        print(f"Appointment error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/appointments/my', methods=['GET'])
@login_required
def get_my_appointments():
    """Get appointments for logged-in donor"""
    try:
        donor_id = session.get('user_id')
        
        appointments = supabase_request('GET', f'appointments?select=*,hospitals!inner(*)&donor_id=eq.{donor_id}&order=created_at.desc')
        
        result = []
        for a in (appointments or []):
            hospital_data = a.get('hospitals', {}) if a.get('hospitals') else {}
            result.append({
                'id': a.get('id'),
                'hospital_name': hospital_data.get('hospital_name') if hospital_data else 'Unknown Hospital',
                'appointment_date': a.get('appointment_date'),
                'appointment_time': a.get('appointment_time'),
                'status': a.get('status'),
                'created_at': a.get('created_at')
            })
        
        return jsonify({
            'success': True,
            'appointments': result
        })
        
    except Exception as e:
        print(f"Get appointments error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ADMIN LOGIN
# ============================================
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        # Check database for admin
        user = supabase_request('GET', f'users?email=eq.{email}&user_type=eq.admin')
        
        if user and len(user) > 0:
            user = user[0]
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                session['user_id'] = user['id']
                session['user_type'] = 'admin'
                session['user_name'] = user['full_name']
                session.permanent = True
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'admin': {
                        'id': user['id'],
                        'email': user['email'],
                        'full_name': user['full_name'],
                        'role': 'super_admin'
                    }
                }), 200
        
        # Fallback hardcoded admin
        if email == 'admin@uhai-damu.co.ke' and password == 'Admin123':
            session['user_id'] = '11111111-1111-1111-1111-111111111111'
            session['user_type'] = 'admin'
            session['user_name'] = 'Super Admin'
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'admin': {
                    'id': '11111111-1111-1111-1111-111111111111',
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
    """Admin logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

# ============================================
# ADMIN APPOINTMENTS
# ============================================
@app.route('/api/admin/appointments', methods=['GET'])
@login_required
def admin_get_appointments():
    """Get all appointments for admin"""
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        appointments = supabase_request('GET', 'appointments?order=created_at.desc')
        
        if not appointments:
            return jsonify({'success': True, 'appointments': []})
        
        result = []
        for a in appointments:
            donor_user = supabase_request('GET', f'users?id=eq.{a["donor_id"]}')
            donor_user_data = donor_user[0] if donor_user else {}
            
            hospital = supabase_request('GET', f'hospitals?id=eq.{a["hospital_id"]}')
            hospital_data = hospital[0] if hospital else {}
            
            result.append({
                'id': a.get('id'),
                'donor_name': donor_user_data.get('full_name', 'Unknown'),
                'donor_email': donor_user_data.get('email', 'No email'),
                'donor_phone': donor_user_data.get('phone', 'N/A'),
                'blood_type': a.get('blood_type', 'N/A'),
                'hospital_name': hospital_data.get('hospital_name', 'Unknown'),
                'appointment_date': a.get('appointment_date'),
                'appointment_time': a.get('appointment_time'),
                'status': a.get('status'),
                'created_at': a.get('created_at')
            })
        
        return jsonify({
            'success': True,
            'appointments': result,
            'count': len(result)
        })
        
    except Exception as e:
        print(f"Admin get appointments error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/appointments/<appointment_id>/approve', methods=['POST'])
@login_required
def admin_approve_appointment(appointment_id):
    """Admin approve appointment"""
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        supabase_request('PATCH', f'appointments?id=eq.{appointment_id}', {
            'status': 'approved',
            'updated_at': datetime.now().isoformat()
        })
        
        return jsonify({'success': True, 'message': 'Appointment approved successfully'}), 200
        
    except Exception as e:
        print(f"Approve appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/appointments/<appointment_id>/reject', methods=['POST'])
@login_required
def admin_reject_appointment(appointment_id):
    """Admin reject appointment"""
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        supabase_request('PATCH', f'appointments?id=eq.{appointment_id}', {
            'status': 'rejected',
            'updated_at': datetime.now().isoformat()
        })
        
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
    """Get all donors for admin"""
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        users = supabase_request('GET', f'users?select=*,donors(*)&user_type=eq.donor&order=created_at.desc')
        
        result = []
        for u in (users or []):
            donor = u.get('donors', {}) if u.get('donors') else {}
            if isinstance(donor, list) and len(donor) > 0:
                donor = donor[0]
            
            result.append({
                'user_id': u.get('id'),
                'full_name': u.get('full_name'),
                'email': u.get('email'),
                'phone_number': u.get('phone'),
                'blood_type': donor.get('blood_type') if donor else None,
                'is_active': donor.get('is_active', True) if donor else True,
                'created_at': u.get('created_at'),
                'county': u.get('county'),
                'constituency': donor.get('constituency') if donor else None
            })
        
        return jsonify({
            'success': True,
            'users': result
        })
        
    except Exception as e:
        print(f"Admin get users error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<user_id>', methods=['PUT'])
@login_required
def admin_update_user(user_id):
    """Update user status (activate/deactivate)"""
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        is_active = data.get('is_active')
        
        result = supabase_request('PATCH', f'donors?id=eq.{user_id}', {
            'is_active': is_active
        })
        
        if result is not None:
            return jsonify({'success': True, 'message': 'User updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update user'}), 500
        
    except Exception as e:
        print(f"Admin update user error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@login_required
def admin_delete_user(user_id):
    """Delete a user completely"""
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        print(f"=" * 50)
        print(f"🗑️ Admin deleting user: {user_id}")
        print(f"=" * 50)
        
        # Get user details for logging
        user = supabase_request('GET', f'users?select=email,full_name&id=eq.{user_id}')
        if user and len(user) > 0:
            print(f"  📧 Email: {user[0].get('email')}")
            print(f"  👤 Name: {user[0].get('full_name')}")
        else:
            print(f"  ⚠️ User not found in database")
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Delete in correct order to handle foreign key constraints
        print(f"  📅 Deleting appointments...")
        supabase_request('DELETE', f'appointments?donor_id=eq.{user_id}')
        
        print(f"  🩸 Deleting donor record...")
        supabase_request('DELETE', f'donors?id=eq.{user_id}')
        
        print(f"  👤 Deleting user record...")
        result = supabase_request('DELETE', f'users?id=eq.{user_id}')
        
        if result is not None:
            print(f"  ✅ User deleted successfully!")
            return jsonify({'success': True, 'message': 'User deleted successfully'})
        else:
            print(f"  ❌ Failed to delete user")
            return jsonify({'success': False, 'error': 'Failed to delete user'}), 500
        
    except Exception as e:
        print(f"Admin delete user error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ADMIN BLOOD STOCK
# ============================================
@app.route('/api/admin/blood-stock', methods=['GET'])
@login_required
def admin_get_blood_stock():
    """Get all blood stock for admin"""
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        stock = supabase_request('GET', f'blood_stock?select=*,hospitals!inner(*)&order=hospital_id')
        
        result = []
        for s in (stock or []):
            hospital = s.get('hospitals', {}) if s.get('hospitals') else {}
            result.append({
                'id': s.get('id'),
                'hospital_name': hospital.get('hospital_name'),
                'blood_type': s.get('blood_type'),
                'units_available': s.get('units_available'),
                'status': s.get('status'),
                'last_updated': s.get('last_updated')
            })
        
        return jsonify({
            'success': True,
            'stock': result
        })
        
    except Exception as e:
        print(f"Admin get blood stock error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/blood-stock/add', methods=['POST'])
@login_required
def admin_add_blood_stock():
    """Add blood stock"""
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        hospital_name = data.get('hospital_name')
        blood_type = data.get('blood_type')
        units = data.get('units_available')
        
        hospitals = supabase_request('GET', f'hospitals?select=id&hospital_name=eq.{hospital_name}')
        
        if not hospitals or len(hospitals) == 0:
            return jsonify({'success': False, 'error': 'Hospital not found'}), 404
        
        hospital_id = hospitals[0]['id']
        
        existing = supabase_request('GET', f'blood_stock?select=*&hospital_id=eq.{hospital_id}&blood_type=eq.{blood_type}')
        
        if existing and len(existing) > 0:
            new_units = existing[0]['units_available'] + units
            supabase_request('PATCH', f'blood_stock?id=eq.{existing[0]["id"]}', {
                'units_available': new_units,
                'last_updated': datetime.now().isoformat()
            })
        else:
            supabase_request('POST', 'blood_stock', {
                'id': str(uuid.uuid4()),
                'hospital_id': hospital_id,
                'blood_type': blood_type,
                'units_available': units
            })
        
        return jsonify({'success': True, 'message': 'Blood stock added successfully'})
        
    except Exception as e:
        print(f"Admin add blood stock error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/blood-stock/<stock_id>', methods=['DELETE'])
@login_required
def admin_delete_blood_stock(stock_id):
    """Delete blood stock"""
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        supabase_request('DELETE', f'blood_stock?id=eq.{stock_id}')
        
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
    """Get dashboard statistics for admin"""
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        donors = supabase_request('GET', f'users?select=id&user_type=eq.donor')
        hospitals = supabase_request('GET', f'hospitals?select=id')
        appointments = supabase_request('GET', f'appointments?select=id')
        pending = supabase_request('GET', f'appointments?select=id&status=eq.pending')
        
        blood_stock = supabase_request('GET', f'blood_stock?select=units_available')
        total_units = sum(item['units_available'] for item in (blood_stock or []))
        critical_stock = sum(1 for item in (blood_stock or []) if item.get('units_available', 0) <= 3)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_donors': len(donors) if donors else 0,
                'total_hospitals': len(hospitals) if hospitals else 0,
                'total_appointments': len(appointments) if appointments else 0,
                'pending_appointments': len(pending) if pending else 0,
                'total_blood_units': total_units,
                'critical_stock': critical_stock
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
    """Hospital login endpoint"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        # Check database for hospital user
        user = supabase_request('GET', f'users?email=eq.{email}&user_type=eq.hospital')
        
        if user and len(user) > 0:
            user = user[0]
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                hospital = supabase_request('GET', f'hospitals?id=eq.{user["id"]}')
                
                session['user_id'] = user['id']
                session['user_type'] = 'hospital'
                session['hospital_name'] = hospital[0]['hospital_name'] if hospital else user['full_name']
                session.permanent = True
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'hospital': {
                        'id': user['id'],
                        'name': hospital[0]['hospital_name'] if hospital else user['full_name'],
                        'email': user['email']
                    }
                }), 200
        
        # Hardcoded hospital credentials (fallback)
        if email == 'hospital@knh.co.ke' and password == 'hospital123':
            session['user_id'] = '22222222-2222-2222-2222-222222222222'
            session['user_type'] = 'hospital'
            session['hospital_name'] = 'Kenyatta National Hospital'
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'hospital': {'id': '22222222-2222-2222-2222-222222222222', 'name': 'Kenyatta National Hospital', 'email': email}
            }), 200
        elif email == 'hospital@mpshah.co.ke' and password == 'hospital123':
            session['user_id'] = '33333333-3333-3333-3333-333333333333'
            session['user_type'] = 'hospital'
            session['hospital_name'] = 'MP Shah Hospital'
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'hospital': {'id': '33333333-3333-3333-3333-333333333333', 'name': 'MP Shah Hospital', 'email': email}
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
    """Get appointments for this hospital"""
    try:
        hospital_id = session.get('user_id')
        
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        appointments = supabase_request('GET', f'appointments?select=*&hospital_id=eq.{hospital_id}&order=created_at.desc')
        
        result = []
        for a in (appointments or []):
            donor_user = supabase_request('GET', f'users?id=eq.{a["donor_id"]}')
            donor_user_data = donor_user[0] if donor_user else {}
            
            result.append({
                'id': a.get('id'),
                'donor_name': donor_user_data.get('full_name', 'Unknown'),
                'donor_email': donor_user_data.get('email', 'No email'),
                'donor_phone': donor_user_data.get('phone', 'N/A'),
                'blood_type': a.get('blood_type'),
                'appointment_date': a.get('appointment_date'),
                'appointment_time': a.get('appointment_time'),
                'status': a.get('status'),
                'notes': a.get('notes'),
                'created_at': a.get('created_at')
            })
        
        return jsonify({
            'success': True,
            'appointments': result
        })
        
    except Exception as e:
        print(f"Hospital get appointments error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/appointments/<appointment_id>/approve', methods=['POST'])
@login_required
def hospital_approve_appointment(appointment_id):
    """Hospital approve appointment"""
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        supabase_request('PATCH', f'appointments?id=eq.{appointment_id}', {
            'status': 'approved',
            'updated_at': datetime.now().isoformat()
        })
        
        return jsonify({'success': True, 'message': 'Appointment approved successfully'}), 200
        
    except Exception as e:
        print(f"Hospital approve appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/appointments/<appointment_id>/reject', methods=['POST'])
@login_required
def hospital_reject_appointment(appointment_id):
    """Hospital reject appointment"""
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        supabase_request('PATCH', f'appointments?id=eq.{appointment_id}', {
            'status': 'rejected',
            'updated_at': datetime.now().isoformat()
        })
        
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
    """Get blood stock for this hospital"""
    try:
        hospital_id = session.get('user_id')
        
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        stock = supabase_request('GET', f'blood_stock?select=*&hospital_id=eq.{hospital_id}')
        
        return jsonify({
            'success': True,
            'stock': stock or []
        })
        
    except Exception as e:
        print(f"Hospital get blood stock error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/blood-stock', methods=['POST'])
@login_required
def hospital_add_blood_stock():
    """Add blood stock for this hospital"""
    try:
        hospital_id = session.get('user_id')
        
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        blood_type = data.get('blood_type')
        units = data.get('units')
        
        if not blood_type or not units:
            return jsonify({'success': False, 'error': 'Blood type and units required'}), 400
        
        existing = supabase_request('GET', f'blood_stock?select=*&hospital_id=eq.{hospital_id}&blood_type=eq.{blood_type}')
        
        if existing and len(existing) > 0:
            new_units = existing[0]['units_available'] + units
            supabase_request('PATCH', f'blood_stock?id=eq.{existing[0]["id"]}', {
                'units_available': new_units,
                'last_updated': datetime.now().isoformat()
            })
        else:
            supabase_request('POST', 'blood_stock', {
                'id': str(uuid.uuid4()),
                'hospital_id': hospital_id,
                'blood_type': blood_type,
                'units_available': units
            })
        
        return jsonify({'success': True, 'message': 'Blood stock updated successfully'}), 200
        
    except Exception as e:
        print(f"Hospital add blood stock error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/blood-stock/<stock_id>', methods=['DELETE'])
@login_required
def hospital_delete_blood_stock(stock_id):
    """Delete blood stock"""
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        supabase_request('DELETE', f'blood_stock?id=eq.{stock_id}')
        
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
    """Get doctors for this hospital"""
    try:
        hospital_id = session.get('user_id')
        
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        doctors = supabase_request('GET', f'doctors?select=*&hospital_id=eq.{hospital_id}')
        
        return jsonify({
            'success': True,
            'doctors': doctors or []
        })
        
    except Exception as e:
        print(f"Hospital get doctors error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/doctors', methods=['POST'])
@login_required
def hospital_add_doctor():
    """Add a new doctor"""
    try:
        hospital_id = session.get('user_id')
        
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        specialization = data.get('specialization')
        
        if not name or not email:
            return jsonify({'success': False, 'error': 'Name and email required'}), 400
        
        existing = supabase_request('GET', f'doctors?select=id&email=eq.{email}')
        if existing and len(existing) > 0:
            return jsonify({'success': False, 'error': 'Email already registered'}), 409
        
        result = supabase_request('POST', 'doctors', {
            'id': str(uuid.uuid4()),
            'hospital_id': hospital_id,
            'name': name,
            'email': email,
            'phone': phone,
            'specialization': specialization
        })
        
        if not result:
            return jsonify({'success': False, 'error': 'Failed to add doctor'}), 500
        
        return jsonify({'success': True, 'message': 'Doctor added successfully'}), 201
        
    except Exception as e:
        print(f"Hospital add doctor error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/doctors/<doctor_id>', methods=['DELETE'])
@login_required
def hospital_delete_doctor(doctor_id):
    """Delete a doctor"""
    try:
        if session.get('user_type') != 'hospital':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        supabase_request('DELETE', f'doctors?id=eq.{doctor_id}')
        
        return jsonify({'success': True, 'message': 'Doctor deleted successfully'}), 200
        
    except Exception as e:
        print(f"Hospital delete doctor error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# LOGOUT
# ============================================
@app.route('/api/logout', methods=['POST'])
def logout():
    """Generic logout for all user types"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

# ============================================
# ERROR HANDLERS
# ============================================
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ============================================
# RUN SERVER (Local development only)
# ============================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    
    print("\n" + "=" * 70)
    print("🩸  UHAI DAMU - Blood Donation Platform")
    print("=" * 70)
    print(f"📅  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗄️  Database: Supabase PostgreSQL (Live Data)")
    print("-" * 70)
    print(f"🌐  Local URL: http://localhost:{port}")
    print(f"🔧  API Test: http://localhost:{port}/api/test")
    print(f"👑  Admin Login: http://localhost:{port}/admin-login.html")
    print(f"📝  Register: http://localhost:{port}/register.html")
    print(f"🏥  Hospital: http://localhost:{port}/hospital-dashboard.html")
    print(f"🩸  Donor: http://localhost:{port}/donor-dashboard.html")
    print("-" * 70)
    print("=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)