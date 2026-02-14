"""
UHAI DAMU - Blood Donation Platform
Flask Backend Application
Version: 2.0 (Production Ready)
Date: February 2026
"""

from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import sys
import logging
import json
import random
import re
from dotenv import load_dotenv

# ============================================
# INITIALIZATION & CONFIGURATION
# ============================================

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, 
            static_folder='../', 
            static_url_path='',
            template_folder='../templates')

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# ============================================
# CORS CONFIGURATION (For deployment)
# ============================================

# Get allowed origins from environment or use defaults
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 
    'http://localhost:5000,http://127.0.0.1:5000,https://uhai-damu.vercel.app,https://uhai-damu-api.onrender.com'
).split(',')

CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

# ============================================
# LOGGING CONFIGURATION
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# DATABASE CONFIGURATION
# ============================================

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'uhai_damu'),
    'pool_name': 'mypool',
    'pool_size': 5,
    'pool_reset_session': True,
    'autocommit': False,
    'charset': 'utf8mb4',
    'use_unicode': True
}

# ============================================
# DATABASE CONNECTION FUNCTIONS
# ============================================

def get_db_connection():
    """Create and return a database connection with error handling"""
    try:
        connection = mysql.connector.connect(**db_config)
        logger.info("Database connection established successfully")
        return connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """Execute SQL query with proper error handling and connection management"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            raise Exception("Failed to connect to database")
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        result = None
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        
        if commit:
            connection.commit()
            result = cursor.lastrowid
        
        return result
        
    except Error as e:
        logger.error(f"Query execution error: {e}")
        if connection:
            connection.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# ============================================
# DATABASE INITIALIZATION
# ============================================

def init_database():
    """Initialize database with tables and sample data"""
    logger.info("Initializing database...")
    
    tables = [
        """
        CREATE TABLE IF NOT EXISTS donors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            phone VARCHAR(15) UNIQUE NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100),
            blood_type ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
            county VARCHAR(50) NOT NULL,
            constituency VARCHAR(50) NOT NULL,
            date_of_birth DATE,
            gender ENUM('male', 'female', 'other'),
            password_hash VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            is_available BOOLEAN DEFAULT TRUE,
            last_donation DATE,
            total_donations INT DEFAULT 0,
            emergency_contact VARCHAR(15),
            consent_given BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_blood_type (blood_type),
            INDEX idx_location (county, constituency),
            INDEX idx_availability (is_available)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS hospitals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            county VARCHAR(50) NOT NULL,
            constituency VARCHAR(50) NOT NULL,
            contact_phone VARCHAR(15),
            contact_email VARCHAR(100),
            address TEXT,
            license_number VARCHAR(50),
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_location (county, constituency),
            INDEX idx_verified (is_verified)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS hospital_staff (
            id INT AUTO_INCREMENT PRIMARY KEY,
            hospital_id INT NOT NULL,
            user_id INT UNIQUE,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            phone VARCHAR(15),
            staff_role VARCHAR(50),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
            INDEX idx_hospital (hospital_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS blood_stock (
            id INT AUTO_INCREMENT PRIMARY KEY,
            hospital_id INT NOT NULL,
            blood_type ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
            component_type ENUM('whole_blood', 'prbc', 'platelets', 'plasma', 'cryo') DEFAULT 'whole_blood',
            units_available INT DEFAULT 0,
            expiry_date DATE,
            donation_date DATE,
            status ENUM('adequate', 'low', 'critical') DEFAULT 'adequate',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
            INDEX idx_hospital (hospital_id),
            INDEX idx_blood_type (blood_type),
            INDEX idx_status (status),
            INDEX idx_expiry (expiry_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS blood_requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            hospital_id INT NOT NULL,
            requested_by INT,
            blood_type ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
            component_type ENUM('whole_blood', 'prbc', 'platelets', 'plasma', 'cryo') DEFAULT 'whole_blood',
            units_needed INT NOT NULL,
            urgency ENUM('normal', 'urgent', 'critical') DEFAULT 'normal',
            patient_details TEXT,
            deadline DATETIME,
            status ENUM('pending', 'processing', 'fulfilled', 'cancelled') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fulfilled_at TIMESTAMP NULL,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
            INDEX idx_status (status),
            INDEX idx_urgency (urgency),
            INDEX idx_created (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS donation_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            donor_id INT,
            hospital_id INT,
            blood_type ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
            component_type ENUM('whole_blood', 'prbc', 'platelets', 'plasma', 'cryo') DEFAULT 'whole_blood',
            units_donated INT DEFAULT 1,
            donation_date DATE NOT NULL,
            health_screening TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE SET NULL,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL,
            INDEX idx_donor (donor_id),
            INDEX idx_date (donation_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS sms_alerts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            alert_type ENUM('emergency', 'reminder', 'welcome', 'general') NOT NULL,
            message TEXT NOT NULL,
            blood_type_filter VARCHAR(3),
            county_filter VARCHAR(50),
            constituency_filter VARCHAR(50),
            recipients_count INT,
            sent_by VARCHAR(100),
            status ENUM('pending', 'sent', 'failed') DEFAULT 'pending',
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_type (alert_type),
            INDEX idx_sent_at (sent_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            donor_id INT NOT NULL,
            hospital_id INT NOT NULL,
            appointment_date DATE NOT NULL,
            appointment_time TIME NOT NULL,
            status ENUM('scheduled', 'completed', 'cancelled', 'missed') DEFAULT 'scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE CASCADE,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
            INDEX idx_date (appointment_date),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            user_type VARCHAR(20),
            action VARCHAR(100) NOT NULL,
            details TEXT,
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user (user_id),
            INDEX idx_action (action),
            INDEX idx_created (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    ]
    
    try:
        for table_sql in tables:
            execute_query(table_sql, commit=True)
        logger.info("Database tables created successfully")
        
        # Insert sample data if tables are empty
        seed_sample_data()
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def seed_sample_data():
    """Insert sample data for testing"""
    
    # Check if hospitals exist
    result = execute_query("SELECT COUNT(*) as count FROM hospitals", fetch_one=True)
    if result and result['count'] == 0:
        logger.info("Seeding sample hospitals...")
        
        hospitals = [
            ('Kenyatta National Hospital', 'Nairobi City County', 'Starehe', '+254202713344', 'info@knh.or.ke', 'Hospital Rd, Nairobi', 'KNH001', True),
            ('MP Shah Hospital', 'Nairobi City County', 'Westlands', '+254204294000', 'info@mpshah.co.ke', 'Shivachi Rd, Nairobi', 'MPS002', True),
            ('Aga Khan University Hospital', 'Nairobi City County', 'Westlands', '+254203660000', 'info@agakhanhospital.org', '3rd Parklands Ave, Nairobi', 'AKU003', True),
            ('Thika Level 5 Hospital', 'Kiambu County', 'Thika Town', '+25467222021', 'thikahospital@health.go.ke', 'General Kago Rd, Thika', 'THK004', True),
            ('Kiambu County Referral Hospital', 'Kiambu County', 'Kiambu', '+25467222000', 'kiambuhospital@health.go.ke', 'Kiambu Town', 'KIA005', True),
            ('Ruiru Sub-County Hospital', 'Kiambu County', 'Ruiru', '+25467222111', 'ruiruhospital@health.go.ke', 'Ruiru Town', 'RUI006', True),
            ('Juja Sub-County Hospital', 'Kiambu County', 'Juja', '+25467222222', 'jujahospital@health.go.ke', 'Juja Town', 'JUJ007', True),
            ('Nairobi West Hospital', 'Nairobi City County', 'Dagoretti South', '+254204444444', 'info@nairobiwest.co.ke', 'Dagoretti Rd, Nairobi', 'NW008', True),
            ('The Mater Hospital', 'Nairobi City County', 'Makadara', '+254205555555', 'info@mater.co.ke', 'Dunga Rd, Nairobi', 'MAT009', True),
            ("Gertrude's Children Hospital", 'Nairobi City County', 'Westlands', '+254206666666', 'info@gertrudes.org', 'Muthaiga Rd, Nairobi', 'GER010', True)
        ]
        
        for h in hospitals:
            execute_query("""
                INSERT INTO hospitals (name, county, constituency, contact_phone, contact_email, address, license_number, is_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, h, commit=True)
        
        logger.info(f"Inserted {len(hospitals)} hospitals")
    
    # Check if blood stock exists
    result = execute_query("SELECT COUNT(*) as count FROM blood_stock", fetch_one=True)
    if result and result['count'] == 0:
        logger.info("Seeding sample blood stock...")
        
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        # Get all hospital IDs
        hospitals = execute_query("SELECT id FROM hospitals", fetch_all=True)
        
        for hospital in hospitals:
            hospital_id = hospital['id']
            for bt in blood_types:
                units = random.randint(1, 25)
                status = 'critical' if units <= 3 else 'low' if units <= 8 else 'adequate'
                expiry = (datetime.now() + timedelta(days=random.randint(10, 42))).date()
                
                execute_query("""
                    INSERT INTO blood_stock (hospital_id, blood_type, units_available, status, expiry_date)
                    VALUES (%s, %s, %s, %s, %s)
                """, (hospital_id, bt, units, status, expiry), commit=True)
        
        logger.info("Blood stock seeded successfully")

# ============================================
# UTILITY FUNCTIONS
# ============================================

def validate_phone(phone):
    """Validate Kenyan phone number format"""
    pattern = r'^(\+254|0)[17]\d{8}$'
    return re.match(pattern, phone) is not None

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def log_audit(user_id, user_type, action, details, request):
    """Log user actions for audit trail"""
    try:
        execute_query("""
            INSERT INTO audit_log (user_id, user_type, action, details, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_id, user_type, action, details,
            request.remote_addr,
            request.user_agent.string if request.user_agent else None
        ), commit=True)
    except Exception as e:
        logger.error(f"Audit log failed: {e}")

# ============================================
# ROUTES - STATIC FILES
# ============================================

@app.route('/')
def serve_index():
    """Serve the main index.html"""
    return send_from_directory('../', 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    """Serve any static file"""
    return send_from_directory('../', filename)

# ============================================
# API ROUTES - HEALTH CHECK
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Uhai Damu API',
        'version': '2.0',
        'environment': os.getenv('FLASK_ENV', 'development')
    })

@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint"""
    return jsonify({
        'message': 'Uhai Damu API is working!',
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

# ============================================
# API ROUTES - LOCATION DATA
# ============================================

@app.route('/api/counties', methods=['GET'])
def get_counties():
    """Get list of supported counties"""
    return jsonify({
        'counties': [
            {'id': 'nairobi', 'name': 'Nairobi City County'},
            {'id': 'kiambu', 'name': 'Kiambu County'}
        ]
    })

@app.route('/api/constituencies/<path:county>', methods=['GET'])
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
    
    # Handle both full name and ID
    if county == 'nairobi':
        county_name = 'Nairobi City County'
    elif county == 'kiambu':
        county_name = 'Kiambu County'
    else:
        county_name = county
    
    return jsonify({
        'constituencies': constituencies.get(county_name, [])
    })

@app.route('/api/blood-types', methods=['GET'])
def get_blood_types():
    """Get list of all blood types"""
    return jsonify({
        'blood_types': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    })

# ============================================
# API ROUTES - BLOOD STOCK
# ============================================

@app.route('/api/blood-stock', methods=['GET'])
@app.route('/api/blood-stock/<path:county>/<path:constituency>', methods=['GET'])
def get_blood_stock(county=None, constituency=None):
    """Get blood stock with optional filters"""
    try:
        # Get query parameters if not in path
        if not county:
            county = request.args.get('county', '')
        if not constituency:
            constituency = request.args.get('constituency', '')
        blood_type = request.args.get('blood_type', '')
        
        # Build query
        query = """
            SELECT 
                h.id as hospital_id,
                h.name as hospital_name,
                h.contact_phone,
                h.contact_email,
                h.address,
                bs.blood_type,
                bs.component_type,
                bs.units_available,
                bs.status,
                bs.last_updated,
                bs.expiry_date
            FROM blood_stock bs
            JOIN hospitals h ON bs.hospital_id = h.id
            WHERE h.is_verified = TRUE
        """
        params = []
        
        if county and county != 'all' and county != '':
            query += " AND h.county = %s"
            params.append(county)
        
        if constituency and constituency != 'all' and constituency != '':
            query += " AND h.constituency = %s"
            params.append(constituency)
        
        if blood_type and blood_type != 'all' and blood_type != '':
            query += " AND bs.blood_type = %s"
            params.append(blood_type)
        
        query += " ORDER BY h.name, bs.blood_type"
        
        results = execute_query(query, params, fetch_all=True)
        
        # Group by hospital
        hospitals = {}
        for row in results:
            hosp_id = row['hospital_id']
            if hosp_id not in hospitals:
                hospitals[hosp_id] = {
                    'id': hosp_id,
                    'name': row['hospital_name'],
                    'contact_phone': row['contact_phone'],
                    'contact_email': row['contact_email'],
                    'address': row['address'],
                    'stock': []
                }
            
            hospitals[hosp_id]['stock'].append({
                'blood_type': row['blood_type'],
                'component_type': row['component_type'],
                'units_available': row['units_available'],
                'status': row['status'],
                'last_updated': row['last_updated'].isoformat() if row['last_updated'] else None,
                'expiry_date': row['expiry_date'].isoformat() if row['expiry_date'] else None
            })
        
        return jsonify({
            'success': True,
            'data': list(hospitals.values()),
            'count': len(hospitals),
            'filters': {
                'county': county,
                'constituency': constituency,
                'blood_type': blood_type
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching blood stock: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blood-stock/summary', methods=['GET'])
def get_blood_summary():
    """Get summary statistics of blood stock"""
    try:
        query = """
            SELECT 
                h.county,
                bs.blood_type,
                SUM(bs.units_available) as total_units,
                COUNT(DISTINCT h.id) as hospital_count,
                SUM(CASE WHEN bs.status = 'critical' THEN 1 ELSE 0 END) as critical_count
            FROM blood_stock bs
            JOIN hospitals h ON bs.hospital_id = h.id
            WHERE h.is_verified = TRUE
            GROUP BY h.county, bs.blood_type
            ORDER BY h.county, bs.blood_type
        """
        
        results = execute_query(query, fetch_all=True)
        
        # Format for charts
        summary = {}
        for row in results:
            county = row['county']
            if county not in summary:
                summary[county] = {
                    'total_units': 0,
                    'by_type': {}
                }
            
            summary[county]['by_type'][row['blood_type']] = row['total_units']
            summary[county]['total_units'] += row['total_units']
        
        return jsonify({
            'success': True,
            'data': summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching blood summary: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# API ROUTES - DONOR REGISTRATION & AUTH
# ============================================

@app.route('/api/donor/register', methods=['POST'])
def register_donor():
    """Register a new donor"""
    try:
        data = request.json
        logger.info(f"Registration attempt for phone: {data.get('phone')}")
        
        # Validate required fields
        required_fields = ['phone', 'first_name', 'last_name', 'blood_type', 'county', 'constituency', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        # Validate phone number
        if not validate_phone(data['phone']):
            return jsonify({
                'success': False,
                'error': 'Invalid phone number format. Use +2547XXXXXXXX or 07XXXXXXXX'
            }), 400
        
        # Validate email if provided
        if data.get('email') and not validate_email(data['email']):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Validate blood type
        valid_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if data['blood_type'] not in valid_blood_types:
            return jsonify({
                'success': False,
                'error': 'Invalid blood type'
            }), 400
        
        # Check if phone already exists
        existing = execute_query(
            "SELECT id FROM donors WHERE phone = %s", 
            (data['phone'],), 
            fetch_one=True
        )
        if existing:
            return jsonify({
                'success': False,
                'error': 'Phone number already registered'
            }), 409
        
        # Hash password
        password_hash = generate_password_hash(data['password'])
        
        # Insert donor
        donor_id = execute_query("""
            INSERT INTO donors (
                phone, first_name, last_name, email, blood_type,
                county, constituency, date_of_birth, gender, password_hash,
                emergency_contact, consent_given
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['phone'], data['first_name'], data['last_name'],
            data.get('email'), data['blood_type'],
            data['county'], data['constituency'],
            data.get('date_of_birth'), data.get('gender'),
            password_hash,
            data.get('emergency_contact'),
            data.get('consent_given', False)
        ), commit=True)
        
        # Log registration
        log_audit(donor_id, 'donor', 'REGISTER', f"New donor registered: {data['first_name']} {data['last_name']}", request)
        
        logger.info(f"Donor registered successfully: ID {donor_id}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'donor_id': donor_id
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'error': 'Registration failed. Please try again.'
        }), 500

@app.route('/api/donor/login', methods=['POST'])
def donor_login():
    """Login donor"""
    try:
        data = request.json
        phone = data.get('phone')
        password = data.get('password')
        
        if not phone or not password:
            return jsonify({
                'success': False,
                'error': 'Phone and password required'
            }), 400
        
        # Get donor from database
        donor = execute_query("""
            SELECT id, first_name, last_name, blood_type, county, constituency, password_hash
            FROM donors 
            WHERE phone = %s AND is_active = TRUE
        """, (phone,), fetch_one=True)
        
        if not donor or not check_password_hash(donor['password_hash'], password):
            # Log failed attempt
            log_audit(None, 'unknown', 'LOGIN_FAILED', f"Failed login attempt for phone: {phone}", request)
            return jsonify({
                'success': False,
                'error': 'Invalid phone number or password'
            }), 401
        
        # Create session
        session.permanent = True
        session['donor_id'] = donor['id']
        session['donor_name'] = f"{donor['first_name']} {donor['last_name']}"
        session['user_type'] = 'donor'
        
        # Log successful login
        log_audit(donor['id'], 'donor', 'LOGIN', "User logged in", request)
        
        # Update last login (would need last_login column in donors)
        
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
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Login failed. Please try again.'
        }), 500

@app.route('/api/donor/logout', methods=['POST'])
def donor_logout():
    """Logout donor"""
    donor_id = session.get('donor_id')
    if donor_id:
        log_audit(donor_id, 'donor', 'LOGOUT', "User logged out", request)
    
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

@app.route('/api/donor/profile', methods=['GET'])
def get_donor_profile():
    """Get donor profile"""
    donor_id = session.get('donor_id')
    
    if not donor_id:
        return jsonify({
            'success': False,
            'error': 'Not authenticated'
        }), 401
    
    try:
        donor = execute_query("""
            SELECT id, phone, first_name, last_name, email, blood_type,
                   county, constituency, date_of_birth, gender,
                   is_available, last_donation, total_donations,
                   emergency_contact, created_at
            FROM donors 
            WHERE id = %s
        """, (donor_id,), fetch_one=True)
        
        if not donor:
            return jsonify({
                'success': False,
                'error': 'Donor not found'
            }), 404
        
        # Get donation history
        history = execute_query("""
            SELECT dh.*, h.name as hospital_name
            FROM donation_history dh
            JOIN hospitals h ON dh.hospital_id = h.id
            WHERE dh.donor_id = %s
            ORDER BY dh.donation_date DESC
            LIMIT 10
        """, (donor_id,), fetch_all=True)
        
        return jsonify({
            'success': True,
            'donor': donor,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch profile'
        }), 500

@app.route('/api/donor/availability', methods=['PUT'])
def update_availability():
    """Update donor availability"""
    donor_id = session.get('donor_id')
    
    if not donor_id:
        return jsonify({
            'success': False,
            'error': 'Not authenticated'
        }), 401
    
    try:
        data = request.json
        is_available = data.get('is_available')
        
        if is_available is None:
            return jsonify({
                'success': False,
                'error': 'is_available field required'
            }), 400
        
        execute_query("""
            UPDATE donors SET is_available = %s WHERE id = %s
        """, (is_available, donor_id), commit=True)
        
        log_audit(donor_id, 'donor', 'UPDATE_AVAILABILITY', 
                 f"Set availability to: {is_available}", request)
        
        return jsonify({
            'success': True,
            'message': 'Availability updated',
            'is_available': is_available
        })
        
    except Exception as e:
        logger.error(f"Availability update error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update availability'
        }), 500

# ============================================
# API ROUTES - DONOR SEARCH
# ============================================

@app.route('/api/donors/search', methods=['GET'])
def search_donors():
    """Search for donors by blood type and location"""
    try:
        blood_type = request.args.get('blood_type')
        county = request.args.get('county', '')
        constituency = request.args.get('constituency', '')
        
        if not blood_type:
            return jsonify({
                'success': False,
                'error': 'Blood type is required'
            }), 400
        
        query = """
            SELECT 
                id, first_name, last_name, blood_type,
                county, constituency, phone,
                is_available, last_donation, total_donations
            FROM donors
            WHERE blood_type = %s
            AND is_active = TRUE
            AND is_available = TRUE
        """
        params = [blood_type]
        
        if county:
            query += " AND county = %s"
            params.append(county)
        
        if constituency:
            query += " AND constituency = %s"
            params.append(constituency)
        
        query += " ORDER BY last_donation IS NULL DESC, last_donation ASC"
        
        donors = execute_query(query, params, fetch_all=True)
        
        return jsonify({
            'success': True,
            'donors': donors,
            'count': len(donors)
        })
        
    except Exception as e:
        logger.error(f"Donor search error: {e}")
        return jsonify({
            'success': False,
            'error': 'Search failed'
        }), 500

# ============================================
# API ROUTES - BLOOD REQUESTS
# ============================================

@app.route('/api/blood-request', methods=['POST'])
def create_blood_request():
    """Create a new blood request (hospital staff only)"""
    # In production, check if user is hospital staff
    try:
        data = request.json
        
        required_fields = ['hospital_id', 'blood_type', 'units_needed']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        request_id = execute_query("""
            INSERT INTO blood_requests (
                hospital_id, requested_by, blood_type, component_type,
                units_needed, urgency, patient_details, deadline
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['hospital_id'], session.get('donor_id'),
            data['blood_type'], data.get('component_type', 'whole_blood'),
            data['units_needed'], data.get('urgency', 'normal'),
            data.get('patient_details'), data.get('deadline')
        ), commit=True)
        
        # Trigger SMS alerts to matching donors
        # This would call a background task
        
        return jsonify({
            'success': True,
            'message': 'Blood request created',
            'request_id': request_id
        }), 201
        
    except Exception as e:
        logger.error(f"Blood request creation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create request'
        }), 500

# ============================================
# API ROUTES - APPOINTMENTS
# ============================================

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    """Schedule a donation appointment"""
    donor_id = session.get('donor_id')
    
    if not donor_id:
        return jsonify({
            'success': False,
            'error': 'Not authenticated'
        }), 401
    
    try:
        data = request.json
        
        required_fields = ['hospital_id', 'appointment_date', 'appointment_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        # Validate date is in future
        appt_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        if appt_date < datetime.now().date():
            return jsonify({
                'success': False,
                'error': 'Appointment date must be in the future'
            }), 400
        
        appointment_id = execute_query("""
            INSERT INTO appointments (
                donor_id, hospital_id, appointment_date, appointment_time, notes
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            donor_id, data['hospital_id'],
            data['appointment_date'], data['appointment_time'],
            data.get('notes')
        ), commit=True)
        
        log_audit(donor_id, 'donor', 'SCHEDULE_APPOINTMENT', 
                 f"Scheduled appointment on {data['appointment_date']}", request)
        
        return jsonify({
            'success': True,
            'message': 'Appointment scheduled',
            'appointment_id': appointment_id
        }), 201
        
    except Exception as e:
        logger.error(f"Appointment creation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to schedule appointment'
        }), 500

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    """Get donor's appointments"""
    donor_id = session.get('donor_id')
    
    if not donor_id:
        return jsonify({
            'success': False,
            'error': 'Not authenticated'
        }), 401
    
    try:
        appointments = execute_query("""
            SELECT a.*, h.name as hospital_name, h.contact_phone
            FROM appointments a
            JOIN hospitals h ON a.hospital_id = h.id
            WHERE a.donor_id = %s
            ORDER BY a.appointment_date DESC
        """, (donor_id,), fetch_all=True)
        
        return jsonify({
            'success': True,
            'appointments': appointments
        })
        
    except Exception as e:
        logger.error(f"Appointment fetch error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch appointments'
        }), 500

# ============================================
# API ROUTES - HOSPITALS
# ============================================

@app.route('/api/hospitals', methods=['GET'])
def get_hospitals():
    """Get list of all verified hospitals"""
    try:
        county = request.args.get('county', '')
        
        query = """
            SELECT id, name, county, constituency, contact_phone, contact_email, address
            FROM hospitals
            WHERE is_verified = TRUE
        """
        params = []
        
        if county:
            query += " AND county = %s"
            params.append(county)
        
        query += " ORDER BY name"
        
        hospitals = execute_query(query, params, fetch_all=True)
        
        return jsonify({
            'success': True,
            'hospitals': hospitals,
            'count': len(hospitals)
        })
        
    except Exception as e:
        logger.error(f"Hospitals fetch error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch hospitals'
        }), 500

@app.route('/api/hospitals/<int:hospital_id>', methods=['GET'])
def get_hospital(hospital_id):
    """Get detailed hospital information"""
    try:
        hospital = execute_query("""
            SELECT * FROM hospitals WHERE id = %s AND is_verified = TRUE
        """, (hospital_id,), fetch_one=True)
        
        if not hospital:
            return jsonify({
                'success': False,
                'error': 'Hospital not found'
            }), 404
        
        # Get blood stock for this hospital
        stock = execute_query("""
            SELECT blood_type, component_type, units_available, status, expiry_date
            FROM blood_stock
            WHERE hospital_id = %s
            ORDER BY blood_type
        """, (hospital_id,), fetch_all=True)
        
        return jsonify({
            'success': True,
            'hospital': hospital,
            'stock': stock
        })
        
    except Exception as e:
        logger.error(f"Hospital detail fetch error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch hospital details'
        }), 500

# ============================================
# API ROUTES - STATIC DATA
# ============================================

@app.route('/api/blood-components', methods=['GET'])
def get_blood_components():
    """Get information about blood components"""
    components = [
        {
            "id": 1,
            "name": "Whole Blood",
            "description": "Contains red cells, white cells, platelets, and plasma. Used mainly in cases of major blood loss from surgery or trauma.",
            "uses": ["Major surgery", "Trauma", "Massive blood loss"],
            "shelf_life": "21-35 days",
            "storage": "2-6°C"
        },
        {
            "id": 2,
            "name": "Packed Red Blood Cells (PRBC)",
            "description": "Red cells with most plasma removed. Used to increase oxygen-carrying capacity in cases of severe anemia or blood loss.",
            "uses": ["Anemia", "Chronic blood loss", "Surgery"],
            "shelf_life": "35-42 days",
            "storage": "2-6°C"
        },
        {
            "id": 3,
            "name": "Platelets",
            "description": "Cell fragments that help blood clotting. Collected via apheresis or from whole blood.",
            "uses": ["Cancer treatment", "Chemotherapy", "Dengue fever"],
            "shelf_life": "5-7 days",
            "storage": "20-24°C with agitation"
        },
        {
            "id": 4,
            "name": "Fresh Frozen Plasma (FFP)",
            "description": "Plasma frozen within 8 hours of collection to preserve clotting factors.",
            "uses": ["Clotting disorders", "Liver disease", "Massive transfusion"],
            "shelf_life": "1 year frozen",
            "storage": "-18°C or below"
        },
        {
            "id": 5,
            "name": "Cryoprecipitate",
            "description": "Rich in fibrinogen, factor VIII, and von Willebrand factor.",
            "uses": ["Hemophilia A", "von Willebrand disease", "Fibrinogen deficiency"],
            "shelf_life": "1 year frozen",
            "storage": "-18°C or below"
        }
    ]
    
    return jsonify({
        "components": components,
        "count": len(components)
    })

@app.route('/api/blood-compatibility', methods=['GET'])
def get_blood_compatibility():
    """Get blood type compatibility information"""
    compatibility = {
        "A+": {
            "can_donate_to": ["A+", "AB+"],
            "can_receive_from": ["A+", "A-", "O+", "O-"]
        },
        "A-": {
            "can_donate_to": ["A+", "A-", "AB+", "AB-"],
            "can_receive_from": ["A-", "O-"]
        },
        "B+": {
            "can_donate_to": ["B+", "AB+"],
            "can_receive_from": ["B+", "B-", "O+", "O-"]
        },
        "B-": {
            "can_donate_to": ["B+", "B-", "AB+", "AB-"],
            "can_receive_from": ["B-", "O-"]
        },
        "AB+": {
            "can_donate_to": ["AB+"],
            "can_receive_from": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        },
        "AB-": {
            "can_donate_to": ["AB+", "AB-"],
            "can_receive_from": ["A-", "B-", "AB-", "O-"]
        },
        "O+": {
            "can_donate_to": ["O+", "A+", "B+", "AB+"],
            "can_receive_from": ["O+", "O-"]
        },
        "O-": {
            "can_donate_to": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
            "can_receive_from": ["O-"]
        }
    }
    
    return jsonify({
        "compatibility": compatibility,
        "universal_donor": "O-",
        "universal_recipient": "AB+"
    })

# ============================================
# API ROUTES - ADMIN (Protected)
# ============================================

@app.route('/api/admin/init', methods=['POST'])
def admin_init():
    """Initialize database with sample data (admin only)"""
    # In production, add authentication check
    if init_database():
        return jsonify({
            'success': True,
            'message': 'Database initialized successfully'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to initialize database'
        }), 500

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """Get system statistics for admin dashboard"""
    try:
        # Get counts
        donors_count = execute_query("SELECT COUNT(*) as count FROM donors WHERE is_active = TRUE", fetch_one=True)
        available_donors = execute_query("SELECT COUNT(*) as count FROM donors WHERE is_available = TRUE AND is_active = TRUE", fetch_one=True)
        hospitals_count = execute_query("SELECT COUNT(*) as count FROM hospitals WHERE is_verified = TRUE", fetch_one=True)
        pending_requests = execute_query("SELECT COUNT(*) as count FROM blood_requests WHERE status = 'pending'", fetch_one=True)
        total_donations = execute_query("SELECT COUNT(*) as count FROM donation_history", fetch_one=True)
        
        # Get blood stock summary
        blood_summary = execute_query("""
            SELECT 
                SUM(CASE WHEN status = 'critical' THEN 1 ELSE 0 END) as critical_count,
                SUM(CASE WHEN status = 'low' THEN 1 ELSE 0 END) as low_count,
                SUM(CASE WHEN status = 'adequate' THEN 1 ELSE 0 END) as adequate_count,
                SUM(units_available) as total_units
            FROM blood_stock
        """, fetch_one=True)
        
        return jsonify({
            'success': True,
            'stats': {
                'donors': donors_count['count'] if donors_count else 0,
                'available_donors': available_donors['count'] if available_donors else 0,
                'hospitals': hospitals_count['count'] if hospitals_count else 0,
                'pending_requests': pending_requests['count'] if pending_requests else 0,
                'total_donations': total_donations['count'] if total_donations else 0,
                'blood_stock': blood_summary
            }
        })
        
    except Exception as e:
        logger.error(f"Admin stats error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch stats'
        }), 500

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🩸  UHAI DAMU - Blood Donation Platform")
    print("="*60)
    print(f"📅  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍  Python: {sys.version}")
    print(f"🌐  Environment: {os.getenv('FLASK_ENV', 'development')}")
    print("-"*60)
    
    # Initialize database
    print("📦  Initializing database...")
    if init_database():
        print("✅  Database ready")
    else:
        print("⚠️  Database initialization had issues")
    
    # Get port from environment
    port = int(os.environ.get('PORT', 5000))
    
    print("-"*60)
    print(f"🚀  Server starting on: http://localhost:{port}")
    print(f"📝  API test: http://localhost:{port}/api/test")
    print("="*60 + "\n")
    
    # Run app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )