from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.location import Location
from models.user import User
from config import Config
import json

location_bp = Blueprint('location', __name__)

@location_bp.route('/hotel-info')
def hotel_info():
    """Display hotel information and location"""
    location_model = Location()
    hotel_info = location_model.get_hotel_info()
    
    # Get nearby places for different categories
    attractions = location_model.get_nearby_places('tourist_attraction')
    restaurants = location_model.get_nearby_places('restaurant')
    shopping = location_model.get_nearby_places('shopping_mall')
    
    location_model.close_connection()
    
    return render_template('location/hotel_info.html',
                         hotel_info=hotel_info,
                         attractions=attractions,
                         restaurants=restaurants,
                         shopping=shopping,
                         google_maps_api_key=Config.GOOGLE_MAPS_API_KEY)

@location_bp.route('/api/nearby-places')
def api_nearby_places():
    """API endpoint to get nearby places"""
    place_type = request.args.get('type', 'tourist_attraction')
    radius = request.args.get('radius', 5000, type=int)
    
    location_model = Location()
    places = location_model.get_nearby_places(place_type, radius)
    location_model.close_connection()
    
    return jsonify({
        'success': True,
        'places': places,
        'type': place_type
    })

@location_bp.route('/directions')
def directions():
    """Get directions to hotel or from hotel to destination"""
    destination = request.args.get('to', '')
    
    location_model = Location()
    directions_url = location_model.get_directions_url(destination if destination else None)
    location_model.close_connection()
    
    if directions_url:
        return redirect(directions_url)
    else:
        return jsonify({'success': False, 'message': 'Unable to generate directions'})

@location_bp.route('/admin/hotel-info')
def admin_hotel_info():
    """Admin page to manage hotel information"""
    # Check if user is admin
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_model = User()
    user = user_model.get_user_by_id(session['user_id'])
    if not user or user.get('role') != 'admin':
        return redirect(url_for('main.dashboard'))
    
    location_model = Location()
    hotel_info = location_model.get_hotel_info()
    location_model.close_connection()
    
    return render_template('admin/hotel_info.html', hotel_info=hotel_info)

@location_bp.route('/admin/hotel-info/update', methods=['POST'])
def admin_update_hotel_info():
    """Update hotel information (admin only)"""
    # Check if user is admin
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    user_model = User()
    user = user_model.get_user_by_id(session['user_id'])
    if not user or user.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'})
    
    try:
        data = request.get_json()
        
        # Prepare updates
        updates = {}
        if 'name' in data:
            updates['name'] = data['name']
        if 'address' in data:
            updates['address'] = data['address']
        if 'coordinates' in data:
            updates['coordinates'] = data['coordinates']
        if 'contact' in data:
            updates['contact'] = data['contact']
        if 'description' in data:
            updates['description'] = data['description']
        if 'amenities' in data:
            updates['amenities'] = data['amenities']
        if 'policies' in data:
            updates['policies'] = data['policies']
        
        location_model = Location()
        result = location_model.update_hotel_info(updates)
        location_model.close_connection()
        user_model.close_connection()
        
        return jsonify(result)
        
    except Exception as e:
        user_model.close_connection()
        return jsonify({'success': False, 'message': str(e)})

@location_bp.route('/contact')
def contact():
    """Contact page with hotel information"""
    location_model = Location()
    hotel_info = location_model.get_hotel_info()
    location_model.close_connection()
    
    return render_template('location/contact.html', 
                         hotel_info=hotel_info,
                         google_maps_api_key=Config.GOOGLE_MAPS_API_KEY)

@location_bp.route('/api/place-details/<place_id>')
def api_place_details(place_id):
    """API endpoint to get detailed place information"""
    location_model = Location()
    place_details = location_model.get_place_details(place_id)
    location_model.close_connection()
    
    if place_details:
        return jsonify({'success': True, 'place': place_details})
    else:
        return jsonify({'success': False, 'message': 'Place details not found'})

@location_bp.route('/api/place-photo/<photo_reference>')
def api_place_photo(photo_reference):
    """API endpoint to get place photo URL"""
    max_width = request.args.get('width', 400, type=int)
    
    location_model = Location()
    photo_url = location_model.get_place_photo_url(photo_reference, max_width)
    location_model.close_connection()
    
    if photo_url:
        return jsonify({'success': True, 'photo_url': photo_url})
    else:
        return jsonify({'success': False, 'message': 'Photo not available'})
