from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime
import os

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/hotel_booking')
            cls._instance.client = MongoClient(mongo_uri)
            cls._instance.db = cls._instance.client.get_database()
        return cls._instance

class User:
    def __init__(self):
        self.db = Database().db
        self.collection = self.db.users
        
    def create_user(self, name, email, password, role='client'):
        """Create a new user"""
        # Check if user already exists
        if self.collection.find_one({'email': email}):
            return {'success': False, 'message': 'Email already exists'}
        
        user_data = {
            'name': name,
            'email': email.lower(),
            'password': generate_password_hash(password),
            'role': role,
            'created_at': datetime.utcnow()
        }
        
        try:
            result = self.collection.insert_one(user_data)
            return {'success': True, 'user_id': str(result.inserted_id)}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        user = self.collection.find_one({'email': email.lower()})
        
        if user and check_password_hash(user['password'], password):
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
            return {'success': True, 'user': user}
        
        return {'success': False, 'message': 'Invalid email or password'}
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                return user
        except:
            pass
        return None
    
    def create_admin_user(self):
        """Create default admin user if none exists"""
        admin = self.collection.find_one({'role': 'admin'})
        if not admin:
            return self.create_user(
                name='Admin',
                email='admin@hotel.com',
                password='admin123',
                role='admin'
            )
