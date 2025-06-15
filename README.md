# SyncAndDine 🍽️

<div align="center">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLAlchemy"/>
  <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap"/>
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render"/>
</div>

## 📱 Live Demo

Experience SyncAndDine in action! Visit [syncanddine.com](https://syncanddine.com) to try it out.

## 🌟 Overview

SyncAndDine is a full-stack web application that revolutionizes how friends decide where to eat. No more endless debates about restaurant choices! With SyncAndDine, users can:

- Connect with friends and create dining groups
- Browse and filter restaurants based on preferences
- Swipe right (like) or left (dislike) on restaurant options
- Discover perfect matches based on everyone's preferences

The application features a warm, food-themed UI with responsive design that works seamlessly across all devices.

## ✨ Key Features

- **User Authentication System** - Secure registration and login with password hashing
- **Social Connections** - Add friends and create dining groups
- **Restaurant Discovery** - Browse with advanced filtering (location, cuisine, price, rating)
- **Tinder-style Swiping** - Intuitive like/dislike interface for restaurants
- **Match Algorithm** - Smart matching based on group preferences
- **Responsive Design** - Optimized experience on desktop, tablet, and mobile
- **Dark/Light Mode** - Toggle between color schemes for comfortable viewing
- **RESTful API** - Complete API for potential mobile app integration

## 🛠️ Technologies Used

### Backend
- **Flask** - Python web framework for rapid development
- **SQLAlchemy** - ORM for database interactions
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and validation
- **Flask-JWT-Extended** - JWT authentication for API
- **Gunicorn** - WSGI HTTP Server for deployment

### Frontend
- **HTML5/CSS3** - Structure and styling
- **Bootstrap 5** - Responsive design framework
- **JavaScript** - Dynamic client-side functionality
- **Font Awesome** - Icon library

### Database
- **SQLite** - Development database
- **PostgreSQL** - Production database (on Render)

### DevOps
- **Git** - Version control
- **Render** - Cloud deployment platform

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd SyncAndDine
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file with:
   ```
   SECRET_KEY=your_secret_key_here
   DATABASE_URI=sqlite:///syncanddine.db
   JWT_SECRET_KEY=your_jwt_secret_key_here
   ```

5. **Run database migrations:**
   ```bash
   python migration_fix_schema.py
   python migration_add_admin.py
   python migration_add_messages.py
   ```

6. **Import sample restaurant data:**
   ```bash
   python import_restaurants.py
   ```

7. **Run the application:**
   ```bash
   python run.py
   ```

8. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## 📂 Project Structure

```
SyncAndDine/
├── syncanddine/                # Main application package
│   ├── __init__.py             # Application factory
│   ├── models/                 # Database models
│   ├── auth/                   # Authentication routes and forms
│   ├── main/                   # Main routes
│   ├── restaurants/            # Restaurant-related features
│   ├── social/                 # Social features (friends, groups)
│   ├── api/                    # API endpoints
│   ├── static/                 # Static files (CSS, JS, images)
│   └── templates/              # HTML templates
├── app.py                      # Legacy routes for compatibility
├── run.py                      # Application entry point
├── import_restaurants.py       # Script to import restaurant data
├── seed_data.py                # Script to seed test data
├── migration_*.py              # Database migration scripts
├── requirements.txt            # Dependencies
├── Procfile                    # Deployment configuration
└── .env                        # Environment variables
```

## 🔄 API Endpoints

The application provides a RESTful API for integration with mobile apps:

- **Authentication**:
  - `POST /api/login`: User login
  - `POST /api/register`: User registration

- **Restaurants**:
  - `GET /api/restaurants`: List restaurants with filters
  - `GET /api/restaurants/<id>`: Get restaurant details
  - `POST /api/restaurants/<id>/like`: Like a restaurant
  - `POST /api/restaurants/<id>/dislike`: Dislike a restaurant

- **Groups**:
  - `GET /api/groups`: List user's groups
  - `POST /api/groups`: Create a new group
  - `GET /api/groups/<id>`: Get group details
  - `POST /api/groups/join/<share_code>`: Join a group

- **Matches**:
  - `GET /api/groups/<id>/matches`: Get restaurant matches for a group

## 🧠 Learning Outcomes & Challenges

During the development of SyncAndDine, I:

- Implemented a complex database schema with relationships between users, groups, and restaurants
- Created an intuitive UI/UX with responsive design principles
- Built a secure authentication system with password hashing and JWT
- Developed a RESTful API with proper error handling and validation
- Optimized database queries for performance
- Deployed a full-stack application to a cloud platform

Key challenges included:
- Designing an algorithm to find restaurant matches based on group preferences
- Implementing real-time updates for group activities
- Creating a responsive design that works well on all device sizes
- Optimizing database queries for larger datasets

## 📈 Future Enhancements

- Real-time notifications using WebSockets
- Integration with Google Maps API for location-based recommendations
- Mobile app using the existing API
- Machine learning for personalized restaurant recommendations
- Social media authentication (OAuth)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<div align="center">
  <p>Designed and developed with ❤️ by <a href="https://github.com/preritsinha">Prerit Sinha</a></p>
  <p>Connect with me on <a href="https://linkedin.com/in/preritsinha">LinkedIn</a></p>
</div>
