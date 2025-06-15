from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from syncanddine import db
from syncanddine.models.user import User
from syncanddine.auth.forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from flask_jwt_extended import create_access_token

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Try to find user by email or username
        user = User.query.filter((User.email == form.email.data) | 
                                (User.username == form.email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Please check username/email and password.', 'danger')
    
    return render_template('auth/login.html', title='Login', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # Here you would send an email with reset instructions
        # For now, we'll just flash a message
        flash('Password reset instructions have been sent to your email.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', title='Forgot Password', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Here you would validate the token and get the user
    # For now, we'll just show the form
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Update the user's password
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)

# API routes for authentication
@auth.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing username/email or password'}), 400
    
    # Try to find user by email or username
    user = User.query.filter((User.email == data.get('email')) | 
                           (User.username == data.get('email'))).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({'message': 'Invalid username/email or password'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token, 'user_id': user.id, 'username': user.username}), 200

@auth.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'message': 'Email already registered'}), 400
    
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'message': 'Username already taken'}), 400
    
    user = User(username=data.get('username'), email=data.get('email'))
    user.set_password(data.get('password'))
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    return jsonify({'message': 'User registered successfully', 'access_token': access_token}), 201