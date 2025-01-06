from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import PickleType
from flask_bcrypt import Bcrypt
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///syncanddine.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

if not os.path.exists('instance/syncanddine.db'):
    with app.app_context():
        db.drop_all()  # Drops all tables (only use this if you're sure)
        db.create_all()  # Creates all tables including the new friendship table

friendship = db.Table('friendship',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    swipes = db.Column(MutableDict.as_mutable(PickleType), default={})
    finished = db.Column(db.Boolean, default=False)
    friends = db.relationship('User',
                              secondary=friendship,
                              primaryjoin=id == friendship.c.user_id,
                              secondaryjoin=id == friendship.c.friend_id,
                              backref=db.backref('friend_of', lazy='dynamic'),
                              lazy='dynamic')

restaurant_data = pd.read_csv('restaurants.csv')
restaurant_data.fillna("",inplace=True)
def clean_rate(value):
    if value is None or pd.isna(value):  # Check for None or NaN
        return ""
    if isinstance(value, str):
        value = value.strip()  # Remove extra spaces
        if '/' in value:  # Check if it has the '/5' format
            return float(value.split('/')[0])
        elif value in ['NEW', '-']:  # Handle special cases
            return ""
    return ""
restaurant_data['rate'] = restaurant_data['rate'].apply(clean_rate)

@app.route('/')
def home():
    # if 'username' in session:
        # return redirect(url_for('profile'))
    return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Received username: {username}, password: {password}")
        user = User.query.filter_by(username=username).first()
        print(f"Found user: {user}")  # Check if user is None or the actual user object
        if user:
            print(f"Stored password: {user.password}")
            # if bcrypt.check_password_hash(user.password, password):
            if user.password==password:
                print(f"Login successful for user: {user}")
                session['username'] = username
                user = User.query.filter_by(username=session['username']).first()
                if user:
                    user.finished = False  # Reset the finished status to False
                    user.swipes = {}
                    db.session.commit()  # Commit the change to the database
                return redirect(url_for('profile'))
            else:
                print("Password mismatch.")
                flash("Invalid username or password", "danger")
        else:
            print("User not found.")
            flash("Invalid username or password", "danger")
    return render_template('login.html')

@app.route('/logout', methods=['GET','POST'])
def logout():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    session.pop('username', None)  # Remove the username from the session
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
        # Check if email already exists
        elif User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
        else:
            # hashed_password = generate_password_hash(password, method='sha256')
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/profile')
def profile():
    user = User.query.filter_by(username=session['username']).first()
    invite_link = f"http://localhost:5000/register/{user.username}"  # Example of invite link
    return render_template('profile.html', user=user, invite_link=invite_link)

@app.route('/get_filters', methods=['GET'])
def get_filters():
    df = restaurant_data
    areas = df['location'].dropna().unique().tolist()
    cuisines = pd.Series(df['cuisines'].str.split(',').explode().str.strip().unique()).tolist()
    rest_types = pd.Series(df['rest_type'].str.split(',').explode().str.strip().unique()).tolist()
    
    # Return a merged response
    return jsonify({
        'areas': areas,
        'cuisines': cuisines,
        'rest_types': rest_types
    })

@app.route('/add_friend', methods=['POST'])
def add_friend():
    if 'username' not in session:
        return redirect(url_for('home'))
    friend_username = request.form.get('username')
    user = User.query.filter_by(username=session['username']).first()  # Get current user
    friend = User.query.filter_by(username=friend_username).first()  # Get friend by username
    if friend and friend != user:  # Ensure the user isn't adding themselves as a friend
        # Add friend to user's friend list (many-to-many relationship)
        user.friends.append(friend)
        db.session.commit()
        flash('Friend added successfully!', 'success')
    else:
        flash('Friend not found or you cannot add yourself!', 'danger')
    return redirect(url_for('profile'))


@app.route('/restaurants', methods=['GET', 'POST'])
def restaurants():
    if 'username' not in session:
        return redirect(url_for('home'))
    filtered_restaurants = restaurant_data.copy()
    filtered_restaurants['rate'] = pd.to_numeric(filtered_restaurants['rate'], errors='coerce').fillna(0)
    filtered_restaurants['approx_cost(for two people)'] = (
        filtered_restaurants['approx_cost(for two people)']
        .replace(',', '', regex=True)  # Remove commas
        .replace(r'[^\d.]', '', regex=True)  # Remove non-numeric characters
        .replace('', '0', regex=False)  # Replace empty strings with '0'
        .astype(float)  # Convert to float
    )
    if request.method == 'POST':
        filters = {
            'area': request.form.get('area'),
            'rating': request.form.get('rating'),
            'cuisines': request.form.getlist('cuisines'),
            'veg_nonveg': request.form.get('veg_nonveg'),
            'open_now': request.form.get('open_now'),
            'rest_type': request.form.getlist('rest_type'),
            'cost': request.form.get('cost')
        }
        # Apply filters directly from CSV data
        if filters['area']:
            filtered_restaurants = filtered_restaurants[filtered_restaurants['location'] == filters['area']]
        if filters['rating']:
            filtered_restaurants = filtered_restaurants[filtered_restaurants['rate'] >= float(filters['rating'])]
        if filters['cuisines']:
            filtered_restaurants = filtered_restaurants[filtered_restaurants['cuisines'].apply(lambda x: any(cuisine in x.split(', ') for cuisine in filters['cuisines']))]
        if filters['veg_nonveg']:
            filtered_restaurants = filtered_restaurants[filtered_restaurants['veg_nonveg'] == filters['veg_nonveg']]
        if filters['rest_type']:
            filtered_restaurants = filtered_restaurants[filtered_restaurants['rest_type'].apply(lambda x: any(rest_type in x.split(', ') for rest_type in filters['rest_type']))]
        if filters['cost']:
            filtered_restaurants = filtered_restaurants[filtered_restaurants['approx_cost(for two people)'] <= float(filters['cost'])]
    restaurants = filtered_restaurants[['url', 'name', 'location', 'rate', 'cuisines', 'approx_cost(for two people)']].to_dict(orient='records')
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/swipe_next', methods=['GET'])
def swipe_next():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    index = int(request.args.get('index', 0))
    filtered_restaurants = restaurant_data[['url', 'name', 'location', 'rate', 'cuisines', 'approx_cost(for two people)']].to_dict(orient='records')
    if index < len(filtered_restaurants):
        return jsonify({'status': 'success', 'restaurant': filtered_restaurants[index]})
    return jsonify({'status': 'end'})
@app.route('/swipe', methods=['POST'])
def swipe():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    restaurant_id = request.json['restaurant_id']
    swipe_type = request.json['swipe_type']
    print("Restaurant ID: {} Swipe Type: {}".format(restaurant_id,swipe_type))
    # Get the current user
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    print("Current user:", user)
    print("Current swipes:", user.swipes)

    # If the swipe_type is valid, update the user's swipes
    if swipe_type in ['like', 'dislike']:
        user.swipes[str(restaurant_id)] = swipe_type  # Store the swipe in the user's swipes dictionary
        print("Updated swipes (before commit):", user.swipes)
        db.session.add(user)
        db.session.commit()  # Commit the change to the database
        print("Updated swipes (after commit):", user.swipes)
        return jsonify({'status': 'success', 'message': f"Swipe {swipe_type} saved!"})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid swipe type'}), 400


@app.route('/finish', methods=['POST'])
def finish():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    user = User.query.filter_by(username=session['username']).first()
    user.finished = True

    user_swipes = request.json.get('swipes', {})
    print(f"User swipes: {user_swipes}")

    db.session.commit()

    # Fetch friends
    friend_ids = db.session.query(friendship.c.friend_id).filter(friendship.c.user_id == user.id).all()
    friend_ids = [friend_id[0] for friend_id in friend_ids]
    friends = User.query.filter(User.id.in_(friend_ids)).all()

    # Check if all friends have finished swiping
    if all(friend.finished for friend in friends):
        all_swipes = [friend.swipes for friend in friends] + [user.swipes]  # Use user's actual swipes
        common_swipes = set.intersection(*[set(s.keys()) for s in all_swipes])

        # Ensure all swipes are 'like' for common restaurants
        matches = [s for s in common_swipes if all(sws.get(s) == 'like' for sws in all_swipes)]

        # Convert matches to integers if needed
        matches = list(map(int, matches))  # Ensure indices match DataFrame format

        if matches:
            matched_restaurants = restaurant_data.loc[matches].to_dict(orient='records')
            return jsonify({'status': 'success', 'matches': matched_restaurants})
        else:
            return jsonify({'status': 'success', 'matches': []})

    return jsonify({'status': 'waiting'})



if __name__ == '__main__':
    if not os.path.exists('/instance/syncanddine.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
