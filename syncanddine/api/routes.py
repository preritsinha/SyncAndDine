from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from syncanddine import db
from syncanddine.models.user import User, Group
from syncanddine.models.restaurant import RestaurantLike
from syncanddine.restaurants.places_service import GooglePlacesService

api = Blueprint('api', __name__)

# Restaurant API endpoints
@api.route('/restaurants', methods=['GET'])
@jwt_required()
def get_restaurants():
    """Get restaurants from Google Places API"""
    lat = request.args.get('lat', 40.7128, type=float)
    lon = request.args.get('lon', -74.0060, type=float)
    
    places_service = GooglePlacesService()
    restaurants = places_service.search_restaurants(lat, lon)
    
    return jsonify(restaurants)

@api.route('/restaurants/<restaurant_id>/like', methods=['POST'])
@jwt_required()
def like_restaurant(restaurant_id):
    """Like a restaurant using Google Place ID"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    data = request.get_json() or {}
    group_id = data.get('group_id')
    
    existing_like = RestaurantLike.query.filter_by(
        user_id=user.id,
        restaurant_google_id=restaurant_id,
        group_id=group_id
    ).first()
    
    if existing_like:
        existing_like.liked = True
    else:
        like = RestaurantLike(
            user_id=user.id,
            restaurant_google_id=restaurant_id,
            group_id=group_id,
            liked=True
        )
        db.session.add(like)
    
    db.session.commit()
    return jsonify({'message': 'Restaurant liked successfully'})

# Group API endpoints
@api.route('/groups', methods=['GET'])
@jwt_required()
def get_groups():
    """Get user's groups"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    result = []
    for group in user.owned_groups + list(user.groups):
        result.append({
            'id': group.id,
            'name': group.name,
            'owner_id': group.owner_id,
            'share_code': group.share_code,
            'is_owner': group.owner_id == user.id
        })
    
    return jsonify(result)