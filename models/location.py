from pymongo import MongoClient
from config import Config
from datetime import datetime
import requests
import json

class Location:
    def __init__(self):
        """Initialize Location model with MongoDB connection"""
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client.hotel_booking
        self.collection = self.db.hotel_info
        self.google_api_key = Config.GOOGLE_MAPS_API_KEY
    
    def get_hotel_info(self):
        """Get hotel location and contact information"""
        try:
            hotel_info = self.collection.find_one({'type': 'hotel_info'})
            if not hotel_info:
                # Create default hotel information
                hotel_info = self.create_default_hotel_info()
            return hotel_info
        except Exception as e:
            print(f"Error getting hotel info: {e}")
            return None
    
    def create_default_hotel_info(self):
        """Create default hotel information"""
        try:
            hotel_info = {
                'type': 'hotel_info',
                'name': 'Grand Manhattan Hotel & Suites',
                'address': '234 W 42nd St, New York, NY 10036',
                'coordinates': {
                    'latitude': 40.7590,  # Times Square area - real coordinates
                    'longitude': -73.9845
                },
                'contact': {
                    'phone': '(212) 555-0123',
                    'email': 'info@grandmanhattanhotel.com',
                    'website': 'www.grandmanhattanhotel.com'
                },
                'description': 'Experience luxury in the heart of Manhattan at Grand Manhattan Hotel & Suites. Located just steps from Times Square, Broadway theaters, and world-class shopping, our elegant accommodations offer the perfect base for exploring New York City.',
                'amenities': [
                    '24/7 Concierge Service',
                    'Complimentary WiFi',
                    'Fitness Center & Spa',
                    'Business Center',
                    'Rooftop Terrace',
                    '24-Hour Room Service',
                    'Valet Parking',
                    'Broadway View Restaurant',
                    'Meeting & Event Spaces',
                    'Airport Transportation'
                ],
                'check_in_time': '3:00 PM',
                'check_out_time': '11:00 AM',
                'policies': {
                    'cancellation': '24 hours before check-in for full refund',
                    'pets': 'Pet-friendly rooms available ($50/night)',
                    'smoking': 'Non-smoking property',
                    'children': 'Children under 12 stay free with adult'
                },
                'social_media': {
                    'facebook': 'https://facebook.com/grandmanhattanhotel',
                    'instagram': '@grandmanhattanhotel',
                    'twitter': '@grandmanhattannyc'
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.collection.insert_one(hotel_info)
            if result.inserted_id:
                hotel_info['_id'] = result.inserted_id
                print("✅ Default hotel information created")
                return hotel_info
            return None
        except Exception as e:
            print(f"Error creating default hotel info: {e}")
            return None
    
    def update_hotel_info(self, updates):
        """Update hotel information"""
        try:
            updates['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'type': 'hotel_info'},
                {'$set': updates}
            )
            return {
                'success': result.modified_count > 0,
                'message': 'Hotel information updated successfully' if result.modified_count > 0 else 'No changes made'
            }
        except Exception as e:
            print(f"Error updating hotel info: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_nearby_places(self, place_type='tourist_attraction', radius=5000):
        """Get nearby places using Google Places API"""
        
        # If API key is not configured, return mock data
        if not self.google_api_key or self.google_api_key == 'YOUR_API_KEY_HERE':
            return self._get_mock_places(place_type)
        
        try:
            hotel_info = self.get_hotel_info()
            if not hotel_info or 'coordinates' not in hotel_info:
                return self._get_mock_places(place_type)
            
            # Map place types to Google Places API types
            google_place_types = {
                'tourist_attraction': 'tourist_attraction',
                'restaurant': 'restaurant',
                'shopping_mall': 'shopping_mall',
                'hospital': 'hospital',
                'bank': 'bank',
                'gas_station': 'gas_station',
                'pharmacy': 'pharmacy'
            }
            
            google_type = google_place_types.get(place_type, 'tourist_attraction')
            coordinates = hotel_info['coordinates']
            
            # Google Places Nearby Search API
            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
            params = {
                'location': f"{coordinates['latitude']},{coordinates['longitude']}",
                'radius': radius,
                'type': google_type,
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                places = []
                
                for place in data.get('results', [])[:10]:  # Limit to 10 results
                    place_info = {
                        'name': place.get('name', 'Unknown'),
                        'address': place.get('vicinity', 'Address not available'),
                        'rating': place.get('rating', 0),
                        'type': place_type.replace('_', ' ').title(),
                        'coordinates': {
                            'lat': place['geometry']['location']['lat'],
                            'lng': place['geometry']['location']['lng']
                        },
                        'place_id': place.get('place_id', ''),
                        'photo_reference': place.get('photos', [{}])[0].get('photo_reference', '') if place.get('photos') else '',
                        'price_level': place.get('price_level', 0),
                        'user_ratings_total': place.get('user_ratings_total', 0)
                    }
                    
                    # Calculate distance (simple approximation)
                    distance = self._calculate_distance(
                        coordinates['latitude'], coordinates['longitude'],
                        place['geometry']['location']['lat'], place['geometry']['location']['lng']
                    )
                    place_info['distance'] = f"{distance:.1f} miles"
                    
                    places.append(place_info)
                
                return places
            else:
                print(f"Google Places API error: {response.status_code}")
                return self._get_mock_places(place_type)
                
        except Exception as e:
            print(f"Error fetching nearby places: {e}")
            return self._get_mock_places(place_type)
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in miles"""
        import math
        
        # Haversine formula
        R = 3959  # Earth's radius in miles
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _get_mock_places(self, place_type):
        """Return mock data when Google API is not available"""
        mock_places = {
            'tourist_attraction': [
                {
                    'name': 'Times Square',
                    'address': 'Times Square, New York, NY 10036',
                    'distance': '0.1 miles',
                    'rating': 4.2,
                    'type': 'Tourist Attraction',
                    'coordinates': {'lat': 40.7580, 'lng': -73.9855}
                },
                {
                    'name': 'Broadway Theater District',
                    'address': 'Broadway, New York, NY 10036',
                    'distance': '0.2 miles',
                    'rating': 4.8,
                    'type': 'Entertainment District',
                    'coordinates': {'lat': 40.7590, 'lng': -73.9845}
                },
                {
                    'name': 'Empire State Building',
                    'address': '350 5th Ave, New York, NY 10118',
                    'distance': '0.6 miles',
                    'rating': 4.5,
                    'type': 'Landmark',
                    'coordinates': {'lat': 40.7484, 'lng': -73.9857}
                },
                {
                    'name': 'Central Park',
                    'address': 'Central Park, New York, NY 10024',
                    'distance': '0.8 miles',
                    'rating': 4.7,
                    'type': 'Park',
                    'coordinates': {'lat': 40.7829, 'lng': -73.9654}
                },
                {
                    'name': 'Rockefeller Center',
                    'address': '45 Rockefeller Plaza, New York, NY 10111',
                    'distance': '0.4 miles',
                    'rating': 4.6,
                    'type': 'Tourist Attraction',
                    'coordinates': {'lat': 40.7587, 'lng': -73.9787}
                }
            ],
            'restaurant': [
                {
                    'name': 'Carmines',
                    'address': '200 W 44th St, New York, NY 10036',
                    'distance': '0.1 miles',
                    'rating': 4.4,
                    'type': 'Italian Restaurant',
                    'coordinates': {'lat': 40.7589, 'lng': -73.9851}
                },
                {
                    'name': 'Juniors Restaurant',
                    'address': '386 Flatbush Ave Ext, Brooklyn, NY 11201',
                    'distance': '0.2 miles',
                    'rating': 4.3,
                    'type': 'American Restaurant',
                    'coordinates': {'lat': 40.7580, 'lng': -73.9840}
                },
                {
                    'name': 'The View Restaurant',
                    'address': '1535 Broadway, New York, NY 10036',
                    'distance': '0.1 miles',
                    'rating': 4.2,
                    'type': 'American Fine Dining',
                    'coordinates': {'lat': 40.7582, 'lng': -73.9856}
                },
                {
                    'name': 'Blue Fin',
                    'address': '1567 Broadway, New York, NY 10036',
                    'distance': '0.1 miles',
                    'rating': 4.1,
                    'type': 'Seafood Restaurant',
                    'coordinates': {'lat': 40.7590, 'lng': -73.9850}
                },
                {
                    'name': "Joe Allen Restaurant",
                    'address': '326 W 46th St, New York, NY 10036',
                    'distance': '0.2 miles',
                    'rating': 4.3,
                    'type': 'American Bistro',
                    'coordinates': {'lat': 40.7595, 'lng': -73.9870}
                }
            ],
            'shopping_mall': [
                {
                    'name': 'Times Square Tower',
                    'address': '7 Times Square, New York, NY 10036',
                    'distance': '0.1 miles',
                    'rating': 4.2,
                    'type': 'Shopping Center',
                    'coordinates': {'lat': 40.7580, 'lng': -73.9855}
                },
                {
                    'name': "Macy's Herald Square",
                    'address': '151 W 34th St, New York, NY 10001',
                    'distance': '0.7 miles',
                    'rating': 4.1,
                    'type': 'Department Store',
                    'coordinates': {'lat': 40.7505, 'lng': -73.9934}
                },
                {
                    'name': 'Bryant Park Shops',
                    'address': 'Bryant Park, New York, NY 10018',
                    'distance': '0.3 miles',
                    'rating': 4.3,
                    'type': 'Shopping District',
                    'coordinates': {'lat': 40.7536, 'lng': -73.9832}
                },
                {
                    'name': 'The Shops at Columbus Circle',
                    'address': '10 Columbus Cir, New York, NY 10019',
                    'distance': '0.9 miles',
                    'rating': 4.4,
                    'type': 'Shopping Mall',
                    'coordinates': {'lat': 40.7681, 'lng': -73.9819}
                }
            ]
        }
        
        return mock_places.get(place_type, [])
    
    def get_place_photo_url(self, photo_reference, max_width=400):
        """Get Google Places photo URL"""
        if not photo_reference or not self.google_api_key or self.google_api_key == 'YOUR_API_KEY_HERE':
            return None
        
        return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photoreference={photo_reference}&key={self.google_api_key}"
    
    def get_place_details(self, place_id):
        """Get detailed information about a place"""
        if not place_id or not self.google_api_key or self.google_api_key == 'YOUR_API_KEY_HERE':
            return None
        
        try:
            url = 'https://maps.googleapis.com/maps/api/place/details/json'
            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,formatted_phone_number,website,opening_hours,reviews,photos,rating,price_level',
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('result', {})
            else:
                print(f"Google Place Details API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching place details: {e}")
            return None
    
    def get_directions_url(self, destination_address=None):
        """Generate Google Maps directions URL"""
        hotel_info = self.get_hotel_info()
        if not hotel_info:
            return None
        
        hotel_address = hotel_info.get('address', '')
        if destination_address:
            # Directions from hotel to destination
            return f"https://www.google.com/maps/dir/{hotel_address.replace(' ', '+')}/{destination_address.replace(' ', '+')}"
        else:
            # Directions to hotel
            return f"https://www.google.com/maps/place/{hotel_address.replace(' ', '+')}"
    
    def close_connection(self):
        """Close MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()
