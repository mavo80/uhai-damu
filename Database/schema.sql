-- Create database
CREATE DATABASE IF NOT EXISTS uhai_damu;
USE uhai_damu;

-- Donors table
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_blood_type (blood_type),
    INDEX idx_location (county, constituency)
);

-- Hospitals table
CREATE TABLE IF NOT EXISTS hospitals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    county VARCHAR(50) NOT NULL,
    constituency VARCHAR(50) NOT NULL,
    contact_phone VARCHAR(15),
    contact_email VARCHAR(100),
    address TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_location (county, constituency)
);

-- Blood stock table
CREATE TABLE IF NOT EXISTS blood_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT,
    blood_type VARCHAR(3) NOT NULL,
    units_available INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'adequate',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
    INDEX idx_hospital (hospital_id),
    INDEX idx_blood_type (blood_type)
);

-- Blood requests table
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
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_urgency (urgency)
);

-- Donation history table
CREATE TABLE IF NOT EXISTS donation_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT,
    hospital_id INT,
    blood_type VARCHAR(3) NOT NULL,
    units_donated INT DEFAULT 1,
    donation_date DATE,
    FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE SET NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL,
    INDEX idx_donor (donor_id),
    INDEX idx_date (donation_date)
);

-- SMS alerts table
CREATE TABLE IF NOT EXISTS sms_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_type VARCHAR(50),
    message TEXT,
    blood_type_filter VARCHAR(3),
    county_filter VARCHAR(50),
    constituency_filter VARCHAR(50),
    recipients_count INT,
    sent_by VARCHAR(100),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO hospitals (name, county, constituency, contact_phone, contact_email, address, is_verified) VALUES
('Kenyatta National Hospital', 'Nairobi City County', 'Starehe', '+254202713344', 'info@knh.or.ke', 'Hospital Rd, Nairobi', TRUE),
('MP Shah Hospital', 'Nairobi City County', 'Westlands', '+254204294000', 'info@mpshah.co.ke', 'Shivachi Rd, Nairobi', TRUE),
('Aga Khan University Hospital', 'Nairobi City County', 'Westlands', '+254203660000', 'info@agakhanhospital.org', '3rd Parklands Ave, Nairobi', TRUE),
('Thika Level 5 Hospital', 'Kiambu County', 'Thika Town', '+25467222021', 'thikahospital@health.go.ke', 'General Kago Rd, Thika', TRUE),
('Kiambu County Referral Hospital', 'Kiambu County', 'Kiambu', '+25467222000', 'kiambuhospital@health.go.ke', 'Kiambu Town', TRUE),
('Ruiru Sub-County Hospital', 'Kiambu County', 'Ruiru', '+25467222111', 'ruiruhospital@health.go.ke', 'Ruiru Town', TRUE),
('Juja Sub-County Hospital', 'Kiambu County', 'Juja', '+25467222222', 'jujahospital@health.go.ke', 'Juja Town', TRUE),
('Nairobi West Hospital', 'Nairobi City County', 'Dagoretti South', '+254204444444', 'info@nairobiwest.co.ke', 'Dagoretti Rd, Nairobi', TRUE),
('The Mater Hospital', 'Nairobi City County', 'Makadara', '+254205555555', 'info@mater.co.ke', 'Dunga Rd, Nairobi', TRUE),
('Gertrudes Children Hospital', 'Nairobi City County', 'Westlands', '+254206666666', 'info@gertrudes.org', 'Muthaiga Rd, Nairobi', TRUE);

-- Add sample blood stock
INSERT INTO blood_stock (hospital_id, blood_type, units_available, status)
SELECT h.id, bt.blood_type, 
    FLOOR(RAND() * 20) + 1,
    CASE 
        WHEN FLOOR(RAND() * 20) + 1 <= 3 THEN 'critical'
        WHEN FLOOR(RAND() * 20) + 1 <= 8 THEN 'low'
        ELSE 'adequate'
    END
FROM hospitals h
CROSS JOIN (
    SELECT 'A+' as blood_type UNION SELECT 'A-' UNION SELECT 'B+' UNION SELECT 'B-'
    UNION SELECT 'AB+' UNION SELECT 'AB-' UNION SELECT 'O+' UNION SELECT 'O-'
) bt
ON DUPLICATE KEY UPDATE 
    units_available = VALUES(units_available),
    status = VALUES(status);