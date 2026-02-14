from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
import random

load_dotenv()

app = Flask(__name__, static_folder='../', static_url_path='')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
CORS(app)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '0737980929'),
    'database': os.getenv('DB_NAME', 'uhai_damu')
}

# ===== DATABASE CONNECTION =====
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

# ===== INITIALIZE DATABASE =====
def init_database():
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS donors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                phone VARCHAR(15) UNIQUE NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100),
                blood_type VARCHAR(3) NOT NULL,
                county VARCHAR(50) NOT NULL,
                constituency VARCHAR(50) NOT NULL,
                date_of_birth DATE,
                gender VARCHAR(10),
                password_hash VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                last_donation DATE,
                total_donations INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hospitals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                county VARCHAR(50) NOT NULL,
                constituency VARCHAR(50) NOT NULL,
                contact_phone VARCHAR(15),
                contact_email VARCHAR(100),
                address TEXT,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blood_stock (
                id INT AUTO_INCREMENT PRIMARY KEY,
                hospital_id INT,
                blood_type VARCHAR(3) NOT NULL,
                units_available INT DEFAULT 0,
                status VARCHAR(20) DEFAULT 'adequate',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blood_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                hospital_id INT,
                blood_type VARCHAR(3) NOT NULL,
                units_needed INT NOT NULL,
                urgency VARCHAR(20) DEFAULT 'normal',
                patient_details TEXT,
                deadline DATETIME,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
            )
        """)
        
        # Insert sample hospitals if none exist
        cursor.execute("SELECT COUNT(*) FROM hospitals")
        if cursor.fetchone()[0] == 0:
            hospitals = [
                ('Kenyatta National Hospital', 'Nairobi City County', 'Starehe', '+254202713344', 'info@knh.or.ke', 'Hospital Rd, Nairobi', True),
                ('MP Shah Hospital', 'Nairobi City County', 'Westlands', '+254204294000', 'info@mpshah.co.ke', 'Shivachi Rd, Nairobi', True),
                ('Aga Khan University Hospital', 'Nairobi City County', 'Westlands', '+254203660000', 'info@agakhanhospital.org', '3rd Parklands Ave, Nairobi', True),
                ('Thika Level 5 Hospital', 'Kiambu County', 'Thika Town', '+25467222021', 'thikahospital@health.go.ke', 'General Kago Rd, Thika', True),
                ('Kiambu County Referral Hospital', 'Kiambu County', 'Kiambu', '+25467222000', 'kiambuhospital@health.go.ke', 'Kiambu Town', True)
            ]
            
            for h in hospitals:
                cursor.execute("""
                    INSERT INTO hospitals (name, county, constituency, contact_phone, contact_email, address, is_verified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, h)
            
            # Add sample blood stock
            blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
            cursor.execute("SELECT id FROM hospitals")
            hospital_ids = [row[0] for row in cursor.fetchall()]
            
            for hid in hospital_ids:
                for bt in blood_types:
                    units = random.randint(1, 25)
                    status = 'critical' if units <= 3 else 'low' if units <= 8 else 'adequate'
                    cursor.execute("""
                        INSERT INTO blood_stock (hospital_id, blood_type, units_available, status)
                        VALUES (%s, %s, %s, %s)
                    """, (hid, bt, units, status))
        
        connection.commit()
        print("Database initialized successfully")
        return True
        
    except Error as e:
        print(f"Database initialization error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

# ===== API ROUTES =====

@app.route('/')
def serve_index():
    return send_from_directory('../', 'index.html')

@app.route('/api/init', methods=['POST'])
def api_init():
    if init_database():
        return jsonify({'success': True, 'message': 'Database initialized'})
    return jsonify({'success': False, 'error': 'Initialization failed'}), 500

@app.route('/api/blood-stock/<path:county>/<path:constituency>', methods=['GET'])
def get_blood_stock(county, constituency):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT h.name, h.contact_phone, h.contact_email, 
                   bs.blood_type, bs.units_available, bs.status, bs.last_updated
            FROM blood_stock bs
            JOIN hospitals h ON bs.hospital_id = h.id
            WHERE h.county = %s AND h.constituency = %s
            ORDER BY h.name, bs.blood_type
        """, (county, constituency))
        
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        
        # Group by hospital
        hospitals = {}
        for row in results:
            name = row['name']
            if name not in hospitals:
                hospitals[name] = {
                    'name': name,
                    'contact_phone': row['contact_phone'],
                    'contact_email': row['contact_email'],
                    'stock': []
                }
            hospitals[name]['stock'].append({
                'blood_type': row['blood_type'],
                'units_available': row['units_available'],
                'status': row['status'],
                'last_updated': row['last_updated'].isoformat() if row['last_updated'] else None
            })
        
        return jsonify(list(hospitals.values()))
        
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/donor/register', methods=['POST'])
def register_donor():
    data = request.json
    required = ['phone', 'first_name', 'last_name', 'blood_type', 'county', 'constituency', 'password']
    
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        password_hash = generate_password_hash(data['password'])
        
        cursor.execute("""
            INSERT INTO donors 
            (phone, first_name, last_name, email, blood_type, county, constituency, date_of_birth, gender, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['phone'], data['first_name'], data['last_name'],
            data.get('email'), data['blood_type'], data['county'],
            data['constituency'], data.get('date_of_birth'), data.get('gender'),
            password_hash
        ))
        
        connection.commit()
        donor_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Registration successful', 'donor_id': donor_id}), 201
        
    except Error as e:
        if 'Duplicate' in str(e):
            return jsonify({'error': 'Phone number already registered'}), 409
        return jsonify({'error': str(e)}), 500

@app.route('/api/donor/login', methods=['POST'])
def donor_login():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    
    if not phone or not password:
        return jsonify({'error': 'Phone and password required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, first_name, last_name, blood_type, county, constituency, password_hash
            FROM donors WHERE phone = %s AND is_active = TRUE
        """, (phone,))
        
        donor = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if donor and check_password_hash(donor['password_hash'], password):
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'donor': {
                    'id': donor['id'],
                    'name': f"{donor['first_name']} {donor['last_name']}",
                    'blood_type': donor['blood_type'],
                    'county': donor['county'],
                    'constituency': donor['constituency']
                }
            })
        else:
            return jsonify({'error': 'Invalid phone or password'}), 401
            
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/donors/nearby', methods=['GET'])
def get_nearby_donors():
    county = request.args.get('county')
    blood_type = request.args.get('blood_type')
    constituency = request.args.get('constituency', '')
    
    if not county or not blood_type:
        return jsonify({'error': 'County and blood type required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT id, first_name, last_name, phone, blood_type, county, constituency
            FROM donors
            WHERE county = %s AND blood_type = %s AND is_active = TRUE
        """
        params = [county, blood_type]
        
        if constituency:
            query += " AND constituency = %s"
            params.append(constituency)
        
        cursor.execute(query, params)
        donors = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify(donors)
        
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/counties', methods=['GET'])
def get_counties():
    return jsonify({
        'counties': ['Nairobi City County', 'Kiambu County']
    })

@app.route('/api/constituencies/<path:county>', methods=['GET'])
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
    
    return jsonify({'constituencies': constituencies.get(county, [])})

@app.route('/api/blood-types', methods=['GET'])
def get_blood_types():
    return jsonify({
        'blood_types': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    })

@app.route('/api/donor/logout', methods=['POST'])
def donor_logout():
    return jsonify({'success': True, 'message': 'Logged out'})

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../', path)

if __name__ == '__main__':
    print("🩸 Uhai Damu Blood Donation Platform")
    print("Initializing database...")
    init_database()
    print("Starting server on http://localhost:5000")
    app.run(debug=True, port=5000)