"""
Location Helper for Real-Time Travel Guide
Uses Google Places API (free tier) and geolocation
"""

import requests
import os
from datetime import datetime, timedelta
from cachetools import TTLCache
from dotenv import load_dotenv
from geopy.distance import geodesic

load_dotenv()

# Google Places API Key (Free tier: 40,000 requests/month)
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")

# Cache for 30 minutes to save API calls
places_cache = TTLCache(maxsize=500, ttl=1800)  # 30 min cache
reviews_cache = TTLCache(maxsize=200, ttl=3600)  # 1 hour cache

def reverse_geocode(lat, lon):
    """
    Enhanced reverse geocoding for street-level accuracy
    Returns detailed address information with high precision
    """
    if not GOOGLE_PLACES_API_KEY:
        return {
            "area": "your current location",
            "city": "your city", 
            "street": "",
            "state": "",
            "country": "India",
            "formatted_address": "Location detection unavailable"
        }
    
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{lat},{lon}",
            "result_type": "street_address|premise|subpremise|neighborhood|sublocality_level_1|sublocality|locality",
            "key": GOOGLE_PLACES_API_KEY
        }
        
        print(f"[DEBUG] Reverse geocoding coordinates: {lat}, {lon}")
        print(f"[DEBUG] API URL: {url}")
        print(f"[DEBUG] API Params: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "OK" and data.get("results"):
                print(f"[DEBUG] Google API returned {len(data['results'])} results")
                print(f"[DEBUG] API Status: {data.get('status')}")
                
                # Use the most accurate result (first one)
                result = data["results"][0]
                
                print(f"[DEBUG] Raw result formatted_address: {result.get('formatted_address', '')}")
                print(f"[DEBUG] Address components: {result.get('address_components', [])}")
                print(f"[DEBUG] Place types: {result.get('types', [])}")
                
                location_info = {
                    "formatted_address": result.get("formatted_address", ""),
                    "street": "",
                    "area": "",
                    "city": "",
                    "state": "",
                    "country": "India",
                    "accuracy_type": result.get("geometry", {}).get("location_type", "APPROXIMATE"),
                    "place_types": result.get("types", [])
                }
                
                # Enhanced parsing with priority order for better accuracy
                components = result.get("address_components", [])
                
                # Parse all components with detailed hierarchy
                for component in components:
                    types = component.get("types", [])
                    name = component.get("long_name", "")
                    short_name = component.get("short_name", "")
                    
                    print(f"[DEBUG] Component: {name} | Types: {types}")
                    
                    # Street/road level (highest precision) - Enhanced detection
                    if any(t in types for t in ["route", "street_address"]) and not location_info["street"]:
                        location_info["street"] = name
                        print(f"[DEBUG] Found street: {name}")
                    
                    # Premise level (building/complex name)
                    elif any(t in types for t in ["premise", "establishment", "subpremise"]) and not location_info["street"]:
                        location_info["street"] = name
                        print(f"[DEBUG] Found premise/building: {name}")
                    
                    # Sublocality levels (area/neighborhood) - Enhanced detection
                    elif "sublocality_level_1" in types and not location_info["area"]:
                        location_info["area"] = name
                        print(f"[DEBUG] Found area (sublocality_1): {name}")
                    elif "sublocality" in types and not location_info["area"]:
                        location_info["area"] = name
                        print(f"[DEBUG] Found area (sublocality): {name}")
                    elif "neighborhood" in types and not location_info["area"]:
                        location_info["area"] = name
                        print(f"[DEBUG] Found area (neighborhood): {name}")
                    elif "sublocality_level_2" in types and not location_info["area"]:
                        location_info["area"] = name
                        print(f"[DEBUG] Found area (sublocality_2): {name}")
                    elif "political" in types and "sublocality" in types and not location_info["area"]:
                        location_info["area"] = name
                        print(f"[DEBUG] Found area (political sublocality): {name}")
                    
                    # City level
                    elif "locality" in types and not location_info["city"]:
                        location_info["city"] = name
                        print(f"[DEBUG] Found city (locality): {name}")
                    elif "administrative_area_level_2" in types and not location_info["city"]:
                        location_info["city"] = name
                        print(f"[DEBUG] Found city (admin_2): {name}")
                    
                    # State level
                    elif "administrative_area_level_1" in types:
                        location_info["state"] = name
                        print(f"[DEBUG] Found state: {name}")
                    
                    # Country
                    elif "country" in types:
                        location_info["country"] = name
                        print(f"[DEBUG] Found country: {name}")
                
                # Fallback if area not found - use premise or point of interest
                if not location_info["area"]:
                    for component in components:
                        types = component.get("types", [])
                        if "premise" in types or "establishment" in types or "point_of_interest" in types:
                            location_info["area"] = component.get("long_name", "")
                            break
                
                # Create a precise location string
                location_parts = []
                if location_info["street"]:
                    location_parts.append(location_info["street"])
                if location_info["area"]:
                    location_parts.append(location_info["area"])
                if location_info["city"]:
                    location_parts.append(location_info["city"])
                
                precise_location = ", ".join(location_parts) if location_parts else "Current Location"
                location_info["precise_location"] = precise_location
                
                print(f"[HIGH-PRECISION GEOCODE] Street: {location_info['street']}, Area: {location_info['area']}, City: {location_info['city']}")
                print(f"[ACCURACY TYPE] {location_info['accuracy_type']}")
                print(f"[PRECISE LOCATION] {precise_location}")
                
                return location_info
        
        # Fallback with less precise requirements
        params_fallback = {
            "latlng": f"{lat},{lon}",
            "key": GOOGLE_PLACES_API_KEY
        }
        
        response_fallback = requests.get(url, params=params_fallback, timeout=10)
        
        if response_fallback.status_code == 200:
            data_fallback = response_fallback.json()
            if data_fallback.get("status") == "OK" and data_fallback.get("results"):
                result = data_fallback["results"][0]
                return {
                    "area": "approximate location",
                    "city": "nearby area",
                    "street": "",
                    "state": "",
                    "country": "India",
                    "formatted_address": result.get("formatted_address", ""),
                    "precise_location": "Approximate Area",
                    "accuracy_type": "APPROXIMATE"
                }
        
        return {
            "area": "location detection failed",
            "city": "unknown area",
            "street": "",
            "state": "",
            "country": "India",
            "formatted_address": "Unable to determine precise location",
            "precise_location": "Location Unknown",
            "accuracy_type": "FAILED"
        }
            
    except Exception as e:
        print(f"[EXCEPTION] Enhanced reverse geocoding error: {e}")
        return {
            "area": "location detection error",
            "city": "unknown area", 
            "street": "",
            "state": "",
            "country": "India",
            "formatted_address": f"Error detecting location: {str(e)}",
            "precise_location": "Location Error",
            "accuracy_type": "ERROR"
        }

def get_nearby_places(lat, lon, place_type="restaurant", radius=5000, keyword=""):
    """
    Get nearby places using Google Places API (free tier)
    Enhanced to support comprehensive place types for real local guide experience
    
    Args:
        lat: Latitude
        lon: Longitude
        place_type: Type of place (restaurant, hotel, cafe, tourist_attraction, pharmacy, bank, etc.)
        radius: Search radius in meters (default 5000m = 5km)
        keyword: Additional search keyword
    
    Returns:
        List of places with details (filtered to 5km max)
    """
    cache_key = f"{lat},{lon},{place_type},{radius},{keyword}"
    
    # Check cache first
    if cache_key in places_cache:
        print(f"[CACHE HIT] Returning cached results for {place_type}")
        return places_cache[cache_key]
    
    # If no API key, return dummy data
    if not GOOGLE_PLACES_API_KEY:
        print("[WARNING] No Google Places API key found. Using dummy data.")
        return get_dummy_places(place_type, lat, lon)
    
    try:
        # Map our custom place types to Google Places API types
        google_place_type_mapping = {
            "pharmacy": "pharmacy",
            "medical_store": "pharmacy", 
            "doctor": "doctor",
            "hospital": "hospital",
            "clinic": "doctor",
            "bank": "bank",
            "atm": "atm",
            "police": "police",
            "post_office": "post_office",
            "government": "local_government_office",
            "transit_station": "transit_station",
            "restaurant": "restaurant",
            "cafe": "cafe",
            "lodging": "lodging",
            "tourist_attraction": "tourist_attraction",
            "shopping_mall": "shopping_mall"
        }
        
        # Get the correct Google API type
        google_type = google_place_type_mapping.get(place_type, place_type)
        
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        
        # Enforce maximum 3km radius as requested by user
        effective_radius = min(radius, 3000)  # Maximum 3000 meters = 3km
        
        params = {
            "location": f"{lat},{lon}",
            "radius": effective_radius,
            "type": google_type,
            "key": GOOGLE_PLACES_API_KEY
        }
        
        print(f"[API REQUEST] Searching within {effective_radius}m radius for {place_type}")
        
        if keyword:
            params["keyword"] = keyword
            
        # For some types, use keyword search instead of type for better results
        if place_type in ["pharmacy", "medical_store"]:
            params["keyword"] = "medical store pharmacy chemist"
            if "type" in params:
                del params["type"]  # Remove type, use keyword only
        elif place_type == "doctor":
            params["keyword"] = "doctor clinic medical center"
            params["type"] = "doctor"
        elif place_type == "government":
            params["keyword"] = "government office municipality"
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "OK":
                places = []
                for place in data.get("results", [])[:10]:  # Limit to 10 results
                    place_data = {
                        "name": place.get("name", "Unknown"),
                        "place_id": place.get("place_id", ""),
                        "address": place.get("vicinity", "Address not available"),
                        "rating": place.get("rating", 0),
                        "user_ratings_total": place.get("user_ratings_total", 0),
                        "price_level": place.get("price_level", None),  # 0-4 scale
                        "types": place.get("types", []),
                        "location": place.get("geometry", {}).get("location", {}),
                        "open_now": place.get("opening_hours", {}).get("open_now", None),
                        "photo_reference": place.get("photos", [{}])[0].get("photo_reference", "") if place.get("photos") else ""
                    }
                    
                    # Calculate precise distance using geodesic calculation
                    place_lat = place_data["location"].get("lat", lat)
                    place_lon = place_data["location"].get("lng", lon)
                    distance = geodesic((lat, lon), (place_lat, place_lon)).kilometers
                    place_data["distance_km"] = round(distance, 3)  # More precise to 3 decimal places
                    place_data["distance_meters"] = round(distance * 1000)
                    
                    # STRICT 3KM LIMIT - Only include places within exactly 3km as requested
                    if distance <= 3.0:
                        places.append(place_data)
                        print(f"[DISTANCE CHECK] {place_data['name']}: {distance:.3f}km ✓ (within 3km)")
                    else:
                        print(f"[DISTANCE CHECK] {place_data['name']}: {distance:.3f}km ✗ (excluded - beyond 3km)")
                
                print(f"[DISTANCE FILTER] Total places within 3km: {len(places)} out of {len(data.get('results', []))}")
                
                # Sort by rating and distance
                places.sort(key=lambda x: (-x["rating"], x["distance_km"]))
                
                # Cache the results
                places_cache[cache_key] = places
                
                print(f"[API SUCCESS] Found {len(places)} {place_type}s")
                return places
            else:
                print(f"[API ERROR] Status: {data.get('status')}, Error: {data.get('error_message', 'Unknown')}")
                return get_dummy_places(place_type, lat, lon)
        else:
            print(f"[HTTP ERROR] Status code: {response.status_code}")
            return get_dummy_places(place_type, lat, lon)
            
    except Exception as e:
        print(f"[EXCEPTION] Error fetching places: {e}")
        return get_dummy_places(place_type, lat, lon)

def get_place_details(place_id):
    """
    Get detailed information about a place
    
    Args:
        place_id: Google Place ID
    
    Returns:
        Dict with place details including reviews, photos, contact info
    """
    cache_key = f"details_{place_id}"
    
    if cache_key in reviews_cache:
        print(f"[CACHE HIT] Returning cached details for place {place_id}")
        return reviews_cache[cache_key]
    
    if not GOOGLE_PLACES_API_KEY:
        return {"error": "No API key"}
    
    try:
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,rating,reviews,formatted_phone_number,website,opening_hours,price_level,photos",
            "key": GOOGLE_PLACES_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "OK":
                details = data.get("result", {})
                
                # Cache the results
                reviews_cache[cache_key] = details
                
                return details
        
        return {"error": "Failed to fetch details"}
            
    except Exception as e:
        print(f"[EXCEPTION] Error fetching place details: {e}")
        return {"error": str(e)}

def get_photo_url(photo_reference, max_width=400):
    """
    Get photo URL from photo reference
    
    Args:
        photo_reference: Photo reference from Places API
        max_width: Maximum width of photo
    
    Returns:
        Photo URL
    """
    if not photo_reference or not GOOGLE_PLACES_API_KEY:
        return f"https://source.unsplash.com/400x300/?hotel,restaurant"
    
    return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photo_reference={photo_reference}&key={GOOGLE_PLACES_API_KEY}"

def compare_places(places, criteria="rating"):
    """
    Compare places based on different criteria
    
    Args:
        places: List of places
        criteria: Comparison criteria (rating, price, distance)
    
    Returns:
        Sorted list with comparison highlights
    """
    if criteria == "rating":
        places.sort(key=lambda x: (-x["rating"], -x["user_ratings_total"]))
    elif criteria == "price":
        # Sort by price level (lower first), handle None values
        places.sort(key=lambda x: (x["price_level"] if x["price_level"] is not None else 999, -x["rating"]))
    elif criteria == "distance":
        places.sort(key=lambda x: x["distance_km"])
    else:
        # Default: best overall (rating + distance)
        places.sort(key=lambda x: (-x["rating"] * 2 + x["distance_km"]))
    
    return places

def get_dummy_places(place_type, lat, lon):
    """
    Generate dummy places when API is not available
    Enhanced to support comprehensive place types for real local guide experience
    """
    city_name = "your location"
    
    # MEDICAL & HEALTH SERVICES
    if place_type in ["pharmacy", "medical_store"]:
        return [
            {
                "name": "Apollo Pharmacy",
                "place_id": "dummy_med_1",
                "address": f"Main Road, {city_name}",
                "rating": 4.3,
                "user_ratings_total": 850,
                "price_level": 2,
                "types": ["pharmacy", "health"],
                "location": {"lat": lat + 0.001, "lng": lon + 0.001},
                "open_now": True,
                "distance_km": 0.3,
                "photo_reference": ""
            },
            {
                "name": "MedPlus Health Services",
                "place_id": "dummy_med_2",
                "address": f"Market Road, {city_name}",
                "rating": 4.1,
                "user_ratings_total": 650,
                "price_level": 2,
                "types": ["pharmacy", "health"],
                "location": {"lat": lat + 0.002, "lng": lon - 0.001},
                "open_now": True,
                "distance_km": 0.6,
                "photo_reference": ""
            },
            {
                "name": "Local Medical Store",
                "place_id": "dummy_med_3",
                "address": f"Near {city_name} hospital",
                "rating": 4.0,
                "user_ratings_total": 420,
                "price_level": 1,
                "types": ["pharmacy", "health"],
                "location": {"lat": lat - 0.001, "lng": lon + 0.002},
                "open_now": True,
                "distance_km": 0.8,
                "photo_reference": ""
            }
        ]
    
    elif place_type == "hospital":
        return [
            {
                "name": f"{city_name} General Hospital",
                "place_id": "dummy_hosp_1",
                "address": f"Hospital Road, {city_name}",
                "rating": 4.2,
                "user_ratings_total": 1200,
                "price_level": None,
                "types": ["hospital", "health"],
                "location": {"lat": lat + 0.003, "lng": lon + 0.003},
                "open_now": True,
                "distance_km": 1.5,
                "photo_reference": ""
            },
            {
                "name": "City Medical Center",
                "place_id": "dummy_hosp_2",
                "address": f"Central {city_name}",
                "rating": 4.5,
                "user_ratings_total": 1800,
                "price_level": 3,
                "types": ["hospital", "health"],
                "location": {"lat": lat - 0.002, "lng": lon - 0.002},
                "open_now": True,
                "distance_km": 2.2,
                "photo_reference": ""
            }
        ]
    
    elif place_type == "doctor":
        return [
            {
                "name": "Dr. Sharma's Clinic",
                "place_id": "dummy_doc_1",
                "address": f"Medical Complex, {city_name}",
                "rating": 4.4,
                "user_ratings_total": 320,
                "price_level": 2,
                "types": ["doctor", "health"],
                "location": {"lat": lat + 0.0015, "lng": lon + 0.0015},
                "open_now": True,
                "distance_km": 0.4,
                "photo_reference": ""
            },
            {
                "name": "City Health Clinic",
                "place_id": "dummy_doc_2",
                "address": f"Main Street, {city_name}",
                "rating": 4.2,
                "user_ratings_total": 180,
                "price_level": 2,
                "types": ["doctor", "health"],
                "location": {"lat": lat - 0.001, "lng": lon + 0.001},
                "open_now": False,
                "distance_km": 0.7,
                "photo_reference": ""
            }
        ]
    
    # FINANCIAL SERVICES
    elif place_type == "bank":
        return [
            {
                "name": "State Bank of India",
                "place_id": "dummy_bank_1",
                "address": f"Banking Street, {city_name}",
                "rating": 3.8,
                "user_ratings_total": 450,
                "price_level": None,
                "types": ["bank", "finance"],
                "location": {"lat": lat + 0.002, "lng": lon + 0.001},
                "open_now": True,
                "distance_km": 0.9,
                "photo_reference": ""
            },
            {
                "name": "HDFC Bank",
                "place_id": "dummy_bank_2",
                "address": f"Commercial Area, {city_name}",
                "rating": 4.0,
                "user_ratings_total": 680,
                "price_level": None,
                "types": ["bank", "finance"],
                "location": {"lat": lat - 0.001, "lng": lon - 0.001},
                "open_now": True,
                "distance_km": 1.1,
                "photo_reference": ""
            }
        ]
    
    elif place_type == "atm":
        return [
            {
                "name": "SBI ATM",
                "place_id": "dummy_atm_1",
                "address": f"Near Bus Stand, {city_name}",
                "rating": 3.5,
                "user_ratings_total": 120,
                "price_level": None,
                "types": ["atm", "finance"],
                "location": {"lat": lat + 0.0005, "lng": lon + 0.0005},
                "open_now": True,
                "distance_km": 0.2,
                "photo_reference": ""
            },
            {
                "name": "HDFC ATM",
                "place_id": "dummy_atm_2",
                "address": f"Market Square, {city_name}",
                "rating": 3.7,
                "user_ratings_total": 95,
                "price_level": None,
                "types": ["atm", "finance"],
                "location": {"lat": lat + 0.001, "lng": lon - 0.001},
                "open_now": True,
                "distance_km": 0.4,
                "photo_reference": ""
            }
        ]
    
    # GOVERNMENT & OFFICIAL
    elif place_type == "police":
        return [
            {
                "name": f"{city_name} Police Station",
                "place_id": "dummy_police_1",
                "address": f"Police Line, {city_name}",
                "rating": 3.2,
                "user_ratings_total": 85,
                "price_level": None,
                "types": ["police", "government"],
                "location": {"lat": lat + 0.002, "lng": lon + 0.002},
                "open_now": True,
                "distance_km": 1.0,
                "photo_reference": ""
            }
        ]
    
    elif place_type == "post_office":
        return [
            {
                "name": f"{city_name} Head Post Office",
                "place_id": "dummy_post_1",
                "address": f"GPO Road, {city_name}",
                "rating": 3.5,
                "user_ratings_total": 150,
                "price_level": None,
                "types": ["post_office", "government"],
                "location": {"lat": lat + 0.0015, "lng": lon + 0.0015},
                "open_now": True,
                "distance_km": 0.6,
                "photo_reference": ""
            }
        ]
    
    # ACCOMMODATION
    elif place_type == "hotel" or place_type == "lodging":
        return [
            {
                "name": "Grand Plaza Hotel",
                "place_id": "dummy_1",
                "address": f"Near {city_name} center, Main Street",
                "rating": 4.5,
                "user_ratings_total": 1250,
                "price_level": 3,
                "types": ["hotel", "lodging"],
                "location": {"lat": lat + 0.001, "lng": lon + 0.001},
                "open_now": True,
                "distance_km": 0.5,
                "photo_reference": ""
            },
            {
                "name": "Budget Inn",
                "place_id": "dummy_2",
                "address": f"Near {city_name} railway station",
                "rating": 4.0,
                "user_ratings_total": 850,
                "price_level": 1,
                "types": ["hotel", "lodging"],
                "location": {"lat": lat + 0.002, "lng": lon - 0.001},
                "open_now": True,
                "distance_km": 0.8,
                "photo_reference": ""
            },
            {
                "name": "Luxury Suites",
                "place_id": "dummy_3",
                "address": f"{city_name} downtown area",
                "rating": 4.7,
                "user_ratings_total": 2100,
                "price_level": 4,
                "types": ["hotel", "lodging"],
                "location": {"lat": lat - 0.001, "lng": lon + 0.002},
                "open_now": True,
                "distance_km": 1.2,
                "photo_reference": ""
            }
        ]
    
    elif place_type == "restaurant":
        return [
            {
                "name": "Spice Garden Restaurant",
                "place_id": "dummy_4",
                "address": f"{city_name} food street",
                "rating": 4.3,
                "user_ratings_total": 980,
                "price_level": 2,
                "types": ["restaurant", "food"],
                "location": {"lat": lat + 0.0015, "lng": lon + 0.0015},
                "open_now": True,
                "distance_km": 0.3,
                "photo_reference": ""
            },
            {
                "name": "Quick Bites Cafe",
                "place_id": "dummy_5",
                "address": f"Near {city_name} market",
                "rating": 4.1,
                "user_ratings_total": 650,
                "price_level": 1,
                "types": ["restaurant", "cafe"],
                "location": {"lat": lat - 0.001, "lng": lon + 0.001},
                "open_now": True,
                "distance_km": 0.4,
                "photo_reference": ""
            },
            {
                "name": "Fine Dining Palace",
                "place_id": "dummy_6",
                "address": f"{city_name} luxury zone",
                "rating": 4.6,
                "user_ratings_total": 1500,
                "price_level": 4,
                "types": ["restaurant", "fine_dining"],
                "location": {"lat": lat + 0.002, "lng": lon - 0.002},
                "open_now": False,
                "distance_km": 1.0,
                "photo_reference": ""
            }
        ]
    
    elif place_type == "cafe":
        return [
            {
                "name": "Coffee Corner",
                "place_id": "dummy_7",
                "address": f"{city_name} main road",
                "rating": 4.4,
                "user_ratings_total": 750,
                "price_level": 2,
                "types": ["cafe", "coffee"],
                "location": {"lat": lat + 0.0005, "lng": lon + 0.0005},
                "open_now": True,
                "distance_km": 0.2,
                "photo_reference": ""
            },
            {
                "name": "Artisan Brew",
                "place_id": "dummy_8",
                "address": f"{city_name} art district",
                "rating": 4.5,
                "user_ratings_total": 890,
                "price_level": 3,
                "types": ["cafe", "bakery"],
                "location": {"lat": lat - 0.0008, "lng": lon + 0.0012},
                "open_now": True,
                "distance_km": 0.6,
                "photo_reference": ""
            }
        ]
    
    else:  # tourist_attraction
        return [
            {
                "name": f"{city_name} Fort",
                "place_id": "dummy_9",
                "address": f"Historic {city_name}",
                "rating": 4.6,
                "user_ratings_total": 3200,
                "price_level": 0,
                "types": ["tourist_attraction", "point_of_interest"],
                "location": {"lat": lat + 0.003, "lng": lon + 0.003},
                "open_now": True,
                "distance_km": 2.5,
                "photo_reference": ""
            },
            {
                "name": f"{city_name} Museum",
                "place_id": "dummy_10",
                "address": f"{city_name} cultural zone",
                "rating": 4.4,
                "user_ratings_total": 1800,
                "price_level": 1,
                "types": ["museum", "tourist_attraction"],
                "location": {"lat": lat - 0.002, "lng": lon - 0.002},
                "open_now": True,
                "distance_km": 1.8,
                "photo_reference": ""
            }
        ]

def format_price_level(price_level):
    """Convert price level to rupee symbols"""
    if price_level is None:
        return "Price not available"
    
    price_map = {
        0: "Free",
        1: "₹ (Budget)",
        2: "₹₹ (Moderate)",
        3: "₹₹₹ (Expensive)",
        4: "₹₹₹₹ (Very Expensive)"
    }
    
    return price_map.get(price_level, "Price not available")

