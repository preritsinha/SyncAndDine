"""
Restaurant Routes Module

This module handles all restaurant-related functionality including:
- Dynamic restaurant listing from Google Places API
- Restaurant filtering and search
- User preferences (likes/dislikes)
- Restaurant details and swiping interface

Author: SyncAndDine Team
Version: 2.0 - Dynamic API Integration
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from syncanddine import db
from syncanddine.models.restaurant import RestaurantLike
from syncanddine.models.user import Group
from syncanddine.restaurants.places_service import GooglePlacesService
from datetime import datetime

# Create restaurants blueprint for modular route organization
restaurants = Blueprint('restaurants', __name__)

@restaurants.route('/restaurants')
@login_required
def list_restaurants():
    """
    Display restaurants dynamically from Google Places API
    
    Features:
    - Live restaurant data based on user location
    - Real-time filtering by rating, cuisine, and price
    - Group-based restaurant viewing
    - Admin controls for group filters
    
    Returns:
        Rendered restaurant list template with live API data
    """
    # Extract filter parameters from URL query string
    city = request.args.get('city', '')
    area = request.args.get('area', '')
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    restaurant_name = request.args.get('restaurant_name', '').strip()
    
    # Combine city and area for search
    location_query = f"{area}, {city}" if area and city else city
    min_rating = request.args.get('min_rating', 0, type=float)
    cuisine = request.args.get('cuisine', '')
    price_range = request.args.get('price_range', '')
    group_id = request.args.get('group_id', 0, type=int)
    
    # Get user's location or use a fallback
    if not city and not (lat and lon):
        # Try to get user's country/region for better defaults
        import os
        default_city = os.getenv('DEFAULT_CITY', 'Bangalore, India')
        default_coords = os.getenv('DEFAULT_COORDS', '12.9716,77.5946').split(',')
        lat, lon = float(default_coords[0]), float(default_coords[1])
    
    # Check if user is admin if group_id is provided
    is_admin = True
    group = None
    
    if group_id > 0:
        group = Group.query.get_or_404(group_id)
        if current_user not in group.members and current_user != group.owner:
            flash('You are not a member of this group.', 'danger')
            return redirect(url_for('social.my_groups'))
        is_admin = group.is_admin(current_user)
    
    # Get live restaurants from Google Places API
    places_service = GooglePlacesService()
    try:
        if location_query:
            restaurants = places_service.search_restaurants(city=location_query, query=restaurant_name)
        else:
            restaurants = places_service.search_restaurants(lat, lon, query=restaurant_name)
    except Exception as e:
        flash('Unable to load restaurants at the moment. Please try again later.', 'warning')
        restaurants = []
    
    # Apply filters
    if min_rating > 0:
        restaurants = [r for r in restaurants if r['rating'] >= min_rating]
    if cuisine:
        restaurants = [r for r in restaurants if cuisine.lower() in r['cuisine_type'].lower()]
    if price_range:
        restaurants = [r for r in restaurants if r['price_range'] == price_range]
    # Remove redundant name filtering since it's now handled by similarity search
    
    # Filter for personal favorites if requested
    liked_only = request.args.get('liked_only', False)
    if liked_only and not group_id:
        from syncanddine.models.restaurant import RestaurantLike
        liked_restaurant_ids = [like.restaurant_google_id for like in 
                              RestaurantLike.query.filter_by(user_id=current_user.id, group_id=None, liked=True).all()]
        restaurants = [r for r in restaurants if r['google_place_id'] in liked_restaurant_ids]
        
        # Add notification for completed selection
        if restaurants:
            flash(f'Great! You have selected {len(restaurants)} favorite restaurants.', 'success')
        else:
            flash('You haven\'t liked any restaurants yet. Go back and like some restaurants first!', 'info')
    
    # Get unique cuisines for filter dropdown
    cuisines = list(set([r['cuisine_type'] for r in restaurants if r['cuisine_type']]))
    
    # Get user preferences for each restaurant
    user_preferences = {}
    leaderboard = []
    
    if restaurants:
        from sqlalchemy import text
        restaurant_ids = [r['google_place_id'] for r in restaurants]
        placeholders = ','.join([':id' + str(i) for i in range(len(restaurant_ids))])
        params = {'user_id': current_user.id, 'group_id': group_id if group_id > 0 else None}
        for i, rid in enumerate(restaurant_ids):
            params[f'id{i}'] = rid
        
        preferences = db.session.execute(
            text(f"SELECT restaurant_google_id, liked FROM restaurant_like WHERE user_id = :user_id AND group_id = :group_id AND restaurant_google_id IN ({placeholders})"),
            params
        ).fetchall()
        
        for pref in preferences:
            user_preferences[pref[0]] = 'liked' if pref[1] else 'disliked'
    
    # Get user's groups
    owned_group_ids = [g.id for g in current_user.owned_groups]
    member_groups = [g for g in current_user.groups if g.id not in owned_group_ids]
    user_groups = current_user.owned_groups + member_groups
    
    return render_template('restaurants/list.html', 
                          title='Restaurants', 
                          restaurants=restaurants,
                          group=group,
                          is_admin=is_admin,
                          cuisines=cuisines,
                          user_groups=user_groups,
                          user_preferences=user_preferences,
                          leaderboard=leaderboard)



@restaurants.route('/restaurants/<restaurant_id>')
@login_required
def restaurant_detail(restaurant_id):
    # Get restaurant details from Google Places API
    places_service = GooglePlacesService()
    try:
        restaurant = places_service.get_restaurant_details(restaurant_id)
        if not restaurant:
            flash('Restaurant not found', 'danger')
            return redirect(url_for('restaurants.list_restaurants'))
    except Exception as e:
        flash('Unable to load restaurant details. Please try again later.', 'warning')
        return redirect(url_for('restaurants.list_restaurants'))
    return render_template('restaurants/detail.html', 
                          title=restaurant['name'], 
                          restaurant=restaurant)

@restaurants.route('/restaurants/like/<restaurant_id>/<int:group_id>', methods=['POST'])
@login_required
def like_restaurant(restaurant_id, group_id):
    try:
        group = None
        
        if group_id > 0:
            group = Group.query.get_or_404(group_id)
            if current_user not in group.members and current_user != group.owner:
                flash('You are not a member of this group.', 'danger')
                return redirect(url_for('restaurants.list_restaurants'))
        
        # Check if user already liked/disliked this restaurant in this group
        # Use raw SQL with correct column name
        from sqlalchemy import text
        existing_like = db.session.execute(
            text("SELECT * FROM restaurant_like WHERE user_id = :user_id AND group_id = :group_id AND restaurant_google_id = :restaurant_id LIMIT 1"),
            {'user_id': current_user.id, 'group_id': group_id if group_id > 0 else None, 'restaurant_id': restaurant_id}
        ).fetchone()
        
        if existing_like:
            # Delete existing record (toggle off)
            db.session.execute(
                text("DELETE FROM restaurant_like WHERE user_id = :user_id AND group_id = :group_id AND restaurant_google_id = :restaurant_id"),
                {'user_id': current_user.id, 'group_id': group_id if group_id > 0 else None, 'restaurant_id': restaurant_id}
            )
            action = 'disliked'
        else:
            # Insert new record using raw SQL
            db.session.execute(
                text("INSERT INTO restaurant_like (user_id, restaurant_google_id, group_id, liked, created_at) VALUES (:user_id, :restaurant_id, :group_id, 1, datetime('now'))"),
                {'user_id': current_user.id, 'restaurant_id': restaurant_id, 'group_id': group_id if group_id > 0 else None}
            )
            action = 'liked'
        
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success', 'action': action})
        
        return redirect(url_for('restaurants.list_restaurants'))
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error'})
        return redirect(url_for('restaurants.list_restaurants'))

@restaurants.route('/restaurants/dislike/<restaurant_id>/<int:group_id>', methods=['POST'])
@login_required
def dislike_restaurant(restaurant_id, group_id):
    try:
        group = None
        
        if group_id > 0:
            group = Group.query.get_or_404(group_id)
            if current_user not in group.members and current_user != group.owner:
                flash('You are not a member of this group.', 'danger')
                return redirect(url_for('restaurants.list_restaurants'))
        
        # Use raw SQL with correct column name
        from sqlalchemy import text
        existing_like = db.session.execute(
            text("SELECT * FROM restaurant_like WHERE user_id = :user_id AND group_id = :group_id AND restaurant_google_id = :restaurant_id LIMIT 1"),
            {'user_id': current_user.id, 'group_id': group_id if group_id > 0 else None, 'restaurant_id': restaurant_id}
        ).fetchone()
        
        if existing_like:
            # Update existing record
            db.session.execute(
                text("UPDATE restaurant_like SET liked = 0 WHERE user_id = :user_id AND group_id = :group_id AND restaurant_google_id = :restaurant_id"),
                {'user_id': current_user.id, 'group_id': group_id if group_id > 0 else None, 'restaurant_id': restaurant_id}
            )
        else:
            # Insert new dislike record
            db.session.execute(
                text("INSERT INTO restaurant_like (user_id, restaurant_google_id, group_id, liked, created_at) VALUES (:user_id, :restaurant_id, :group_id, 0, datetime('now'))"),
                {'user_id': current_user.id, 'restaurant_id': restaurant_id, 'group_id': group_id if group_id > 0 else None}
            )
        
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success'})
        
        return redirect(url_for('restaurants.list_restaurants'))
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error'})
        return redirect(url_for('restaurants.list_restaurants'))

@restaurants.route('/restaurants/finish-personal-selection')
@login_required
def finish_personal_selection():
    """Handle personal selection completion with summary and export options"""
    from syncanddine.models.restaurant import RestaurantLike
    
    # Get user's liked restaurants
    liked_restaurants = RestaurantLike.query.filter_by(
        user_id=current_user.id, 
        group_id=None, 
        liked=True
    ).all()
    
    # Get restaurant details from Google Places API
    places_service = GooglePlacesService()
    restaurant_details = []
    
    try:
        # Track unique restaurant IDs to avoid duplicates
        seen_restaurants = set()
        
        for like in liked_restaurants:
            if like.restaurant_google_id not in seen_restaurants:
                details = places_service.get_restaurant_details(like.restaurant_google_id)
                if details:
                    restaurant_details.append(details)
                    seen_restaurants.add(like.restaurant_google_id)
    except Exception as e:
        flash('Some restaurant details could not be loaded.', 'warning')
    
    return render_template('restaurants/personal_summary.html',
                          title='My Restaurant Selections',
                          restaurants=restaurant_details,
                          total_count=len(restaurant_details))

@restaurants.route('/restaurants/finish-group-selection/<int:group_id>')
@login_required
def finish_group_selection(group_id):
    """Handle group selection completion with matches, recommendations, and notifications"""
    from syncanddine.models.restaurant import RestaurantLike
    try:
        from syncanddine.models.message import Message
    except ImportError:
        Message = None
    
    group = Group.query.get_or_404(group_id)
    
    if current_user not in group.members:
        flash('You are not a member of this group.', 'danger')
        return redirect(url_for('social.my_groups'))
    
    # Notify other group members that user finished selection
    if Message:
        for member in group.members:
            if member != current_user:
                notification = Message(
                    sender_id=current_user.id,
                    recipient_id=member.id,
                    content=f'{current_user.username} finished selecting restaurants in group "{group.name}"!'
                )
                db.session.add(notification)
    
    db.session.commit()
    
    # Get all group members' liked restaurants
    group_likes = RestaurantLike.query.filter_by(group_id=group_id, liked=True).all()
    
    # Find restaurants liked by ALL members (perfect matches)
    restaurant_votes = {}
    for like in group_likes:
        if like.restaurant_google_id not in restaurant_votes:
            restaurant_votes[like.restaurant_google_id] = set()
        restaurant_votes[like.restaurant_google_id].add(like.user_id)
    
    total_members = group.members.count()
    perfect_matches = []
    partial_matches = []
    
    for restaurant_id, voters in restaurant_votes.items():
        if len(voters) == total_members:
            perfect_matches.append(restaurant_id)
        elif len(voters) >= max(2, total_members // 2):  # At least half or 2 people
            partial_matches.append((restaurant_id, len(voters)))
    
    # Sort partial matches by vote count
    partial_matches.sort(key=lambda x: x[1], reverse=True)
    
    # Get restaurant details from Google Places API
    places_service = GooglePlacesService()
    perfect_restaurants = []
    recommended_restaurants = []
    
    try:
        # Get perfect matches
        for restaurant_id in perfect_matches:
            details = places_service.get_restaurant_details(restaurant_id)
            if details:
                perfect_restaurants.append(details)
        
        # Get recommendations if no perfect matches
        if not perfect_matches and partial_matches:
            for restaurant_id, votes in partial_matches[:5]:  # Top 5 recommendations
                details = places_service.get_restaurant_details(restaurant_id)
                if details:
                    details['vote_count'] = votes
                    details['vote_percentage'] = round((votes / total_members) * 100)
                    recommended_restaurants.append(details)
    
    except Exception as e:
        flash('Some restaurant details could not be loaded.', 'warning')
    
    return render_template('restaurants/group_results.html',
                          title=f'Results for {group.name}',
                          group=group,
                          perfect_matches=perfect_restaurants,
                          recommendations=recommended_restaurants,
                          total_members=total_members)

@restaurants.route('/restaurants/export-selections')
@login_required
def export_selections():
    """Export user's restaurant selections as JSON"""
    from syncanddine.models.restaurant import RestaurantLike
    import json
    
    group_id = request.args.get('group_id', type=int)
    
    if group_id:
        likes = RestaurantLike.query.filter_by(
            user_id=current_user.id,
            group_id=group_id,
            liked=True
        ).all()
        filename = f'group_{group_id}_selections.json'
    else:
        likes = RestaurantLike.query.filter_by(
            user_id=current_user.id,
            group_id=None,
            liked=True
        ).all()
        filename = 'my_restaurant_selections.json'
    
    # Get restaurant details
    places_service = GooglePlacesService()
    export_data = {
        'user': current_user.username,
        'export_date': datetime.utcnow().isoformat(),
        'restaurants': []
    }
    
    try:
        for like in likes:
            details = places_service.get_restaurant_details(like.restaurant_google_id)
            if details:
                export_data['restaurants'].append({
                    'name': details['name'],
                    'location': details['location'],
                    'rating': details['rating'],
                    'google_place_id': details['google_place_id'],
                    'phone': details.get('phone', ''),
                    'website': details.get('website', '')
                })
    except Exception as e:
        flash('Error exporting selections.', 'danger')
        return redirect(url_for('restaurants.list_restaurants'))
    
    response = jsonify(export_data)
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

@restaurants.route('/restaurants/remove-selection/<restaurant_id>', methods=['POST'])
@login_required
def remove_selection(restaurant_id):
    """Remove a restaurant from user's personal selections"""
    try:
        from sqlalchemy import text
        
        # Remove the restaurant from personal selections (group_id = None)
        db.session.execute(
            text("DELETE FROM restaurant_like WHERE user_id = :user_id AND restaurant_google_id = :restaurant_id AND group_id IS NULL"),
            {'user_id': current_user.id, 'restaurant_id': restaurant_id}
        )
        
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success'})
        
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error'})
    
    return redirect(url_for('restaurants.finish_personal_selection'))

@restaurants.route('/restaurants/delete-all-selections', methods=['POST'])
@login_required
def delete_all_selections():
    """Delete all personal restaurant selections"""
    try:
        from sqlalchemy import text
        
        # Delete all personal selections (group_id = None)
        db.session.execute(
            text("DELETE FROM restaurant_like WHERE user_id = :user_id AND group_id IS NULL"),
            {'user_id': current_user.id}
        )
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
    
    return redirect(url_for('restaurants.finish_personal_selection'))

@restaurants.route('/restaurants/matches/<int:group_id>')
@login_required
def group_matches(group_id):
    try:
        group = Group.query.get_or_404(group_id)
        
        # Check if user is in the group
        if current_user not in group.members and current_user != group.owner:
            flash('You are not a member of this group.', 'danger')
            return redirect(url_for('social.my_groups'))
        
        # Get all members of the group
        members = list(group.members)
        if group.owner not in members:
            members.append(group.owner)
        
        # Get all restaurant IDs that at least one member liked
        liked_restaurant_ids = db.session.query(RestaurantLike.restaurant_google_id).filter(
            RestaurantLike.group_id == group_id,
            RestaurantLike.liked == True
        ).distinct().all()
        
        matched_restaurants = []
        places_service = GooglePlacesService()
        
        # Check each restaurant for unanimous likes
        for (restaurant_id,) in liked_restaurant_ids:
            all_liked = True
            for member in members:
                like = RestaurantLike.query.filter_by(
                    user_id=member.id,
                    restaurant_google_id=restaurant_id,
                    group_id=group_id,
                    liked=True
                ).first()
                
                if not like:
                    all_liked = False
                    break
            
            if all_liked:
                # Get restaurant details from Google Places API
                try:
                    restaurant_details = places_service.get_restaurant_details(restaurant_id)
                    if restaurant_details:
                        matched_restaurants.append(restaurant_details)
                except Exception:
                    # Skip restaurants that can't be loaded
                    continue
        
        return render_template('restaurants/matches.html',
                              title='Group Matches',
                              group=group,
                              matches=matched_restaurants)
    except Exception as e:
        flash('Error loading matches', 'danger')
        return redirect(url_for('social.group_detail', group_id=group_id))

