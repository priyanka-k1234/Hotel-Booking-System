from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

class Room:
    def __init__(self):
        self.db = self._get_database()
        self.collection = self.db.rooms
        
    def _get_database(self):
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/hotel_booking')
        client = MongoClient(mongo_uri)
        return client.get_database()
    
    def create_room(self, name, description, price, capacity, amenities=None, image_url=None):
        """Create a new room"""
        if amenities is None:
            amenities = []
            
        room_data = {
            'name': name,
            'description': description,
            'price': float(price),
            'capacity': int(capacity),
            'amenities': amenities,
            'image_url': image_url or '',
            'available': True,
            'created_at': datetime.utcnow()
        }
        
        try:
            result = self.collection.insert_one(room_data)
            return {'success': True, 'room_id': str(result.inserted_id)}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_all_rooms(self, available_only=False):
        """Get all rooms or only available ones"""
        query = {'available': True} if available_only else {}
        try:
            rooms = list(self.collection.find(query).sort('price', 1))
            for room in rooms:
                room['_id'] = str(room['_id'])
            return {'success': True, 'rooms': rooms}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_room_by_id(self, room_id):
        """Get room by ID"""
        try:
            room = self.collection.find_one({'_id': ObjectId(room_id)})
            if room:
                room['_id'] = str(room['_id'])
                return {'success': True, 'room': room}
            return {'success': False, 'message': 'Room not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def update_room(self, room_id, name=None, description=None, price=None, capacity=None, amenities=None, image_url=None, available=None):
        """Update room details"""
        try:
            update_data = {}
            if name is not None:
                update_data['name'] = name
            if description is not None:
                update_data['description'] = description
            if price is not None:
                update_data['price'] = float(price)
            if capacity is not None:
                update_data['capacity'] = int(capacity)
            if amenities is not None:
                update_data['amenities'] = amenities
            if image_url is not None:
                update_data['image_url'] = image_url
            if available is not None:
                update_data['available'] = available
            
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {'_id': ObjectId(room_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'Room updated successfully'}
            return {'success': False, 'message': 'No changes made or room not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def delete_room(self, room_id):
        """Delete a room"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(room_id)})
            if result.deleted_count > 0:
                return {'success': True, 'message': 'Room deleted successfully'}
            return {'success': False, 'message': 'Room not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def search_rooms(self, min_price=None, max_price=None, min_capacity=None, amenities=None):
        """Search rooms with filters"""
        try:
            query = {'available': True}
            
            if min_price is not None:
                query['price'] = {'$gte': float(min_price)}
            if max_price is not None:
                if 'price' in query:
                    query['price']['$lte'] = float(max_price)
                else:
                    query['price'] = {'$lte': float(max_price)}
            if min_capacity is not None:
                query['capacity'] = {'$gte': int(min_capacity)}
            if amenities:
                query['amenities'] = {'$in': amenities}
            
            rooms = list(self.collection.find(query).sort('price', 1))
            for room in rooms:
                room['_id'] = str(room['_id'])
            
            return {'success': True, 'rooms': rooms}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_room_count(self):
        """Get total room count"""
        try:
            total = self.collection.count_documents({})
            available = self.collection.count_documents({'available': True})
            return {'success': True, 'total': total, 'available': available}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def create_sample_rooms(self):
        """Create sample rooms for testing"""
        sample_rooms = [
            {
                'name': 'Deluxe Single Room',
                'description': 'A comfortable single room with modern amenities and city view.',
                'price': 89.99,
                'capacity': 1,
                'amenities': ['WiFi', 'TV', 'Air Conditioning', 'Mini Bar', 'City View'],
                'image_url': 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=500'
            },
            {
                'name': 'Premium Double Room',
                'description': 'Spacious double room with premium furnishing and garden view.',
                'price': 129.99,
                'capacity': 2,
                'amenities': ['WiFi', 'TV', 'Air Conditioning', 'Mini Bar', 'Garden View', 'Balcony'],
                'image_url': 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=500'
            },
            {
                'name': 'Family Suite',
                'description': 'Large family suite with separate bedroom and living area.',
                'price': 199.99,
                'capacity': 4,
                'amenities': ['WiFi', 'TV', 'Air Conditioning', 'Kitchen', 'Living Area', 'Ocean View'],
                'image_url': 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=500'
            },
            {
                'name': 'Executive Business Room',
                'description': 'Perfect for business travelers with work desk and meeting area.',
                'price': 159.99,
                'capacity': 2,
                'amenities': ['WiFi', 'TV', 'Air Conditioning', 'Work Desk', 'Business Center Access'],
                'image_url': 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=500'
            },
            {
                'name': 'Luxury Penthouse',
                'description': 'Ultimate luxury with panoramic views and premium services.',
                'price': 399.99,
                'capacity': 6,
                'amenities': ['WiFi', 'TV', 'Air Conditioning', 'Jacuzzi', 'Panoramic View', 'Butler Service', 'Private Terrace'],
                'image_url': 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=500'
            }
        ]
        
        created_count = 0
        for room_data in sample_rooms:
            result = self.create_room(**room_data)
            if result['success']:
                created_count += 1
        
        return {'success': True, 'created': created_count, 'total': len(sample_rooms)}
