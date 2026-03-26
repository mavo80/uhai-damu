"""
UHAI DAMU - Working Test Server
Serves all HTML files
"""

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
from datetime import datetime

# Create Flask app
app = Flask(__name__, static_folder='../', static_url_path='')
CORS(app)

# ============================================
# SERVE HTML FILES
# ============================================

@app.route('/')
def serve_index():
    """Serve the main index.html"""
    return send_from_directory('..', 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    """Serve any HTML/CSS/JS file from the parent directory"""
    # Prevent directory traversal attacks
    if '..' in filename or filename.startswith('/'):
        return "Invalid path", 400
    return send_from_directory('..', filename)

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Uhai Damu API is running',
        'time': datetime.now().isoformat()
    })

@app.route('/api/test')
def test():
    """Test endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

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
    """Get constituencies for a county"""
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
    
    # Handle both full name and id
    county_name = county
    if county == 'nairobi':
        county_name = 'Nairobi City County'
    elif county == 'kiambu':
        county_name = 'Kiambu County'
    
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
# MAIN
# ============================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🩸 UHAI DAMU - Blood Donation Platform")
    print("=" * 60)
    print(f"📅  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    print(f"🌐  Website:     http://localhost:5001")
    print(f"🔧  API Test:    http://localhost:5001/api/test")
    print(f"👑  Admin Login: http://localhost:5001/admin-login.html")
    print(f"📝  Register:    http://localhost:5001/register.html")
    print(f"🏥  Live Status: http://localhost:5001/live-status.html")
    print("-" * 60)
    print("🔑  Admin Credentials:")
    print("    Email:    admin@uhai-damu.co.ke")
    print("    Password: Admin123")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)