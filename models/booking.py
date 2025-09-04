from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import os

class Booking:
    def __init__(self):
        self.db = self._get_database()
        self.collection = self.db.bookings
        
    def _get_database(self):
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/hotel_booking')
        client = MongoClient(mongo_uri)
        return client.get_database()
    
    def create_booking(self, user_id, room_id, check_in, check_out, total_price):
        """Create a new booking"""
        # Convert date objects to datetime objects for MongoDB compatibility
        if hasattr(check_in, 'date'):
            # It's already a datetime object
            check_in_dt = check_in
        else:
            # It's a date object, convert to datetime
            check_in_dt = datetime.combine(check_in, datetime.min.time())
            
        if hasattr(check_out, 'date'):
            # It's already a datetime object
            check_out_dt = check_out
        else:
            # It's a date object, convert to datetime
            check_out_dt = datetime.combine(check_out, datetime.min.time())
        
        # Validate dates
        if check_in >= check_out:
            return {'success': False, 'message': 'Check-out date must be after check-in date'}
        
        if check_in < datetime.now().date():
            return {'success': False, 'message': 'Check-in date cannot be in the past'}
        
        # Check room availability
        if not self.is_room_available(room_id, check_in, check_out):
            return {'success': False, 'message': 'Room is not available for the selected dates'}
        
        booking_data = {
            'user_id': ObjectId(user_id),
            'room_id': ObjectId(room_id),
            'check_in': check_in_dt,
            'check_out': check_out_dt,
            'total_price': float(total_price),
            'status': 'pending',
            'payment_id': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        try:
            result = self.collection.insert_one(booking_data)
            return {'success': True, 'booking_id': str(result.inserted_id)}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def is_room_available(self, room_id, check_in, check_out):
        """Check if room is available for given dates"""
        try:
            # Convert date objects to datetime objects for MongoDB compatibility
            if hasattr(check_in, 'date'):
                # It's already a datetime object
                check_in_dt = check_in
            else:
                # It's a date object, convert to datetime
                check_in_dt = datetime.combine(check_in, datetime.min.time())
                
            if hasattr(check_out, 'date'):
                # It's already a datetime object
                check_out_dt = check_out
            else:
                # It's a date object, convert to datetime
                check_out_dt = datetime.combine(check_out, datetime.min.time())
            
            # Find conflicting bookings
            conflicting_count = self.collection.count_documents({
                'room_id': ObjectId(room_id),
                'status': {'$in': ['pending', 'confirmed']},
                '$or': [
                    # Check-in date conflicts
                    {
                        'check_in': {'$lte': check_in_dt},
                        'check_out': {'$gt': check_in_dt}
                    },
                    # Check-out date conflicts
                    {
                        'check_in': {'$lt': check_out_dt},
                        'check_out': {'$gte': check_out_dt}
                    },
                    # Booking encompasses the requested period
                    {
                        'check_in': {'$gte': check_in_dt},
                        'check_out': {'$lte': check_out_dt}
                    }
                ]
            })
            
            return conflicting_count == 0
        except Exception as e:
            print(f"Error checking availability: {e}")
            return False
    
    def get_user_bookings(self, user_id):
        """Get all bookings for a user"""
        try:
            pipeline = [
                {'$match': {'user_id': ObjectId(user_id)}},
                {'$lookup': {
                    'from': 'rooms',
                    'localField': 'room_id',
                    'foreignField': '_id',
                    'as': 'room'
                }},
                {'$unwind': '$room'},
                {'$sort': {'created_at': -1}}
            ]
            
            bookings = list(self.collection.aggregate(pipeline))
            for booking in bookings:
                booking['_id'] = str(booking['_id'])
                booking['user_id'] = str(booking['user_id'])
                booking['room_id'] = str(booking['room_id'])
                booking['room']['_id'] = str(booking['room']['_id'])
                
                # Calculate additional fields
                check_in = booking['check_in']
                check_out = booking['check_out']
                
                # Handle both datetime and date objects
                if hasattr(check_in, 'date'):
                    check_in_date = check_in.date()
                else:
                    check_in_date = check_in
                    
                if hasattr(check_out, 'date'):
                    check_out_date = check_out.date()
                else:
                    check_out_date = check_out
                
                booking['nights'] = (check_out_date - check_in_date).days
                booking['guests'] = booking['room'].get('capacity', 1)  # Default to room capacity
            
            return {'success': True, 'bookings': bookings}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_all_bookings(self):
        """Get all bookings (admin use)"""
        try:
            pipeline = [
                {'$lookup': {
                    'from': 'rooms',
                    'localField': 'room_id',
                    'foreignField': '_id',
                    'as': 'room'
                }},
                {'$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user'
                }},
                {'$unwind': '$room'},
                {'$unwind': '$user'},
                {'$sort': {'created_at': -1}}
            ]
            
            bookings = list(self.collection.aggregate(pipeline))
            for booking in bookings:
                booking['_id'] = str(booking['_id'])
                booking['user_id'] = str(booking['user_id'])
                booking['room_id'] = str(booking['room_id'])
                booking['room']['_id'] = str(booking['room']['_id'])
                booking['user']['_id'] = str(booking['user']['_id'])
                # Remove password from user data
                booking['user'].pop('password', None)
                
                # Calculate additional fields
                check_in = booking['check_in']
                check_out = booking['check_out']
                
                # Handle both datetime and date objects
                if hasattr(check_in, 'date'):
                    check_in_date = check_in.date()
                else:
                    check_in_date = check_in
                    
                if hasattr(check_out, 'date'):
                    check_out_date = check_out.date()
                else:
                    check_out_date = check_out
                
                booking['nights'] = (check_out_date - check_in_date).days
                booking['guests'] = booking['room'].get('capacity', 1)  # Default to room capacity
            
            return {'success': True, 'bookings': bookings}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_booking_by_id(self, booking_id):
        """Get booking by ID"""
        try:
            pipeline = [
                {'$match': {'_id': ObjectId(booking_id)}},
                {'$lookup': {
                    'from': 'rooms',
                    'localField': 'room_id',
                    'foreignField': '_id',
                    'as': 'room'
                }},
                {'$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user'
                }},
                {'$unwind': '$room'},
                {'$unwind': '$user'}
            ]
            
            booking = list(self.collection.aggregate(pipeline))
            if booking:
                booking = booking[0]
                booking['_id'] = str(booking['_id'])
                booking['user_id'] = str(booking['user_id'])
                booking['room_id'] = str(booking['room_id'])
                booking['room']['_id'] = str(booking['room']['_id'])
                booking['user']['_id'] = str(booking['user']['_id'])
                booking['user'].pop('password', None)
                
                # Calculate additional fields
                check_in = booking['check_in']
                check_out = booking['check_out']
                
                # Handle both datetime and date objects
                if hasattr(check_in, 'date'):
                    check_in_date = check_in.date()
                else:
                    check_in_date = check_in
                    
                if hasattr(check_out, 'date'):
                    check_out_date = check_out.date()
                else:
                    check_out_date = check_out
                
                booking['nights'] = (check_out_date - check_in_date).days
                booking['guests'] = booking['room'].get('capacity', 1)  # Default to room capacity
                
                return {'success': True, 'booking': booking}
            
            return {'success': False, 'message': 'Booking not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def update_booking_status(self, booking_id, status, payment_id=None):
        """Update booking status"""
        valid_statuses = ['pending', 'confirmed', 'cancelled', 'completed']
        if status not in valid_statuses:
            return {'success': False, 'message': 'Invalid status'}
        
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow()
            }
            
            if payment_id:
                update_data['payment_id'] = payment_id
            
            result = self.collection.update_one(
                {'_id': ObjectId(booking_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': f'Booking status updated to {status}'}
            return {'success': False, 'message': 'Booking not found or no changes made'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def cancel_booking(self, booking_id, user_id=None):
        """Cancel a booking"""
        try:
            # Build query
            query = {'_id': ObjectId(booking_id)}
            if user_id:  # User can only cancel their own bookings
                query['user_id'] = ObjectId(user_id)
            
            # Check if booking exists and can be cancelled
            booking = self.collection.find_one(query)
            if not booking:
                return {'success': False, 'message': 'Booking not found or access denied'}
            
            if booking['status'] == 'cancelled':
                return {'success': False, 'message': 'Booking is already cancelled'}
            
            if booking['status'] == 'completed':
                return {'success': False, 'message': 'Cannot cancel completed booking'}
            
            # Check if cancellation is allowed (e.g., not on the same day)
            check_in_date = booking['check_in']
            if isinstance(check_in_date, datetime):
                check_in_date = check_in_date.date()
            
            if check_in_date <= datetime.now().date():
                return {'success': False, 'message': 'Cannot cancel booking on or after check-in date'}
            
            # Update status
            result = self.collection.update_one(
                query,
                {
                    '$set': {
                        'status': 'cancelled',
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'Booking cancelled successfully'}
            return {'success': False, 'message': 'Failed to cancel booking'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_booking_stats(self):
        """Get booking statistics for admin dashboard"""
        try:
            total_bookings = self.collection.count_documents({})
            pending_bookings = self.collection.count_documents({'status': 'pending'})
            confirmed_bookings = self.collection.count_documents({'status': 'confirmed'})
            cancelled_bookings = self.collection.count_documents({'status': 'cancelled'})
            completed_bookings = self.collection.count_documents({'status': 'completed'})
            
            # Calculate total revenue (confirmed + completed bookings)
            revenue_pipeline = [
                {'$match': {'status': {'$in': ['confirmed', 'completed']}}},
                {'$group': {'_id': None, 'total_revenue': {'$sum': '$total_price'}}}
            ]
            
            revenue_result = list(self.collection.aggregate(revenue_pipeline))
            total_revenue = revenue_result[0]['total_revenue'] if revenue_result else 0
            
            return {
                'success': True,
                'stats': {
                    'total': total_bookings,
                    'pending': pending_bookings,
                    'confirmed': confirmed_bookings,
                    'cancelled': cancelled_bookings,
                    'completed': completed_bookings,
                    'revenue': total_revenue
                }
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def calculate_booking_price(self, room_price, check_in, check_out):
        """Calculate total booking price"""
        if isinstance(check_in, str):
            check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
        if isinstance(check_out, str):
            check_out = datetime.strptime(check_out, '%Y-%m-%d').date()
        
        nights = (check_out - check_in).days
        return float(room_price) * nights if nights > 0 else 0
