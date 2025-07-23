import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///syncanddine.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt_dev_key')
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    jwt.init_app(app)
    
    # Register blueprints
    from syncanddine.auth.routes import auth
    from syncanddine.main.routes import main
    from syncanddine.restaurants.routes import restaurants
    from syncanddine.social.routes import social
    from syncanddine.api.routes import api
    from syncanddine.api.location_routes import location_api
    from syncanddine.api.notification_routes import notification_api
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(restaurants)
    app.register_blueprint(social)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(location_api)
    app.register_blueprint(notification_api)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app