# Hotel Booking System

A complete hotel booking application built with Flask, MongoDB, and Google APIs. This production-ready system manages hotel operations including room booking, user management, location services, and nearby attractions.

## 🌟 Features Overview

### 🏨 **Core Hotel Operations**
- **Complete Booking System** - Room reservations with real-time availability checking
- **User Management** - Registration, authentication, and role-based access control  
- **Room Management** - Admin interface for room CRUD operations with search/filtering
- **Admin Dashboard** - Comprehensive management interface with booking oversight

### 📍 **Location & Maps Integration**
- **Hotel Location Display** - Clean location information with Google Maps integration
- **Nearby Places** - Real-time attractions, restaurants, and shopping data via Google Places API
- **Live Data Refresh** - Dynamic loading of nearby places with ratings and reviews
- **Direct Maps Links** - One-click access to Google Maps for directions and details

### 🔐 **Security & Authentication**
- **Secure User Authentication** - Password hashing with session management
- **Role-Based Access Control** - Admin and Client user roles with protected routes
- **Input Validation** - Comprehensive form validation and data sanitization

### 📱 **User Experience**
- **Responsive Design** - Mobile-first Bootstrap interface
- **Interactive Elements** - AJAX-powered live data updates
- **Clean Navigation** - Intuitive user interface with role-specific dashboards
- **Real-time Feedback** - Toast notifications and loading states

## 🚀 Technology Stack

**Backend:**
- **Flask 2.3.3** - Python web framework
- **MongoDB** - NoSQL database with PyMongo
- **Google APIs** - Places API for location services
- **Werkzeug** - Password hashing and security

**Frontend:**
- **Bootstrap 5** - Responsive CSS framework
- **JavaScript (ES6+)** - Interactive functionality
- **Font Awesome** - Icons and visual elements
- **AJAX** - Asynchronous data loading

**Integration:**
- **Google Places API** - Real-time nearby places data
- **Google Maps** - Location and directions services
- **RESTful APIs** - Clean API endpoints for data exchange
- Add, edit, delete rooms
- Room statistics dashboard
- Sample room creation
- Real-time room count display

✅ **Public Room Browsing**
- Browse available rooms
- Advanced filtering (price, capacity, amenities)
- Room details page
- Responsive room cards with images

✅ **MongoDB Integration**
- User model with CRUD operations
- Room model with search functionality
- Database connection management
- Automatic admin user creation

✅ **Responsive Design**
- Bootstrap 5 integration
- Mobile-friendly interface
- Clean and modern UI

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB (local installation or MongoDB Atlas)
- Google Maps API Key (for location features)

### Installation

1. **Clone and navigate to the project**
   ```bash
   cd "c:\Users\admin\Documents\@ popop\08th Aug\hotelbooking"
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file with the following:
   ```env
   SECRET_KEY=your-secret-key-here
   MONGO_URI=mongodb://localhost:27017/hotel_booking
   GOOGLE_MAPS_API_KEY=your-google-maps-api-key
   ```

5. **Set up MongoDB**
   - **Local MongoDB**: Ensure MongoDB is running on `mongodb://localhost:27017`
   - **MongoDB Atlas**: Update the `MONGO_URI` in `.env` file

6. **Get Google Maps API Key**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Places API for your project
   - Create an API key and add it to `.env`

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Access the application**
   - Open your browser and go to `http://localhost:5000`

## 🔐 Default Admin Account

A default admin account is automatically created on first run:
- **Email**: admin@hotel.com
- **Password**: admin123

## 📁 Project Structure

```
hotel-booking-system/
├── app.py                    # Main Flask application
├── config.py                # Configuration settings  
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── models/                  # Database models
│   ├── user.py             # User model and authentication
│   ├── room.py             # Room model and management
│   ├── booking.py          # Booking model and operations
│   └── location.py         # Location and Google API integration
├── routes/                  # Application routes
│   ├── auth.py             # Authentication routes
│   ├── main.py             # Main pages (dashboard, home)
│   ├── room.py             # Room management routes
│   ├── booking.py          # Booking system routes
│   └── location.py         # Location and maps routes
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── index.html          # Homepage
│   ├── dashboard.html      # User dashboard
│   ├── auth/               # Authentication templates
│   │   ├── login.html      # Login page
│   │   └── register.html   # Registration page
│   ├── rooms/              # Room templates
│   │   ├── browse.html     # Room browsing page
│   │   └── details.html    # Room details page
│   ├── booking/            # Booking templates
│   │   ├── book_room.html  # Room booking page
│   │   ├── booking_details.html # Booking details
│   │   ├── booking_form.html    # Booking form
│   │   └── my_bookings.html     # User bookings
│   ├── location/           # Location templates
│   │   ├── hotel_info.html # Hotel location and info
│   │   └── contact.html    # Contact page
│   └── admin/              # Admin templates
│       ├── dashboard.html  # Admin dashboard
│       ├── rooms.html      # Room management
│       ├── room_form.html  # Room create/edit form
│       ├── manage_bookings.html # Booking management
│       └── hotel_info.html # Hotel info management
├── static/                 # Static files
│   ├── css/
│   │   └── style.css      # Custom styles
│   ├── js/
│   │   └── main.js        # JavaScript functionality
│   └── images/            # Static images
└── utils/                 # Utility functions
    └── helpers.py         # Helper functions
```
│   ├── auth/
│   │   ├── login.html    # Login form
│   │   └── register.html # Registration form
│   └── admin/
│       └── dashboard.html # Admin dashboard
├── models/              # Database models
│   ├── __init__.py
│   └── user.py          # User model
├── routes/              # Route handlers
│   ├── __init__.py
│   ├── auth.py          # Authentication routes
│   └── main.py          # Main routes
└── utils/               # Helper functions
    ├── __init__.py
    └── helpers.py       # Utility functions
```

## 🔧 API Endpoints

### Authentication
- `GET/POST /auth/register` - User registration
- `GET/POST /auth/login` - User login  
- `GET /auth/logout` - User logout

### Main Routes
- `GET /` - Homepage
- `GET /dashboard` - User dashboard (login required)

### Room Management
- `GET /rooms` - Browse available rooms with filters
- `GET /rooms/<room_id>` - Room details page
- `GET/POST /rooms/book/<room_id>` - Book a room

### Booking Management
- `GET /bookings/my-bookings` - User's bookings
- `GET /bookings/<booking_id>` - Booking details
- `POST /bookings/<booking_id>/cancel` - Cancel booking

### Location Services
- `GET /location/hotel-info` - Hotel information and nearby places
- `GET /location/contact` - Contact page
- `GET /location/api/nearby-places` - API for nearby places data

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/rooms` - Room management
- `GET/POST /admin/rooms/add` - Add/edit rooms
- `GET /admin/bookings` - Booking management
- `POST /admin/bookings/<booking_id>/delete` - Delete booking
- `GET/POST /admin/hotel-info` - Hotel information management

## 🛡️ Security Features

- **Password Hashing**: Secure password storage with Werkzeug
- **Session Management**: Flask session-based authentication
- **Role-Based Access**: Admin and client roles with protected routes
- **Input Validation**: Server-side validation for all forms
- **Environment Variables**: Secure configuration management
- **CSRF Protection**: Form security measures

## 🎨 UI/UX Features

- **Responsive Design**: Mobile-first Bootstrap 5 interface
- **Interactive Elements**: AJAX-powered live data updates
- **Modern UI**: Clean, professional design with Font Awesome icons
- **User Feedback**: Toast notifications and loading states
- **Intuitive Navigation**: Role-based navigation and breadcrumbs
- **Form Validation**: Real-time client and server-side validation

## 🗄️ Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string",
  "password": "hashed_string",
  "role": "admin|client",
  "created_at": "datetime"
}
```

### Rooms Collection
```json
{
  "_id": "ObjectId", 
  "name": "string",
  "description": "string",
  "price_per_night": "number",
  "capacity": "number",
  "amenities": ["string"],
  "available": "boolean",
  "created_at": "datetime"
}
```

### Bookings Collection
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "room_id": "ObjectId", 
  "check_in_date": "datetime",
  "check_out_date": "datetime",
  "guests": "number",
  "total_amount": "number",
  "status": "confirmed|cancelled",
  "created_at": "datetime"
}
```

### Hotel Info Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "description": "string",
  "address": "string",
  "coordinates": {
    "latitude": "number",
    "longitude": "number"
  },
  "contact": {
    "phone": "string",
    "email": "string", 
    "website": "string"
  },
  "amenities": ["string"],
  "policies": {
    "cancellation": "string",
    "pets": "string",
    "smoking": "string", 
    "children": "string"
  },
  "check_in_time": "string",
  "check_out_time": "string"
}
```

### Rooms Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "description": "string",
  "price": "number",
  "capacity": "number",
  "amenities": ["array of strings"],
  "image_url": "string",
  "available": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## 🔄 Next Phases

- **Phase 3**: Booking System
- **Phase 4**: Google Maps Integration
- **Phase 5**: Payment Integration & Final Features

## 🧪 Testing

To test the application:

1. **User Registration & Authentication**
   - Go to `/auth/register` to create a new account
   - Test login functionality with created account
   - Verify role-based access control

2. **Admin Features**
   - Login with admin@hotel.com / admin123
   - Access admin dashboard at `/admin/dashboard`
   - Test room management (create, edit, delete rooms)
   - Test booking management and statistics

3. **Booking System**
   - Browse rooms at `/rooms`
   - Test room filtering and search
   - Make a booking and verify availability checking
   - View booking details and history

4. **Location Features**
   - Visit `/location/hotel-info`
   - Test live data refresh for nearby places
   - Verify Google Maps integration links

## 🛠️ Development

### Adding New Features
1. Create models in `models/` directory
2. Add routes in `routes/` directory  
3. Create templates in `templates/` directory
4. Update navigation in `base.html`

### Database Operations
- All database operations are handled through model classes
- Connection pooling is managed automatically
- Error handling is built into model methods

## 📦 Dependencies

```
Flask==2.3.3
pymongo==4.3.3
python-dotenv==1.0.0
Werkzeug==2.3.7
requests==2.31.0
```

Additional frontend dependencies:
- **Bootstrap 5**: Responsive CSS framework
- **Font Awesome**: Professional icons  
- **JavaScript (ES6+)**: Interactive functionality

## 🚀 Deployment

For production deployment:

1. **Environment Configuration**
   ```env
   SECRET_KEY=strong-random-secret-key-here
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/hotel_booking
   GOOGLE_MAPS_API_KEY=your-production-api-key
   FLASK_ENV=production
   ```

2. **Use Production WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

3. **Database Setup**
   - Use MongoDB Atlas for cloud database
   - Configure proper database indexes
   - Set up backup procedures

4. **Security Considerations**
   - Enable HTTPS
   - Configure API key restrictions
   - Set up proper logging
   - Enable database authentication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Review the documentation
- Check the troubleshooting section in plan.md

---

**Hotel Booking System** - A complete hotel management solution built with modern web technologies.
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## 📄 License

This project is for educational purposes.

---

**Phase 2 Complete!** 🎉

## 🆕 What's New in Phase 2

### Room Management System
- **Admin Panel**: Complete room management interface
- **CRUD Operations**: Add, edit, delete, and view rooms
- **Room Statistics**: Real-time dashboard with room counts
- **Sample Data**: One-click sample room creation

### Public Features
- **Room Browsing**: Public page to view available rooms
- **Advanced Filtering**: Filter by price, capacity, and amenities
- **Room Details**: Detailed view with images and amenities
- **Responsive Design**: Mobile-friendly room cards

### Enhanced Navigation
- **Updated Menus**: New room browsing links
- **Admin Dropdown**: Organized admin functions
- **Breadcrumbs**: Easy navigation on room pages

Ready to proceed with Phase 3: Booking System!
