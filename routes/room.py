from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.room import Room
from routes.main import admin_required

room_bp = Blueprint('room', __name__)
room_model = Room()

@room_bp.route('/admin/rooms')
@admin_required
def manage_rooms():
    """Admin room management page"""
    result = room_model.get_all_rooms()
    rooms = result.get('rooms', []) if result['success'] else []
    count_result = room_model.get_room_count()
    room_stats = count_result if count_result['success'] else {'total': 0, 'available': 0}
    
    return render_template('admin/rooms.html', rooms=rooms, room_stats=room_stats)

@room_bp.route('/admin/rooms/add', methods=['GET', 'POST'])
@admin_required
def add_room():
    """Add new room"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        capacity = request.form.get('capacity')
        amenities = request.form.getlist('amenities')
        image_url = request.form.get('image_url')
        
        # Validation
        if not all([name, description, price, capacity]):
            flash('All required fields must be filled', 'error')
            return render_template('admin/room_form.html', action='Add')
        
        try:
            price = float(price)
            capacity = int(capacity)
            if price <= 0 or capacity <= 0:
                raise ValueError("Price and capacity must be positive")
        except ValueError as e:
            flash('Invalid price or capacity value', 'error')
            return render_template('admin/room_form.html', action='Add')
        
        # Filter out empty amenities
        amenities = [a.strip() for a in amenities if a.strip()]
        
        result = room_model.create_room(name, description, price, capacity, amenities, image_url)
        
        if result['success']:
            flash('Room added successfully!', 'success')
            return redirect(url_for('room.manage_rooms'))
        else:
            flash(f'Error adding room: {result["message"]}', 'error')
    
    return render_template('admin/room_form.html', action='Add')

@room_bp.route('/admin/rooms/edit/<room_id>', methods=['GET', 'POST'])
@admin_required
def edit_room(room_id):
    """Edit existing room"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        capacity = request.form.get('capacity')
        amenities = request.form.getlist('amenities')
        image_url = request.form.get('image_url')
        available = request.form.get('available') == 'on'
        
        # Validation
        if not all([name, description, price, capacity]):
            flash('All required fields must be filled', 'error')
            return redirect(url_for('room.edit_room', room_id=room_id))
        
        try:
            price = float(price)
            capacity = int(capacity)
            if price <= 0 or capacity <= 0:
                raise ValueError("Price and capacity must be positive")
        except ValueError:
            flash('Invalid price or capacity value', 'error')
            return redirect(url_for('room.edit_room', room_id=room_id))
        
        # Filter out empty amenities
        amenities = [a.strip() for a in amenities if a.strip()]
        
        result = room_model.update_room(
            room_id, name, description, price, capacity, amenities, image_url, available
        )
        
        if result['success']:
            flash('Room updated successfully!', 'success')
            return redirect(url_for('room.manage_rooms'))
        else:
            flash(f'Error updating room: {result["message"]}', 'error')
    
    # Get room data for editing
    result = room_model.get_room_by_id(room_id)
    if not result['success']:
        flash('Room not found', 'error')
        return redirect(url_for('room.manage_rooms'))
    
    room = result['room']
    return render_template('admin/room_form.html', action='Edit', room=room)

@room_bp.route('/admin/rooms/delete/<room_id>', methods=['POST'])
@admin_required
def delete_room(room_id):
    """Delete room"""
    result = room_model.delete_room(room_id)
    
    if result['success']:
        flash('Room deleted successfully!', 'success')
    else:
        flash(f'Error deleting room: {result["message"]}', 'error')
    
    return redirect(url_for('room.manage_rooms'))

@room_bp.route('/admin/rooms/create-samples', methods=['POST'])
@admin_required
def create_sample_rooms():
    """Create sample rooms for testing"""
    result = room_model.create_sample_rooms()
    
    if result['success']:
        flash(f'Created {result["created"]} sample rooms successfully!', 'success')
    else:
        flash('Error creating sample rooms', 'error')
    
    return redirect(url_for('room.manage_rooms'))

@room_bp.route('/rooms')
def browse_rooms():
    """Public room browsing page"""
    # Get filter parameters
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_capacity = request.args.get('min_capacity', type=int)
    amenities = request.args.getlist('amenities')
    
    # Search rooms
    if any([min_price, max_price, min_capacity, amenities]):
        result = room_model.search_rooms(min_price, max_price, min_capacity, amenities)
    else:
        result = room_model.get_all_rooms(available_only=True)
    
    rooms = result.get('rooms', []) if result['success'] else []
    
    # Get all amenities for filter dropdown
    all_amenities = set()
    all_rooms_result = room_model.get_all_rooms(available_only=True)
    if all_rooms_result['success']:
        for room in all_rooms_result['rooms']:
            all_amenities.update(room.get('amenities', []))
    
    return render_template('rooms/browse.html', 
                         rooms=rooms, 
                         all_amenities=sorted(all_amenities),
                         filters={
                             'min_price': min_price,
                             'max_price': max_price,
                             'min_capacity': min_capacity,
                             'amenities': amenities
                         })

@room_bp.route('/rooms/<room_id>')
def room_details(room_id):
    """Room details page"""
    result = room_model.get_room_by_id(room_id)
    
    if not result['success']:
        flash('Room not found', 'error')
        return redirect(url_for('room.browse_rooms'))
    
    room = result['room']
    if not room['available']:
        flash('This room is currently not available', 'error')
        return redirect(url_for('room.browse_rooms'))
    
    return render_template('rooms/details.html', room=room)

@room_bp.route('/api/rooms/stats')
@admin_required
def room_stats_api():
    """API endpoint for room statistics"""
    result = room_model.get_room_count()
    if result['success']:
        return jsonify(result)
    return jsonify({'success': False, 'message': 'Failed to get stats'}), 500
