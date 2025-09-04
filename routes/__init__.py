from .auth import auth_bp
from .main import main_bp
from .room import room_bp
from .booking import booking_bp
from .location import location_bp

__all__ = ['auth_bp', 'main_bp', 'room_bp', 'booking_bp', 'location_bp']
