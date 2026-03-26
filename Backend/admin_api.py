"""
UHAI DAMU - Admin API
Handles admin dashboard functions
"""

from flask import Blueprint, request, jsonify, session
from flask_cors import CORS
from datetime import datetime

# Create blueprint for admin
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# ============================================
# SAMPLE DATA
# ============================================

# Sample users
sample_users = [
    {
        'user_id': 1,
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'phone_number': '+254712345678',
        'blood_type': 'O+',
        'user_type': 'donor',
        'is_active': True,
        'created_at': '2025-03-15 10:00:00',
        'county': 'Nairobi City County',
        'constituency': 'Westlands'
    },
    {
        'user_id': 2,
        'full_name': 'Jane Smith',
        'email': 'jane@example.com',
        'phone_number': '+254723456789',
        'blood_type': 'A-',
        'user_type': 'donor',
        'is_active': True,
        'created_at': '2025-03-16 14:30:00',
        'county': 'Kiambu County',
        'constituency': 'Thika Town'
    },
    {
        'user_id': 3,
        'full_name': 'Peter Omondi',
        'email': 'peter@example.com',
        'phone_number': '+254734567890',
        'blood_type': 'B+',
        'user_type': 'donor',
        'is_active': False,
        'created_at': '2025-03-17 09:15:00',
        'county': 'Nairobi City County',
        'constituency': 'Kasarani'
    }
]

# Sample blood stock
sample_blood_stock = [
    {'id': 1, 'hospital_name': 'Kenyatta National Hospital', 'blood_type': 'A+', 'units_available': 15, 'status': 'adequate', 'last_updated': '2025-03-20 08:00:00'},
    {'id': 2, 'hospital_name': 'Kenyatta National Hospital', 'blood_type': 'O+', 'units_available': 20, 'status': 'adequate', 'last_updated': '2025-03-20 08:00:00'},
    {'id': 3, 'hospital_name': 'Kenyatta National Hospital', 'blood_type': 'O-', 'units_available': 3, 'status': 'critical', 'last_updated': '2025-03-20 08:00:00'},
    {'id': 4, 'hospital_name': 'MP Shah Hospital', 'blood_type': 'A+', 'units_available': 10, 'status': 'adequate', 'last_updated': '2025-03-20 08:00:00'},
    {'id': 5, 'hospital_name': 'MP Shah Hospital', 'blood_type': 'B+', 'units_available': 8, 'status': 'low', 'last_updated': '2025-03-20 08:00:00'},
    {'id': 6, 'hospital_name': 'Thika Level 5 Hospital', 'blood_type': 'O+', 'units_available': 12, 'status': 'adequate', 'last_updated': '2025-03-20 08:00:00'}
]

# ============================================
# AUTHENTICATION
# ============================================

@admin_bp.route('/check', methods=['GET'])
def check_auth():
    """Check if admin is logged in"""
    if session.get('admin_logged_in'):
        return jsonify({'success': True, 'logged_in': True})
    return jsonify({'success': True, 'logged_in': False})

@admin_bp.route('/login', methods=['POST'])
def login():
    """Admin login"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if email == 'admin@uhai-damu.co.ke' and password == 'Admin123':
            session['admin_logged_in'] = True
            session['admin_email'] = email
            session['admin_name'] = 'Super Admin'
            session['admin_role'] = 'super_admin'
            
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

@admin_bp.route('/logout', methods=['POST'])
def logout():
    """Admin logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

# ============================================
# USER MANAGEMENT
# ============================================

@admin_bp.route('/users', methods=['GET'])
def get_users():
    """Get all registered users"""
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        stats = {
            'total_users': len(sample_users),
            'total_donors': len([u for u in sample_users if u['user_type'] == 'donor']),
            'active_users': len([u for u in sample_users if u['is_active']])
        }
        
        return jsonify({
            'success': True,
            'users': sample_users,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user status"""
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        data = request.json
        is_active = data.get('is_active')
        
        # Find and update user
        for user in sample_users:
            if user['user_id'] == user_id:
                user['is_active'] = is_active
                break
        
        return jsonify({
            'success': True,
            'message': f'User {"activated" if is_active else "deactivated"} successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# BLOOD STOCK MANAGEMENT
# ============================================

@admin_bp.route('/blood-stock', methods=['GET'])
def get_blood_stock():
    """Get all blood stock"""
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        return jsonify({
            'success': True,
            'stock': sample_blood_stock
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/blood-stock/add', methods=['POST'])
def add_blood_stock():
    """Add blood stock"""
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        data = request.json
        new_id = len(sample_blood_stock) + 1
        
        new_stock = {
            'id': new_id,
            'hospital_name': data.get('hospital_name'),
            'blood_type': data.get('blood_type'),
            'units_available': data.get('units_available'),
            'status': 'critical' if data.get('units_available') <= 3 else 'low' if data.get('units_available') <= 8 else 'adequate',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        sample_blood_stock.append(new_stock)
        
        return jsonify({
            'success': True,
            'message': 'Blood stock added successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/blood-stock/<int:stock_id>', methods=['DELETE'])
def delete_blood_stock(stock_id):
    """Delete blood stock"""
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        # Find and remove stock
        for i, stock in enumerate(sample_blood_stock):
            if stock['id'] == stock_id:
                sample_blood_stock.pop(i)
                break
        
        return jsonify({
            'success': True,
            'message': 'Blood stock deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# DASHBOARD STATISTICS
# ============================================

@admin_bp.route('/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        # Calculate blood stats
        total_units = sum(s['units_available'] for s in sample_blood_stock)
        critical_units = sum(s['units_available'] for s in sample_blood_stock if s['status'] == 'critical')
        low_units = sum(s['units_available'] for s in sample_blood_stock if s['status'] == 'low')
        adequate_units = sum(s['units_available'] for s in sample_blood_stock if s['status'] == 'adequate')
        
        # Blood type distribution
        blood_distribution = {}
        for s in sample_blood_stock:
            bt = s['blood_type']
            blood_distribution[bt] = blood_distribution.get(bt, 0) + s['units_available']
        
        blood_distribution_list = [{'blood_type': k, 'total_units': v} for k, v in blood_distribution.items()]
        
        return jsonify({
            'success': True,
            'stats': {
                'users': {
                    'total_users': len(sample_users),
                    'total_donors': len([u for u in sample_users if u['user_type'] == 'donor']),
                    'active_users': len([u for u in sample_users if u['is_active']])
                },
                'blood': {
                    'total_units': total_units,
                    'critical_units': critical_units,
                    'low_units': low_units,
                    'adequate_units': adequate_units
                },
                'blood_distribution': blood_distribution_list
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# EMAIL NOTIFICATIONS
# ============================================

@admin_bp.route('/send-email', methods=['POST'])
def send_email():
    """Send email notification (simulated)"""
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        data = request.json
        recipient_type = data.get('recipient_type')
        subject = data.get('subject')
        message = data.get('message')
        
        # Count recipients (simulated)
        if recipient_type == 'all':
            recipient_count = len(sample_users)
        elif recipient_type == 'donors':
            recipient_count = len([u for u in sample_users if u['user_type'] == 'donor'])
        else:
            recipient_count = 0
        
        print(f"\n📧 EMAIL NOTIFICATION (SIMULATED):")
        print(f"   To: {recipient_type} ({recipient_count} recipients)")
        print(f"   Subject: {subject}")
        print(f"   Message: {message[:100]}...")
        
        return jsonify({
            'success': True,
            'message': f'Email sent to {recipient_count} recipients',
            'sent': recipient_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500