# SyncAndDine

SyncAndDine is a restaurant matching application that allows users to connect with friends, create groups, browse restaurants, and find matches based on mutual likes.

## Features

- User registration and authentication
- Friend connections
- Group creation and management
- Restaurant browsing with filters
- Restaurant swiping (like/dislike)
- Match finding based on mutual likes

## Tech Stack

- **Backend**: Flask with SQLAlchemy
- **Frontend**: HTML/CSS with minimal JavaScript
- **Database**: SQLite
- **Authentication**: Session-based + JWT

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd SyncAndDine-test
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (or update the .env file):
   ```
   SECRET_KEY=your_secret_key_here
   FLASK_APP=app.py
   FLASK_ENV=development
   DATABASE_URI=sqlite:///syncanddine.db
   JWT_SECRET_KEY=your_jwt_secret_key_here
   ```

5. Run the application:
   ```
   flask run
   ```

## Project Structure

```
SyncAndDine-test/
├── syncanddine/
│   ├── __init__.py         # Application factory
│   ├── models/             # Database models
│   ├── auth/               # Authentication routes and forms
│   ├── main/               # Main routes
│   ├── restaurants/        # Restaurant-related routes
│   ├── social/             # Social features (friends, groups)
│   ├── api/                # API endpoints
│   ├── static/             # Static files (CSS, JS, images)
│   └── templates/          # HTML templates
├── app.py                  # Application entry point
├── requirements.txt        # Dependencies
└── .env                    # Environment variables
```

## API Endpoints

The application provides a RESTful API for integration with mobile apps or other services:

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

## License

This project is licensed under the MIT License - see the LICENSE file for details.
## Database Migration

Before running the application, you need to run the migration script to add the admin functionality:

```
python migration_add_admin.py
```

This will add the necessary column to the database to support admin features.
## Fix Database Schema

Before running the application, you need to run the migration script to fix the database schema:

```
python migration_fix_schema.py
```

This will add missing columns to the database tables and fix any schema issues.