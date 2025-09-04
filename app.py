from flask import Flask
from config import config
from routes import auth_bp, main_bp, room_bp, booking_bp, location_bp
from models.user import User
from models.location import Location
import os

def create_app(config_name=None):
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_CONFIG', 'development')
    app.config.from_object(config[config_name])
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(room_bp)
    app.register_blueprint(booking_bp, url_prefix='/booking')
    app.register_blueprint(location_bp, url_prefix='/location')
    
    # Initialize database and create admin user and hotel info
    with app.app_context():
        user_model = User()
        admin_result = user_model.create_admin_user()
        if admin_result and admin_result.get('success'):
            print("✅ Default admin user created: admin@hotel.com / admin123")
        else:
            print("ℹ️  Admin user already exists or error occurred")
        
        # Initialize hotel information
        location_model = Location()
        hotel_info = location_model.get_hotel_info()
        if hotel_info:
            print("✅ Hotel information initialized")
        location_model.close_connection()
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🏨 Hotel Booking App - Phase 4 Complete")
    print("=" * 50)
    print("Features implemented:")
    print("✅ User registration and login")
    print("✅ Role-based access control (Admin/Client)")
    print("✅ Session management")
    print("✅ Password hashing")
    print("✅ MongoDB integration")
    print("✅ Responsive design")
    print("✅ Basic templates and navigation")
    print("✅ Room management system")
    print("✅ Admin panel for rooms")
    print("✅ Public room browsing")
    print("✅ Room search and filtering")
    print("✅ Booking system with availability checking")
    print("✅ User booking management")
    print("✅ Admin booking oversight")
    print("✅ Real-time availability validation")
    print("✅ Booking statistics and reporting")
    print("✅ Hotel location and information management")
    print("✅ Interactive maps with nearby places")
    print("✅ Contact information and forms")
    print("✅ Admin hotel information management")
    print("")
    print("Default admin account:")
    print("Email: admin@hotel.com")
    print("Password: admin123")
    print("")
    print("Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
