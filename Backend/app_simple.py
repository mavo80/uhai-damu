"""
UHAI DAMU - Simple Flask App (Test Version)
"""

from flask import Flask, send_from_directory, jsonify
import os
from datetime import datetime

# Create Flask app
app = Flask(__name__, static_folder='../', static_url_path='')

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
            'Westlands', 'Starehe', 'Kasarani', 'Langata', 'Embakasi', 'Dagoretti'
        ],
        'Kiambu County': [
            'Thika', 'Ruiru', 'Kiambaa', 'Kikuyu', 'Limuru', 'Juja'
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
# LOGIN ENDPOINTS (Simple Demo)
# ============================================

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    from flask import request
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if email == 'admin@uhai-damu.co.ke' and password == 'Admin123':
        return jsonify({'success': True, 'message': 'Login successful', 'admin': {'email': email, 'full_name': 'Super Admin'}})
    else:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/donor/login', methods=['POST'])
def donor_login():
    from flask import request
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # Demo donor
    if email and password:
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'donor': {
                'id': '44444444-4444-4444-4444-444444444444',
                'firstName': 'Kirimi',
                'lastName': 'Marvin',
                'email': '2304340@students.kcau.ac.ke',
                'phone': '+254712345678',
                'bloodType': 'O+',
                'county': 'Nairobi',
                'constituency': 'Westlands',
                'weight': 70,
                'height': 175
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/hospital/login', methods=['POST'])
def hospital_login():
    from flask import request
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if email == 'hospital@knh.co.ke' and password == 'hospital123':
        return jsonify({'success': True, 'message': 'Login successful', 'hospital': {'id': 1, 'name': 'Kenyatta National Hospital', 'email': email}})
    else:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    return jsonify({'success': True, 'message': 'Logged out'})

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    port = 5001
    
    print("\n" + "=" * 60)
    print("🩸  UHAI DAMU - Simple Test Server")
    print("=" * 60)
    print(f"🌐  Website: http://localhost:{port}")
    print(f"🔧  API Test: http://localhost:{port}/api/test")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)