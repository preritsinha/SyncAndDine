from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from syncanddine import db
from syncanddine.models.user import User, Group
from syncanddine.models.restaurant import Restaurant, RestaurantLike

api = Blueprint('api', __name__)

# Restaurant API endpoints
@api.route('/restaurants', methods=['GET'])
@jwt_required()
def get_restaurants():
    # Get filter parameters
    location = request.args.get('location', '')
    min_rating = request.args.get('min_rating', 0, type=float)
    cuisine = request.args.get('cuisine', '')
    veg_only = request.args.get('veg_only', 'false')
    price_range = request.args.get('price_range', '')
    
    # Convert string to boolean
    veg_only = veg_only.lower() == 'true'
    
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
    
    restaurants = query.all()
    
    # Convert to JSON
    result = []
    for restaurant in restaurants:
        result.append({
            'id': restaurant.id,
            'name': restaurant.name,
            'location': restaurant.location,
            'rating': restaurant.rating,
            'cuisine_type': restaurant.cuisine_type,
            'price_range': restaurant.price_range,
            'is_vegetarian': restaurant.is_vegetarian,
            'distance': restaurant.distance,
            'image_url': restaurant.image_url
        })
    
    return jsonify(result)

@api.route('/restaurants/<int:restaurant_id>', methods=['GET'])
@jwt_required()
def get_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    result = {
        'id': restaurant.id,
        'name': restaurant.name,
        'location': restaurant.location,
        'rating': restaurant.rating,
        'cuisine_type': restaurant.cuisine_type,
        'price_range': restaurant.price_range,
        'is_vegetarian': restaurant.is_vegetarian,
        'distance': restaurant.distance,
        'image_url': restaurant.image_url
    }
    
    return jsonify(result)

@api.route('/restaurants/<int:restaurant_id>/like', methods=['POST'])
@jwt_required()
def like_restaurant(restaurant_id):
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    data = request.get_json() or {}
    group_id = data.get('group_id')
    
    group = None
    if group_id:
        group = Group.query.get_or_404(group_id)
        # Check if user is in the group
        if user not in group.members and user != group.owner:
            return jsonify({'message': 'You are not a member of this group'}), 403
    
    # Check if user already liked/disliked this restaurant in this group
    existing_like = RestaurantLike.query.filter_by(
        user_id=user.id,
        restaurant_id=restaurant.id,
        group_id=group_id
    ).first()
    
    if existing_like:
        existing_like.liked = True
    else:
        like = RestaurantLike(
            user_id=user.id,
            restaurant_id=restaurant.id,
            group_id=group_id,
            liked=True
        )
        db.session.add(like)
    
    db.session.commit()
    
    return jsonify({'message': 'Restaurant liked successfully'})

@api.route('/restaurants/<int:restaurant_id>/dislike', methods=['POST'])
@jwt_required()
def dislike_restaurant(restaurant_id):
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    data = request.get_json() or {}
    group_id = data.get('group_id')
    
    group = None
    if group_id:
        group = Group.query.get_or_404(group_id)
        # Check if user is in the group
        if user not in group.members and user != group.owner:
            return jsonify({'message': 'You are not a member of this group'}), 403
    
    # Check if user already liked/disliked this restaurant in this group
    existing_like = RestaurantLike.query.filter_by(
        user_id=user.id,
        restaurant_id=restaurant.id,
        group_id=group_id
    ).first()
    
    if existing_like:
        existing_like.liked = False
    else:
        like = RestaurantLike(
            user_id=user.id,
            restaurant_id=restaurant.id,
            group_id=group_id,
            liked=False
        )
        db.session.add(like)
    
    db.session.commit()
    
    return jsonify({'message': 'Restaurant disliked successfully'})

# Group API endpoints
@api.route('/groups', methods=['GET'])
@jwt_required()
def get_groups():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    owned_groups = user.owned_groups
    member_groups = user.groups.all()
    
    result = []
    
    # Add owned groups
    for group in owned_groups:
        result.append({
            'id': group.id,
            'name': group.name,
            'owner_id': group.owner_id,
            'share_code': group.share_code,
            'is_owner': True,
            'member_count': group.members.count()
        })
    
    # Add groups where user is a member but not owner
    for group in member_groups:
        if group.owner_id != user.id:
            result.append({
                'id': group.id,
                'name': group.name,
                'owner_id': group.owner_id,
                'share_code': group.share_code,
                'is_owner': False,
                'member_count': group.members.count()
            })
    
    return jsonify(result)

@api.route('/groups', methods=['POST'])
@jwt_required()
def create_group():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'message': 'Group name is required'}), 400
    
    import uuid
    share_code = str(uuid.uuid4())[:8]
    
    group = Group(name=data['name'], owner_id=user.id, share_code=share_code)
    group.members.append(user)
    
    db.session.add(group)
    db.session.commit()
    
    return jsonify({
        'id': group.id,
        'name': group.name,
        'owner_id': group.owner_id,
        'share_code': group.share_code
    }), 201

@api.route('/groups/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    group = Group.query.get_or_404(group_id)
    
    # Check if user is in the group
    if user not in group.members and user != group.owner:
        return jsonify({'message': 'You are not a member of this group'}), 403
    
    members = []
    for member in group.members:
        members.append({
            'id': member.id,
            'username': member.username
        })
    
    result = {
        'id': group.id,
        'name': group.name,
        'owner_id': group.owner_id,
        'share_code': group.share_code,
        'is_owner': group.owner_id == user.id,
        'members': members
    }
    
    return jsonify(result)

@api.route('/groups/join/<share_code>', methods=['POST'])
@jwt_required()
def join_group(share_code):
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    group = Group.query.filter_by(share_code=share_code).first()
    
    if not group:
        return jsonify({'message': 'Invalid group code'}), 404
    
    if user in group.members:
        return jsonify({'message': 'You are already a member of this group'}), 400
    
    group.members.append(user)
    db.session.commit()
    
    return jsonify({'message': 'Joined group successfully', 'group_id': group.id})

# Matches API endpoint
@api.route('/groups/<int:group_id>/matches', methods=['GET'])
@jwt_required()
def get_group_matches(group_id):
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    group = Group.query.get_or_404(group_id)
    
    # Check if user is in the group
    if user not in group.members and user != group.owner:
        return jsonify({'message': 'You are not a member of this group'}), 403
    
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
            matched_restaurants.append({
                'id': restaurant.id,
                'name': restaurant.name,
                'location': restaurant.location,
                'rating': restaurant.rating,
                'cuisine_type': restaurant.cuisine_type,
                'price_range': restaurant.price_range,
                'is_vegetarian': restaurant.is_vegetarian,
                'distance': restaurant.distance,
                'image_url': restaurant.image_url
            })
    
    return jsonify(matched_restaurants)