from datetime import datetime, timedelta
from syncanddine import db

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    @staticmethod
    def create_unique_notification(sender_id, recipient_id, content):
        """Create notification only if it doesn't exist in last 24 hours"""
        from datetime import timedelta
        recent_time = datetime.utcnow() - timedelta(hours=24)
        
        existing = Message.query.filter_by(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content
        ).filter(Message.timestamp > recent_time).first()
        
        if not existing:
            notification = Message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                content=content
            )
            db.session.add(notification)
            return notification
        return None

    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='messages_sent')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='messages_received')
    
    def __repr__(self):
        return f'<Message {self.id}: {self.sender_id} to {self.recipient_id}>'