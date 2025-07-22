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
        default_city = os.getenv('DEFAULT_CITY', 'Mumbai, India')
        default_coords = os.getenv('DEFAULT_COORDS', '19.0760,72.8777').split(',')
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
    if location_query:
        restaurants = places_service.search_restaurants(city=location_query)
    else:
        restaurants = places_service.search_restaurants(lat, lon)
    
    # Apply filters
    if min_rating > 0:
        restaurants = [r for r in restaurants if r['rating'] >= min_rating]
    if cuisine:
        restaurants = [r for r in restaurants if cuisine.lower() in r['cuisine_type'].lower()]
    if price_range:
        restaurants = [r for r in restaurants if r['price_range'] == price_range]
    
    # Get unique cuisines for filter dropdown
    cuisines = list(set([r['cuisine_type'] for r in restaurants if r['cuisine_type']]))
    
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
                          user_groups=user_groups)

@restaurants.route('/restaurants/swipe')
@login_required
def swipe_restaurants():
    # Get filter parameters (same as list_restaurants)
    location = request.args.get('location', '')
    min_rating = request.args.get('min_rating', 0, type=float)
    cuisine = request.args.get('cuisine', '')
    veg_only = request.args.get('veg_only', False, type=bool)
    price_range = request.args.get('price_range', '')
    group_id = request.args.get('group_id', 0, type=int)
    
    # Check if user is admin if group_id is provided
    is_admin = True  # Default for personal filters
    group = None
    
    if group_id > 0:
        group = Group.query.get_or_404(group_id)
        # Check if user is in the group
        if current_user not in group.members and current_user != group.owner:
            flash('You are not a member of this group.', 'danger')
            return redirect(url_for('social.my_groups'))
        
        # Check if user is admin
        is_admin = group.is_admin(current_user)
    
    # Build query
    query = Restaurant.query
    
    if location:
        query = query.filter(Restaurant.location.ilike(f'%{location}%'))
    if min_rating > 0:
        query = query.filter(Restaurant.rating >= min_rating)
    if cuisine:
        query = query.filter(Restaurant.cuisine_type == cuisine)
    if veg_only:
        query = query.filter(Restaurant.is_vegetarian == True)
    if price_range:
        query = query.filter(Restaurant.price_range == price_range)
    
    # Get live restaurants from Google Places API
    places_service = GooglePlacesService()
    all_restaurants = places_service.search_restaurants(lat, lon)
    
    # Apply filters
    if min_rating > 0:
        all_restaurants = [r for r in all_restaurants if r['rating'] >= min_rating]
    if cuisine:
        all_restaurants = [r for r in all_restaurants if cuisine.lower() in r['cuisine_type'].lower()]
    if price_range:
        all_restaurants = [r for r in all_restaurants if r['price_range'] == price_range]
    
    # Get the first restaurant for swiping
    restaurant = all_restaurants[0] if all_restaurants else None
    
    # Get unique cuisines for filter dropdown
    cuisines = list(set([r['cuisine_type'] for r in all_restaurants if r['cuisine_type']]))
    
    # Get user's groups for the group filter (avoid duplicates)
    owned_group_ids = [g.id for g in current_user.owned_groups]
    member_groups = [g for g in current_user.groups if g.id not in owned_group_ids]
    user_groups = current_user.owned_groups + member_groups
    
    return render_template('restaurants/swipe.html', 
                          title='Swipe Restaurants', 
                          restaurant=restaurant,
                          group=group,
                          group_id=group_id,
                          is_admin=is_admin,
                          cuisines=cuisines,
                          user_groups=user_groups)

@restaurants.route('/restaurants/<restaurant_id>')
@login_required
def restaurant_detail(restaurant_id):
    # Get restaurant details from Google Places API
    places_service = GooglePlacesService()
    restaurant = places_service.get_restaurant_details(restaurant_id)
    if not restaurant:
        flash('Restaurant not found', 'danger')
        return redirect(url_for('restaurants.list_restaurants'))
    return render_template('restaurants/detail.html', 
                          title=restaurant['name'], 
                          restaurant=restaurant)

@restaurants.route('/restaurants/like/<restaurant_id>/<int:group_id>', methods=['POST'])
@login_required
def like_restaurant(restaurant_id, group_id):
    group = None
    
    if group_id > 0:
        group = Group.query.get_or_404(group_id)
        if current_user not in group.members and current_user != group.owner:
            flash('You are not a member of this group.', 'danger')
            return redirect(url_for('restaurants.list_restaurants'))
    
    # Check if user already liked/disliked this restaurant in this group
    existing_like = RestaurantLike.query.filter_by(
        user_id=current_user.id,
        restaurant_google_id=restaurant_id,
        group_id=group_id if group else None
    ).first()
    
    if existing_like:
        existing_like.liked = True
    else:
        like = RestaurantLike(
            user_id=current_user.id,
            restaurant_google_id=restaurant_id,
            group_id=group_id if group else None,
            liked=True
        )
        db.session.add(like)
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success'})
    
    flash('Restaurant liked!', 'success')
    return redirect(url_for('restaurants.list_restaurants'))

@restaurants.route('/restaurants/dislike/<restaurant_id>/<int:group_id>', methods=['POST'])
@login_required
def dislike_restaurant(restaurant_id, group_id):
    group = None
    
    if group_id > 0:
        group = Group.query.get_or_404(group_id)
        if current_user not in group.members and current_user != group.owner:
            flash('You are not a member of this group.', 'danger')
            return redirect(url_for('restaurants.list_restaurants'))
    
    existing_like = RestaurantLike.query.filter_by(
        user_id=current_user.id,
        restaurant_google_id=restaurant_id,
        group_id=group_id if group else None
    ).first()
    
    if existing_like:
        existing_like.liked = False
    else:
        like = RestaurantLike(
            user_id=current_user.id,
            restaurant_google_id=restaurant_id,
            group_id=group_id if group else None,
            liked=False
        )
        db.session.add(like)
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success'})
    
    flash('Restaurant disliked.', 'info')
    return redirect(url_for('restaurants.list_restaurants'))

@restaurants.route('/restaurants/matches/<int:group_id>')
@login_required
def group_matches(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Check if user is in the group
    if current_user not in group.members and current_user != group.owner:
        flash('You are not a member of this group.', 'danger')
        return redirect(url_for('social.my_groups'))
    
    # Get all members of the group
    members = list(group.members)
    if group.owner not in members:
        members.append(group.owner)
    
    # Find restaurants that all members liked
    matched_restaurants = []
    
    # Get all restaurants that at least one member liked
    liked_restaurants = db.session.query(Restaurant).join(RestaurantLike).filter(
        RestaurantLike.group_id == group_id,
        RestaurantLike.liked == True
    ).distinct().all()
    
    # Check if all members liked each restaurant
    for restaurant in liked_restaurants:
        all_liked = True
        for member in members:
            like = RestaurantLike.query.filter_by(
                user_id=member.id,
                restaurant_id=restaurant.id,
                group_id=group_id,
                liked=True
            ).first()
            
            if not like:
                all_liked = False
                break
        
        if all_liked:
            matched_restaurants.append(restaurant)
    
    return render_template('restaurants/matches.html',
                          title='Group Matches',
                          group=group,
                          matches=matched_restaurants)

