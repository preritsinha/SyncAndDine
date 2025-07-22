"""
Google Places API Service

This service provides a clean interface to Google Places API for restaurant discovery.
It handles API authentication, request formatting, and response parsing.

Features:
- Location-based restaurant search
- Restaurant detail retrieval
- Automatic data formatting for frontend consumption
- Error handling and fallback responses

Author: SyncAndDine Team
Version: 2.0 - Production Ready
"""

import requests
import os
from typing import List, Dict, Optional

class GooglePlacesService:
    """
    Google Places API integration service
    
    Provides methods to search for restaurants and retrieve detailed information
    using Google's Places API with proper error handling and data formatting.
    """
    
    def __init__(self):
        """Initialize the service with API credentials and base configuration"""
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        
        if not self.api_key:
            raise ValueError("Google Places API key not found in environment variables")
    
    def search_restaurants(self, lat: float = None, lon: float = None, city: str = None, radius: int = 10000) -> List[Dict]:
        """Search restaurants using Google Places API with pagination"""
        all_restaurants = []
        next_page_token = None
        
        for page in range(10):  # Get up to 200 results (10 pages × 20 results)
            if city:
                params = {
                    'query': f'restaurants in {city}',
                    'type': 'restaurant',
                    'key': self.api_key
                }
                endpoint = f"{self.base_url}/textsearch/json"
            else:
                params = {
                    'location': f"{lat},{lon}",
                    'radius': radius,
                    'type': 'restaurant',
                    'key': self.api_key
                }
                endpoint = f"{self.base_url}/nearbysearch/json"
            
            if next_page_token:
                params['pagetoken'] = next_page_token
            
            try:
                response = requests.get(endpoint, params=params)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    all_restaurants.extend([self._format_restaurant(r) for r in results])
                    
                    next_page_token = data.get('next_page_token')
                    if not next_page_token:
                        break
                    
                    # Google requires a short delay between paginated requests
                    import time
                    time.sleep(2)
                else:
                    break
            except Exception as e:
                print(f"Google Places API error: {e}")
                break
        
        return all_restaurants
    
    def _format_restaurant(self, place: Dict) -> Dict:
        """Format restaurant data for our database"""
        geometry = place.get('geometry', {}).get('location', {})
        return {
            'google_place_id': place.get('place_id'),
            'name': place.get('name', ''),
            'location': place.get('vicinity', ''),
            'latitude': float(geometry.get('lat', 0)),
            'longitude': float(geometry.get('lng', 0)),
            'rating': float(place.get('rating', 0)),
            'cuisine_type': self._extract_cuisine(place.get('types', [])),
            'price_range': self._get_price_range(place.get('price_level', 2)),
            'is_vegetarian': False,
            'image_url': self._get_photo_url(place.get('photos', [])),
        }
    
    def _extract_cuisine(self, types: List[str]) -> str:
        # Dynamic cuisine extraction from Google Places types
        cuisine_keywords = {
            'chinese': 'Chinese', 'italian': 'Italian', 'mexican': 'Mexican',
            'indian': 'Indian', 'japanese': 'Japanese', 'thai': 'Thai',
            'korean': 'Korean', 'vietnamese': 'Vietnamese', 'american': 'American',
            'french': 'French', 'mediterranean': 'Mediterranean', 'pizza': 'Pizza',
            'bakery': 'Bakery', 'cafe': 'Cafe', 'fast_food': 'Fast Food',
            'seafood': 'Seafood', 'vegetarian': 'Vegetarian', 'barbecue': 'BBQ'
        }
        
        for place_type in types:
            for keyword, cuisine in cuisine_keywords.items():
                if keyword in place_type.lower():
                    return cuisine
        
        return 'Restaurant'
    
    def _get_price_range(self, price_level: int) -> str:
        # Dynamic price range based on Google's 0-4 scale
        if price_level == 0: return 'Free'
        elif price_level == 1: return '$'
        elif price_level == 2: return '$$'
        elif price_level == 3: return '$$$'
        elif price_level == 4: return '$$$$'
        else: return '$$'  # Default for unknown
    
    def _get_photo_url(self, photos: List[Dict]) -> str:
        if photos and self.api_key:
            photo_ref = photos[0].get('photo_reference')
            return f"{self.base_url}/photo?maxwidth=400&photoreference={photo_ref}&key={self.api_key}"
        return ''
    
    def get_restaurant_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed restaurant information with photos"""
        params = {
            'place_id': place_id,
            'fields': 'name,rating,formatted_phone_number,website,price_level,photos,formatted_address',
            'key': self.api_key
        }
        
        try:
            response = requests.get(f"{self.base_url}/details/json", params=params)
            if response.status_code == 200:
                result = response.json().get('result', {})
                photos = result.get('photos', [])
                photo_urls = []
                
                # Get up to 10 photos
                for photo in photos[:10]:
                    photo_ref = photo.get('photo_reference')
                    if photo_ref:
                        photo_urls.append(f"{self.base_url}/photo?maxwidth=800&photoreference={photo_ref}&key={self.api_key}")
                
                return {
                    'google_place_id': place_id,
                    'name': result.get('name', ''),
                    'location': result.get('formatted_address', ''),
                    'rating': float(result.get('rating', 0)),
                    'phone': result.get('formatted_phone_number', ''),
                    'website': result.get('website', ''),
                    'price_range': self._get_price_range(result.get('price_level', 2)),
                    'image_url': photo_urls[0] if photo_urls else '',
                    'photos': photo_urls
                }
        except Exception as e:
            print(f"Google Places API error: {e}")
        
        return None