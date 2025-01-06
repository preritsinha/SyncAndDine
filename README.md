
# SyncAndDine

SyncAndDine is a fun and interactive app for friends and couples to discover the perfect restaurant together. Inspired by the swiping feature from dating apps, SyncAndDine allows users to swipe through restaurant options, like or dislike them, and find their ideal dining experience based on mutual preferences.

## Features

- **Tinder-Style Swiping**: Swipe right (like) or left (dislike) on restaurant options.
- **Personalized Recommendations**: The app suggests restaurants based on both users' swipes and preferences.
- **User Profiles**: Each user can save their preferences and see their swiped history.
- **Real-Time Sync**: Both users' choices are taken into account to generate the best dining options.
- **Flask Backend**: The backend is built with Flask to handle restaurant swipes and recommendations.
- **Python Logic**: Uses machine learning for generating recommendations based on user preferences and restaurant features.

## Tech Stack

- **Frontend**: iOS (Swift)
- **Backend**: Flask (Python)
- **Database**: In-memory data storage for demonstration (can be extended to use a database like SQLite, PostgreSQL, etc.)
- **Recommendation Engine**: Based on cosine similarity of user preferences and restaurant features.
- **Hosting**: Local (can be deployed using services like Heroku or AWS for production).

## Setup

To run this project locally, follow these steps: (FOR NOW LOCAL SUPPORT HAS ONLY BEEN TESTED, WILL BE ADDING UI AND FE LATER)

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

### 4. Frontend Setup

You can set up the iOS frontend with Swift by integrating with the API endpoints provided in `api.py`. For the frontend, use a `POST` request to the `/swipe` endpoint and a `GET` request to the `/recommend` endpoint.

### 5. Access the Application

- Open `http://127.0.0.1:5000/recommend` in a browser or Postman to see restaurant recommendations.
- Use `curl` or Postman to send a `POST` request to `/swipe` to test the swiping functionality.

## API Endpoints

### `POST /swipe`

- **Request Body**:
    ```json
    {
        "user": "User1",
        "restaurant_name": "restaurant1",
        "action": "r"
    }
    ```

- **Response**:
    ```json
    {
        "status": "success",
        "result": "User1 swiped right on restaurant1"
    }
    ```

### `GET /recommend`

- **Response**:
    ```json
    {
        "recommendations": [
            {
                "name": "restaurant1",
                "similarity_score": 0.95
            },
            {
                "name": "restaurant3",
                "similarity_score": 0.89
            },
            {
                "name": "restaurant2",
                "similarity_score": 0.85
            }
        ]
    }
    ```

### Created with love ❤️
