"""
UHAI DAMU - Main Application
Serves HTML files and provides API endpoints
"""

from flask import Flask, send_from_directory, jsonify, request, session
from flask_cors import CORS
import os
from datetime import datetime
import logging

# Create Flask app
app = Flask(__name__, static_folder='../', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'uhai-damu-secret-key-2025')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base directory where HTML files are stored
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(f"📁 Serving files from: {BASE_DIR}")

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
    
    try:
        return send_from_directory(BASE_DIR, filename)
    except Exception as e:
        logger.error(f"File not found: {filename}")
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
        'port': 5001
    })

@app.route('/api/test')
def test():
    """Test endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'port': 5001
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
    
    # Handle both full name and short name
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
# BLOOD STOCK (Sample Data)
# ============================================

@app.route('/api/blood-stock/<county>/<constituency>')
def get_blood_stock(county, constituency):
    """Get blood stock for a specific location"""
    
    # Sample hospitals data
    hospitals = [
        {
            'id': 1,
            'name': 'Kenyatta National Hospital',
            'contact_phone': '+254 20 271 3344',
            'contact_email': 'info@knh.or.ke',
            'address': 'Hospital Rd, Nairobi',
            'stock': [
                {'blood_type': 'A+', 'units_available': 15, 'status': 'adequate'},
                {'blood_type': 'A-', 'units_available': 8, 'status': 'low'},
                {'blood_type': 'B+', 'units_available': 12, 'status': 'adequate'},
                {'blood_type': 'B-', 'units_available': 5, 'status': 'low'},
                {'blood_type': 'AB+', 'units_available': 4, 'status': 'low'},
                {'blood_type': 'AB-', 'units_available': 2, 'status': 'critical'},
                {'blood_type': 'O+', 'units_available': 20, 'status': 'adequate'},
                {'blood_type': 'O-', 'units_available': 3, 'status': 'critical'}
            ]
        },
        {
            'id': 2,
            'name': 'MP Shah Hospital',
            'contact_phone': '+254 20 429 4000',
            'contact_email': 'info@mpshah.co.ke',
            'address': 'Shivachi Rd, Nairobi',
            'stock': [
                {'blood_type': 'A+', 'units_available': 10, 'status': 'adequate'},
                {'blood_type': 'B+', 'units_available': 8, 'status': 'low'},
                {'blood_type': 'O+', 'units_available': 12, 'status': 'adequate'},
                {'blood_type': 'O-', 'units_available': 2, 'status': 'critical'}
            ]
        },
        {
            'id': 3,
            'name': 'Aga Khan University Hospital',
            'contact_phone': '+254 20 366 0000',
            'contact_email': 'info@agakhanhospital.org',
            'address': '3rd Parklands Ave, Nairobi',
            'stock': [
                {'blood_type': 'A+', 'units_available': 18, 'status': 'adequate'},
                {'blood_type': 'B+', 'units_available': 15, 'status': 'adequate'},
                {'blood_type': 'O+', 'units_available': 25, 'status': 'adequate'},
                {'blood_type': 'AB-', 'units_available': 1, 'status': 'critical'}
            ]
        }
    ]
    
    return jsonify({
        'success': True,
        'hospitals': hospitals,
        'count': len(hospitals)
    })

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
        
        # Simple admin check
        if email == 'admin@uhai-damu.co.ke' and password == 'Admin123':
            session['admin_logged_in'] = True
            session['admin_email'] = email
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'admin': {
                    'id': 1,
                    'email': email,
                    'full_name': 'Super Admin',
                    'role': 'super_admin'
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Admin logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

# ============================================
# DONOR REGISTRATION
# ============================================

@app.route('/api/donor/register', methods=['POST'])
def donor_register():
    """Simple donor registration"""
    try:
        data = request.json
        logger.info(f"Registration attempt: {data.get('email')}")
        
        # Simple validation
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        # In production, save to database
        return jsonify({
            'success': True,
            'message': 'Registration successful! You can now login.',
            'user_id': 1
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/donor/login', methods=['POST'])
def donor_login():
    """Simple donor login"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            session['user_logged_in'] = True
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': 1,
                    'name': 'Test User',
                    'email': email
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
    except Exception as e:
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
        
        if email == 'hospital@knh.co.ke' and password == 'hospital123':
            session['hospital_logged_in'] = True
            session['hospital_name'] = 'Kenyatta National Hospital'
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
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# RUN SERVER - PORT 5001
# ============================================

if __name__ == '__main__':
    # Use port 5001 as originally set
    port = int(os.environ.get('PORT', 5001))
    
    print("\n" + "=" * 60)
    print("🩸  UHAI DAMU - Blood Donation Platform")
    print("=" * 60)
    print(f"📅  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍  Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print("-" * 60)
    print(f"🌐  Website: http://localhost:{port}")
    print(f"🔧  API Test: http://localhost:{port}/api/test")
    print(f"👑  Admin Login: http://localhost:{port}/admin-login.html")
    print(f"📝  Register: http://localhost:{port}/register.html")
    print("-" * 60)
    print("🔑  Demo Credentials:")
    print("    Admin: admin@uhai-damu.co.ke / Admin123")
    print("    Hospital: hospital@knh.co.ke / hospital123")
    print("    Donor: any email / any password")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)