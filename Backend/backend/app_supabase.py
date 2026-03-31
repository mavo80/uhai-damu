"""
UHAI DAMU - Supabase Backend
Blood Donation Platform with Supabase PostgreSQL
"""

from flask import Flask, send_from_directory, jsonify, request, session
from flask_cors import CORS
import os
import bcrypt
from supabase import create_client, Client
from datetime import datetime
import logging
import re

# Create Flask app
app = Flask(__name__, static_folder='../', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'uhai-damu-secret-key-2025')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

# Enable CORS
CORS(app, supports_credentials=True, origins=['http://localhost:5001', 'http://127.0.0.1:5001'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(f"📁 Serving files from: {BASE_DIR}")

# ============================================
# SUPABASE CONFIGURATION
# ============================================

# Replace these with your Supabase credentials!
SUPABASE_URL = "https://ruegihawtsprdpkzksms.supabase.co"  
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ1ZWdpaGF3dHNwcmRwa3prc21zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3MjQwODYsImV4cCI6MjA5MDMwMDA4Nn0.YxUkWDXltr4mmuGVMiujgBcydambnVdGOC8ToOZLeNc"  

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def supabase_query(table, select="*", filters=None, insert=None, update=None, delete=False, order=None):
    """Helper function to query Supabase"""
    try:
        query = supabase.table(table).select(select)
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        if order:
            query = query.order(order, desc=True)
        
        if insert:
            result = supabase.table(table).insert(insert).execute()
            return result.data
        elif update:
            result = supabase.table(table).update(update).eq('id', update.get('id')).execute()
            return result.data
        elif delete:
            result = supabase.table(table).delete().eq('id', delete).execute()
            return result.data
        else:
            result = query.execute()
            return result.data
            
    except Exception as e:
        logger.error(f"Supabase query error: {e}")
        raise e

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
        'success': True,
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
    
    return jsonify({
        'success': True,
        'constituencies': constituencies.get(county_name, [])
    })

@app.route('/api/blood-types')
def get_blood_types():
    return jsonify({
        'success': True,
        'blood_types': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    })

# ============================================
# BLOOD STOCK
# ============================================

@app.route('/api/blood-stock/<county>/<constituency>')
def get_blood_stock(county, constituency):
    # Sample data (in production, fetch from Supabase)
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
    return jsonify(hospitals)

# ============================================
# DONOR REGISTRATION
# ============================================

@app.route('/api/donor/register', methods=['POST'])
def donor_register():
    try:
        data = request.json
        logger.info(f"Registration attempt: {data.get('email')}")
        
        required = ['first_name', 'last_name', 'email', 'phone', 'blood_type', 'password']
        for field in required:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        phone_pattern = r'^(\+254|0)[17]\d{8}$'
        if not re.match(phone_pattern, data['phone']):
            return jsonify({'success': False, 'error': 'Invalid phone number'}), 400
        
        valid_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if data['blood_type'] not in valid_blood_types:
            return jsonify({'success': False, 'error': 'Invalid blood type'}), 400
        
        # Check if user exists in Supabase
        existing = supabase.table('users').select('user_id').eq('email', data['email']).execute()
        
        if existing.data:
            return jsonify({'success': False, 'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        full_name = f"{data['first_name']} {data['last_name']}"
        
        # Insert into Supabase
        new_user = supabase.table('users').insert({
            'email': data['email'],
            'password_hash': password_hash,
            'full_name': full_name,
            'phone_number': data['phone'],
            'blood_type': data['blood_type'],
            'county': data.get('county'),
            'constituency': data.get('constituency'),
            'weight': data.get('weight'),
            'height': data.get('height'),
            'date_of_birth': data.get('date_of_birth'),
            'user_type': 'donor'
        }).execute()
        
        logger.info(f"User registered: {data['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful!',
            'user_id': new_user.data[0]['user_id']
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
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
        donor = supabase.table('users').select('*').eq('email', email).eq('user_type', 'donor').eq('is_active', True).execute()
        
        if not donor.data:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        donor = donor.data[0]
        
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
            'dateOfBirth': donor['date_of_birth'],
            'county': donor['county'],
            'constituency': donor['constituency'],
            'weight': donor['weight'],
            'height': donor['height'],
            'registrationDate': donor['created_at'],
            'donationStatus': {
                'tattoosLast6Months': donor['tattoos_last_6months'] or False,
                'alcoholLast24Hours': donor['alcohol_last_24hours'] or False,
                'medication': donor['on_medication'] or False,
                'healthIssues': donor['health_issues'] or False
            }
        }
        
        session['donor_id'] = donor['user_id']
        session['donor_email'] = donor['email']
        session['donor_name'] = donor['full_name']
        session['user_type'] = 'donor'
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'donor': donor_data
        }), 200
            
    except Exception as e:
        logger.error(f"Login error: {e}")
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
        
        donor = supabase.table('users').select('*').eq('user_id', donor_id).eq('user_type', 'donor').execute()
        
        if not donor.data:
            return jsonify({'success': False, 'error': 'Donor not found'}), 404
        
        donor = donor.data[0]
        
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
            'dateOfBirth': donor['date_of_birth'],
            'county': donor['county'],
            'constituency': donor['constituency'],
            'weight': donor['weight'],
            'height': donor['height'],
            'registrationDate': donor['created_at'],
            'donationStatus': {
                'tattoosLast6Months': donor['tattoos_last_6months'] or False,
                'alcoholLast24Hours': donor['alcohol_last_24hours'] or False,
                'medication': donor['on_medication'] or False,
                'healthIssues': donor['health_issues'] or False
            }
        }
        
        return jsonify({
            'success': True,
            'donor': donor_data
        })
        
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# UPDATE DONOR STATUS
# ============================================

@app.route('/api/donor/status', methods=['PUT'])
def update_donor_status():
    try:
        donor_id = session.get('donor_id')
        
        if not donor_id:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        data = request.json
        
        supabase.table('users').update({
            'tattoos_last_6months': data.get('tattoosLast6Months', False),
            'alcohol_last_24hours': data.get('alcoholLast24Hours', False),
            'on_medication': data.get('medication', False),
            'health_issues': data.get('healthIssues', False),
            'weight': data.get('weight'),
            'height': data.get('height')
        }).eq('user_id', donor_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'Donation status updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Status update error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# APPOINTMENT ENDPOINTS
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
        notes = data.get('notes', '')
        
        if not hospital_name or not appointment_date or not appointment_time:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get donor details
        donor = supabase.table('users').select('user_id, full_name, email, phone_number, blood_type').eq('user_id', donor_id).execute()
        
        if not donor.data:
            return jsonify({'success': False, 'error': 'Donor not found'}), 404
        
        donor = donor.data[0]
        
        # Create appointment
        new_appointment = supabase.table('appointments').insert({
            'donor_id': donor['user_id'],
            'donor_name': donor['full_name'],
            'donor_email': donor['email'],
            'donor_phone': donor['phone_number'],
            'blood_type': donor['blood_type'],
            'hospital_name': hospital_name,
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'notes': notes,
            'status': 'pending'
        }).execute()
        
        return jsonify({
            'success': True,
            'message': 'Appointment request submitted successfully',
            'appointment_id': new_appointment.data[0]['id']
        }), 201
        
    except Exception as e:
        logger.error(f"Create appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/appointments/my', methods=['GET'])
def get_my_appointments():
    try:
        donor_id = session.get('donor_id')
        
        if not donor_id:
            return jsonify({'success': False, 'error': 'Please login first'}), 401
        
        appointments = supabase.table('appointments').select('*').eq('donor_id', donor_id).order('requested_at', desc=True).execute()
        
        return jsonify({
            'success': True,
            'appointments': appointments.data
        })
        
    except Exception as e:
        logger.error(f"Get my appointments error: {e}")
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
        
        admin = supabase.table('users').select('*').eq('email', email).eq('user_type', 'admin').eq('is_active', True).execute()
        
        if not admin.data:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        admin = admin.data[0]
        
        if not bcrypt.checkpw(password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        session['admin_id'] = admin['user_id']
        session['admin_email'] = admin['email']
        session['admin_name'] = admin['full_name']
        session['user_type'] = 'admin'
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'admin': {
                'id': admin['user_id'],
                'email': admin['email'],
                'full_name': admin['full_name'],
                'role': 'super_admin'
            }
        }), 200
            
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

# ============================================
# ADMIN APPOINTMENTS
# ============================================

@app.route('/api/admin/appointments', methods=['GET'])
def admin_get_appointments():
    try:
        admin_id = session.get('admin_id')
        
        if not admin_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        status_filter = request.args.get('status', 'all')
        
        query = supabase.table('appointments').select('*').order('requested_at', desc=True)
        
        if status_filter != 'all':
            query = query.eq('status', status_filter)
        
        appointments = query.execute()
        
        return jsonify({
            'success': True,
            'appointments': appointments.data,
            'count': len(appointments.data)
        })
        
    except Exception as e:
        logger.error(f"Admin get appointments error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/appointments/<int:appointment_id>/approve', methods=['POST'])
def admin_approve_appointment(appointment_id):
    try:
        admin_id = session.get('admin_id')
        
        if not admin_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        supabase.table('appointments').update({
            'status': 'approved',
            'approved_at': datetime.now().isoformat(),
            'approved_by': admin_id
        }).eq('id', appointment_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'Appointment approved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Approve appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/appointments/<int:appointment_id>/reject', methods=['POST'])
def admin_reject_appointment(appointment_id):
    try:
        admin_id = session.get('admin_id')
        
        if not admin_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        supabase.table('appointments').update({
            'status': 'rejected',
            'rejected_at': datetime.now().isoformat()
        }).eq('id', appointment_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'Appointment rejected'
        }), 200
        
    except Exception as e:
        logger.error(f"Reject appointment error: {e}")
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
        
        # Demo hospital credentials
        if email == 'hospital@knh.co.ke' and password == 'hospital123':
            session['hospital_logged_in'] = True
            session['hospital_name'] = 'Kenyatta National Hospital'
            session['hospital_id'] = 1
            session['user_type'] = 'hospital'
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'hospital': {
                    'id': 1,
                    'name': 'Kenyatta National Hospital',
                    'email': email
                }
            })
        elif email == 'hospital@mpshah.co.ke' and password == 'hospital123':
            session['hospital_logged_in'] = True
            session['hospital_name'] = 'MP Shah Hospital'
            session['hospital_id'] = 2
            session['user_type'] = 'hospital'
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'hospital': {
                    'id': 2,
                    'name': 'MP Shah Hospital',
                    'email': email
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Hospital login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/appointments', methods=['GET'])
def hospital_get_appointments():
    try:
        hospital_name = session.get('hospital_name')
        
        if not hospital_name:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        status_filter = request.args.get('status', 'all')
        
        query = supabase.table('appointments').select('*').eq('hospital_name', hospital_name).order('requested_at', desc=True)
        
        if status_filter != 'all':
            query = query.eq('status', status_filter)
        
        appointments = query.execute()
        
        return jsonify({
            'success': True,
            'appointments': appointments.data,
            'count': len(appointments.data)
        })
        
    except Exception as e:
        logger.error(f"Hospital get appointments error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/appointments/<int:appointment_id>/approve', methods=['POST'])
def hospital_approve_appointment(appointment_id):
    try:
        hospital_name = session.get('hospital_name')
        
        if not hospital_name:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Verify appointment belongs to this hospital
        appointment = supabase.table('appointments').select('*').eq('id', appointment_id).eq('hospital_name', hospital_name).execute()
        
        if not appointment.data:
            return jsonify({'success': False, 'error': 'Appointment not found'}), 404
        
        supabase.table('appointments').update({
            'status': 'approved',
            'approved_at': datetime.now().isoformat()
        }).eq('id', appointment_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'Appointment approved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Hospital approve appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/appointments/<int:appointment_id>/reject', methods=['POST'])
def hospital_reject_appointment(appointment_id):
    try:
        hospital_name = session.get('hospital_name')
        
        if not hospital_name:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        appointment = supabase.table('appointments').select('*').eq('id', appointment_id).eq('hospital_name', hospital_name).execute()
        
        if not appointment.data:
            return jsonify({'success': False, 'error': 'Appointment not found'}), 404
        
        supabase.table('appointments').update({
            'status': 'rejected',
            'rejected_at': datetime.now().isoformat()
        }).eq('id', appointment_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'Appointment rejected'
        }), 200
        
    except Exception as e:
        logger.error(f"Hospital reject appointment error: {e}")
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
    print("🩸  UHAI DAMU - Supabase Backend")
    print("=" * 70)
    print(f"📅  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗄️  Database: Supabase PostgreSQL")
    print("-" * 70)
    print(f"🌐  Website: http://localhost:{port}")
    print(f"🔧  API Test: http://localhost:{port}/api/test")
    print("=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)