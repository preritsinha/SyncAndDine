from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from syncanddine.models.message import Message
from datetime import datetime, timedelta

notification_api = Blueprint('notification_api', __name__)

@notification_api.route('/api/notifications')
@login_required
def get_notifications():
    # Get latest 50 unread messages as notifications
    notifications = Message.query.filter_by(
        recipient_id=current_user.id,
        is_read=False
    ).order_by(Message.timestamp.desc()).limit(50).all()
    
    # Clean up old notifications (keep only latest 50 per user)
    old_notifications = Message.query.filter_by(
        recipient_id=current_user.id
    ).order_by(Message.timestamp.desc()).offset(50).all()
    
    for old_notif in old_notifications:
        db.session.delete(old_notif)
    
    if old_notifications:
        db.session.commit()
    
    notification_data = []
    for notification in notifications:
        notification_data.append({
            'id': notification.id,
            'sender_name': notification.sender.username,
            'content': notification.content,
            'time_ago': get_time_ago(notification.timestamp)
        })
    
    return jsonify({'notifications': notification_data})

@notification_api.route('/api/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    Message.query.filter_by(
        recipient_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    
    from syncanddine import db
    db.session.commit()
    
    return jsonify({'status': 'success'})

def get_time_ago(timestamp):
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600}h ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60}m ago"
    else:
        return "Just now"