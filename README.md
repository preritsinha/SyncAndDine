
# SyncAndDine

**Dataset:** https://www.kaggle.com/code/bablukd/zomato-bangalore-restaurant-rating-prediction/input#

**Link:** https://preritsinha.pythonanywhere.com

SyncAndDine is a fun and interactive app for friends and couples to discover the perfect restaurant together. Inspired by the swiping feature from dating apps, SyncAndDine allows users to swipe through restaurant options, like or dislike them, and find their ideal dining experience based on mutual preferences.

## Features

- **Tinder-Style Swiping**: Swipe right (like) or left (dislike) on restaurant options.
- **Personalized Recommendations**: The app suggests restaurants based on both users' swipes and preferences.
- **User Profiles**: Each user can save their preferences and see their swiped history.
- **Real-Time Sync**: Both users' choices are taken into account to generate the best dining options.
- **Flask Backend**: The backend is built with Flask to handle restaurant swipes and recommendations.

## Tech Stack

- **Frontend**: HTML/CSS
- **Backend**: Flask (Python)
- **Database**: In-memory data storage for demonstration (can be extended to use a database like SQLite, PostgreSQL, etc.)
- **Hosting**: Done on pythonanywhere.com. Can also be deployed locally.

## Setup

To run this project locally, follow these steps: 

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/SyncAndDine.git
cd SyncAndDine
```

### 2. Install Dependencies

Install the required Python libraries for the backend.

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should include:
```
Flask
scikit-learn
```

### 3. Run the Flask Backend

Start the Flask development server.

```bash
python api.py
```

This will run the backend on `http://127.0.0.1:5000/`.

### 4. Access the Application

- Open `http://127.0.0.1:5000` in a browser or Postman to see the login page.

## DISCLAIMER
<b>Website navigation is not fully tested so you might encounter "Internal Server Error" more frequently than desired. <br> Thanks for your patience.</b>

### Created with love ❤️
