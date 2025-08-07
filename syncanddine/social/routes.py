from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from syncanddine import db
from syncanddine.models.user import User, Group, group_members
from datetime import datetime, timedelta
import uuid
import json

social = Blueprint('social', __name__)

@social.route('/connections')
@login_required
def connections():
    friends = current_user.friends.all()
    # Get owned groups for sidebar
    owned_groups = current_user.owned_groups
    member_groups = current_user.groups.all()
    
    return render_template('social/connections.html', 
                          title='My Connections',
                          friends=friends,
                          owned_groups=owned_groups,
                          member_groups=member_groups)

@social.route('/connections/search', methods=['GET', 'POST'])
@login_required
def search_connections():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        
        if not username:
            flash('Please enter a username to search.', 'warning')
            return render_template('social/search.html', title='Find Friends')
        
        if len(username) < 2:
            flash('Search term must be at least 2 characters.', 'warning')
            return render_template('social/search.html', title='Find Friends')
        
        # Limit search results
        users = User.query.filter(
            User.username.ilike(f'%{username}%')
        ).filter(
            User.id != current_user.id
        ).limit(20).all()
        return render_template('social/search_results.html',
                              title='Search Results',
                              users=users,
                              search_term=username)
    
    return render_template('social/search.html', title='Find Friends')

@social.route('/connections/add/<int:user_id>', methods=['POST'])
@login_required
def add_connection(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        if user == current_user:
            flash('You cannot add yourself as a friend.', 'warning')
        elif current_user.is_friend(user):
            flash(f'You are already friends with {user.username}.', 'info')
        else:
            current_user.add_friend(user)
            
            # Create unique notification for the added user
            from syncanddine.models.message import Message
            Message.create_unique_notification(
                sender_id=current_user.id,
                recipient_id=user_id,
                content=f'{current_user.username} added you as a connection!'
            )
            db.session.commit()
            
            flash(f'You are now friends with {user.username}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding connection. Please try again.', 'danger')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success'})
    
    return redirect(url_for('social.connections'))

@social.route('/connections/remove/<int:user_id>', methods=['POST'])
@login_required
def remove_connection(user_id):
    user = User.query.get_or_404(user_id)
    
    if not current_user.is_friend(user):
        flash(f'You are not friends with {user.username}.', 'warning')
    else:
        current_user.remove_friend(user)
        db.session.commit()
        flash(f'You are no longer friends with {user.username}.', 'info')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success'})
    
    return redirect(url_for('social.connections'))

@social.route('/groups')
@login_required
def my_groups():
    owned_groups = current_user.owned_groups
    member_groups = current_user.groups.all()
    
    return render_template('social/groups.html',
                          title='My Groups',
                          owned_groups=owned_groups,
                          member_groups=member_groups)

@social.route('/groups/create', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        result_email = request.form.get('result_email', '').strip()
        time_preset = request.form.get('time_preset', '24')
        
        if time_preset == 'custom':
            deadline_hours = request.form.get('deadline_hours', 24, type=int)
            deadline_minutes = request.form.get('deadline_minutes', 0, type=int)
        else:
            deadline_hours = int(time_preset)
            deadline_minutes = 0
        
        if not name:
            flash('Group name is required.', 'danger')
            return redirect(url_for('social.create_group'))
        
        if not result_email:
            flash('Results email is required.', 'danger')
            return redirect(url_for('social.create_group'))
        
        if '@' not in result_email or '.' not in result_email:
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('social.create_group'))
        
        # Calculate deadline
        from datetime import datetime, timedelta
        deadline = datetime.utcnow() + timedelta(hours=deadline_hours, minutes=deadline_minutes)
        
        # Generate unique share code
        max_attempts = 5
        for attempt in range(max_attempts):
            share_code = str(uuid.uuid4())[:8].upper()
            existing = Group.query.filter_by(share_code=share_code).first()
            if not existing:
                break
        else:
            flash('Unable to generate unique group code. Please try again.', 'danger')
            return redirect(url_for('social.create_group'))
        
        group = Group(
            name=name, 
            owner_id=current_user.id, 
            share_code=share_code,
            result_email=result_email,
            selection_deadline=deadline
        )
        group.members.append(current_user)
        
        # Add selected members
        member_ids = request.form.getlist('members[]')
        if member_ids:
            for member_id in member_ids:
                try:
                    user_id = int(member_id)
                    user = User.query.get(user_id)
                    if user and user != current_user and user not in group.members:
                        group.members.append(user)
                except (ValueError, TypeError):
                    continue
        
        db.session.add(group)
        db.session.commit()
        
        flash(f'Group "{name}" created! Now select restaurants from the list.', 'success')
        return redirect(url_for('restaurants.list_restaurants', group_id=group.id))
    
    return render_template('social/create_group.html', title='Create Group')

@social.route('/groups/<int:group_id>/select-restaurants')
@login_required
def select_restaurants(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Only owner can select restaurants
    if current_user.id != group.owner_id:
        flash('Only group owner can select restaurants.', 'danger')
        return redirect(url_for('social.group_detail', group_id=group.id))
    
    # Get restaurants from Google Places API
    from syncanddine.restaurants.places_service import GooglePlacesService
    places_service = GooglePlacesService()
    
    try:
        restaurants = places_service.search_restaurants(lat=12.9716, lon=77.5946)  # Default Bangalore
    except Exception as e:
        flash('Unable to load restaurants. Please try again later.', 'warning')
        restaurants = []
    
    return render_template('social/select_restaurants.html',
                          title=f'Select Restaurants - {group.name}',
                          group=group,
                          restaurants=restaurants)

@social.route('/groups/<int:group_id>/save-selection', methods=['POST'])
@login_required
def save_restaurant_selection(group_id):
    group = Group.query.get_or_404(group_id)
    
    if current_user.id != group.owner_id:
        flash('Only group owner can save restaurant selection.', 'danger')
        return redirect(url_for('social.group_detail', group_id=group.id))
    
    selected_restaurants = request.form.getlist('restaurants[]')
    
    if not selected_restaurants:
        flash('Please select at least one restaurant.', 'warning')
        return redirect(url_for('social.select_restaurants', group_id=group.id))
    
    if len(selected_restaurants) > 20:
        flash('Please select maximum 20 restaurants.', 'warning')
        return redirect(url_for('social.select_restaurants', group_id=group.id))
    
    # Save selected restaurants
    group.set_preselected_restaurants(selected_restaurants)
    db.session.commit()
    
    flash(f'Selected {len(selected_restaurants)} restaurants! Share the group link now.', 'success')
    return redirect(url_for('social.group_detail', group_id=group.id))

@social.route('/join/<share_code>')
def join_group_public(share_code):
    """Public join route that handles both logged in and new users"""
    group = Group.query.filter_by(share_code=share_code).first()
    
    if not group:
        flash('Invalid group link.', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if group has expired
    if group.is_expired():
        flash('This group selection has expired.', 'warning')
        return redirect(url_for('main.index'))
    
    # If user is logged in, add them to group
    if current_user.is_authenticated:
        if current_user in group.members:
            flash(f'You are already in {group.name}.', 'info')
        else:
            group.members.append(current_user)
            db.session.commit()
            flash(f'Welcome to {group.name}!', 'success')
        
        return redirect(url_for('restaurants.list_restaurants', group_id=group.id))
    
    # For new users, redirect to registration with group code
    return redirect(url_for('auth.register', join_code=share_code))

@social.route('/groups/<int:group_id>')
@login_required
def group_detail(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Check if user is in the group
    if current_user not in group.members and current_user != group.owner:
        flash('You are not a member of this group.', 'danger')
        return redirect(url_for('social.my_groups'))
    
    # Get admin status for all members
    admin_members = db.session.query(User.id).join(group_members).filter(
        group_members.c.group_id == group_id,
        group_members.c.is_admin == True
    ).all()
    
    admin_ids = [user_id for (user_id,) in admin_members]
    is_admin = current_user.id == group.owner_id or current_user.id in admin_ids
    
    return render_template('social/group_detail.html',
                          title=group.name,
                          group=group,
                          admin_ids=admin_ids,
                          is_admin=is_admin)

@social.route('/groups/join/<share_code>')
@login_required
def join_group(share_code):
    """Legacy join route for logged in users"""
    return redirect(url_for('social.join_group_public', share_code=share_code))

@social.route('/groups/<int:group_id>/add_member', methods=['POST'])
@login_required
def add_group_member(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Check if user is the group owner or an admin
    if not group.is_admin(current_user):
        flash('Only group admins can add members.', 'danger')
        return redirect(url_for('social.group_detail', group_id=group.id))
    
    user_id = request.form.get('user_id')
    
    if not user_id:
        flash('Please select a user to add.', 'warning')
        return redirect(url_for('social.group_detail', group_id=group.id))
    
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        flash('Invalid user selection.', 'danger')
        return redirect(url_for('social.group_detail', group_id=group.id))
    
    user = User.query.get_or_404(user_id)
    
    # Check group size limit
    if len(group.members) >= 10:
        flash('Group has reached maximum capacity (10 members).', 'warning')
        return redirect(url_for('social.group_detail', group_id=group.id))
    
    if user in group.members:
        flash(f'{user.username} is already a member of this group.', 'info')
    else:
        group.members.append(user)
        
        # Create notification for added member
        from syncanddine.models.message import Message
        notification = Message(
            sender_id=current_user.id,
            recipient_id=user.id,
            content=f'{current_user.username} added you to group "{group.name}"!'
        )
        db.session.add(notification)
        db.session.commit()
        flash(f'{user.username} has been added to the group!', 'success')
    
    return redirect(url_for('social.group_detail', group_id=group.id))

@social.route('/groups/<int:group_id>/remove_member/<int:user_id>', methods=['POST'])
@login_required
def remove_group_member(group_id, user_id):
    group = Group.query.get_or_404(group_id)
    
    # Check if user is the group owner or an admin
    if not group.is_admin(current_user):
        flash('Only group admins can remove members.', 'danger')
        return redirect(url_for('social.group_detail', group_id=group.id))
    
    user = User.query.get_or_404(user_id)
    
    if user == group.owner:
        flash('You cannot remove the group owner.', 'warning')
    elif user not in group.members:
        flash(f'{user.username} is not a member of this group.', 'warning')
    # Non-owner admins can't remove other admins
    elif current_user != group.owner and group.is_admin(user):
        flash('Only the group owner can remove admins.', 'warning')
    else:
        group.members.remove(user)
        
        # Notify the removed user
        from syncanddine.models.message import Message
        notification = Message(
            sender_id=current_user.id,
            recipient_id=user.id,
            content=f'You were removed from group "{group.name}" by {current_user.username}'
        )
        db.session.add(notification)
        
        db.session.commit()
        flash(f'{user.username} has been removed from the group.', 'info')
    
    return redirect(url_for('social.group_detail', group_id=group.id))

@social.route('/groups/<int:group_id>/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(group_id, user_id):
    group = Group.query.get_or_404(group_id)
    user = User.query.get_or_404(user_id)
    
    # Only the owner can make other users admins
    if current_user.id != group.owner_id:
        flash('Only the group owner can change admin status.', 'danger')
        return redirect(url_for('social.group_detail', group_id=group.id))
    
    # Cannot change owner's admin status
    if user.id == group.owner_id:
        flash('Cannot change the owner\'s admin status.', 'warning')
        return redirect(url_for('social.group_detail', group_id=group.id))
    
    # Check if user is a member
    if user not in group.members:
        flash(f'{user.username} is not a member of this group.', 'warning')
        return redirect(url_for('social.group_detail', group_id=group.id))
    
    # Check current admin status
    is_admin = db.session.query(group_members).filter_by(
        user_id=user.id,
        group_id=group.id,
        is_admin=True
    ).first() is not None
    
    # If making user an admin, first remove admin status from all other members
    # including the current owner (issue #4)
    if not is_admin:
        # Remove admin status from all members except the target user
        remove_stmt = group_members.update().where(
            (group_members.c.group_id == group.id) &
            (group_members.c.user_id != user.id)
        ).values(is_admin=False)
        
        db.session.execute(remove_stmt)
        
        # Transfer ownership to the new admin
        group.owner_id = user.id
        db.session.add(group)
    
    # Toggle admin status for the target user
    stmt = group_members.update().where(
        (group_members.c.user_id == user.id) & 
        (group_members.c.group_id == group.id)
    ).values(is_admin=not is_admin)
    
    db.session.execute(stmt)
    db.session.commit()
    
    if is_admin:
        flash(f'{user.username} is no longer an admin.', 'info')
    else:
        flash(f'{user.username} is now the admin and owner of the group.', 'success')
    
    return redirect(url_for('social.group_detail', group_id=group.id))

@social.route('/groups/<int:group_id>/leave', methods=['POST'])
@login_required
def leave_group(group_id):
    group = Group.query.get_or_404(group_id)
    
    if current_user not in group.members:
        flash('You are not a member of this group.', 'warning')
        return redirect(url_for('social.my_groups'))
    
    # If user is owner, require ownership transfer
    if current_user.id == group.owner_id:
        new_owner_id = request.form.get('new_owner_id')
        if not new_owner_id:
            flash('As group owner, you must transfer ownership before leaving.', 'warning')
            return redirect(url_for('social.group_detail', group_id=group.id))
        
        new_owner = User.query.get_or_404(new_owner_id)
        if new_owner not in group.members:
            flash('New owner must be a group member.', 'danger')
            return redirect(url_for('social.group_detail', group_id=group.id))
        
        # Transfer ownership
        group.owner_id = new_owner.id
        
        # Notify new owner
        from syncanddine.models.message import Message
        notification = Message(
            sender_id=current_user.id,
            recipient_id=new_owner.id,
            content=f'You are now the owner of group "{group.name}"!'
        )
        db.session.add(notification)
    
    # Remove user from group
    group.members.remove(current_user)
    
    # Check if group becomes empty
    if group.members.count() == 0:
        # Delete empty group
        from sqlalchemy import text
        db.session.execute(text("DELETE FROM restaurant_like WHERE group_id = :group_id"), {'group_id': group.id})
        db.session.delete(group)
        db.session.commit()
        flash(f'You have left {group.name}. Group was deleted as it became empty.', 'info')
        return redirect(url_for('social.my_groups'))
    
    # Notify remaining members
    from syncanddine.models.message import Message
    for member in group.members:
        notification = Message(
            sender_id=current_user.id,
            recipient_id=member.id,
            content=f'{current_user.username} left group "{group.name}"'
        )
        db.session.add(notification)
    
    db.session.commit()
    flash(f'You have left {group.name}.', 'info')
    return redirect(url_for('social.my_groups'))

@social.route('/groups/<int:group_id>/delete', methods=['POST'])
@login_required
def delete_group(group_id):
    try:
        group = Group.query.get_or_404(group_id)
        
        # Only owner can delete group
        if current_user.id != group.owner_id:
            flash('Only the group owner can delete the group.', 'danger')
            return redirect(url_for('social.group_detail', group_id=group.id))
        
        group_name = group.name
        
        # Notify all members about group deletion
        from syncanddine.models.message import Message
        for member in group.members:
            if member != current_user:
                notification = Message(
                    sender_id=current_user.id,
                    recipient_id=member.id,
                    content=f'Group "{group_name}" was deleted by {current_user.username}'
                )
                db.session.add(notification)
        
        # Delete group data (likes, etc.)
        from sqlalchemy import text
        db.session.execute(text("DELETE FROM restaurant_like WHERE group_id = :group_id"), {'group_id': group.id})
        
        # Delete the group
        db.session.delete(group)
        db.session.commit()
        
        flash(f'Group "{group_name}" has been deleted.', 'info')
        return redirect(url_for('social.my_groups'))
    except Exception as e:
        db.session.rollback()
        flash('Error deleting group. Please try again.', 'danger')
        return redirect(url_for('social.group_detail', group_id=group_id))

@social.route('/messages/<int:friend_id>', methods=['GET', 'POST'])
@login_required
def messages(friend_id):
    from syncanddine.models.message import Message
    
    friend = User.query.get_or_404(friend_id)
    
    # Check if they are friends
    if not current_user.is_friend(friend):
        flash('You can only message your connections.', 'danger')
        return redirect(url_for('social.connections'))
    
    # Handle new message submission
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        
        if not content:
            flash('Message cannot be empty.', 'warning')
        elif len(content) > 1000:
            flash('Message must be less than 1000 characters.', 'warning')
        else:
            try:
                message = Message(
                    sender_id=current_user.id,
                    recipient_id=friend_id,
                    content=content
                )
                db.session.add(message)
                db.session.commit()
                flash('Message sent!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error sending message. Please try again.', 'danger')
    
    # Get conversation history (messages between current user and friend)
    sent_messages = Message.query.filter_by(
        sender_id=current_user.id, 
        recipient_id=friend_id
    ).all()
    
    received_messages = Message.query.filter_by(
        sender_id=friend_id, 
        recipient_id=current_user.id
    ).all()
    
    # Mark received messages as read
    for message in received_messages:
        if not message.is_read:
            message.is_read = True
    
    db.session.commit()
    
    # Combine and sort messages by timestamp
    messages = sorted(sent_messages + received_messages, key=lambda x: x.timestamp)
    
    return render_template('social/messages.html',
                          title=f'Messages with {friend.username}',
                          friend=friend,
                          messages=messages)