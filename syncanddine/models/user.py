from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from syncanddine import db, login_manager

# Association table for user friendships
friendships = db.Table('friendships',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Association table for group memberships
group_members = db.Table('group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('is_admin', db.Boolean, default=False)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    friends = db.relationship(
        'User', 
        secondary=friendships,
        primaryjoin=(friendships.c.user_id == id),
        secondaryjoin=(friendships.c.friend_id == id),
        backref=db.backref('friend_of', lazy='dynamic'),
        lazy='dynamic'
    )
    
    owned_groups = db.relationship('Group', backref='owner', lazy=True)
    restaurant_likes = db.relationship('RestaurantLike', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_friend(self, user):
        if not self.is_friend(user):
            self.friends.append(user)
            user.friends.append(self)
            return True
        return False
    
    def remove_friend(self, user):
        if self.is_friend(user):
            self.friends.remove(user)
            user.friends.remove(self)
            return True
        return False
    
    def is_friend(self, user):
        return self.friends.filter(friendships.c.friend_id == user.id).count() > 0
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    share_code = db.Column(db.String(20), unique=True)
    
    # Relationships
    members = db.relationship('User', secondary=group_members, lazy='dynamic',
                             backref=db.backref('groups', lazy='dynamic'))
    
    def is_admin(self, user):
        """Check if a user is an admin of this group"""
        # Owner is always an admin
        if user.id == self.owner_id:
            return True
            
        # Check if user is marked as admin in the group_members table
        member = db.session.query(group_members).filter_by(
            user_id=user.id, 
            group_id=self.id,
            is_admin=True
        ).first()
        
        return member is not None
    
    def __repr__(self):
        return f'<Group {self.name}>'