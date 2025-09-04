from flask import Blueprint, render_template, session, redirect, url_for, flash
from functools import wraps
from models.user import User
from models.room import Room
from models.booking import Booking

main_bp = Blueprint('main', __name__)
user_model = User()
room_model = Room()
booking_model = Booking()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    user = user_model.get_user_by_id(session['user_id'])
    
    # Get user's recent bookings
    bookings_result = booking_model.get_user_bookings(session['user_id'])
    recent_bookings = bookings_result['bookings'][:3] if bookings_result['success'] else []
    
    return render_template('dashboard.html', user=user, recent_bookings=recent_bookings)

@main_bp.route('/admin')
@admin_required
def admin_dashboard():
    user = user_model.get_user_by_id(session['user_id'])
    
    # Get statistics
    room_stats = room_model.get_room_count()
    booking_stats = booking_model.get_booking_stats()
    
    stats = {
        'rooms': room_stats if room_stats['success'] else {'total': 0, 'available': 0},
        'bookings': booking_stats['stats'] if booking_stats['success'] else {
            'total': 0, 'pending': 0, 'confirmed': 0, 'cancelled': 0, 'completed': 0, 'revenue': 0
        }
    }
    
    return render_template('admin/dashboard.html', user=user, stats=stats)
