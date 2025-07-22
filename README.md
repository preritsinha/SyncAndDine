# SyncAndDine 🍽️

<div align="center">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/Google_Places_API-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Places"/>
  <img src="https://img.shields.io/badge/Apple_Design-000000?style=for-the-badge&logo=apple&logoColor=white" alt="Apple Design"/>
  <img src="https://img.shields.io/badge/Dark_Mode-1C1C1E?style=for-the-badge&logo=moon&logoColor=white" alt="Dark Mode"/>
</div>

## 🌟 Overview

SyncAndDine is a sophisticated web application that revolutionizes how friends decide where to eat. Built with Apple's design philosophy, it features a clean, intuitive interface with dynamic restaurant discovery powered by Google Places API.

### ✨ Key Features

- **🎯 Dynamic Restaurant Discovery** - Live data from Google Places API
- **📍 Location-Based Search** - Find restaurants near you automatically  
- **👥 Social Groups** - Create dining groups and find mutual preferences
- **💫 Apple-Inspired UI** - Sophisticated design with glassmorphism effects
- **🌙 Dark Mode** - System-aware theme switching
- **📱 Responsive Design** - Perfect on all devices
- **⚡ Real-Time Filtering** - Instant results by cuisine, rating, and price

## 🚀 Live Demo

Experience SyncAndDine: [Your Deployment URL]

## 🏗️ Architecture

### Frontend
- **Apple Design System** - SF Pro fonts, blur effects, smooth animations
- **Responsive Layout** - Bootstrap 5 with custom Apple-style components
- **Theme System** - Automatic dark/light mode with system preference detection
- **Progressive Enhancement** - Works without JavaScript

### Backend
- **Flask Framework** - Modular blueprint architecture
- **Dynamic API Integration** - No database storage for restaurant data
- **User Management** - Secure authentication with Flask-Login
- **Group Management** - Social features for collaborative dining

### APIs & Services
- **Google Places API** - Live restaurant data and photos
- **Geolocation API** - Automatic location detection
- **RESTful Design** - Clean API endpoints for future mobile apps

## 📦 Installation

### Prerequisites
- Python 3.8+
- Google Places API Key
- Modern web browser

### Setup Steps

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd SyncAndDine
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   # Create .env file
   SECRET_KEY=your_secret_key_here
   DATABASE_URI=sqlite:///syncanddine.db
   JWT_SECRET_KEY=your_jwt_secret_key
   GOOGLE_PLACES_API_KEY=your_google_places_api_key
   ```

5. **Run Application**
   ```bash
   python run_app.py
   ```

6. **Access Application**
   ```
   http://localhost:5000
   ```

## 🎨 Design System

### Apple-Inspired Interface
- **Typography** - SF Pro Display font family
- **Colors** - Dynamic color system with dark mode support
- **Spacing** - Apple's 8pt grid system
- **Animations** - Smooth, purposeful transitions
- **Glassmorphism** - Translucent surfaces with blur effects

### Theme System
```javascript
// Automatic theme detection
const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

// Manual theme toggle
document.documentElement.setAttribute('data-theme', theme);
```

## 🔧 Core Features

### 1. Dynamic Restaurant Discovery
```python
@restaurants.route('/restaurants')
@login_required
def list_restaurants():
    """
    Fetch live restaurant data from Google Places API
    Apply real-time filters and return results
    """
    places_service = GooglePlacesService()
    restaurants = places_service.search_restaurants(lat, lon)
    # Apply filters and return results
```

**Features:**
- Live Google Places API integration
- Location-based search radius
- Real-time filtering by rating, cuisine, price
- No database storage - always fresh data

### 2. Social Group Management
```python
class Group(db.Model):
    """
    Dining groups for collaborative restaurant selection
    Supports admin controls and member management
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    share_code = db.Column(db.String(20), unique=True)
```

**Features:**
- Create and join dining groups
- Share groups via unique codes
- Admin controls for group settings
- Member preference tracking

### 3. User Preferences System
```python
class RestaurantLike(db.Model):
    """
    Track user preferences using Google Place IDs
    Supports group-specific preferences
    """
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    restaurant_google_id = db.Column(db.String(100))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    liked = db.Column(db.Boolean, default=True)
```

**Features:**
- Like/dislike restaurants
- Group-specific preferences
- Preference-based matching
- No duplicate storage

### 4. Location Services
```javascript
// Get user's current location
navigator.geolocation.getCurrentPosition(
    function(position) {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        // Update restaurant search with user location
    }
);
```

**Features:**
- Automatic location detection
- Manual coordinate input
- Location-based restaurant search
- Privacy-conscious implementation

## 📱 User Interface

### Restaurant Cards
- **Apple-style cards** with subtle shadows and rounded corners
- **High-quality images** from Google Places API
- **Rating badges** with star indicators
- **Smooth hover effects** with scale and blur transitions
- **Like buttons** with heart animations

### Navigation
- **Translucent navbar** with backdrop blur
- **Sticky positioning** for easy access
- **Responsive collapse** on mobile devices
- **Profile dropdown** with theme toggle

### Filtering System
- **Real-time filters** applied to API results
- **Location input** with coordinate support
- **Cuisine selection** from available options
- **Rating sliders** for minimum requirements
- **Price range** selection

## 🔐 Security Features

### Authentication
- **Secure password hashing** with Werkzeug
- **Session management** with Flask-Login
- **CSRF protection** with Flask-WTF
- **Input validation** on all forms

### API Security
- **Environment variables** for sensitive keys
- **Rate limiting** considerations
- **Input sanitization** for all user data
- **Secure headers** implementation

## 🚀 Performance Optimizations

### Frontend
- **Lazy loading** for images
- **CSS animations** with hardware acceleration
- **Minimal JavaScript** for core functionality
- **Responsive images** with appropriate sizing

### Backend
- **Efficient API calls** with caching considerations
- **Database optimization** for user queries
- **Minimal data storage** approach
- **Fast response times** with streamlined routes

## 🧪 Testing

### Manual Testing Checklist
- [ ] User registration and login
- [ ] Location detection and manual input
- [ ] Restaurant filtering and search
- [ ] Group creation and management
- [ ] Like/dislike functionality
- [ ] Theme switching
- [ ] Responsive design on all devices
- [ ] API error handling

### Browser Compatibility
- ✅ Chrome 90+
- ✅ Safari 14+
- ✅ Firefox 88+
- ✅ Edge 90+

## 🔮 Future Enhancements

### Planned Features
- **Real-time notifications** with WebSockets
- **Advanced matching algorithms** with ML
- **Social media integration** for sharing
- **Mobile app** using existing API structure
- **Restaurant reservations** integration
- **Review system** with user ratings

### Technical Improvements
- **Caching layer** for API responses
- **Background jobs** for data processing
- **Advanced analytics** for user behavior
- **Performance monitoring** with metrics
- **Automated testing** suite

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Style
- **PEP 8** compliance for Python
- **ESLint** configuration for JavaScript
- **Consistent naming** conventions
- **Comprehensive comments** and docstrings

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Apple Design System** - Inspiration for UI/UX
- **Google Places API** - Restaurant data provider
- **Flask Community** - Framework and extensions
- **Bootstrap Team** - Responsive design foundation

---

<div align="center">
  <p>Built with ❤️ and lots of ☕</p>
  <p>© 2024 SyncAndDine. Designed for food lovers, by food lovers.</p>
</div>