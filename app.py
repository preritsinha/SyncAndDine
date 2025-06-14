from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import PickleType
from flask_bcrypt import Bcrypt
import pandas as pd
import os
from datetime import datetime, timezone
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///syncanddine.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # JWT configuration

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

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
    filter_preferences = db.Column(MutableDict.as_mutable(PickleType), default={})
    admin_groups = db.relationship('ConnectionGroup', backref='admin', lazy=True)
    friends = db.relationship('User',
                              secondary=friendship,
                              primaryjoin=id == friendship.c.user_id,
                              secondaryjoin=id == friendship.c.friend_id,
                              backref=db.backref('friend_of', lazy='dynamic'),
                              lazy='dynamic')
    def __repr__(self):
        return f'<User {self.username}>'

class ConnectionGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_members = db.relationship('GroupMember', backref='group', lazy=True)
    def __repr__(self):
        return f'<ConnectionGroup {self.name}>'

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('connection_group.id'), nullable=False)
    join_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    def __repr__(self):
        return f'<GroupMember {self.user.username}>'

csv_path = os.path.join(os.path.dirname(__file__), 'restaurants.csv')
restaurant_data = pd.read_csv(csv_path)
restaurant_data.fillna("", inplace=True)

def clean_rate(value):
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, str):
        value = value.strip()
        if '/' in value:
            return float(value.split('/')[0])
        elif value in ['NEW', '-']:
            return ""
    return ""

restaurant_data['rate'] = restaurant_data['rate'].apply(clean_rate)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({'msg': 'Invalid username or password'}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/connection', methods=['GET', 'POST'])
@jwt_required()
def connection():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    invite_link = f"{request.url_root}add_friend?username={user.username}"
    if request.method == 'POST':
        if 'create_group' in request.form:
            group_name = request.form['group_name']
            members = request.form.getlist('members')  # List of friends to add to the group
            
            group = ConnectionGroup(name=group_name, admin=user)
            db.session.add(group)
            
            for member_username in members:
                member = User.query.filter_by(username=member_username).first()
                if member:
                    group.members.append(member)
            
            db.session.commit()
        
        elif 'remove_from_group' in request.form:
            group_id = request.form['group_id']
            friend_username = request.form['friend_username']
            group = ConnectionGroup.query.get(group_id)
            if group:
                friend = User.query.filter_by(username=friend_username).first()
                if friend in group.members:
                    group.members.remove(friend)
                    db.session.commit()
    user_friends = user.friends.all()
    user_groups = user.admin_groups
    return render_template('connection.html', user=user, friends=user_friends, invite_link=invite_link, groups=user_groups)

@app.route('/get_filters', methods=['GET'])
def get_filters():
    df = restaurant_data
    areas = df['location'].dropna().unique().tolist()
    cuisines = pd.Series(df['cuisines'].str.split(',').explode().str.strip().unique()).tolist()
    rest_types = pd.Series(df['rest_type'].str.split(',').explode().str.strip().unique()).tolist()
    return jsonify({'areas': areas, 'cuisines': cuisines, 'rest_types': rest_types})
@app.route('/add_friend', methods=['POST', 'GET'])
def add_friend():
    if 'username' not in session:
        return redirect(url_for('home'))
    user = User.query.filter_by(username=session['username']).first()  # Get current user
    # Handle GET request for invite links
    if request.method == 'GET':
        friend_username = request.args.get('username')  # Extract username from query params
        friend = User.query.filter_by(username=friend_username).first()  # Get friend by username
        if friend and friend != user:  # Ensure the user isn't adding themselves as a friend
            if friend in user.friends:
                flash('Friend is already in your friend list!', 'info')
            else:
                user.friends.append(friend)
                db.session.commit()
                flash('Friend added successfully via invite link!', 'success')
        else:
            flash('Invalid invite link or user not found!', 'danger')
        return redirect(url_for('connection'))
    # Handle POST request for manual friend addition
    if request.method == 'POST':
        friend_username = request.form.get('username')
        friend = User.query.filter_by(username=friend_username).first()  # Get friend by username
        if friend and friend != user:  # Ensure the user isn't adding themselves as a friend
            if friend in user.friends:
                flash('Friend is already in your friend list!', 'info')
            else:
                user.friends.append(friend)
                db.session.commit()
                flash('Friend added successfully!', 'success')
        else:
            flash('Friend not found or you cannot add yourself!', 'danger')
        return redirect(url_for('connection'))

@app.route('/remove_friend', methods=['POST'])
def remove_friend():
    if 'username' not in session:
        return redirect(url_for('home'))

    user = User.query.filter_by(username=session['username']).first()  # Get current user
    friend_username = request.form.get('friend_username')
    friend = User.query.filter_by(username=friend_username).first()  # Get friend by username

    if friend and friend in user.friends:  # Ensure the friend exists and is in the user's friend list
        user.friends.remove(friend)  # Remove friend from the list
        db.session.commit()  # Commit changes to the database
        flash(f'Removed {friend.username} from your friend list.', 'success')
    else:
        flash('Friend not found in your list.', 'danger')

    return redirect(url_for('connection'))

@app.route('/set_filters', methods=['POST'])
def set_filters():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    user = User.query.filter_by(username=session['username']).first()

    # Check if the user is an admin for any of their friends
    admin_friendship = db.session.query(friendship).filter_by(user_id=user.id).first()
    if admin_friendship and admin_friendship.is_admin:
        # Get the filter values from the form
        cuisine = request.form.get('cuisine')
        area = request.form.get('area')
        # Save the filters in the user's connection
        user.filter_preferences = {
            'cuisine': cuisine,
            'area': area
        }
        db.session.commit()

        # Sync filters to all friends
        for friend in user.friends:
            friend.filter_preferences = user.filter_preferences
        db.session.commit()

        flash('Filters set and synced with your friends!', 'success')
    else:
        flash('You must be an admin to set filters.', 'danger')

    return redirect(url_for('connection'))

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
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)), debug=True)