from flask import Blueprint, jsonify, request
import requests
import os
from functools import lru_cache

location_api = Blueprint('location_api', __name__)

@location_api.route('/api/cities')
def get_cities():
    """Get cities from predefined list (Google Places doesn't provide city lists)"""
    cities = [
        'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 
        'Pune', 'Ahmedabad', 'Jaipur', 'Surat', 'Lucknow', 'Kanpur', 
        'Nagpur', 'Indore', 'Bhopal', 'Visakhapatnam', 'Patna', 'Vadodara',
        'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik', 'Faridabad', 'Meerut'
    ]
    return jsonify(sorted(cities))

@location_api.route('/api/areas')
def get_areas():
    """Get areas based on city using Google Places autocomplete"""
    city = request.args.get('city')
    if not city:
        return jsonify([])
    
    try:
        # Search for popular areas in the city
        params = {
            'query': f'popular areas neighborhoods {city} India',
            'key': os.getenv('GOOGLE_PLACES_API_KEY')
        }
        
        response = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json', params=params)
        if response.status_code == 200:
            data = response.json()
            areas = []
            for place in data.get('results', []):
                name = place.get('name', '')
                # Filter out restaurants and keep only area names
                if not any(word in name.lower() for word in ['restaurant', 'hotel', 'cafe', 'mall']):
                    if name and name not in areas:
                        areas.append(name)
            return jsonify(areas[:15])
    except Exception as e:
        print(f"Error fetching areas: {e}")
    
    return jsonify([])