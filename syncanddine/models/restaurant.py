from datetime import datetime
from syncanddine import db

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    rating = db.Column(db.Float, default=0.0)
    cuisine_type = db.Column(db.String(50))
    price_range = db.Column(db.String(20))
    is_vegetarian = db.Column(db.Boolean, default=False)
    distance = db.Column(db.Float)  # Distance in km
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    likes = db.relationship('RestaurantLike', backref='restaurant', lazy=True)
    
    def __repr__(self):
        return f'<Restaurant {self.name}>'

class RestaurantLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)
    liked = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'restaurant_id', 'group_id', name='unique_user_restaurant_group'),
    )
    
    def __repr__(self):
        return f'<RestaurantLike user_id={self.user_id} restaurant_id={self.restaurant_id} liked={self.liked}>'