"""
UHAI DAMU - Blood Donation Platform
Complete Flask Application with Database Integration
"""

from flask import Flask, send_from_directory, jsonify, request, session
from flask_cors import CORS
import os
import bcrypt
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging
import re

# Create Flask app
app = Flask(__name__, static_folder='../', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'uhai-damu-secret-key-2025')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Enable CORS with credentials
CORS(app, supports_credentials=True, origins=['http://localhost:5001', 'http://127.0.0.1:5001'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base directory where HTML files are stored
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(f"📁 Serving files from: {BASE_DIR}")

# ============================================
# DATABASE CONFIGURATION
# ============================================

db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '0737980929'),
    'database': os.environ.get('DB_NAME', 'uhai_damu'),
    'charset': 'utf8mb4',
    'use_unicode': True
}

def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        logger.error(f"Database error: {e}")
        return None

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """Execute SQL query with error handling"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            logger.error("Failed to connect to database")
            return None
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = None
        
        if commit:
            connection.commit()
            result = cursor.lastrowid if cursor.lastrowid else True
        
        return result
    except Error as e:
        logger.error(f"Query error: {e}")
        if connection:
            connection.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# ============================================
# INITIALIZE DATABASE TABLES
# ============================================

def init_database():
    """Create database tables if they don't exist"""
    try:
        # Create users table
        execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(150) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(200) NOT NULL,
                phone_number VARCHAR(15),
                blood_type VARCHAR(3),
                date_of_birth DATE,
                county VARCHAR(100),
                constituency VARCHAR(100),
                weight DECIMAL(5,2),
                height DECIMAL(5,2),
                user_type ENUM('donor', 'hospital_staff', 'admin') DEFAULT 'donor',
                is_active BOOLEAN DEFAULT TRUE,
                last_donation DATE,
                tattoos_last_6months BOOLEAN DEFAULT FALSE,
                alcohol_last_24hours BOOLEAN DEFAULT FALSE,
                on_medication BOOLEAN DEFAULT FALSE,
                health_issues BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """, commit=True)
        
        # Create appointments table
        execute_query("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                donor_id INT NOT NULL,
                donor_name VARCHAR(200) NOT NULL,
                donor_email VARCHAR(150) NOT NULL,
                donor_phone VARCHAR(15),
                blood_type VARCHAR(3),
                hospital_name VARCHAR(200) NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time VARCHAR(20) NOT NULL,
                notes TEXT,
                status ENUM('pending', 'approved', 'rejected', 'completed') DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP NULL,
                rejected_at TIMESTAMP NULL,
                approved_by INT NULL,
                INDEX idx_donor (donor_id),
                INDEX idx_status (status),
                INDEX idx_hospital (hospital_name),
                INDEX idx_date (appointment_date)
            )
        """, commit=True)
        
        # Create blood_stock table
        execute_query("""
            CREATE TABLE IF NOT EXISTS blood_stock (
                id INT AUTO_INCREMENT PRIMARY KEY,
                hospital_id INT,
                blood_type VARCHAR(3) NOT NULL,
                units_available INT DEFAULT 0,
                status VARCHAR(20) DEFAULT 'adequate',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """, commit=True)
        
        # Create hospitals table
        execute_query("""
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
        """, commit=True)
        
        # Check if admin exists
        admin = execute_query(
            "SELECT user_id FROM users WHERE email = %s AND user_type = 'admin'",
            ('admin@uhai-damu.co.ke',),
            fetch_one=True
        )
        
        if not admin:
            # Create default admin (password: Admin123)
            password_hash = bcrypt.hashpw(b'Admin123', bcrypt.gensalt()).decode('utf-8')
            execute_query("""
                INSERT INTO users (email, password_hash, full_name, user_type)
                VALUES (%s, %s, %s, 'admin')
            """, ('admin@uhai-damu.co.ke', password_hash, 'System Administrator'), commit=True)
            logger.info("Default admin created")
        
        # Check if test donor exists
        donor = execute_query(
            "SELECT user_id FROM users WHERE email = %s",
            ('2304340@students.kcau.ac.ke',),
            fetch_one=True
        )
        
        if not donor:
            # Create test donor (password: donor123)
            password_hash = bcrypt.hashpw(b'donor123', bcrypt.gensalt()).decode('utf-8')
            execute_query("""
                INSERT INTO users (email, password_hash, full_name, phone_number, blood_type, county, constituency, weight, height, user_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'donor')
            """, ('2304340@students.kcau.ac.ke', password_hash, 'Kirimi Marvin', '+254712345678', 'O+', 'Nairobi City County', 'Westlands', 70, 175), commit=True)
            logger.info("Test donor created")
        
        # Insert sample hospitals if none exist
        hospital_count = execute_query("SELECT COUNT(*) as count FROM hospitals", fetch_one=True)
        if hospital_count and hospital_count['count'] == 0:
            sample_hospitals = [
                ('Kenyatta National Hospital', 'Nairobi City County', 'Starehe', '+254202713344', 'info@knh.or.ke', 'Hospital Rd, Nairobi', True),
                ('MP Shah Hospital', 'Nairobi City County', 'Westlands', '+254204294000', 'info@mpshah.co.ke', 'Shivachi Rd, Nairobi', True),
                ('Aga Khan University Hospital', 'Nairobi City County', 'Westlands', '+254203660000', 'info@agakhanhospital.org', '3rd Parklands Ave, Nairobi', True),
                ('Thika Level 5 Hospital', 'Kiambu County', 'Thika Town', '+25467222021', 'thikahospital@health.go.ke', 'General Kago Rd, Thika', True),
                ('Kiambu County Referral Hospital', 'Kiambu County', 'Kiambu', '+25467222000', 'kiambuhospital@health.go.ke', 'Kiambu Town', True)
            ]
            for h in sample_hospitals:
                execute_query("""
                    INSERT INTO hospitals (name, county, constituency, contact_phone, contact_email, address, is_verified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, h, commit=True)
            logger.info("Sample hospitals created")
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

# Run initialization
init_database()

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
# HOSPITAL LIST
# ============================================

@app.route('/api/hospitals')
def get_hospitals():
    """Get list of all hospitals"""
    try:
        hospitals = execute_query("""
            SELECT id, name, county, constituency, contact_phone, contact_email, address
            FROM hospitals
            WHERE is_verified = TRUE
            ORDER BY name
        """, fetch_all=True)
        
        return jsonify({
            'success': True,
            'hospitals': hospitals
        })
    except Exception as e:
        logger.error(f"Get hospitals error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# DONOR REGISTRATION
# ============================================

@app.route('/api/donor/register', methods=['POST'])
def donor_register():
    """Register a new donor"""
    try:
        data = request.json
        logger.info(f"Registration attempt: {data.get('email')}")
        
        # Validate required fields
        required = ['first_name', 'last_name', 'email', 'phone', 'blood_type', 'password']
        for field in required:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Validate phone number (Kenyan format)
        phone_pattern = r'^(\+254|0)[17]\d{8}$'
        if not re.match(phone_pattern, data['phone']):
            return jsonify({'success': False, 'error': 'Invalid phone number. Use +2547XXXXXXXX or 07XXXXXXXX'}), 400
        
        # Validate blood type
        valid_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if data['blood_type'] not in valid_blood_types:
            return jsonify({'success': False, 'error': 'Invalid blood type'}), 400
        
        # Check if user exists
        existing = execute_query(
            "SELECT user_id FROM users WHERE email = %s",
            (data['email'],),
            fetch_one=True
        )
        
        if existing:
            return jsonify({'success': False, 'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Format full name
        full_name = f"{data['first_name']} {data['last_name']}"
        
        # Insert user
        user_id = execute_query("""
            INSERT INTO users (
                email, password_hash, full_name, phone_number, blood_type, 
                county, constituency, weight, height, user_type, date_of_birth
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'donor', %s)
        """, (
            data['email'], password_hash, full_name, data['phone'], data['blood_type'],
            data.get('county'), data.get('constituency'),
            data.get('weight'), data.get('height'),
            data.get('date_of_birth')
        ), commit=True)
        
        logger.info(f"User registered successfully: {data['email']} with ID: {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful! You can now login.',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
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
        donor = execute_query("""
            SELECT user_id, email, full_name, phone_number, blood_type, 
                   date_of_birth, county, constituency, weight, height,
                   last_donation, tattoos_last_6months, alcohol_last_24hours,
                   on_medication, health_issues, created_at, password_hash
            FROM users 
            WHERE email = %s AND user_type = 'donor' AND is_active = TRUE
        """, (email,), fetch_one=True)
        
        if not donor:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), donor['password_hash'].encode('utf-8')):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Format names
        name_parts = donor['full_name'].split()
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[-1] if len(name_parts) > 1 else ''
        
        # Format donor data for frontend
        donor_data = {
            'id': donor['user_id'],
            'firstName': first_name,
            'lastName': last_name,
            'email': donor['email'],
            'phone': donor['phone_number'],
            'bloodType': donor['blood_type'],
            'dateOfBirth': donor['date_of_birth'].isoformat() if donor['date_of_birth'] else '',
            'county': donor['county'],
            'constituency': donor['constituency'],
            'weight': donor['weight'],
            'height': donor['height'],
            'lastDonation': donor['last_donation'].isoformat() if donor['last_donation'] else None,
            'registrationDate': donor['created_at'].isoformat() if donor['created_at'] else '',
            'donationStatus': {
                'tattoosLast6Months': donor['tattoos_last_6months'] or False,
                'alcoholLast24Hours': donor['alcohol_last_24hours'] or False,
                'medication': donor['on_medication'] or False,
                'healthIssues': donor['health_issues'] or False
            }
        }
        
        # Store in session
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
    """Get current donor profile from session"""
    try:
        donor_id = session.get('donor_id')
        
        if not donor_id:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        donor = execute_query("""
            SELECT user_id, email, full_name, phone_number, blood_type, 
                   date_of_birth, county, constituency, weight, height,
                   last_donation, tattoos_last_6months, alcohol_last_24hours,
                   on_medication, health_issues, created_at
            FROM users 
            WHERE user_id = %s AND user_type = 'donor'
        """, (donor_id,), fetch_one=True)
        
        if not donor:
            return jsonify({'success': False, 'error': 'Donor not found'}), 404
        
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
            'dateOfBirth': donor['date_of_birth'].isoformat() if donor['date_of_birth'] else '',
            'county': donor['county'],
            'constituency': donor['constituency'],
            'weight': donor['weight'],
            'height': donor['height'],
            'lastDonation': donor['last_donation'].isoformat() if donor['last_donation'] else None,
            'registrationDate': donor['created_at'].isoformat() if donor['created_at'] else '',
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
    """Update donor donation status"""
    try:
        donor_id = session.get('donor_id')
        
        if not donor_id:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        data = request.json
        
        execute_query("""
            UPDATE users 
            SET tattoos_last_6months = %s,
                alcohol_last_24hours = %s,
                on_medication = %s,
                health_issues = %s,
                weight = %s,
                height = %s
            WHERE user_id = %s
        """, (
            data.get('tattoosLast6Months', False),
            data.get('alcoholLast24Hours', False),
            data.get('medication', False),
            data.get('healthIssues', False),
            data.get('weight'),
            data.get('height'),
            donor_id
        ), commit=True)
        
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
    """Create a new appointment request"""
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
        donor = execute_query("""
            SELECT user_id, full_name, email, phone_number, blood_type
            FROM users WHERE user_id = %s
        """, (donor_id,), fetch_one=True)
        
        if not donor:
            return jsonify({'success': False, 'error': 'Donor not found'}), 404
        
        logger.info(f"Creating appointment for donor: {donor['full_name']}")
        
        # Create appointment
        appointment_id = execute_query("""
            INSERT INTO appointments (
                donor_id, donor_name, donor_email, donor_phone, blood_type,
                hospital_name, appointment_date, appointment_time, notes, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        """, (
            donor['user_id'],
            donor['full_name'],
            donor['email'],
            donor['phone_number'],
            donor['blood_type'],
            hospital_name,
            appointment_date,
            appointment_time,
            notes
        ), commit=True)
        
        logger.info(f"Appointment created: ID {appointment_id}")
        
        return jsonify({
            'success': True,
            'message': 'Appointment request submitted successfully',
            'appointment_id': appointment_id
        }), 201
        
    except Exception as e:
        logger.error(f"Create appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/appointments/my', methods=['GET'])
def get_my_appointments():
    """Get appointments for logged-in donor"""
    try:
        donor_id = session.get('donor_id')
        
        if not donor_id:
            return jsonify({'success': False, 'error': 'Please login first'}), 401
        
        appointments = execute_query("""
            SELECT id, hospital_name, appointment_date, appointment_time, notes, status, requested_at
            FROM appointments
            WHERE donor_id = %s
            ORDER BY requested_at DESC
        """, (donor_id,), fetch_all=True)
        
        # Format dates for JSON
        for appt in appointments:
            if appt.get('appointment_date'):
                appt['appointment_date'] = appt['appointment_date'].isoformat() if hasattr(appt['appointment_date'], 'isoformat') else str(appt['appointment_date'])
            if appt.get('requested_at'):
                appt['requested_at'] = appt['requested_at'].isoformat() if hasattr(appt['requested_at'], 'isoformat') else str(appt['requested_at'])
        
        return jsonify({
            'success': True,
            'appointments': appointments
        })
        
    except Exception as e:
        logger.error(f"Get my appointments error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/appointments', methods=['GET'])
def admin_get_appointments():
    """Get all appointments for admin"""
    try:
        admin_id = session.get('admin_id')
        
        if not admin_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        status_filter = request.args.get('status', 'all')
        
        query = """
            SELECT id, donor_id, donor_name, donor_email, donor_phone, blood_type,
                   hospital_name, appointment_date, appointment_time, notes, status, requested_at
            FROM appointments
        """
        params = []
        
        if status_filter != 'all':
            query += " WHERE status = %s"
            params.append(status_filter)
        
        query += " ORDER BY requested_at DESC"
        
        appointments = execute_query(query, params, fetch_all=True)
        
        # Format dates
        for appt in appointments:
            if appt.get('appointment_date'):
                appt['appointment_date'] = appt['appointment_date'].isoformat() if hasattr(appt['appointment_date'], 'isoformat') else str(appt['appointment_date'])
            if appt.get('requested_at'):
                appt['requested_at'] = appt['requested_at'].isoformat() if hasattr(appt['requested_at'], 'isoformat') else str(appt['requested_at'])
        
        return jsonify({
            'success': True,
            'appointments': appointments,
            'count': len(appointments)
        })
        
    except Exception as e:
        logger.error(f"Admin get appointments error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/appointments', methods=['GET'])
def hospital_get_appointments():
    """Get appointments for a specific hospital"""
    try:
        hospital_name = session.get('hospital_name')
        
        if not hospital_name:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        status_filter = request.args.get('status', 'all')
        
        query = """
            SELECT id, donor_id, donor_name, donor_email, donor_phone, blood_type,
                   appointment_date, appointment_time, notes, status, requested_at
            FROM appointments
            WHERE hospital_name = %s
        """
        params = [hospital_name]
        
        if status_filter != 'all':
            query += " AND status = %s"
            params.append(status_filter)
        
        query += " ORDER BY requested_at DESC"
        
        appointments = execute_query(query, params, fetch_all=True)
        
        # Format dates
        for appt in appointments:
            if appt.get('appointment_date'):
                appt['appointment_date'] = appt['appointment_date'].isoformat() if hasattr(appt['appointment_date'], 'isoformat') else str(appt['appointment_date'])
            if appt.get('requested_at'):
                appt['requested_at'] = appt['requested_at'].isoformat() if hasattr(appt['requested_at'], 'isoformat') else str(appt['requested_at'])
        
        return jsonify({
            'success': True,
            'appointments': appointments,
            'count': len(appointments)
        })
        
    except Exception as e:
        logger.error(f"Hospital get appointments error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/appointments/<int:appointment_id>/approve', methods=['POST'])
def admin_approve_appointment(appointment_id):
    """Admin approve appointment"""
    try:
        admin_id = session.get('admin_id')
        
        if not admin_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get appointment details
        appointment = execute_query("""
            SELECT donor_id, donor_name, donor_email, hospital_name, appointment_date, appointment_time
            FROM appointments WHERE id = %s
        """, (appointment_id,), fetch_one=True)
        
        if not appointment:
            return jsonify({'success': False, 'error': 'Appointment not found'}), 404
        
        # Update appointment status
        execute_query("""
            UPDATE appointments 
            SET status = 'approved', approved_at = NOW(), approved_by = %s
            WHERE id = %s
        """, (admin_id, appointment_id), commit=True)
        
        logger.info(f"Appointment {appointment_id} approved by admin {admin_id}")
        
        return jsonify({
            'success': True,
            'message': f'Appointment for {appointment["donor_name"]} approved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Approve appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/appointments/<int:appointment_id>/reject', methods=['POST'])
def admin_reject_appointment(appointment_id):
    """Admin reject appointment"""
    try:
        admin_id = session.get('admin_id')
        
        if not admin_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get appointment details
        appointment = execute_query("""
            SELECT donor_id, donor_name, donor_email, hospital_name, appointment_date, appointment_time
            FROM appointments WHERE id = %s
        """, (appointment_id,), fetch_one=True)
        
        if not appointment:
            return jsonify({'success': False, 'error': 'Appointment not found'}), 404
        
        # Update appointment status
        execute_query("""
            UPDATE appointments 
            SET status = 'rejected', rejected_at = NOW()
            WHERE id = %s
        """, (appointment_id,), commit=True)
        
        logger.info(f"Appointment {appointment_id} rejected by admin {admin_id}")
        
        return jsonify({
            'success': True,
            'message': f'Appointment for {appointment["donor_name"]} rejected'
        }), 200
        
    except Exception as e:
        logger.error(f"Reject appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/appointments/<int:appointment_id>/approve', methods=['POST'])
def hospital_approve_appointment(appointment_id):
    """Hospital approve appointment"""
    try:
        hospital_name = session.get('hospital_name')
        
        if not hospital_name:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Verify appointment belongs to this hospital
        appointment = execute_query("""
            SELECT id, donor_name, donor_email FROM appointments 
            WHERE id = %s AND hospital_name = %s
        """, (appointment_id, hospital_name), fetch_one=True)
        
        if not appointment:
            return jsonify({'success': False, 'error': 'Appointment not found'}), 404
        
        # Update appointment status
        execute_query("""
            UPDATE appointments SET status = 'approved', approved_at = NOW()
            WHERE id = %s
        """, (appointment_id,), commit=True)
        
        logger.info(f"Appointment {appointment_id} approved by hospital {hospital_name}")
        
        return jsonify({
            'success': True,
            'message': f'Appointment for {appointment["donor_name"]} approved'
        }), 200
        
    except Exception as e:
        logger.error(f"Hospital approve appointment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/appointments/<int:appointment_id>/reject', methods=['POST'])
def hospital_reject_appointment(appointment_id):
    """Hospital reject appointment"""
    try:
        hospital_name = session.get('hospital_name')
        
        if not hospital_name:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Verify appointment belongs to this hospital
        appointment = execute_query("""
            SELECT id, donor_name, donor_email FROM appointments 
            WHERE id = %s AND hospital_name = %s
        """, (appointment_id, hospital_name), fetch_one=True)
        
        if not appointment:
            return jsonify({'success': False, 'error': 'Appointment not found'}), 404
        
        # Update appointment status
        execute_query("""
            UPDATE appointments SET status = 'rejected', rejected_at = NOW()
            WHERE id = %s
        """, (appointment_id,), commit=True)
        
        logger.info(f"Appointment {appointment_id} rejected by hospital {hospital_name}")
        
        return jsonify({
            'success': True,
            'message': f'Appointment for {appointment["donor_name"]} rejected'
        }), 200
        
    except Exception as e:
        logger.error(f"Hospital reject appointment error: {e}")
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
        
        # Get admin from database
        admin = execute_query("""
            SELECT user_id, email, full_name, password_hash
            FROM users 
            WHERE email = %s AND user_type = 'admin' AND is_active = TRUE
        """, (email,), fetch_one=True)
        
        if not admin:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        session['admin_id'] = admin['user_id']
        session['admin_email'] = admin['email']
        session['admin_name'] = admin['full_name']
        session['user_type'] = 'admin'
        session.permanent = True
        
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
    """Admin logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

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
        
        # For demo purposes, hardcoded hospital credentials
        # In production, store in database
        if email == 'hospital@knh.co.ke' and password == 'hospital123':
            session['hospital_logged_in'] = True
            session['hospital_name'] = 'Kenyatta National Hospital'
            session['hospital_id'] = 1
            session['user_type'] = 'hospital'
            session.permanent = True
            
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
            session.permanent = True
            
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

# ============================================
# LOGOUT
# ============================================

@app.route('/api/logout', methods=['POST'])
def logout():
    """Generic logout for all user types"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    
    print("\n" + "=" * 70)
    print("🩸  UHAI DAMU - Blood Donation Platform")
    print("=" * 70)
    print(f"📅  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍  Environment: {os.environ.get('FLASK_ENV', 'development')}")
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
    print("    🩸 Donor: 2304340@students.kcau.ac.ke / donor123")
    print("    🏥 Hospital: hospital@knh.co.ke / hospital123")
    print("=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)