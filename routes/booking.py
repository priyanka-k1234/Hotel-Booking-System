from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.booking import Booking
from models.room import Room
from routes.main import login_required, admin_required
from datetime import datetime

booking_bp = Blueprint('booking', __name__)
booking_model = Booking()
room_model = Room()

@booking_bp.route('/book/<room_id>')
@login_required
def book_room(room_id):
    """Show booking form for a specific room"""
    room_result = room_model.get_room_by_id(room_id)
    if not room_result['success']:
        flash('Room not found', 'error')
        return redirect(url_for('room.browse_rooms'))
    
    room = room_result['room']
    return render_template('booking/book_room.html', room=room, date=datetime)

@booking_bp.route('/create', methods=['POST'])
@login_required
def create_booking():
    """Create a new booking"""
    room_id = request.form.get('room_id')
    check_in_str = request.form.get('check_in')
    check_out_str = request.form.get('check_out')
    
    # Validation
    if not all([room_id, check_in_str, check_out_str]):
        flash('All fields are required', 'error')
        return redirect(url_for('booking.book_room', room_id=room_id))
    
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format', 'error')
        return redirect(url_for('booking.book_room', room_id=room_id))
    
    # Get room to calculate price
    room_result = room_model.get_room_by_id(room_id)
    if not room_result['success']:
        flash('Room not found', 'error')
        return redirect(url_for('room.browse'))
    
    room = room_result['room']
    total_price = booking_model.calculate_booking_price(room['price'], check_in, check_out)
    
    if total_price <= 0:
        flash('Invalid date range', 'error')
        return redirect(url_for('booking.book_room', room_id=room_id))
    
    # Create booking
    result = booking_model.create_booking(
        user_id=session['user_id'],
        room_id=room_id,
        check_in=check_in,
        check_out=check_out,
        total_price=total_price
    )
    
    if result['success']:
        flash(f'Booking created successfully! Total: ${total_price:.2f}', 'success')
        return redirect(url_for('booking.booking_details', booking_id=result['booking_id']))
    else:
        flash(result['message'], 'error')
        return redirect(url_for('booking.book_room', room_id=room_id))

@booking_bp.route('/my-bookings')
@login_required
def my_bookings():
    """Show user's bookings"""
    result = booking_model.get_user_bookings(session['user_id'])
    bookings = result['bookings'] if result['success'] else []
    
    # Calculate booking statistics
    stats = {
        'total': len(bookings),
        'confirmed': len([b for b in bookings if b['status'] == 'confirmed']),
        'pending': len([b for b in bookings if b['status'] == 'pending']),
        'completed': len([b for b in bookings if b['status'] == 'completed'])
    }
    
    return render_template('booking/my_bookings.html', bookings=bookings, stats=stats)

@booking_bp.route('/details/<booking_id>')
@login_required
def booking_details(booking_id):
    """Show booking details"""
    result = booking_model.get_booking_by_id(booking_id)
    
    if not result['success']:
        flash('Booking not found', 'error')
        return redirect(url_for('booking.my_bookings'))
    
    booking = result['booking']
    
    # Check if user owns this booking or is admin
    if session['user_role'] != 'admin' and str(booking['user_id']) != session['user_id']:
        flash('Access denied', 'error')
        return redirect(url_for('booking.my_bookings'))
    
    return render_template('booking/booking_details.html', booking=booking)

@booking_bp.route('/cancel/<booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking"""
    user_id = session['user_id'] if session['user_role'] != 'admin' else None
    result = booking_model.cancel_booking(booking_id, user_id)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('booking.booking_details', booking_id=booking_id))

@booking_bp.route('/admin/bookings')
@admin_required
def admin_bookings():
    """Admin view of all bookings"""
    result = booking_model.get_all_bookings()
    bookings = result['bookings'] if result['success'] else []
    
    # Calculate booking statistics
    stats = {
        'total': len(bookings),
        'confirmed': len([b for b in bookings if b['status'] == 'confirmed']),
        'pending': len([b for b in bookings if b['status'] == 'pending']),
        'completed': len([b for b in bookings if b['status'] == 'completed']),
        'cancelled': len([b for b in bookings if b['status'] == 'cancelled'])
    }
    
    return render_template('admin/manage_bookings.html', bookings=bookings, stats=stats)

@booking_bp.route('/admin/update-status/<booking_id>', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    """Update booking status (admin only)"""
    new_status = request.form.get('status')
    payment_id = request.form.get('payment_id')
    
    result = booking_model.update_booking_status(booking_id, new_status, payment_id)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('booking.admin_bookings'))

@booking_bp.route('/admin/booking/details/<booking_id>')
@admin_required
def admin_booking_details(booking_id):
    """Get booking details for admin modal (AJAX endpoint)"""
    result = booking_model.get_booking_by_id(booking_id)
    
    if not result['success']:
        return jsonify({'success': False, 'message': 'Booking not found'})
    
    booking = result['booking']
    
    # Render the booking details as HTML
    html_content = render_template('admin/booking_details_modal.html', booking=booking)
    
    return jsonify({'success': True, 'html': html_content})

@booking_bp.route('/admin/booking/delete/<booking_id>', methods=['POST'])
@admin_required
def admin_delete_booking(booking_id):
    """Delete a booking (admin only)"""
    result = booking_model.cancel_booking(booking_id)
    
    if result['success']:
        return jsonify({'success': True, 'message': 'Booking deleted successfully'})
    else:
        return jsonify({'success': False, 'message': result['message']})

@booking_bp.route('/check-availability', methods=['POST'])
def check_availability():
    """AJAX endpoint to check room availability"""
    room_id = request.json.get('room_id')
    check_in_str = request.json.get('check_in')
    check_out_str = request.json.get('check_out')
    
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
        
        available = booking_model.is_room_available(room_id, check_in, check_out)
        
        if available:
            # Calculate price
            room_result = room_model.get_room_by_id(room_id)
            if room_result['success']:
                total_price = booking_model.calculate_booking_price(
                    room_result['room']['price'], check_in, check_out
                )
                nights = (check_out - check_in).days
                return jsonify({
                    'available': True,
                    'total_price': total_price,
                    'nights': nights,
                    'price_per_night': room_result['room']['price']
                })
        
        return jsonify({'available': False, 'message': 'Room not available for selected dates'})
    
    except Exception as e:
        return jsonify({'available': False, 'message': 'Invalid request'}), 400
