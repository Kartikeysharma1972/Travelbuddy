# 🗺️ Real-Time Travel Guide - Setup & Usage Guide

## Overview

Your TravelBuddy now includes a **Real-Time Local Guide** feature that acts like a virtual local assistant! It uses your current location to find and compare nearby hotels, restaurants, cafes, and attractions - just like hiring a local guide.

---

## 🎯 Features Implemented

### ✅ Core Features
1. **Browser Geolocation** - Detects user's real-time location
2. **Google Places API Integration** - Finds nearby places (free tier: 40,000 requests/month)
3. **Smart Comparison** - Compares places by rating, price, and distance
4. **Caching System** - Saves API calls (30 min cache for places, 1 hour for reviews)
5. **Multi-language Support** - Works with Hindi/Hinglish commands
6. **Booking Integration** - Direct links to Booking.com, MakeMyTrip, Zomato, etc.
7. **Open/Closed Status** - Shows if places are currently open
8. **Distance Calculation** - Shows exact distance from your location

### 🔍 What You Can Search
- 🏨 **Hotels & Accommodations**
- 🍽️ **Restaurants & Food**
- ☕ **Cafes & Coffee Shops**
- 🎯 **Tourist Attractions**
- 🛍️ **Shopping Malls & Markets**

---

## 📋 Prerequisites

### Required APIs (All FREE for local testing!)

#### 1. **Google Places API** (Recommended but Optional)
- **Free Tier**: 40,000 requests/month
- **Cost**: $0 for first 40K requests
- **How to get**:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/)
  2. Create a new project
  3. Enable "Places API" and "Geocoding API"
  4. Go to "Credentials" → Create API Key
  5. Restrict the key (optional but recommended):
     - API restrictions: Select "Places API" and "Geocoding API"
     - HTTP referrers: `localhost:*` for local testing

#### 2. **Groq API** (Already configured)
- **Free Tier**: Unlimited for now (very fast!)
- **Status**: ✅ You already have this

#### 3. **Gemini API** (Already configured)
- **Free Tier**: 60 requests/minute
- **Status**: ✅ You already have this

---

## 🚀 Installation Steps

### Step 1: Install New Dependencies

```bash
pip install cachetools geopy
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Add to your `.env` file:

```env
# Existing keys (keep as is)
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
SERPAPI_API_KEY=your_serpapi_key_here

# NEW: Add Google Places API Key (optional but recommended)
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here
```

**Note**: If you don't add `GOOGLE_PLACES_API_KEY`, the system will use **dummy data** for testing. This is perfect for development!

### Step 3: Run the Application

```bash
python app.py
```

The app will start at `http://127.0.0.1:5000`

---

## 📱 How to Use Real-Time Guide

### Activating Real-Time Guide

**Method 1**: Direct activation
```
User: "Enable real-time guide"
User: "I need a local guide"
User: "Show me nearby places"
```

**Method 2**: Hindi/Hinglish (more natural!)
```
User: "Mai pahuch gaya Jaipur"
User: "Yaha hu location detect karo"
User: "Nearby hotel dikhao"
```

### Searching for Places

Once activated, you can search for:

#### Hotels
```
"Show hotels nearby"
"Hotel dikhao paas mein"
"Where to stay here"
"Rukne ke liye jagah"
```

#### Restaurants
```
"Food nearby"
"Khane ka kya scene hai"
"Restaurants around me"
"Lunch ke liye kaha jaun"
```

#### Cafes
```
"Coffee shops nearby"
"Chai coffee kaha milegi"
"Cafe dikhao"
```

#### Tourist Attractions
```
"Places to visit"
"Ghumne ke liye kya hai"
"Tourist spots"
"Dekhne ke liye monuments"
```

### Booking & Directions

The system provides:
- **Directions** button → Opens Google Maps
- **Reviews** button → Shows Google reviews
- **Booking.com** / **MakeMyTrip** links for hotels
- **Zomato** / **Swiggy** links for restaurants

---

## 🔧 Architecture & Files

### New Files Created

1. **`location_helper.py`** - Location and Places API logic
   - `get_nearby_places()` - Fetches nearby places
   - `compare_places()` - Sorts by rating/price/distance
   - `get_place_details()` - Gets detailed info
   - `get_dummy_places()` - Fallback dummy data

### Modified Files

1. **`travel_assistant.py`**
   - Added `realtime_mode`, `current_lat`, `current_lon` state
   - Added `activate_realtime_guide()` method
   - Added `handle_realtime_query()` method
   - Modified `process_message()` to accept location

2. **`app.py`**
   - Updated to receive `lat` and `lon` in POST requests
   - Save real-time state in session

3. **`templates/chat.html`**
   - Added geolocation JavaScript functions
   - Added `getLocation()` for permission request
   - Added `startWatchingLocation()` for continuous tracking
   - Auto-sends location with each message
   - Added CSS for place cards

4. **`requirements.txt`**
   - Added `cachetools` for API caching
   - Added `geopy` for distance calculation

---

## 💰 Cost Breakdown (Per Month)

For **2 users** testing locally:

| Service | Free Tier | Est. Usage | Cost |
|---------|-----------|------------|------|
| **Google Places API** | 40,000 req/month | ~500 req | **$0** |
| **Groq API** | Unlimited (beta) | Unlimited | **$0** |
| **Gemini API** | 60 req/min | ~1000 req | **$0** |
| **Geolocation** | Browser API | Unlimited | **$0** |
| **Caching** | Local | Unlimited | **$0** |
| **Total** | | | **$0** ✅ |

---

## 🧪 Testing Without API Keys

If you don't want to get Google Places API key right away, the system works with **dummy data**!

### What happens without API key:
- ✅ All features work
- ✅ Dummy hotels, restaurants shown
- ✅ Ratings, prices, distances displayed
- ✅ Booking links work
- ❌ Real-time data not available
- ❌ Photos from Unsplash (not actual places)

**This is perfect for local development!**

---

## 🎨 UI Features

### Place Cards Show:
- ✅ Place name
- ✅ Rating (⭐ 4.5 / 1250 reviews)
- ✅ Price level (₹₹ - Moderate)
- ✅ Distance (0.5 km away)
- ✅ Open/Closed status
- ✅ Address
- ✅ Photo
- ✅ Directions button
- ✅ Reviews button
- ✅ Booking buttons

### Smart Sorting:
- By default: Best rating + closest distance
- Can be customized for:
  - "Show cheaper options" → Sort by price
  - "Show closest" → Sort by distance
  - "Best rated" → Sort by rating

---

## 🔒 Privacy & Security

### Location Permissions
- Browser asks for permission first
- User must explicitly allow
- Location is NOT stored permanently
- Only used during active session
- Can be disabled anytime

### Data Storage
- Location stored in session only
- Cleared on logout
- Not saved to database
- Not shared with third parties

---

## 📊 Caching Strategy

To minimize API calls and stay within free tier:

| Data Type | Cache Duration | Reason |
|-----------|---------------|--------|
| **Nearby Places** | 30 minutes | Hotels/restaurants don't change often |
| **Place Details** | 1 hour | Reviews update slowly |
| **User Location** | 30 seconds | Update location while moving |

Cache is **in-memory** (not persistent). Clears on app restart.

---

## 🐛 Troubleshooting

### Issue: "Location not detected"
**Solution**: 
- Make sure you're using **HTTPS** or **localhost**
- Check browser permissions (Settings → Privacy → Location)
- Try different browser (Chrome recommended)

### Issue: "No places found"
**Solution**:
- Check if you added `GOOGLE_PLACES_API_KEY` in `.env`
- Without API key, dummy data will show
- Check API quota on Google Cloud Console

### Issue: "API key invalid"
**Solution**:
- Verify API key in Google Cloud Console
- Make sure "Places API" is enabled
- Check API restrictions (should allow localhost)

### Issue: Browser geolocation not working
**Solution**:
- Geolocation only works on HTTPS or localhost
- If using http://192.168.x.x, it won't work
- Use `localhost:5000` instead

---

## 🎯 Example Conversation Flow

```
User: "Mai Jaipur pahuch gaya"

Bot: 🗺️ Real-Time Local Guide Activated!
     Please enable location access.
     [Share My Location Button]

[User clicks button, grants permission]

Bot: ✅ Location detected! Latitude: 26.9124, Longitude: 75.7873
     What would you like to find nearby?

User: "Hotel dikhao paas mein"

Bot: 📍 Found 6 hotels near you!
     Sorted by rating and distance.
     
     1. Grand Plaza Hotel ⭐ 4.5 (1250 reviews)
        Near Jaipur center, Main Street
        🚗 0.5 km away | ₹₹₹ (Expensive)
        [Directions] [Reviews] [Booking.com] [MakeMyTrip]
     
     2. Budget Inn ⭐ 4.0 (850 reviews)
        Near Jaipur railway station
        🚗 0.8 km away | ₹ (Budget)
        [Directions] [Reviews] [Booking.com] [MakeMyTrip]
     
     ...

User: "Khane ke liye kya hai paas mein"

Bot: 📍 Found 6 restaurants near you!
     ...
```

---

## 📈 Future Enhancements (Not Implemented Yet)

These can be added later:

1. **Offline Maps** - Pre-download city data
2. **AR View** - Point camera to see place info
3. **Voice Commands** - "OK TravelBuddy, find restaurants"
4. **Push Notifications** - "You're near Hawa Mahal!"
5. **Weather Integration** - Show weather-based suggestions
6. **Crowd Levels** - "This place is 80% full right now"
7. **Price Prediction** - "Prices usually drop in 2 hours"
8. **Local Events** - "Festival happening nearby!"

---

## 📞 Support

If you face any issues:

1. Check console logs: `F12` → Console tab
2. Check terminal logs: Look for `[REALTIME GUIDE]` messages
3. Test with dummy data first (without API key)
4. Make sure all dependencies installed

---

## 🎉 Summary

**What You Built:**
- ✅ Real-time location tracking
- ✅ Google Places integration (free tier)
- ✅ Smart comparison engine
- ✅ Caching to save API costs
- ✅ Hindi/Hinglish support
- ✅ Booking integration
- ✅ Beautiful UI with cards
- ✅ Works offline (dummy data)

**Total Cost:** $0 for local testing! 🎊

**Ready to Scale?** When you want to deploy for more users, we can add:
- Redis for distributed caching
- PostgreSQL for location history
- Nginx for load balancing
- Docker for easy deployment

---

## 🚀 Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open browser
# Go to http://localhost:5000

# Login and go to Chat
# Type: "real-time guide"
# Click "Share My Location"
# Ask: "Show hotels nearby"

# Enjoy! 🎉
```

---

**Built with ❤️ using free APIs and open-source tools!**


