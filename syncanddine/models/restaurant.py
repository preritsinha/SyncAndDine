from datetime import datetime
from syncanddine import db

class RestaurantLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_google_id = db.Column(db.String(100), nullable=False)  # Google Place ID
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)
    liked = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'restaurant_google_id', 'group_id', name='unique_user_restaurant_group'),
    )
    
    def __repr__(self):
        return f'<RestaurantLike user_id={self.user_id} restaurant_id={self.restaurant_google_id} liked={self.liked}>'