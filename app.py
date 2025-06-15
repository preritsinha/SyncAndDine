from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from syncanddine import create_app, db
from syncanddine.models.user import User, Group
from syncanddine.models.restaurant import Restaurant
import uuid

app = create_app()

# Login and registration routes for old templates
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Try to find user by username or email
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email) # type: ignore
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Add compatibility routes for old URLs
@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    return redirect(url_for('social.create_group'))

@app.route('/groups')
def groups():
    return redirect(url_for('social.my_groups'))

@app.route('/add_friend', methods=['GET', 'POST'])
def add_friend():
    return redirect(url_for('social.search_connections'))

@app.route('/connection')
def connection():
    return redirect(url_for('social.connections'))

@app.route('/messages/<int:friend_id>', methods=['GET', 'POST'])
@login_required
def messages(friend_id):
    return redirect(url_for('social.messages', friend_id=friend_id))

@app.route('/edit_group/<int:group_id>')
def edit_group(group_id):
    return redirect(url_for('social.group_detail', group_id=group_id))

@app.route('/join_group/<share_code>')
def join_group(share_code):
    return redirect(url_for('social.join_group', share_code=share_code))

@app.route('/restaurants')
def restaurants():
    # Check if there are query parameters
    if request.args:
        # Forward all query parameters to the blueprint route
        return redirect(url_for('restaurants.list_restaurants', **request.args))
    return redirect(url_for('restaurants.list_restaurants'))

@app.route('/like_restaurant/<int:restaurant_id>', methods=['POST'])
@login_required
def like_restaurant(restaurant_id):
    group_id = request.args.get('group_id', 0, type=int)
    return redirect(url_for('restaurants.like_restaurant', restaurant_id=restaurant_id, group_id=group_id))

@app.route('/dislike_restaurant/<int:restaurant_id>', methods=['POST'])
@login_required
def dislike_restaurant(restaurant_id):
    group_id = request.args.get('group_id', 0, type=int)
    return redirect(url_for('restaurants.dislike_restaurant', restaurant_id=restaurant_id, group_id=group_id))

@app.route('/restaurant/<int:restaurant_id>')
@login_required
def restaurant_detail(restaurant_id):
    return redirect(url_for('restaurants.restaurant_detail', restaurant_id=restaurant_id))

@app.route('/swipe')
@login_required
def swipe():
    # Forward all query parameters to the blueprint route
    return redirect(url_for('restaurants.swipe_restaurants', **request.args))

@app.route('/matches/<int:group_id>')
@login_required
def matches(group_id):
    return redirect(url_for('restaurants.group_matches', group_id=group_id))

if __name__ == '__main__':
    app.run()
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return redirect(url_for('main.index'))