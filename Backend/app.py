"""
UHAI DAMU - Main Application
Serves all HTML files correctly
"""

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
from datetime import datetime

# Create Flask app
app = Flask(__name__)
CORS(app)

# Set the directory where your HTML files are
# This should be the parent folder (where index.html is)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(f"📁 Serving files from: {BASE_DIR}")

# ============================================
# SERVE HTML FILES
# ============================================

@app.route('/')
def serve_index():
    """Serve the main index.html"""
    index_path = os.path.join(BASE_DIR, 'index.html')
    print(f"Looking for index.html at: {index_path}")
    if os.path.exists(index_path):
        return send_from_directory(BASE_DIR, 'index.html')
    else:
        return f"""
        <h1>🩸 UHAI DAMU</h1>
        <p>index.html not found at: {index_path}</p>
        <p>Files in directory: {os.listdir(BASE_DIR)}</p>
        """

@app.route('/<path:filename>')
def serve_file(filename):
    """Serve any file from the base directory"""
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(BASE_DIR, filename)
    else:
        return f"File not found: {filename}", 404

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/test')
def test():
    return jsonify({"status": "ok", "message": "API is working!"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/counties')
def get_counties():
    return jsonify({
        'counties': ['Nairobi City County', 'Kiambu County']
    })

@app.route('/api/constituencies/<county>')
def get_constituencies(county):
    constituencies = {
        'Nairobi City County': ['Westlands', 'Starehe', 'Kasarani', 'Langata', 'Embakasi', 'Dagoretti', 'Mathare'],
        'Kiambu County': ['Thika', 'Ruiru', 'Kiambaa', 'Kikuyu', 'Limuru', 'Juja']
    }
    return jsonify({'constituencies': constituencies.get(county, [])})

@app.route('/api/blood-types')
def get_blood_types():
    return jsonify({'blood_types': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']})

@app.route('/api/blood-stock/<county>/<constituency>')
def get_blood_stock(county, constituency):
    hospitals = [
        {
            'name': 'Kenyatta National Hospital',
            'contact_phone': '+254 20 271 3344',
            'contact_email': 'info@knh.or.ke',
            'stock': [
                {'blood_type': 'A+', 'units_available': 15, 'status': 'adequate'},
                {'blood_type': 'B+', 'units_available': 8, 'status': 'low'},
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
                {'blood_type': 'O+', 'units_available': 12, 'status': 'adequate'},
                {'blood_type': 'AB-', 'units_available': 2, 'status': 'critical'}
            ]
        }
    ]
    return jsonify(hospitals)

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🩸  UHAI DAMU - Blood Donation Platform")
    print("=" * 60)
    print(f"📁  HTML folder: {BASE_DIR}")
    print(f"📄  index.html exists: {os.path.exists(os.path.join(BASE_DIR, 'index.html'))}")
    print("-" * 60)
    print(f"🌐  Open: http://localhost:5001")
    print(f"🔧  API:  http://localhost:5001/api/test")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)