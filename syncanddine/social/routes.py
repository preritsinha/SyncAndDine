from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from syncanddine import db
from syncanddine.models.user import User, Group, group_members
import uuid

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
        username = request.form.get('username')
        users = User.query.filter(User.username.ilike(f'%{username}%')).all()
        return render_template('social/search_results.html',
                              title='Search Results',
                              users=users,
                              search_term=username)
    
    return render_template('social/search.html', title='Find Friends')

@social.route('/connections/add/<int:user_id>', methods=['POST'])
@login_required
def add_connection(user_id):
    user = User.query.get_or_404(user_id)
    
    if user == current_user:
        flash('You cannot add yourself as a friend.', 'warning')
    elif current_user.is_friend(user):
        flash(f'You are already friends with {user.username}.', 'info')
    else:
        current_user.add_friend(user)
        db.session.commit()
        
        # Create notification for the added user
        from syncanddine.models.message import Message
        notification = Message(
            sender_id=current_user.id,
            recipient_id=user_id,
            content=f'{current_user.username} added you as a connection!'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash(f'You are now friends with {user.username}!', 'success')
    
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
        name = request.form.get('name')
        
        if not name:
            flash('Group name is required.', 'danger')
            return redirect(url_for('social.create_group'))
        
        # Generate a unique share code
        share_code = str(uuid.uuid4())[:8]
        
        group = Group(name=name, owner_id=current_user.id, share_code=share_code)
        group.members.append(current_user)
        
        # Add selected members to the group
        member_ids = request.form.getlist('members[]')
        if member_ids:
            for member_id in member_ids:
                user = User.query.get(int(member_id))
                if user and user != current_user:
                    group.members.append(user)
                    
                    # Create notification for added member
                    from syncanddine.models.message import Message
                    notification = Message(
                        sender_id=current_user.id,
                        recipient_id=user.id,
                        content=f'{current_user.username} added you to group "{name}"!'
                    )
                    db.session.add(notification)
        
        # Set the owner as admin in the association table
        stmt = group_members.update().where(
            (group_members.c.user_id == current_user.id) & 
            (group_members.c.group_id == group.id)
        ).values(is_admin=True)
        
        db.session.add(group)
        db.session.commit()
        
        # Execute the update after commit to ensure the group_id exists
        db.session.execute(stmt)
        db.session.commit()
        
        flash(f'Group "{name}" created successfully!', 'success')
        return redirect(url_for('social.group_detail', group_id=group.id))
    
    return render_template('social/create_group.html', title='Create Group')

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
    group = Group.query.filter_by(share_code=share_code).first()
    
    if not group:
        flash('Invalid group code.', 'danger')
        return redirect(url_for('social.my_groups'))
    
    if current_user in group.members:
        flash(f'You are already a member of {group.name}.', 'info')
    else:
        group.members.append(current_user)
        db.session.commit()
        flash(f'You have joined {group.name}!', 'success')
    
    return redirect(url_for('social.group_detail', group_id=group.id))

@social.route('/groups/<int:group_id>/add_member', methods=['POST'])
@login_required
def add_group_member(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Check if user is the group owner or an admin
    if not group.is_admin(current_user):
        flash('Only group admins can add members.', 'danger')
        return redirect(url_for('social.group_detail', group_id=group.id))
    
    user_id = request.form.get('user_id')
    user = User.query.get_or_404(user_id)
    
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
        content = request.form.get('content')
        if content:
            message = Message(
                sender_id=current_user.id,
                recipient_id=friend_id,
                content=content
            )
            db.session.add(message)
            db.session.commit()
            flash('Message sent!', 'success')
    
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