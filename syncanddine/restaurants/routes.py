from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from syncanddine import db
from syncanddine.models.restaurant import Restaurant, RestaurantLike
from syncanddine.models.user import Group

restaurants = Blueprint('restaurants', __name__)

@restaurants.route('/restaurants')
@login_required
def list_restaurants():
    # Get filter parameters
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
    
    # Get all restaurants
    restaurants = query.all()
    
    # Get unique locations and cuisines for filter dropdowns
    all_locations = db.session.query(Restaurant.location).distinct().all()
    locations = [loc[0] for loc in all_locations if loc[0]]
    
    all_cuisines = db.session.query(Restaurant.cuisine_type).distinct().all()
    cuisines = [cuisine[0] for cuisine in all_cuisines if cuisine[0]]
    
    # Get user's groups for the group filter (avoid duplicates)
    owned_group_ids = [g.id for g in current_user.owned_groups]
    member_groups = [g for g in current_user.groups if g.id not in owned_group_ids]
    user_groups = current_user.owned_groups + member_groups
    
    return render_template('restaurants/list.html', 
                          title='Restaurants', 
                          restaurants=restaurants,
                          group=group,
                          is_admin=is_admin,
                          locations=locations,
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
    
    # Get restaurants that the user hasn't swiped on yet in this group
    swiped_restaurant_ids = db.session.query(RestaurantLike.restaurant_id).filter_by(
        user_id=current_user.id,
        group_id=group_id if group_id else None
    ).all()
    
    swiped_restaurant_ids = [r[0] for r in swiped_restaurant_ids]
    
    if swiped_restaurant_ids:
        query = query.filter(~Restaurant.id.in_(swiped_restaurant_ids))
    
    # Get the first restaurant
    restaurant = query.first()
    
    # Get all locations and cuisines for filter dropdowns
    all_locations = db.session.query(Restaurant.location).distinct().all()
    locations = [loc[0] for loc in all_locations if loc[0]]
    
    all_cuisines = db.session.query(Restaurant.cuisine_type).distinct().all()
    cuisines = [cuisine[0] for cuisine in all_cuisines if cuisine[0]]
    
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
                          locations=locations,
                          cuisines=cuisines,
                          user_groups=user_groups)

@restaurants.route('/restaurants/<int:restaurant_id>')
@login_required
def restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    return render_template('restaurants/detail.html', 
                          title=restaurant.name, 
                          restaurant=restaurant)

@restaurants.route('/restaurants/like/<int:restaurant_id>/<int:group_id>', methods=['POST'])
@login_required
def like_restaurant(restaurant_id, group_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    group = None
    
    if group_id > 0:
        group = Group.query.get_or_404(group_id)
        # Check if user is in the group
        if current_user not in group.members and current_user != group.owner:
            flash('You are not a member of this group.', 'danger')
            return redirect(url_for('restaurants.list_restaurants'))
    
    # Check if user already liked/disliked this restaurant in this group
    existing_like = RestaurantLike.query.filter_by(
        user_id=current_user.id,
        restaurant_id=restaurant.id,
        group_id=group_id if group else None
    ).first()
    
    if existing_like:
        existing_like.liked = True
    else:
        like = RestaurantLike(
            user_id=current_user.id,
            restaurant_id=restaurant.id,
            group_id=group_id if group else None,
            liked=True
        )
        db.session.add(like)
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success'})
    
    flash(f'You liked {restaurant.name}!', 'success')
    
    # If coming from swipe view, redirect back to swipe with same parameters
    if request.referrer and 'swipe' in request.referrer:
        return redirect(url_for('restaurants.swipe_restaurants', group_id=group_id))
    
    return redirect(url_for('restaurants.list_restaurants'))

@restaurants.route('/restaurants/dislike/<int:restaurant_id>/<int:group_id>', methods=['POST'])
@login_required
def dislike_restaurant(restaurant_id, group_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    group = None
    
    if group_id > 0:
        group = Group.query.get_or_404(group_id)
        # Check if user is in the group
        if current_user not in group.members and current_user != group.owner:
            flash('You are not a member of this group.', 'danger')
            return redirect(url_for('restaurants.list_restaurants'))
    
    # Check if user already liked/disliked this restaurant in this group
    existing_like = RestaurantLike.query.filter_by(
        user_id=current_user.id,
        restaurant_id=restaurant.id,
        group_id=group_id if group else None
    ).first()
    
    if existing_like:
        existing_like.liked = False
    else:
        like = RestaurantLike(
            user_id=current_user.id,
            restaurant_id=restaurant.id,
            group_id=group_id if group else None,
            liked=False
        )
        db.session.add(like)
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success'})
    
    flash(f'You disliked {restaurant.name}.', 'info')
    
    # If coming from swipe view, redirect back to swipe with same parameters
    if request.referrer and 'swipe' in request.referrer:
        return redirect(url_for('restaurants.swipe_restaurants', group_id=group_id))
    
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