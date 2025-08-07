from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from syncanddine import db
from syncanddine.models.user import User
from syncanddine.auth.forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from flask_jwt_extended import create_access_token
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

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
        if user:
            token = user.get_reset_token()
            send_reset_email(user, token)
        # Always show success message for security
        flash('If an account with that email exists, password reset instructions have been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', title='Forgot Password', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired reset token.', 'warning')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
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

def send_reset_email(user, token):
    """Send password reset email"""
    try:
        # Email configuration from environment variables
        SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
        EMAIL_USER = os.getenv('EMAIL_USER')
        EMAIL_PASS = os.getenv('EMAIL_PASS')
        
        if not EMAIL_USER or not EMAIL_PASS:
            print("Email credentials not configured")
            return False
        
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        # Create HTML email
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #FF6B35; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">🍽️ SyncAndDine</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2 style="color: #333;">Password Reset Request</h2>
                <p>Hello {user.username},</p>
                <p>You requested a password reset for your SyncAndDine account.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background: #FF6B35; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Password</a>
                </div>
                
                <p style="color: #666; font-size: 14px;">This link will expire in 30 minutes.</p>
                <p style="color: #666; font-size: 14px;">If you didn't request this, please ignore this email.</p>
            </div>
            
            <div style="background: #333; color: white; padding: 15px; text-align: center; font-size: 12px;">
                <p>© 2024 SyncAndDine. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'SyncAndDine - Password Reset Request'
        msg['From'] = EMAIL_USER
        msg['To'] = user.email
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Failed to send reset email: {str(e)}")
        return False