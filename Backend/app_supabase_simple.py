"""
UHAI DAMU - Supabase Backend (Using HTTP Requests)
No extra packages needed - just Flask and requests
"""

from flask import Flask, send_from_directory, jsonify, request, session
from flask_cors import CORS
import os
import bcrypt
import requests
from datetime import datetime
import re

# Create Flask app
app = Flask(__name__, static_folder='../', static_url_path='')
app.secret_key = 'uhai-damu-secret-key-2025'
CORS(app, supports_credentials=True, origins=['http://localhost:5001', 'http://127.0.0.1:5001'])

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================
# SUPABASE CONFIGURATION 
# ============================================
SUPABASE_URL = "https://ruegihawtsprdpkzksms.supabase.co"  
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ1ZWdpaGF3dHNwcmRwa3prc21zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3MjQwODYsImV4cCI6MjA5MDMwMDA4Nn0.YxUkWDXltr4mmuGVMiujgBcydambnVdGOC8ToOZLeNc"  

def supabase_request(method, endpoint, data=None):
    """Make HTTP request to Supabase REST API"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, json=data)
        else:
            return None
        
        return response.json() if response.status_code < 400 else None
    except Exception as e:
        print(f"Supabase error: {e}")
        return None

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
    return send_from_directory(BASE_DIR, filename)

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Uhai Damu API is running',
        'timestamp': datetime.now().isoformat(),
        'database': 'Supabase'
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
        'counties': ['Nairobi City County', 'Kiambu County']
    })

@app.route('/api/constituencies/<county>')
def get_constituencies(county):
    constituencies = {
        'Nairobi City County': [
            'Westlands', 'Starehe', 'Kasarani', 'Langata', 'Embakasi', 'Dagoretti'
        ],
        'Kiambu County': [
            'Thika', 'Ruiru', 'Kiambaa', 'Kikuyu', 'Limuru', 'Juja'
        ]
    }
    return jsonify({'constituencies': constituencies.get(county, [])})

@app.route('/api/blood-types')
def get_blood_types():
    return jsonify({'blood_types': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']})

# ============================================
# BLOOD STOCK (Sample Data)
# ============================================

@app.route('/api/blood-stock/<county>/<constituency>')
def get_blood_stock(county, constituency):
    hospitals = [
        {
            'name': 'Kenyatta National Hospital',
            'contact_phone': '+254 20 271 3344',
            'stock': [
                {'blood_type': 'A+', 'units_available': 15, 'status': 'adequate'},
                {'blood_type': 'O+', 'units_available': 20, 'status': 'adequate'},
                {'blood_type': 'O-', 'units_available': 3, 'status': 'critical'}
            ]
        },
        {
            'name': 'MP Shah Hospital',
            'contact_phone': '+254 20 429 4000',
            'stock': [
                {'blood_type': 'A+', 'units_available': 10, 'status': 'adequate'},
                {'blood_type': 'B+', 'units_available': 5, 'status': 'low'}
            ]
        }
    ]
    return jsonify(hospitals)

# ============================================
# DONOR REGISTRATION
# ============================================

@app.route('/api/donor/register', methods=['POST'])
def donor_register():
    try:
        data = request.json
        print(f"Registration: {data.get('email')}")
        
        # Simple validation
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        # Check if user exists in Supabase
        existing = supabase_request('GET', f'users?email=eq.{data["email"]}')
        
        if existing and len(existing) > 0:
            return jsonify({'success': False, 'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        full_name = f"{data['first_name']} {data['last_name']}"
        
        # Insert into Supabase
        new_user = supabase_request('POST', 'users', {
            'email': data['email'],
            'password_hash': password_hash,
            'full_name': full_name,
            'phone_number': data['phone'],
            'blood_type': data['blood_type'],
            'county': data.get('county'),
            'constituency': data.get('constituency'),
            'weight': data.get('weight'),
            'height': data.get('height'),
            'user_type': 'donor'
        })
        
        return jsonify({
            'success': True,
            'message': 'Registration successful!'
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# DONOR LOGIN
# ============================================

@app.route('/api/donor/login', methods=['POST'])
def donor_login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        # Get donor from Supabase
        donor = supabase_request('GET', f'users?email=eq.{email}&user_type=eq.donor&is_active=eq.true')
        
        if not donor or len(donor) == 0:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        donor = donor[0]
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), donor['password_hash'].encode('utf-8')):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Format names
        name_parts = donor['full_name'].split()
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[-1] if len(name_parts) > 1 else ''
        
        donor_data = {
            'id': donor['user_id'],
            'firstName': first_name,
            'lastName': last_name,
            'email': donor['email'],
            'phone': donor['phone_number'],
            'bloodType': donor['blood_type'],
            'county': donor['county'],
            'constituency': donor['constituency'],
            'weight': donor['weight'],
            'height': donor['height']
        }
        
        session['donor_id'] = donor['user_id']
        session['donor_email'] = donor['email']
        session['donor_name'] = donor['full_name']
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'donor': donor_data
        }), 200
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# GET DONOR PROFILE
# ============================================

@app.route('/api/donor/profile', methods=['GET'])
def get_donor_profile():
    try:
        donor_id = session.get('donor_id')
        
        if not donor_id:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        donor = supabase_request('GET', f'users?user_id=eq.{donor_id}')
        
        if not donor or len(donor) == 0:
            return jsonify({'success': False, 'error': 'Donor not found'}), 404
        
        donor = donor[0]
        
        name_parts = donor['full_name'].split()
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[-1] if len(name_parts) > 1 else ''
        
        donor_data = {
            'id': donor['user_id'],
            'firstName': first_name,
            'lastName': last_name,
            'email': donor['email'],
            'phone': donor['phone_number'],
            'bloodType': donor['blood_type'],
            'county': donor['county'],
            'constituency': donor['constituency'],
            'weight': donor['weight'],
            'height': donor['height']
        }
        
        return jsonify({
            'success': True,
            'donor': donor_data
        })
        
    except Exception as e:
        print(f"Profile error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# APPOINTMENTS
# ============================================

@app.route('/api/appointments/create', methods=['POST'])
def create_appointment():
    try:
        donor_id = session.get('donor_id')
        
        if not donor_id:
            return jsonify({'success': False, 'error': 'Please login first'}), 401
        
        data = request.json
        hospital_name = data.get('hospital')
        appointment_date = data.get('date')
        appointment_time = data.get('time')
        
        # Get donor details
        donor = supabase_request('GET', f'users?user_id=eq.{donor_id}')
        
        if not donor or len(donor) == 0:
            return jsonify({'success': False, 'error': 'Donor not found'}), 404
        
        donor = donor[0]
        
        # Create appointment
        supabase_request('POST', 'appointments', {
            'donor_id': donor['user_id'],
            'donor_name': donor['full_name'],
            'donor_email': donor['email'],
            'donor_phone': donor['phone_number'],
            'blood_type': donor['blood_type'],
            'hospital_name': hospital_name,
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'status': 'pending'
        })
        
        return jsonify({
            'success': True,
            'message': 'Appointment request submitted successfully'
        }), 201
        
    except Exception as e:
        print(f"Appointment error: {e}")
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
            session['admin_logged_in'] = True
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🩸  UHAI DAMU - Supabase Backend")
    print("=" * 60)
    print("🌐  Website: http://localhost:5001")
    print("🔧  API Test: http://localhost:5001/api/test")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)