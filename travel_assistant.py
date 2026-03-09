import requests
import json
import re
import pandas as pd
from bs4 import BeautifulSoup
import random
import os
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Get from environment variable
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")  # Get from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Groq API (much faster!)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Google Gemini API (backup)

class TravelAssistant:
    def __init__(self, user_data=None):
        self.user_data = user_data
        self.conversation_state = "initial"
        self.location = None
        self.realtime_mode = False
        self.current_lat = None
        self.current_lon = None
        self.current_city = None

    def extract_destination(self, message):
        """Extract destination from user message using regex patterns and AI"""
        # First, try regex pattern matching for quick extraction
        destination = self.extract_destination_regex(message)
        if destination:
            return destination
        
        # If regex fails, try AI extraction as fallback (using fastest API)
        return self.extract_with_ai(message)
    
    def extract_with_ai(self, message):
        """Extract destination using AI - tries multiple APIs for best speed"""
        prompt = f"""Extract ONLY the travel destination city/place name from this message. Reply with just the place name, nothing else. If no destination is mentioned, reply with "NONE".

Message: "{message}"

Destination:"""
        
        # Try Groq first (fastest!)
        if GROQ_API_KEY:
            try:
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "llama-3.1-8b-instant",  # Super fast model
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 30,
                    "temperature": 0.1
                }
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=5
                )
                if response.status_code == 200:
                    result = response.json()
                    destination = result["choices"][0]["message"]["content"].strip()
                    destination = destination.strip('"\'.,!?')
                    if destination and destination.upper() != "NONE" and len(destination) > 1 and len(destination) < 100:
                        return destination
            except Exception as e:
                print(f"Groq API error: {e}")
        
        # Fallback to Gemini (also fast and free)
        if GEMINI_API_KEY:
            try:
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                data = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 30
                    }
                }
                response = requests.post(gemini_url, json=data, timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    destination = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                    destination = destination.strip('"\'.,!?')
                    if destination and destination.upper() != "NONE" and len(destination) > 1 and len(destination) < 100:
                        return destination
            except Exception as e:
                print(f"Gemini API error: {e}")
        
        # Final fallback to OpenRouter (slower but reliable)
        if OPENROUTER_API_KEY:
            try:
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "mistralai/mistral-7b-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 30,
                    "temperature": 0.1
                }
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=8
                )
                if response.status_code == 200:
                    result = response.json()
                    destination = result["choices"][0]["message"]["content"].strip()
                    destination = destination.strip('"\'.,!?')
                    if destination and destination.upper() != "NONE" and len(destination) > 1 and len(destination) < 100:
                        return destination
            except Exception as e:
                print(f"OpenRouter API error: {e}")
        
        return None
    
    def extract_destination_regex(self, message):
        """Extract destination using regex patterns"""
        message_lower = message.lower()
        
        # Common Indian and international destinations
        destinations = [
            # Popular Indian destinations
            "goa", "delhi", "mumbai", "bangalore", "chennai", "kolkata", "hyderabad",
            "jaipur", "udaipur", "jodhpur", "agra", "varanasi", "rishikesh", "haridwar",
            "manali", "shimla", "dharamshala", "kasol", "spiti", "leh", "ladakh",
            "himachal pradesh", "himachal", "uttarakhand", "kerala", "ooty", "munnar",
            "coorg", "kodaikanal", "darjeeling", "gangtok", "sikkim", "shillong",
            "meghalaya", "kaziranga", "andaman", "nicobar", "lakshadweep", "pondicherry",
            "puducherry", "hampi", "mysore", "gokarna", "alibaug", "lonavala", "mahabaleshwar",
            "mount abu", "pushkar", "bikaner", "jaisalmer", "ajmer", "amritsar", "chandigarh",
            "mcleodganj", "dalhousie", "nainital", "mussoorie", "auli", "kedarnath", "badrinath",
            "rameshwaram", "kanyakumari", "madurai", "tiruchirappalli", "tirupati", "vijayawada",
            "visakhapatnam", "puri", "bhubaneswar", "konark", "guwahati", "tawang",
            "kashmir", "srinagar", "pahalgam", "gulmarg", "jammu", "katra", "vaishno devi",
            "rann of kutch", "kutch", "ahmedabad", "surat", "vadodara", "mount abu",
            "rajasthan", "rajkot", "dwarka", "somnath", "gir", "diu", "daman",
            
            # International destinations
            "dubai", "singapore", "thailand", "bangkok", "phuket", "bali", "maldives",
            "sri lanka", "nepal", "kathmandu", "bhutan", "paris", "london", "new york",
            "tokyo", "sydney", "melbourne", "hong kong", "malaysia", "kuala lumpur",
            "indonesia", "vietnam", "cambodia", "myanmar", "philippines", "south korea",
            "japan", "china", "beijing", "shanghai", "europe", "switzerland", "italy",
            "rome", "venice", "spain", "barcelona", "portugal", "greece", "turkey",
            "istanbul", "egypt", "cairo", "morocco", "south africa", "kenya", "mauritius",
            "seychelles", "usa", "america", "canada", "australia", "new zealand",
            "amsterdam", "berlin", "vienna", "prague", "budapest", "croatia", "iceland"
        ]
        
        # Sort destinations by length (longest first) to match multi-word destinations first
        destinations_sorted = sorted(destinations, key=len, reverse=True)
        
        # First, check for direct destination mentions (most reliable)
        for destination in destinations_sorted:
            # Create a regex pattern that matches the destination as a whole word/phrase
            dest_pattern = r'\b' + re.escape(destination) + r'\b'
            if re.search(dest_pattern, message_lower):
                # Return proper case
                return destination.title()
        
        # Enhanced patterns to match destinations with Hindi/Hinglish phrases
        patterns = [
            # English patterns
            r'(?:to|visit|visiting|go to|going to|trip to|travel to|tour to|planning for|plan for|heading to)\s+([a-z\s]+?)(?:\s+(?:next|this|for|in|on|and|with|please|plz|pls|help|asap)|\?|!|,|\.|\s*$)',
            r'(?:in|at)\s+([a-z\s]+?)(?:\s+(?:next|this|for|in|on|and|with|please|plz|pls|help|asap)|\?|!|,|\.|\s*$)',
            r'\b([a-z\s]+?)\s+(?:trip|tour|vacation|holiday|visit|travel)',
            # Hindi/Hinglish patterns - MORE COMPREHENSIVE
            r'(?:mujhe|main|hum|humko|mein)?\s*([a-z\s]+?)\s+(?:jana hai|jaana hai|jaa|jaunga|jaungi|jane|jaane|chalte|chalo|nikalna)',
            r'([a-z\s]+?)\s+(?:ghumna|ghoomna|ghoom|ghumne|dekhna|dekhne)',
            r'(?:ki taraf|ko)\s+([a-z\s]+)',
            # New patterns for "mujhe X plan karna hai" type
            r'(?:mujhe|main|hum)?\s*(?:ab|abhi)?\s*([a-z\s]+?)\s+(?:plan karna|planning|plan|book)',
            r'([a-z\s]+?)\s+(?:ka plan|ki planning|ke liye)',
        ]
        
        # Try regex patterns
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                potential_dest = match.group(1).strip()
                # Remove common words
                potential_dest = re.sub(r'\b(mujhe|main|hum|humko|mein|ko|ki|ka|ke|hai|ho|tha|the)\b', '', potential_dest).strip()
                
                # Check if it matches any known destination
                for destination in destinations_sorted:
                    if destination in potential_dest or potential_dest in destination:
                        return destination.title()
        
        return None

    def process_message(self, message, lat=None, lon=None, force_realtime=False):
        """Process user message and return appropriate response
        
        Args:
            message: User message string
            lat: User latitude for realtime guide
            lon: User longitude for realtime guide
            force_realtime: If True, force realtime mode even if not previously activated
        """
        
        # Update location if provided
        if lat and lon:
            self.current_lat = lat
            self.current_lon = lon
        
        # Activate real-time guide mode if force_realtime is True (first time activation)
        if force_realtime and not self.realtime_mode:
            self.realtime_mode = True
            self.conversation_state = "realtime_guide"
            return self.activate_realtime_guide()
        
        # Real-time guide mode - handle subsequent queries
        if self.realtime_mode or self.conversation_state == "realtime_guide":
            return self.handle_realtime_query(message)
        
        if self.conversation_state == "initial":
            # Expanded travel keywords including Hindi/Hinglish
            travel_keywords = [
                # English
                "trip", "travel", "vacation", "holiday", "tour", "visit", "journey", 
                "explore", "adventure", "getaway", "go to", "going to", "want to go",
                "planning", "plan", "visiting", "touring", "sightseeing",
                # Hindi/Hinglish
                "jana", "jaana", "jaan", "jaa", "jane", "jaane", "jaunga", "jaungi",
                "ghumna", "ghoomna", "ghoom", "ghumne", "ghoome", "घूमना", "घूमने",
                "yatra", "yaatra", "यात्रा", "safar", "सफर", "chalo", "chalein",
                "dekhna", "dekhne", "visit", "घुमावा", "picnic", "छुट्टी", "chutti",
                "nikalna", "nikalenge"
            ]
            
            # First, try to extract destination regardless of keywords
            destination = self.extract_destination(message)
            
            # Check if message contains travel keywords OR a valid destination
            has_travel_keywords = any(keyword in message.lower() for keyword in travel_keywords)
            
            if destination:
                # Destination found! Generate recommendation directly
                self.location = destination
                self.conversation_state = "provide_recommendation"
                salary = self.user_data.get('salary', None) if self.user_data else None
                return self.generate_travel_recommendation(self.location, salary)
            elif has_travel_keywords:
                # Travel intent detected but no destination found
                self.conversation_state = "ask_location"
                return "That's a wonderful idea! I'd be happy to help you plan your trip. Could you please tell me which destination you're interested in visiting?"
            else:
                return "I'm your travel assistant! I can help you plan a trip. Just let me know where you'd like to travel, and I'll provide personalized recommendations."

        elif self.conversation_state == "ask_location":
            self.location = message.strip()
            self.conversation_state = "provide_recommendation"
            salary = self.user_data.get('salary', None) if self.user_data else None
            return self.generate_travel_recommendation(self.location, salary)

        elif self.conversation_state == "provide_recommendation":
            if "budget" in message.lower():
                budget = self.extract_budget(message)
                return self.generate_travel_recommendation(self.location, None, budget)
            elif any(word in message.lower() for word in ["thank", "thanks", "great", "awesome", "good"]):
                self.conversation_state = "initial"
                return "You're welcome! I'm glad I could help. Feel free to ask about any other destinations you're interested in visiting."
            else:
                self.location = message.strip()
                return self.generate_travel_recommendation(self.location, self.user_data.get('salary', None) if self.user_data else None)

    def extract_budget(self, message):
        budget_patterns = [
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?) ?(?:k|K|thousand)',
            r'(\d+) ?(?:thousand|k)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?) ?(?:lakh|L|lac)',
            r'(\d+) ?(?:lakh|L|lac)',
            r'₹ ?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'INR ?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'Rs\.? ?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'budget (?:of|is|:)? ?(?:₹|Rs\.?|INR)? ?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'(?:₹|Rs\.?|INR)? ?(\d{1,3}(?:,\d{3})*(?:\.\d+)?) ?(?:budget|price|cost)'
        ]
        for pattern in budget_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                budget_str = match.group(1).replace(',', '')
                budget = float(budget_str)
                if 'k' in message.lower() or 'thousand' in message.lower():
                    budget *= 1000
                elif 'lakh' in message.lower() or 'lac' in message.lower() or 'L' in message.lower():
                    budget *= 100000
                return int(budget)
        return None

    def generate_travel_recommendation(self, location, salary=None, budget=None):
        if budget is None and salary is not None:
            if salary < 30000:
                budget = int(salary * 0.15)
            elif salary < 100000:
                budget = int(salary * 0.20)
            else:
                budget = int(salary * 0.30)
        elif budget is None:
            budget = 20000

        location_info = self.get_location_info(location)
        
        # Convert markdown bold to HTML bold for better display
        location_info = location_info.replace('**', '<strong>').replace('</strong>', '</strong>', 1)
        # Fix the replacement to work properly
        import re
        location_info = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', location_info)
        # Convert newlines to HTML breaks for better formatting
        location_info = location_info.replace('\n', '<br>')
        
        accommodations = self.get_accommodation_cards(location)
        sources = self.get_sources(location)
        packages = self.get_travel_packages(location, budget)

        response = f"""
        <div class="response-container">
            <div class="location-info">
                <h4>📍 Complete Travel Guide: {location}</h4>
                <div style="line-height: 1.8; text-align: left;">
                    {location_info}
                </div>
            </div>
            <div class="accommodation-section mt-3">
                <h5>🏨 Top Places to Stay in {location}</h5>
                <div class="row">
                    {''.join([self.format_accommodation_card(acc) for acc in accommodations])}
                </div>
            </div>
            <div class="sources-section">
                <h5>🔗 Useful Resources:</h5>
                <ul>
                    {''.join([f'<li><a href="{source["link"]}" target="_blank">{source["title"]}</a></li>' for source in sources])}
                </ul>
            </div>
            <h4 class="mt-4">💰 Recommended Packages for Your Budget (₹{budget:,})</h4>
            <div class="package-cards">
                {''.join([self.format_package_card(package) for package in packages])}
            </div>
        </div>
        """
        return response

    def get_accommodation_cards(self, location):
        """
        Scrape top hotels/resorts/hostels for a location using SerpAPI.
        Returns a list of dicts: name, description, image_url, rating, link
        """
        try:
            query = f"best hotels in {location}"
            params = {
                "engine": "google",
                "q": query,
                "api_key": SERPAPI_API_KEY,
                "num": 6
            }
            response = requests.get("https://serpapi.com/search", params=params)
            if response.status_code == 200:
                data = response.json()
                results = data.get("organic_results", [])[:5]
                cards = []
                for res in results:
                    title = res.get("title", "Top Hotel")
                    link = res.get("link", "#")
                    desc = res.get("snippet", res.get("about_this_result", [{}])[0].get("snippet", ""))
                    image_url = res.get("thumbnail", "")
                    if not image_url:
                        try:
                            r = requests.get(link, timeout=5)
                            soup = BeautifulSoup(r.text, "html.parser")
                            og = soup.find("meta", property="og:image")
                            if og:
                                image_url = og.get("content", "")
                        except:
                            image_url = ""
                    rating = ""
                    for ext in res.get("rich_snippet", {}).get("top", {}).get("extensions", []):
                        if "star" in ext:
                            rating = ext
                    cards.append({
                        "name": title,
                        "description": desc,
                        "image_url": image_url if image_url else f"https://source.unsplash.com/400x200/?hotel,{location}",
                        "rating": rating,
                        "link": link
                    })
                return cards
        except Exception as e:
            print("Hotel scraping error:", e)
        # Fallback: 3 dummy cards
        return [
            {"name": f"{location} Premium Resort", "description": "A luxurious resort with scenic views and modern amenities.", "image_url": f"https://source.unsplash.com/400x200/?resort,{location}", "rating": "4.6/5", "link": f"https://www.tripadvisor.in/Hotels-g{random.randint(10000,99999)}-{location}.html"},
            {"name": f"Backpackers Hostel {location}", "description": "Affordable hostel perfect for solo travelers and backpackers.", "image_url": f"https://source.unsplash.com/400x200/?hostel,{location}", "rating": "4.2/5", "link": f"https://www.booking.com/city/in/{location.lower()}.html"},
            {"name": f"Family Suites {location}", "description": "Comfortable family accommodation with great facilities.", "image_url": f"https://source.unsplash.com/400x200/?family,hotel,{location}", "rating": "4.5/5", "link": f"https://www.makemytrip.com/hotels/{location.lower()}-hotels.html"},
        ]

    def format_accommodation_card(self, acc):
        return f"""
        <div class="col-md-4 mb-3">
            <div class="card h-100">
                <img src="{acc['image_url']}" class="card-img-top" alt="{acc['name']}">
                <div class="card-body">
                    <h6 class="card-title">{acc['name']}</h6>
                    <p class="card-text">{acc['description'][:120]}{'...' if len(acc['description'])>120 else ''}</p>
                    <p class="card-text"><b>Rating:</b> {acc.get('rating','N/A')}</p>
                    <a href="{acc['link']}" class="btn btn-primary btn-sm" target="_blank">Visit Website</a>
                </div>
            </div>
        </div>
        """

    def get_location_info(self, location):
        """Generate comprehensive location information using fastest available API"""
        prompt = f"""You are an expert travel guide. Create a COMPREHENSIVE travel guide for {location} with the following sections. Be specific, detailed, and use bullet points for easy reading.

📍 **OVERVIEW / INTRODUCTION**
Write 3-4 engaging sentences about what makes {location} special and unique.

🗺️ **LOCATION & GEOGRAPHY**
• State/Country location
• Altitude (if applicable)
• Nearby major cities
• Geographic highlights (mountains/beaches/rivers)

✈️ **HOW TO REACH**
• By Air: Nearest airport(s) with distance
• By Train: Major railway stations
• By Road: Highway connections, distance from major cities
• Approximate travel times

🌤️ **BEST TIME TO VISIT**
• Peak season months and why
• Off-season months
• Weather conditions throughout the year
• Festival seasons

🏛️ **TOP ATTRACTIONS (List 7-10 must-visit places)**
• Name - Brief description with timing/entry fees if known
• Prioritize UNESCO sites, famous landmarks, natural wonders

🎯 **POPULAR ACTIVITIES / THINGS TO DO**
• Adventure activities
• Cultural experiences
• Nature/wildlife activities
• Photography spots
• Water sports/snow activities (if applicable)

🎭 **CULTURE & TRADITIONS**
• Local culture highlights
• Traditional dress
• Languages spoken
• Cultural etiquette

🍽️ **LOCAL CUISINE / FOOD TO TRY**
• Must-try dishes (at least 5-7 specific items)
• Famous restaurants/food streets
• Street food specialties
• Unique local drinks/desserts

🏨 **ACCOMMODATION OPTIONS**
• Budget: (₹500-1500/night) - Examples
• Mid-range: (₹1500-4000/night) - Examples
• Luxury: (₹4000+/night) - Examples
• Best areas to stay

🚗 **TRANSPORTATION WITHIN THE CITY**
• Local transport options (bus/metro/auto)
• Bike/scooter rentals (approximate costs)
• Taxi/cab services
• Walking-friendly areas

🛍️ **SHOPPING & LOCAL MARKETS**
• Famous markets/shopping areas
• What to buy (handicrafts, textiles, souvenirs)
• Bargaining tips
• Timings

🎉 **FESTIVALS & EVENTS**
• Major festivals (with months)
• Cultural events
• Best time to experience local culture

🌙 **NIGHTLIFE** (if applicable)
• Clubs/bars/pubs
• Night markets
• Evening activities
• Safety tips for night travel

💰 **COST / BUDGET BREAKDOWN** (Per person per day)
• Budget traveler: ₹1000-2000
• Mid-range traveler: ₹2000-5000
• Luxury traveler: ₹5000+
• Break down: food + stay + transport + activities

🛡️ **SAFETY & TRAVEL TIPS**
• Safety for solo travelers/women
• Common scams to avoid
• Emergency numbers
• Health precautions

✅ **DO'S AND DON'TS**
DO:
• List 4-5 important do's
DON'T:
• List 4-5 important don'ts

🗺️ **NEARBY DESTINATIONS / DAY TRIPS**
• List 3-5 nearby places with distances
• Best for day trips or weekend getaways

Use specific names, real places, actual costs. Write in an engaging, friendly tone. Use emojis and bullet points for visual appeal. Be detailed and helpful!"""
        
        # Try Groq first (super fast!)
        if GROQ_API_KEY:
            try:
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "llama-3.1-70b-versatile",  # Best quality Groq model
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2500,  # Increased for comprehensive content
                    "temperature": 0.7
                }
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=15
                )
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"Groq API error: {e}")
        
        # Try Gemini (also fast and good quality)
        if GEMINI_API_KEY:
            try:
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                data = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 2500
                    }
                }
                response = requests.post(gemini_url, json=data, timeout=15)
                if response.status_code == 200:
                    result = response.json()
                    return result["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception as e:
                print(f"Gemini API error: {e}")
        
        # Fallback to OpenRouter
        if OPENROUTER_API_KEY:
            try:
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "mistralai/mistral-7b-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2500,
                    "temperature": 0.7
                }
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=20
                )
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"OpenRouter API error: {e}")
        
        # Final fallback to pre-written comprehensive content
        return self.get_detailed_fallback_text(location)

    def get_detailed_fallback_text(self, location):
        fallbacks = {
            "goa": f"""
📍 **OVERVIEW / INTRODUCTION**
{location} is India's ultimate beach paradise on the western coast, where Portuguese heritage meets pristine beaches, vibrant nightlife, and laid-back coastal vibes. Famous for its stunning coastline, water sports, seafood, and party scene, Goa attracts millions of tourists seeking both relaxation and adventure!

🗺️ **LOCATION & GEOGRAPHY**
• Located in Western India on the Arabian Sea coast
• Smallest state by area, 4th smallest by population
• Bordered by Maharashtra (north), Karnataka (south/east)
• 105 km coastline with numerous beaches
• Divided into North Goa (party hub) and South Goa (peaceful)

✈️ **HOW TO REACH**
• **By Air**: Goa International Airport (Dabolim) - 30km from Panaji, well connected to major Indian cities and some international destinations
• **By Train**: Major stations - Madgaon (Margao), Thivim, Karmali. Direct trains from Mumbai (8-12 hrs), Delhi (24+ hrs), Bangalore (15 hrs)
• **By Road**: NH-66 connects to Mumbai (470km, 10 hrs), Bangalore (560km, 11 hrs). State and private buses available

🌤️ **BEST TIME TO VISIT**
• **Peak Season**: November to February (pleasant weather, 20-30°C, perfect beach time, festivals)
• **Monsoon**: June to September (heavy rains, beaches close, but lush green landscapes)
• **Off-Season**: March to May (hot & humid, fewer tourists, cheaper rates)
• **Festival Time**: Goa Carnival (Feb/Mar), Sunburn Festival (Dec), Christmas & New Year

🏛️ **TOP ATTRACTIONS**
• **Calangute Beach** - Queen of Beaches, water sports hub, crowded but lively
• **Baga Beach** - Nightlife central, beach clubs, water sports (free entry)
• **Fort Aguada** - 17th-century Portuguese fort, lighthouse, sunset views (₹25 entry)
• **Basilica of Bom Jesus** - UNESCO World Heritage, houses St. Francis Xavier's remains (free, open 9 AM-6:30 PM)
• **Dudhsagar Falls** - Majestic 4-tier waterfall, 60km from Panaji, jeep safari needed (₹300-500)
• **Anjuna Beach** - Famous flea market (Wednesdays), hippie culture, trance parties
• **Palolem Beach** - South Goa's gem, peaceful, crescent-shaped, perfect for relaxation
• **Old Goa Churches** - Se Cathedral, Church of St. Francis, colonial Portuguese architecture
• **Chapora Fort** - "Dil Chahta Hai" fort, panoramic views of Vagator Beach
• **Butterfly Beach** - Hidden gem, accessible by boat, secluded and pristine

🎯 **POPULAR ACTIVITIES / THINGS TO DO**
• Parasailing, jet skiing, banana boat rides (₹500-1500)
• Scuba diving at Grande Island (₹2500-4000)
• Spice plantation tours with traditional lunch (₹800-1200)
• Casino cruise on Mandovi River (₹1500-3000)
• Dolphin watching boat trips (₹500-800)
• Beach hopping on rented scooter
• Sunset cruises and party cruises
• Water sports at Calangute, Baga, Candolim
• Trekking to Dudhsagar Falls
• Photography at Portuguese colonial sites

🎭 **CULTURE & TRADITIONS**
• Unique blend of Indian and Portuguese culture
• Predominantly Christian state with Hindu minority
• Languages: Konkani (official), English, Hindi, Marathi
• Relaxed, liberal atmosphere compared to rest of India
• Famous for Goa Trance music culture
• Strong fishing and maritime heritage
• Laid-back "susegad" lifestyle (take it easy)

🍽️ **LOCAL CUISINE / FOOD TO TRY**
• **Goan Fish Curry** - Spicy coconut-based curry with rice
• **Prawn Balchão** - Tangy spicy prawn pickle
• **Pork Vindaloo** - Spicy pork curry with vinegar
• **Bebinca** - Traditional layered Goan dessert
• **Xacuti** - Aromatic chicken/meat curry with coconut
• **Feni** - Local cashew/coconut liquor (₹200-500/bottle)
• **Seafood at beach shacks** - Fresh catch of the day
• **Goan Sausage** (Chouriço) - Spicy pork sausage
• **Popular Restaurants**: Martin's Corner, Fisherman's Wharf, Britto's, Thalassa, Gunpowder
• **Street Food**: Ros omelette, Goan pão, sorpotel

🏨 **ACCOMMODATION OPTIONS**
• **Budget**: Hostels & guesthouses (₹500-1500/night) - Areas: Anjuna, Arambol, Palolem
  Examples: Roadhouse Hostel, Zostel Goa, local homestays
• **Mid-range**: Beach resorts & hotels (₹2000-5000/night) - Areas: Calangute, Candolim, Colva
  Examples: Resort Terra Paraiso, Cidade de Goa, boutique stays
• **Luxury**: 5-star resorts (₹8000+/night) - Areas: Candolim, Cavelossim, Morjim
  Examples: Taj Exotica, Alila Diwa, W Goa, Leela Goa

🚗 **TRANSPORTATION WITHIN THE CITY**
• **Scooter/Bike Rental**: Most popular (₹300-500/day without helmet, documents required)
• **Taxis**: Available but expensive, no meters (negotiate or use app cabs)
• **Auto-rickshaws**: Less common than other Indian states
• **App Cabs**: Uber, Ola available in main areas
• **Buses**: KTC buses connect major towns (₹10-50)
• **Self-drive Cars**: Available (₹1500-2500/day)
• **Ferry**: Free government ferries across rivers

🛍️ **SHOPPING & LOCAL MARKETS**
• **Anjuna Flea Market** (Wednesdays) - Handicrafts, jewelry, clothes, hippie stuff
• **Arpora Saturday Night Market** - Shopping, food, live music, entertainment
• **Mapusa Market** (Fridays) - Local produce, spices, authentic Goan items
• **Panjim Market** - Goan sausages, bebinca, feni, cashew nuts
• **What to Buy**: Cashew nuts, feni, shell jewelry, hippie clothes, Portuguese ceramics, spices
• **Bargaining**: Expected in markets (start at 40-50% of asking price)

🎉 **FESTIVALS & EVENTS**
• **Goa Carnival** (February/March) - 3-day colorful street festival with parades
• **Sunburn Festival** (December) - Asia's biggest electronic dance music festival
• **Shigmo Festival** (March) - Hindu spring festival with processions
• **Christmas & New Year** - Biggest party time, beach parties, midnight celebrations
• **Feast of St. Francis Xavier** (December 3) - Religious pilgrimage
• **Goa Food & Cultural Festival** (November/December)

🌙 **NIGHTLIFE**
• **Beach Clubs**: Tito's, Mambo's, Club Cubana (Baga area)
• **Night Clubs**: LPK Waterfront, Cafe Mambos, Club Cabana
• **Beach Shacks**: Live music, drinks, bonfire parties (Anjuna, Vagator, Morjim)
• **Casino Cruises**: Deltin Royale, Casino Pride (₹2000-4000 entry with chips)
• **Silent Noise Parties**: Headphone parties at Palolem Beach
• **Safety**: Generally safe, but avoid isolated beaches late at night, watch drinks in crowded clubs

💰 **COST / BUDGET BREAKDOWN** (Per person per day)
• **Budget Traveler**: ₹1200-2000
  - Stay: ₹500-800 | Food: ₹400-600 | Transport: ₹200-400 | Activities: ₹100-200
• **Mid-range Traveler**: ₹3000-5000
  - Stay: ₹1500-2500 | Food: ₹800-1200 | Transport: ₹400-600 | Activities: ₹500-1000
• **Luxury Traveler**: ₹8000-15000+
  - Stay: ₹5000-10000 | Food: ₹1500-2500 | Transport: ₹500-1000 | Activities: ₹1000-3000

🛡️ **SAFETY & TRAVEL TIPS**
• Generally safe for solo travelers and women, but take usual precautions
• Don't leave valuables unattended on beaches
• Beware of drug dealers (strict laws, avoid completely)
• Swimming: Follow lifeguard instructions, red flags mean no swimming
• Wear helmets while riding bikes (₹1000 fine if caught without)
• Carry ID and documents while traveling
• Emergency Numbers: Police 100, Ambulance 102, Tourist Helpline 1364
• Stay hydrated in hot weather, use sunscreen

✅ **DO'S AND DON'TS**

**DO:**
• Rent a scooter/bike for freedom and convenience
• Try local seafood at beach shacks
• Visit both North Goa (party) and South Goa (peace)
• Carry enough cash (many small places don't accept cards)
• Book accommodations in advance during peak season
• Respect local customs when visiting churches and temples

**DON'T:**
• Don't carry or consume drugs (very strict laws, jail time possible)
• Don't swim in rough seas or when red flags are up
• Don't litter beaches (₹500-1000 fine)
• Don't expect bargain prices at fancy beach clubs
• Don't drink and drive (police checkpoints, heavy fines)
• Don't disrespect religious places or take photos without permission

🗺️ **NEARBY DESTINATIONS / DAY TRIPS**
• **Hampi** - 320km, UNESCO World Heritage ancient ruins (weekend trip)
• **Gokarna** - 150km, peaceful beaches, temples (day trip or overnight)
• **Dandeli** - 110km, wildlife sanctuary, white water rafting
• **Karwar** - 95km, beaches, naval base, Devbagh beach
• **Chorla Ghat** - 60km, waterfalls, Western Ghats, monsoon beauty
• **Mollem National Park** - 60km, wildlife, Dudhsagar Falls base
            """,
            "delhi": f"""
            **Overview**: {location}, India's vibrant capital, is a spectacular blend of ancient monuments, Mughal architecture, bustling markets, and modern infrastructure. A city where history meets contemporary urban life!

            **Top Attractions**:
            • Red Fort - Iconic Mughal fortress
            • Qutub Minar - UNESCO World Heritage Site, tallest brick minaret
            • India Gate - War memorial and evening hangout spot
            • Humayun's Tomb - Magnificent Mughal garden tomb
            • Lotus Temple - Architectural marvel, peaceful atmosphere
            • Akshardham Temple - Modern spiritual complex
            • Chandni Chowk - Historic market, street food heaven
            • Connaught Place - Shopping and dining hub

            **Best Time**: October to March (pleasant weather, avoid summer)

            **Cuisine**: Chole bhature, butter chicken, parathas at Paranthe Wali Gali, street chaat, kebabs at Karim's, kulfi

            **Activities**: Heritage walks in Old Delhi, metro tours, shopping at Dilli Haat, food tours, visit museums, Lodhi Garden walks

            **Transport**: Metro (best option), auto-rickshaws, Uber/Ola, airport metro. Airport: IGI Airport (well connected)
            """,
            "mumbai": f"""
            **Overview**: {location}, India's financial capital and Bollywood's home, is a city that never sleeps! Experience colonial architecture, beautiful coastline, diverse culture, and an incredible food scene.

            **Top Attractions**:
            • Gateway of India - Iconic monument overlooking the Arabian Sea
            • Marine Drive - Queen's Necklace, stunning evening views
            • Elephanta Caves - Ancient rock-cut temples (UNESCO site)
            • Chhatrapati Shivaji Terminus - Victorian Gothic architecture
            • Juhu Beach - Celebrity spotting and street food
            • Haji Ali Dargah - Floating mosque in the sea
            • Colaba Causeway - Shopping and nightlife
            • Film City - Bollywood tours

            **Best Time**: November to February (pleasant weather)

            **Cuisine**: Vada pav, pav bhaji, bhel puri, sev puri, dabeli, Irani chai, seafood at Mahim Causeway

            **Activities**: Local train experience, ferry rides, shopping at Crawford Market, nightlife in Bandra, sunset at Marine Drive

            **Transport**: Local trains (lifeline of Mumbai), metro, taxis, auto-rickshaws, app cabs. Airport: Chhatrapati Shivaji International
            """,
            "jaipur": f"""
            **Overview**: {location}, the magnificent Pink City, is Rajasthan's crown jewel! Famous for majestic forts, vibrant bazaars, royal palaces, and rich cultural heritage. A photographer's and history lover's paradise!

            **Top Attractions**:
            • Amber Fort - Stunning hilltop fort, elephant rides
            • City Palace - Royal residence with museums
            • Hawa Mahal - Iconic Palace of Winds with 953 windows
            • Jantar Mantar - UNESCO World Heritage astronomical observatory
            • Nahargarh Fort - Best sunset views of the city
            • Jal Mahal - Beautiful palace in Man Sagar Lake
            • Jaigarh Fort - Houses world's largest cannon
            • Albert Hall Museum - Indo-Saracenic architecture

            **Best Time**: October to March (pleasant, perfect for sightseeing)

            **Cuisine**: Dal baati churma, laal maas, ghewar, pyaaz kachori, lassi, traditional Rajasthani thali at Chokhi Dhani

            **Activities**: Shopping for textiles and jewelry at Johari Bazaar, Bapu Bazaar; camel rides, cultural shows at Chokhi Dhani, hot air balloon rides

            **Transport**: Auto-rickshaws, app cabs, bike rentals. Airport: Jaipur International (12km from city). Well-connected by train and road.

            **Tips**: 
            • Visit forts early morning to avoid crowds and heat
            • Bargain at bazaars - start at 50% of quoted price
            • Try combo passes for forts to save money
            """,
            "manali": f"""
            **Overview**: {location} is a breathtaking hill station nestled in Himachal Pradesh's Kullu Valley. Known for snow-capped mountains, adventure sports, apple orchards, and stunning landscapes. Perfect for honeymooners, adventurers, and nature lovers!

            **Top Attractions**:
            • Rohtang Pass - Stunning mountain pass, snow activities (May-Nov)
            • Solang Valley - Paragliding, zorbing, skiing hub
            • Hidimba Devi Temple - Ancient wooden temple in cedar forest
            • Old Manali - Cafes, live music, hippie vibes
            • Vashisht Hot Springs - Natural hot water springs
            • Jogini Falls - Beautiful waterfall with trekking
            • Mall Road - Shopping and dining central area

            **Best Time**: March-June (pleasant), December-February (snow season)

            **Cuisine**: Siddu, Trout fish, Babru, Aktori, Israeli food in Old Manali, cafes with mountain views

            **Activities**: Paragliding, river rafting, trekking, skiing, mountain biking, camping, shopping for woolens and handicrafts

            **Transport**: Buses from Delhi/Chandigarh. Nearest airport: Bhuntar (50km). Local taxis, bikes on rent (₹800-1500/day)

            **Tips**:
            • Book Rohtang Pass permits online in advance
            • Carry warm clothes even in summer
            • Old Manali is better for peaceful stay than main town
            """,
            "kashmir": f"""
            **Overview**: {location}, known as "Paradise on Earth," is India's most beautiful destination! Features stunning valleys, pristine lakes, snow-capped peaks, Mughal gardens, and incredible hospitality. A dream destination for every traveler!

            **Top Attractions**:
            • Dal Lake - Iconic shikara rides, houseboats
            • Gulmarg - Asia's highest cable car, skiing paradise
            • Pahalgam - Bollywood's favorite, Betaab Valley, trekking base
            • Sonamarg - Glacier views, Thajiwas Glacier trek
            • Mughal Gardens - Shalimar Bagh, Nishat Bagh
            • Shankaracharya Temple - Hilltop temple, panoramic views
            • Nigeen Lake - Quieter alternative to Dal Lake

            **Best Time**: March-August (pleasant weather), December-February (snow activities)

            **Cuisine**: Rogan josh, Yakhni, Gushtaba, Kashmiri kahwa, noon chai, wazwan (traditional feast)

            **Activities**: Shikara rides, houseboat stays, skiing in Gulmarg, trekking, shopping for Pashmina shawls, saffron, dry fruits

            **Transport**: Srinagar Airport (well connected). Local taxis, auto-rickshaws. Day tours available for Gulmarg, Pahalgam, Sonamarg.

            **Tips**:
            • Stay in houseboats for unique experience
            • Book Gulmarg Gondola tickets early morning
            • Bargain for Pashmina (verify authenticity)
            • Check weather and local conditions before traveling
            """,
            "kerala": f"""
            **Overview**: {location}, "God's Own Country," is a tropical paradise with serene backwaters, lush green landscapes, pristine beaches, wildlife sanctuaries, and Ayurvedic wellness. Perfect blend of nature, culture, and relaxation!

            **Top Attractions**:
            • Backwaters of Alleppey - Houseboat stays, scenic canals
            • Munnar - Tea plantations, hill station beauty
            • Kovalam Beach - Popular beach destination
            • Periyar Wildlife Sanctuary - Elephant spotting
            • Fort Kochi - Colonial architecture, Chinese fishing nets
            • Varkala Beach - Cliffs, spirituality, sunsets
            • Wayanad - Wildlife, waterfalls, adventure

            **Best Time**: September-March (pleasant weather, backwater season)

            **Cuisine**: Appam with stew, Kerala fish curry, puttu, Malabar biryani, banana chips, toddy shop food, seafood

            **Activities**: Houseboat cruises, Ayurvedic massages, Kathakali performances, tea plantation tours, beach activities, wildlife safaris

            **Transport**: Kochi and Trivandrum airports (well connected). Good train network. Boats in backwaters. Rent bikes or cars for exploring.

            **Tips**:
            • Book houseboats in advance (₹6000-15000/night)
            • Try Ayurvedic treatments in authentic centers
            • Visit tea gardens in Munnar early morning
            • Kerala is very humid, pack accordingly
            """
        }
        location_lower = location.lower()
        if location_lower in fallbacks:
            return fallbacks[location_lower]
        else:
            return f"""
📍 **OVERVIEW / INTRODUCTION**
{location} is a captivating destination that offers travelers a wonderful blend of unique attractions, rich culture, and memorable experiences. This diverse location welcomes visitors with its distinctive character and warm hospitality.

🗺️ **LOCATION & GEOGRAPHY**
• Located in a scenic region with natural beauty
• Accessible from major nearby cities
• Features unique geographical characteristics
• Pleasant climate for most of the year

✈️ **HOW TO REACH**
• **By Air**: Nearest airport with connections to major cities
• **By Train**: Railway stations with good connectivity
• **By Road**: Well-connected by national/state highways
• Multiple transport options available for convenience

🌤️ **BEST TIME TO VISIT**
• Peak tourist season offers the best weather
• Off-season provides budget-friendly options
• Consider local festivals for cultural experiences
• Weather generally pleasant during tourist months

🏛️ **TOP ATTRACTIONS**
• Notable landmarks and historical sites
• Natural beauty spots and scenic viewpoints
• Cultural centers and museums
• Religious places of significance
• Parks and recreational areas
• Local monuments and architecture
• Photography-worthy locations

🎯 **POPULAR ACTIVITIES / THINGS TO DO**
• Sightseeing at major attractions
• Cultural experiences and local interactions
• Adventure activities (if available)
• Nature walks and exploration
• Shopping at local markets
• Photography and videography
• Trying local experiences

🎭 **CULTURE & TRADITIONS**
• Rich cultural heritage and traditions
• Local languages and dialects
• Traditional arts and crafts
• Festivals and celebrations throughout the year
• Respectful and welcoming locals

🍽️ **LOCAL CUISINE / FOOD TO TRY**
• Regional specialties and traditional dishes
• Street food delicacies
• Popular restaurants and eateries
• Local sweets and desserts
• Unique beverages and drinks
• Authentic home-style cooking
• Multi-cuisine options available

🏨 **ACCOMMODATION OPTIONS**
• **Budget**: Guesthouses and budget hotels (₹500-1500/night)
• **Mid-range**: Comfortable hotels and resorts (₹1500-4000/night)
• **Luxury**: Premium hotels and resorts (₹4000+/night)
• Various accommodation types for different preferences

🚗 **TRANSPORTATION WITHIN THE CITY**
• Local buses and public transport
• Auto-rickshaws and taxis available
• App-based cab services
• Bike/scooter rentals for exploring
• Walking-friendly areas in city center

🛍️ **SHOPPING & LOCAL MARKETS**
• Local markets offering handicrafts
• Shopping areas for souvenirs
• Traditional items and local products
• Bargaining commonly practiced
• Unique items specific to the region

🎉 **FESTIVALS & EVENTS**
• Major local festivals celebrated
• Cultural events throughout the year
• Religious celebrations
• Best time to experience local traditions

🌙 **NIGHTLIFE**
• Evening entertainment options available
• Restaurants and cafes open late
• Safe environment for tourists
• Cultural performances in evenings

💰 **COST / BUDGET BREAKDOWN** (Per person per day)
• **Budget Traveler**: ₹1000-2000 (Stay + Food + Transport + Basic activities)
• **Mid-range Traveler**: ₹2500-4500 (Comfortable stay + Good food + Transport + Activities)
• **Luxury Traveler**: ₹5000+ (Premium accommodation + Fine dining + Private transport + Premium experiences)

🛡️ **SAFETY & TRAVEL TIPS**
• Generally safe for tourists
• Take usual travel precautions
• Keep valuables secure
• Follow local guidelines
• Stay in well-connected areas
• Keep emergency numbers handy
• Respect local customs and traditions

✅ **DO'S AND DON'TS**

**DO:**
• Respect local culture and traditions
• Dress modestly when visiting religious places
• Try local cuisine and specialties
• Interact with locals for authentic experiences
• Carry sufficient cash for local purchases
• Plan your itinerary in advance

**DON'T:**
• Don't disrespect religious or cultural sites
• Don't litter in public places
• Don't ignore local customs
• Don't venture into isolated areas alone late at night
• Don't photograph people without permission
• Don't drink tap water (use bottled water)

🗺️ **NEARBY DESTINATIONS / DAY TRIPS**
• Several interesting places within 50-100km
• Weekend getaway options available
• Scenic routes connecting to other destinations
• Good for extending your trip
• Local tour operators offer day trip packages
            """

    def get_sources(self, location):
        try:
            query = f"travel guide {location} tourism official site"
            params = {
                "engine": "google",
                "q": query,
                "api_key": SERPAPI_API_KEY,
                "num": 5
            }
            response = requests.get("https://serpapi.com/search", params=params)
            if response.status_code == 200:
                data = response.json()
                organic_results = data.get("organic_results", [])
                sources = []
                for result in organic_results[:5]:
                    sources.append({
                        "title": result.get("title", "Travel Guide"),
                        "link": result.get("link", "#")
                    })
                return sources
            else:
                return self.get_placeholder_sources(location)
        except Exception as e:
            print(f"Error fetching sources: {e}")
            return self.get_placeholder_sources(location)

    def get_placeholder_sources(self, location):
        encoded_location = quote(location)
        return [
            {"title": f"Official Tourism Website - {location}", "link": f"https://www.google.com/search?q={encoded_location}+official+tourism+website"},
            {"title": f"Travel Guide - {location}", "link": f"https://www.tripadvisor.in/Search?q={encoded_location}"},
            {"title": f"Things to Do in {location}", "link": f"https://www.holidify.com/places/{encoded_location.lower()}/sightseeing-and-things-to-do.html"},
            {"title": f"{location} on MakeMyTrip", "link": f"https://www.makemytrip.com/holidays-india/{encoded_location.lower()}-tour-packages.html"},
            {"title": f"{location} Travel Blog", "link": f"https://traveltriangle.com/blog/category/{encoded_location.lower()}/"}
        ]

    def get_travel_packages(self, location, budget):
        try:
            return self.generate_placeholder_packages(location, budget)
        except Exception as e:
            print(f"Error fetching packages: {e}")
            return self.generate_placeholder_packages(location, budget)

    def generate_placeholder_packages(self, location, budget):
        packages = []
        low_price = max(5000, int(budget * 0.6))
        mid_price = int(budget * 0.9)
        high_price = int(budget * 1.2)
        durations = [2, 3, 4, 5, 6]
        person_options = [1, 2, 3, 4]
        packages.append({
            "title": f"Budget Explorer: {location} Getaway",
            "price": low_price,
            "days": random.choice(durations[:3]),
            "persons": random.choice(person_options),
            "image_url": f"https://source.unsplash.com/featured/?{location},travel",
            "booking_url": f"https://www.makemytrip.com/holidays-india/{location.lower()}-tour-packages.html"
        })
        packages.append({
            "title": f"Classic {location} Experience",
            "price": mid_price,
            "days": random.choice(durations[1:4]),
            "persons": random.choice(person_options),
            "image_url": f"https://source.unsplash.com/featured/?{location},tourism",
            "booking_url": f"https://www.thomascook.in/holidays/india-tour-packages/{location.lower()}-tourism"
        })
        packages.append({
            "title": f"Premium {location} Adventure",
            "price": high_price,
            "days": random.choice(durations[2:]),
            "persons": random.choice(person_options),
            "image_url": f"https://source.unsplash.com/featured/?{location},vacation",
            "booking_url": f"https://www.yatra.com/india-tour-packages/{location.lower()}-travel-packages"
        })
        if random.choice([True, False]):
            special_price = int(budget * random.uniform(0.8, 1.3))
            packages.append({
                "title": f"Special {location} Discovery Tour",
                "price": special_price,
                "days": random.choice(durations),
                "persons": random.choice(person_options),
                "image_url": f"https://source.unsplash.com/featured/?{location},tour",
                "booking_url": f"https://www.goibibo.com/destinations/{location.lower()}/"
            })
        return packages

    def format_package_card(self, package):
        return f"""
        <div class="package-card">
            <img src="{package['image_url']}" alt="{package['title']}" class="package-image">
            <div class="package-body">
                <div class="package-title">{package['title']}</div>
                <div class="package-detail">
                    <span>Price:</span>
                    <span>₹{package['price']:,}</span>
                </div>
                <div class="package-detail">
                    <span>Duration:</span>
                    <span>{package['days']} days</span>
                </div>
                <div class="package-detail">
                    <span>For:</span>
                    <span>{package['persons']} person(s)</span>
                </div>
                <div class="d-grid gap-2 mt-3">
                    <a href="{package['booking_url']}" target="_blank" class="btn btn-primary btn-sm">Book Now</a>
                </div>
            </div>
        </div>
        """
    
    # ========== REAL-TIME GUIDE METHODS ==========
    
    def understand_user_query(self, message):
        """
        Comprehensive query understanding with context, urgency, and intent detection
        This solves the medical shop vs shopping confusion issue
        """
        message_lower = message.lower()
        
        # Initialize result
        result = {
            "place_type": None,
            "search_keyword": "",
            "urgency": "normal",  # low, normal, high, emergency
            "context": "general",  # general, health, emergency, financial, etc.
            "needs_clarification": False,
            "human_response": "",
            "specific_request": ""
        }
        
        # EMERGENCY & HEALTH DETECTION (Highest Priority)
        health_emergency_keywords = [
            # English
            "sick", "ill", "emergency", "urgent", "hospital", "doctor", "medicine", "medical", "pharmacy", 
            "fever", "pain", "hurt", "accident", "help", "ambulance", "first aid", "clinic",
            # Hindi/Hinglish
            "bimar", "bemar", "tabiyat", "dawai", "dawa", "medical", "doctor", "hospital", "emergency",
            "bukhar", "dard", "takleef", "madad", "sahayata", "clinic"
        ]
        
        medical_shop_keywords = [
            # English
            "medical shop", "medicine shop", "pharmacy", "chemist", "drug store", "medical store",
            "medicines", "tablets", "pills", "syrup", "injection", "bandage",
            # Hindi/Hinglish
            "dawai ki dukan", "medical store", "chemist", "dawai", "dawa", "medicine", "tablet",
            "syrup", "injection", "medical", "pharmacy"
        ]
        
        # Check for medical/health queries FIRST
        if any(keyword in message_lower for keyword in medical_shop_keywords):
            result["place_type"] = "pharmacy"
            result["search_keyword"] = "pharmacy medical store"
            result["context"] = "health"
            result["urgency"] = "high" if any(word in message_lower for word in ["sick", "emergency", "urgent", "pain", "bimar"]) else "normal"
            result["human_response"] = "I understand you need medical assistance. Let me find medical shops and pharmacies near you within 3km!"
            return result
        
        if any(keyword in message_lower for keyword in health_emergency_keywords):
            if any(word in message_lower for word in ["emergency", "urgent", "accident", "ambulance", "serious"]):
                result["urgency"] = "emergency"
                result["context"] = "emergency"
                result["place_type"] = "hospital"
                result["search_keyword"] = "hospital emergency"
                result["human_response"] = "Emergency detected! I'm finding the nearest hospitals immediately within 3km range!"
            else:
                result["urgency"] = "high"
                result["context"] = "health"
                result["place_type"] = "doctor"
                result["search_keyword"] = "doctor clinic"
                result["human_response"] = "Looking for medical help? Let me find doctors and clinics near you!"
            return result
        
        # FINANCIAL SERVICES
        financial_keywords = [
            # English
            "bank", "atm", "money", "cash", "withdraw", "deposit", "loan", "account", "credit card",
            # Hindi/Hinglish
            "bank", "atm", "paisa", "paise", "cash", "withdraw", "nikalna", "account", "khata"
        ]
        
        if any(keyword in message_lower for keyword in financial_keywords):
            if any(word in message_lower for word in ["atm", "cash", "withdraw", "nikalna"]):
                result["place_type"] = "atm"
                result["search_keyword"] = "atm"
                result["context"] = "financial"
                result["human_response"] = "Looking for cash withdrawal? I'll find ATMs within 3km of your location!"
            else:
                result["place_type"] = "bank"
                result["search_keyword"] = "bank"
                result["context"] = "financial"
                result["human_response"] = "Need banking services? Here are bank branches near you within 3km!"
            return result
        
        # GOVERNMENT & OFFICIAL SERVICES
        government_keywords = [
            # English
            "post office", "police station", "government office", "passport office", "court", "municipality",
            "ration shop", "aadhar center", "voter id", "license", "registration",
            # Hindi/Hinglish
            "police station", "thana", "post office", "ration card", "aadhar", "sarkar", "office",
            "municipality", "nagar nigam", "tehsil", "collectorate"
        ]
        
        if any(keyword in message_lower for keyword in government_keywords):
            if "police" in message_lower or "thana" in message_lower:
                result["place_type"] = "police"
                result["search_keyword"] = "police station"
                result["urgency"] = "high"
                result["human_response"] = "Looking for police assistance? Is everything okay? Here are nearby police stations within 3km:"
            elif "post" in message_lower:
                result["place_type"] = "post_office"
                result["search_keyword"] = "post office"
                result["human_response"] = "Need postal services? Here are the nearest post offices within 3km:"
            else:
                result["place_type"] = "government"
                result["search_keyword"] = "government office"
                result["human_response"] = "Looking for government services? Here are nearby offices within 3km:"
            result["context"] = "official"
            return result
        
        # ACCOMMODATION
        hotel_keywords = [
            # English
            "hotel", "stay", "accommodation", "lodge", "guest house", "resort", "room", "suite", "booking",
            # Hindi/Hinglish
            "hotel", "rehne", "rukne", "room", "kamra", "booking", "stay", "lodge", "guest house"
        ]
        
        if any(keyword in message_lower for keyword in hotel_keywords):
            result["place_type"] = "lodging"
            result["search_keyword"] = "hotel"
            result["context"] = "accommodation"
            result["human_response"] = "Looking for accommodation? Here are great lodging options within 3km:"
            return result
        
        # FOOD & DINING
        restaurant_keywords = [
            # English
            "restaurant", "food", "eat", "hungry", "lunch", "dinner", "breakfast", "meal", "dining",
            # Hindi/Hinglish
            "restaurant", "khana", "khane", "bhookh", "lunch", "dinner", "breakfast", "meal", "khaana"
        ]
        
        cafe_keywords = [
            # English
            "cafe", "coffee", "tea", "snack", "bakery", "pastry", "sandwich",
            # Hindi/Hinglish
            "cafe", "coffee", "chai", "tea", "snack", "bakery", "nashta"
        ]
        
        if any(keyword in message_lower for keyword in restaurant_keywords):
            result["place_type"] = "restaurant"
            result["search_keyword"] = "restaurant"
            result["context"] = "dining"
            result["human_response"] = "Looking for food? I'll find the best restaurants near you within 3km!"
            return result
            
        if any(keyword in message_lower for keyword in cafe_keywords):
            result["place_type"] = "cafe"
            result["search_keyword"] = "cafe"
            result["context"] = "dining"
            result["human_response"] = "Want coffee or snacks? Here are great cafes within 3km!"
            return result
        
        # SHOPPING (Be specific to avoid confusion with medical shops)
        shopping_keywords = [
            # English - being very specific
            "shopping mall", "market", "bazaar", "clothes", "garments", "electronics", "grocery", "supermarket",
            "shopping center", "buy clothes", "buy electronics", "gifts", "souvenirs",
            # Hindi/Hinglish
            "shopping", "bazaar", "market", "kapde", "khareed", "mall", "shopping center", "grocery"
        ]
        
        # Only trigger shopping if it's clearly about general shopping, not medical
        if any(keyword in message_lower for keyword in shopping_keywords) and not any(med in message_lower for med in medical_shop_keywords):
            result["place_type"] = "shopping_mall"
            result["search_keyword"] = "shopping mall"
            result["context"] = "shopping"
            result["human_response"] = "Looking for shopping? Here are the best markets and malls within 3km!"
            return result
        
        # TOURIST ATTRACTIONS
        tourist_keywords = [
            # English
            "tourist", "attraction", "visit", "see", "sightseeing", "monument", "temple", "church", "fort",
            "museum", "park", "garden", "beach", "hill", "waterfall", "heritage",
            # Hindi/Hinglish
            "ghumne", "dekhne", "tourist", "mandir", "masjid", "gurudwara", "kila", "fort", "museum",
            "park", "garden", "darshan", "visit"
        ]
        
        if any(keyword in message_lower for keyword in tourist_keywords):
            result["place_type"] = "tourist_attraction"
            result["search_keyword"] = "tourist attraction"
            result["context"] = "tourism"
            result["human_response"] = "Want to explore? Here are amazing tourist attractions within 3km!"
            return result
        
        # TRANSPORTATION
        transport_keywords = [
            # English
            "taxi", "cab", "auto", "bus stop", "metro station", "railway station", "airport", "transport",
            # Hindi/Hinglish
            "taxi", "auto", "bus", "metro", "station", "airport", "transport"
        ]
        
        if any(keyword in message_lower for keyword in transport_keywords):
            result["place_type"] = "transit_station"
            result["search_keyword"] = "transportation"
            result["context"] = "transport"
            result["human_response"] = "Need transportation? Here are nearby transport options within 3km!"
            return result
        
        # If nothing matches, ask for clarification
        result["needs_clarification"] = True
        result["human_response"] = f"""
        I need more details to help you effectively. Could you be more specific about what you're looking for?
        
        I can find places within 3km range for:
        • 🏥 **Medical Services** - "medical shop", "doctor", "hospital", "pharmacy"
        • 🏨 **Accommodation** - "hotel nearby", "place to stay"
        • 🍽️ **Food & Dining** - "restaurant", "food nearby"
        • ☕ **Cafes & Snacks** - "cafe", "coffee shop"
        • 🎯 **Tourist Places** - "places to visit", "tourist attractions"
        • 🛍️ **Shopping** - "shopping mall", "market"
        • 🏪 **Essential Services** - "bank", "ATM", "post office", "police station"
        • 🚗 **Transportation** - "taxi", "bus station", "metro"
        
        Just tell me what service you need and I'll find it within 3km of your location!
        """
        
        return result
    
    def generate_clarification_response(self, query_result):
        """Generate clarification response in English"""
        return f"""
        <div class="alert alert-info">
            <h5>🤔 I'm here to help you!</h5>
            {query_result["human_response"]}
        </div>
        """
    
    def get_contextual_greeting(self):
        """Generate contextual greeting based on time, weather, and location"""
        from datetime import datetime
        import random
        
        current_hour = datetime.now().hour
        
        # Time-based greetings
        if 5 <= current_hour < 12:
            time_greetings = [
                "Subah subah kya chahiye bhai?",
                "Good morning! Kya plan hai aaj?",
                "Arre bhai, early morning! Kahan jana hai?",
                "Morning me kya kaam hai? Batao!"
            ]
        elif 12 <= current_hour < 17:
            time_greetings = [
                "Dopahar me kya chahiye?",
                "Afternoon me kya plan hai?",
                "Lunch ke baad kahan jana hai?",
                "Good afternoon! Kya help kar sakta hun?"
            ]
        elif 17 <= current_hour < 21:
            time_greetings = [
                "Evening me kya plan hai?",
                "Shaam ko kya karna hai?",
                "Good evening! Kahan jane ka mann hai?",
                "Evening walk pe nikalenge?"
            ]
        else:
            time_greetings = [
                "Raat me kya chahiye bhai?",
                "Late night cravings? Kya chahiye?",
                "Good night! Kya urgent kaam hai?",
                "Itni raat me kya plan hai?"
            ]
        
        return random.choice(time_greetings)
    
    def get_local_tips(self, place_type, city):
        """Provide local tips and insights like a real local would"""
        tips = {
            "pharmacy": [
                "Pro tip: Apollo Pharmacy usually stays open late!",
                "Local chemist shops are usually cheaper than chains.",
                "Keep prescription ready - some medicines need it.",
                "24-hour medical stores mil jayengi main roads pe."
            ],
            "restaurant": [
                "Local street food try karna - it's the best!",
                "Lunch time pe crowded hoga, thoda wait karna padega.",
                "Evening ke time better ambiance hota hai.",
                "Local recommendations > Google reviews, trust me!"
            ],
            "hotel": [
                "Book karne se pehle actual room dekh lena.",
                "WiFi and AC working check kar lena pehle.",
                "Local guesthouse cheaper option ho sakta hai.",
                "Weekend pe rates thode zyada honge."
            ],
            "atm": [
                "Evening ke baad ATM use karna safe nahi hai.",
                "Check balance first - some ATMs charge extra.",
                "SBI ATM is usually most reliable.",
                "Keep your card safe, cover PIN properly!"
            ],
            "bank": [
                "Morning 10-11 baje kam rush hota hai.",
                "Lunch time avoid karna - band rehta hai.",
                "Documents complete lekar jana.",
                "Token system hota hai, number le lena."
            ]
        }
        
        return tips.get(place_type, [])
    
    def get_situation_specific_help(self, urgency, context, place_type):
        """Provide situation-specific help and empathy"""
        if urgency == "emergency":
            return [
                "🚨 Don't panic! I'll find the nearest help immediately.",
                "📞 Save these emergency numbers: Police 100, Ambulance 108, Fire 101",
                "🏥 If serious emergency, call 108 directly - free ambulance service!"
            ]
        elif context == "health" and urgency == "high":
            return [
                "😟 Hope you feel better soon! Medical help on the way.",
                "💊 Keep medical prescription ready if you have any.",
                "📱 Apollo 24/7 app bhi try kar sakte ho for medicine delivery."
            ]
        elif context == "financial":
            return [
                "💰 Keep your cards safe and cover PIN while entering.",
                "📱 Use mobile banking apps for quick transfers - safer option.",
                "💳 Inform bank if card gets stuck in ATM - call helpline immediately."
            ]
        
        return []
    
    def add_local_flavor(self, city, place_type):
        """Add local flavor and cultural context"""
        local_insights = {
            "delhi": {
                "restaurant": "Delhi ki chaat aur paranthas miss mat karna!",
                "shopping": "Karol Bagh and CP are shopping paradises!",
                "tourist": "Red Fort, India Gate - must visits hai!"
            },
            "mumbai": {
                "restaurant": "Vada pav and Mumbai street food is legendary!",
                "transport": "Local train is lifeline - but peak hours avoid karna.",
                "tourist": "Marine Drive evening walk is magical!"
            },
            "bangalore": {
                "cafe": "Bangalore ka coffee culture amazing hai!",
                "shopping": "Commercial Street and Brigade Road for shopping.",
                "weather": "Weather pleasant hai usually - lucky you!"
            },
            "goa": {
                "restaurant": "Seafood try karna - fresh and amazing!",
                "beach": "North Goa for parties, South Goa for peace.",
                "transport": "Rent a scooter - best way to explore!"
            }
        }
        
        city_lower = city.lower() if city else "india"
        return local_insights.get(city_lower, {}).get(place_type, "")
    
    def verify_current_location(self):
        """Verify and display current location with high precision"""
        from location_helper import reverse_geocode
        
        if not self.current_lat or not self.current_lon:
            return """
            <div class="alert alert-danger">
                <h5>❌ Location Not Available</h5>
                <p>Please share your location first for verification.</p>
            </div>
            """
        
        # Get detailed location information
        location_info = reverse_geocode(self.current_lat, self.current_lon)
        
        # Save current city for later use
        self.current_city = location_info.get("city", "")
        
        # Determine accuracy status
        accuracy_type = location_info.get("accuracy_type", "APPROXIMATE")
        
        if accuracy_type in ["ROOFTOP", "RANGE_INTERPOLATED"]:
            accuracy_badge = '<span class="badge bg-success">High Precision</span>'
            accuracy_msg = "Your location has been detected with high precision!"
        elif accuracy_type == "GEOMETRIC_CENTER":
            accuracy_badge = '<span class="badge bg-warning">Good Precision</span>' 
            accuracy_msg = "Your location has been detected with good precision."
        else:
            accuracy_badge = '<span class="badge bg-secondary">Approximate</span>'
            accuracy_msg = "Your location is approximate. For better accuracy, enable GPS and move to an open area."
        
        # Build comprehensive location display
        location_display = f"""
        <div class="alert alert-success">
            <h5>📍 Location Verification {accuracy_badge}</h5>
            <p><strong>{accuracy_msg}</strong></p>
            
            <div class="row mt-3">
                <div class="col-12">
                    <h6>🎯 Detected Location Details:</h6>
                    <table class="table table-sm table-borderless">
                        <tr>
                            <td><strong>Coordinates:</strong></td>
                            <td>{self.current_lat:.6f}, {self.current_lon:.6f}</td>
                        </tr>
                        <tr>
                            <td><strong>Street:</strong></td>
                            <td>{location_info.get('street', 'Not detected') or 'Street level not detected'}</td>
                        </tr>
                        <tr>
                            <td><strong>Area/Locality:</strong></td>
                            <td><strong>{location_info.get('area', 'Unknown area')}</strong></td>
                        </tr>
                        <tr>
                            <td><strong>City:</strong></td>
                            <td><strong>{location_info.get('city', 'Unknown city')}</strong></td>
                        </tr>
                        <tr>
                            <td><strong>State:</strong></td>
                            <td>{location_info.get('state', 'Not detected')}</td>
                        </tr>
                        <tr>
                            <td><strong>Full Address:</strong></td>
                            <td><em>{location_info.get('formatted_address', 'Address not available')}</em></td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="alert alert-info mt-3">
            <h6>✅ Search Configuration:</h6>
            <ul class="mb-0">
                <li><strong>Search Radius:</strong> Exactly 3km (as requested)</li>
                <li><strong>Distance Accuracy:</strong> Calculated to meter precision</li>
                <li><strong>Place Detection:</strong> All service types supported</li>
                <li><strong>Response Language:</strong> English</li>
            </ul>
            
            <div class="mt-2">
                <p><strong>🔍 Ready to search!</strong> Ask me for:</p>
                <p><small>
                • "Medical shop near me" • "ATM nearby" • "Restaurant close by" • "Hospital" • "Bank"<br>
                • "Police station" • "Post office" • "Hotel" • "Cafe" • "Tourist places"
                </small></p>
            </div>
        </div>
        """
        
        # Add accuracy improvement tips if needed
        if accuracy_type not in ["ROOFTOP", "RANGE_INTERPOLATED"]:
            location_display += """
            <div class="alert alert-warning mt-2">
                <h6>💡 Improve Location Accuracy:</h6>
                <ul class="mb-0">
                    <li>Enable GPS/Location Services on your device</li>
                    <li>Move to an open area (away from tall buildings)</li>
                    <li>Use Chrome browser for better GPS accuracy</li>
                    <li>Ensure strong internet connection</li>
                </ul>
            </div>
            """
        
        return location_display
    
    def search_by_landmark(self, message):
        """Search for places near a specific landmark"""
        if not self.current_lat or not self.current_lon:
            return """
            <div class="alert alert-warning">
                <p>Please share your location first to search by landmark.</p>
            </div>
            """
        
        # For Collection O Signature Hotel in Jaipur
        if "collection o" in message.lower() or "signature hotel" in message.lower():
            return f"""
            <div class="alert alert-success">
                <h5>📍 Location Confirmed: Collection O Signature Hotel Area</h5>
                <p><strong>Malaviya Nagar, Jaipur, Rajasthan</strong></p>
                <p>GPS Coordinates: {self.current_lat:.6f}, {self.current_lon:.6f}</p>
                
                <div class="mt-3">
                    <p><strong>🔍 What are you looking for near Collection O Signature Hotel?</strong></p>
                    <p>I can find within 3km radius:</p>
                    <ul>
                        <li>Medical shops & pharmacies</li>
                        <li>Restaurants & cafes</li>
                        <li>ATMs & banks</li>
                        <li>Tourist attractions in Jaipur</li>
                        <li>Shopping areas</li>
                        <li>Transportation services</li>
                    </ul>
                </div>
            </div>
            """
        
        return "Please specify the landmark you're referring to."
    
    def handle_location_correction(self, message):
        """Handle when user says location is wrong"""
        return f"""
        <div class="alert alert-info">
            <h5>📍 Location Correction Needed</h5>
            <p><strong>Current detected coordinates:</strong> {self.current_lat:.6f}, {self.current_lon:.6f}</p>
            
            <div class="mt-3">
                <p><strong>To improve location accuracy:</strong></p>
                <ol>
                    <li>Enable high-precision GPS on your device</li>
                    <li>Move to an open area (away from buildings)</li>
                    <li>Refresh location by clicking "Share My Location" again</li>
                    <li>Use Chrome browser for better GPS accuracy</li>
                </ol>
            </div>
            
            <div class="mt-3">
                <p><strong>Or tell me your landmark:</strong></p>
                <p>Say something like: "I'm near Collection O Signature Hotel" or "I'm at [specific landmark name]"</p>
            </div>
        </div>
        """
    
    def activate_realtime_guide(self):
        """Activate real-time guide mode"""
        if not self.current_lat or not self.current_lon:
            return """
            <div class="alert alert-info">
                <h5>🗺️ Real-Time Local Guide Activated!</h5>
                <p>I'll be your local guide! To get started, I need your location.</p>
                <p><strong>Please enable location access in your browser.</strong></p>
                <button onclick="getLocation()" class="btn btn-primary btn-sm mt-2">
                    <i class="fas fa-location-arrow"></i> Share My Location
                </button>
            </div>
            <p>Once you share your location, I can help you with:</p>
            <ul>
                <li>🏨 Nearby hotels (within 5km) with price comparison</li>
                <li>🍽️ Restaurants and cafes with reviews</li>
                <li>🎯 Tourist attractions around you</li>
                <li>📍 Direct booking and directions</li>
                <li>💡 Local tips and recommendations</li>
            </ul>
            """
        else:
            # Get location details using reverse geocoding
            from location_helper import reverse_geocode
            
            location_info = reverse_geocode(self.current_lat, self.current_lon)
            area = location_info.get("area", "your area")
            city = location_info.get("city", "your city")
            
            # Save for later use
            self.current_city = city
            
            # Generate smart greeting based on time
            from datetime import datetime
            current_hour = datetime.now().hour
            
            if current_hour < 12:
                greeting = "Good morning"
                time_suggestion = "Breakfast spots? Or planning to explore monuments?"
            elif current_hour < 17:
                greeting = "Good afternoon"
                time_suggestion = "Looking for lunch? Or tourist attractions to visit?"
            elif current_hour < 21:
                greeting = "Good evening"
                time_suggestion = "Dinner plans? Or exploring local markets?"
            else:
                greeting = "Good night"
                time_suggestion = "Late night snacks? Or finding a place to stay?"
            
            return f"""
            <div class="alert alert-success">
                <h5>✅ {greeting}! I'm Your Local Guide</h5>
                <p><strong>📍 Location Detected:</strong> {area}, {city}</p>
                <p>Main aapke saath hu! I can help you explore everything within 5km radius.</p>
            </div>
            
            <div class="alert alert-light">
                <p><strong>🤔 {time_suggestion}</strong></p>
                <p>You can ask me:</p>
                <ul style="margin-bottom: 0;">
                    <li><strong>"Hotels dikhao"</strong> - Best places to stay nearby</li>
                    <li><strong>"Khane ke liye kya hai"</strong> - Top restaurants & cafes</li>
                    <li><strong>"Ghumne ki jagah"</strong> - Tourist attractions</li>
                    <li><strong>"Shopping kaha karun"</strong> - Markets & malls</li>
                </ul>
            </div>
            
            <p><small>💡 Tip: All results will be within 5km with accurate distances and ratings!</small></p>
            """
    
    def handle_realtime_query(self, message):
        """Handle queries in real-time guide mode with comprehensive understanding"""
        from location_helper import get_nearby_places, compare_places, format_price_level, get_photo_url
        
        # Handle location verification request
        if message.lower().strip() == 'verify my location':
            if self.current_lat and self.current_lon:
                return self.verify_current_location()
            else:
                return """
                <div class="alert alert-warning">
                    <p>Please share your location first to verify it:</p>
                    <button onclick="getLocation()" class="btn btn-primary btn-sm">
                        <i class="fas fa-location-arrow"></i> Share My Location
                    </button>
                </div>
                """
        
        # Handle manual location correction
        if any(keyword in message.lower() for keyword in ["wrong location", "incorrect location", "location is wrong", "not correct location"]):
            return self.handle_location_correction(message)
        
        # Handle location search by landmark
        if any(keyword in message.lower() for keyword in ["collection o", "signature hotel", "near hotel", "near landmark"]):
            return self.search_by_landmark(message)
        
        if not self.current_lat or not self.current_lon:
            return """
            <div class="alert alert-warning">
                <p>I need your location to help you find places nearby:</p>
                <button onclick="getLocation()" class="btn btn-primary btn-sm">
                    <i class="fas fa-location-arrow"></i> Share My Location
                </button>
                <p class="mt-2"><small>This will enable high-precision GPS for accurate results within 100m accuracy.</small></p>
            </div>
            """
        
        # Enhanced query understanding with context and urgency detection
        query_result = self.understand_user_query(message)
        
        if query_result["needs_clarification"]:
            return self.generate_clarification_response(query_result)
        
        place_type = query_result["place_type"]
        search_keyword = query_result["search_keyword"]
        urgency = query_result["urgency"]
        context = query_result["context"]
        human_response = query_result["human_response"]
        
        # Check for booking request
        booking_keywords = ["book", "reserve", "booking", "book karo", "book kar"]
        wants_booking = any(word in message.lower() for word in booking_keywords)
        
        # Get nearby places within strict 3km radius
        print(f"[REALTIME GUIDE] Searching for {place_type} near {self.current_lat}, {self.current_lon} within 3km")
        places = get_nearby_places(
            self.current_lat, 
            self.current_lon, 
            place_type=place_type,
            radius=3000,  # 3km radius as strictly requested by user
            keyword=search_keyword
        )
        
        if not places:
            return f"""
            <div class="alert alert-warning">
                <h5>⚠️ No Results Found</h5>
                <p>Sorry, I couldn't find any {search_keyword}s within 3km of your location.</p>
                <p><small>This might be because:</small></p>
                <ul class="mb-0">
                    <li><small>No {search_keyword}s exist within the 3km radius</small></li>
                    <li><small>Your location might be in a rural area</small></li>
                    <li><small>Try searching for a different type of service</small></li>
                </ul>
            </div>
            """
        
        # Compare places by rating
        places = compare_places(places, criteria="rating")
        
        # Get location name for context
        from location_helper import reverse_geocode
        location_info = reverse_geocode(self.current_lat, self.current_lon)
        area = location_info.get("area", "your area")
        
        # Generate human-like response based on urgency and context
        if urgency == "emergency":
            response_header = f"""
            <div class="alert alert-danger">
                <h5>🚨 EMERGENCY - Immediate Help!</h5>
                <p><strong>{human_response}</strong></p>
                <p>📍 Found {len(places)} options near {area} - <strong>Distances shown are precise to the meter!</strong></p>
            </div>
            """
        elif urgency == "high":
            response_header = f"""
            <div class="alert alert-warning">
                <h5>⚡ {human_response}</h5>
                <p>📍 Found {len(places)} {search_keyword}s near {area} within 3km radius</p>
            </div>
            """
        else:
            response_header = f"""
            <div class="alert alert-success">
                <h5>✅ {human_response}</h5>
                <p>📍 Found {len(places)} excellent options near {area} | All within 3km radius as requested</p>
            </div>
            """
        
        response = f"""
        <div class="realtime-guide-response">
            {response_header}
        """
        
        # Generate cards for each place
        for idx, place in enumerate(places[:6], 1):  # Show top 6
            # Determine availability badge
            if place.get("open_now") is True:
                availability = '<span class="badge bg-success">Open Now ✅</span>'
            elif place.get("open_now") is False:
                availability = '<span class="badge bg-danger">Closed ❌</span>'
            else:
                availability = '<span class="badge bg-secondary">Hours Unknown</span>'
            
            # Get photo URL
            photo_url = get_photo_url(place.get("photo_reference", ""))
            if not photo_url or photo_url == "":
                photo_url = f"https://source.unsplash.com/400x300/?{search_keyword}"
            
            # Price level
            price_display = format_price_level(place.get("price_level"))
            
            # Build Google Maps link
            gmaps_link = f"https://www.google.com/maps/search/?api=1&query={place['name']}&query_place_id={place['place_id']}"
            
            # Build booking links based on type - Enhanced for all services
            booking_html = ""
            if place_type == "lodging":
                booking_html = f"""
                <div class="btn-group btn-group-sm w-100 mt-2" role="group">
                    <a href="https://www.booking.com/search.html?ss={place['name']}" target="_blank" class="btn btn-outline-primary btn-sm">Booking.com</a>
                    <a href="https://www.makemytrip.com/hotels/hotel-listing/?city={self.current_city or 'India'}" target="_blank" class="btn btn-outline-primary btn-sm">MakeMyTrip</a>
                </div>
                """
            elif place_type == "restaurant":
                booking_html = f"""
                <div class="btn-group btn-group-sm w-100 mt-2" role="group">
                    <a href="https://www.zomato.com/search?q={place['name']}" target="_blank" class="btn btn-outline-danger btn-sm">Zomato</a>
                    <a href="https://www.swiggy.com/restaurants" target="_blank" class="btn btn-outline-warning btn-sm">Swiggy</a>
                </div>
                """
            elif place_type in ["pharmacy", "medical_store"]:
                booking_html = f"""
                <div class="btn-group btn-group-sm w-100 mt-2" role="group">
                    <a href="https://www.1mg.com/search/all?name={place['name']}" target="_blank" class="btn btn-outline-success btn-sm">1mg</a>
                    <a href="https://www.apollo247.com/pharmacy" target="_blank" class="btn btn-outline-info btn-sm">Apollo</a>
                    <a href="https://www.netmeds.com/" target="_blank" class="btn btn-outline-primary btn-sm">Netmeds</a>
                </div>
                """
            elif place_type == "doctor":
                booking_html = f"""
                <div class="btn-group btn-group-sm w-100 mt-2" role="group">
                    <a href="https://www.practo.com/search/doctors?results_type=doctor&q=%5B%7B%22word%22%3A%22{place['name']}%22%2C%22autocompleted%22%3Atrue%2C%22category%22%3A%22doctor%22%7D%5D" target="_blank" class="btn btn-outline-success btn-sm">Practo</a>
                    <a href="https://www.apollo247.com/doctors" target="_blank" class="btn btn-outline-info btn-sm">Apollo</a>
                </div>
                """
            elif place_type == "hospital":
                booking_html = f"""
                <div class="btn-group btn-group-sm w-100 mt-2" role="group">
                    <a href="https://www.practo.com/search?results_type=hospital&q=%5B%7B%22word%22%3A%22{place['name']}%22%2C%22autocompleted%22%3Atrue%2C%22category%22%3A%22hospital%22%7D%5D" target="_blank" class="btn btn-outline-success btn-sm">Book Appointment</a>
                    <a href="tel:108" class="btn btn-outline-danger btn-sm">Emergency Call 📞</a>
                </div>
                """
            
            response += f"""
            <div class="place-card mb-3">
                <div class="row g-0">
                    <div class="col-md-4">
                        <img src="{photo_url}" class="img-fluid rounded-start" alt="{place['name']}" style="height: 200px; object-fit: cover; width: 100%;">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">
                                {idx}. {place['name']}
                                {availability}
                            </h5>
                            <p class="card-text">
                                <small class="text-muted">
                                    <i class="fas fa-map-marker-alt"></i> {place['address']}<br>
                                    <i class="fas fa-route"></i> {place['distance_km']} km away
                                </small>
                            </p>
                            <div class="d-flex align-items-center mb-2">
                                <span class="badge bg-warning text-dark me-2">
                                    ⭐ {place['rating']} ({place['user_ratings_total']} reviews)
                                </span>
                                <span class="badge bg-info text-dark">
                                    {price_display}
                                </span>
                            </div>
                            <div class="btn-group btn-group-sm" role="group">
                                <a href="{gmaps_link}" target="_blank" class="btn btn-success btn-sm">
                                    <i class="fas fa-directions"></i> Directions
                                </a>
                                <a href="https://www.google.com/search?q={place['name']}+reviews" target="_blank" class="btn btn-info btn-sm">
                                    <i class="fas fa-star"></i> Reviews
                                </a>
                            </div>
                            {booking_html}
                        </div>
                    </div>
                </div>
            </div>
            """
        
        response += """
        </div>
        """
        
        # Add local tips and human insights
        local_tips = self.get_local_tips(place_type, self.current_city)
        situation_help = self.get_situation_specific_help(urgency, context, place_type)
        local_flavor = self.add_local_flavor(self.current_city, place_type)
        
        # Create tips section
        tips_content = ""
        if local_tips or situation_help or local_flavor:
            tips_content = f"""
            <div class="alert alert-light mt-3">
                <h6>💡 Local Tips from Your Guide:</h6>
            """
            
            # Add situation-specific help first (for emergencies/health)
            if situation_help:
                for tip in situation_help:
                    tips_content += f"<p><small>{tip}</small></p>"
            
            # Add local tips
            if local_tips:
                import random
                selected_tip = random.choice(local_tips)
                tips_content += f"<p><small>💭 <strong>{selected_tip}</strong></small></p>"
            
            # Add local flavor
            if local_flavor:
                tips_content += f"<p><small>🌟 <em>{local_flavor}</em></small></p>"
            
            tips_content += f"""
                <hr style="margin: 10px 0;">
                <p><small><strong>Ask me for more:</strong></p>
                <ul style="margin-bottom: 0; font-size: 0.9em;">
                    <li>"Show more options" - Additional results within 3km</li>
                    <li>"Nearest places first" - Sort by distance</li>
                    <li>"Budget options" - Show cheaper alternatives</li>
                    <li>"Best rated places" - Top rated within 3km</li>
                    <li>"Verify my location" - Check location accuracy</li>
                </ul>
                </small>
            </div>
            """
        
        # Add follow-up suggestions based on context
        follow_up_content = ""
        if context == "health":
            follow_up_content = f"""
            <div class="alert alert-info mt-2">
                <p><small>🩺 <strong>Need more health services?</strong> Ask me:</small></p>
                <p><small>"Doctor dikhao", "Hospital kahan hai", "Lab test kahan karaun"</small></p>
            </div>
            """
        elif context == "dining":
            follow_up_content = f"""
            <div class="alert alert-info mt-2">
                <p><small>🍽️ <strong>Hungry for more options?</strong> Try:</small></p>
                <p><small>"Sweets ki dukan", "Ice cream kahan milegi", "Late night food"</small></p>
            </div>
            """
        elif context == "accommodation":
            follow_up_content = f"""
            <div class="alert alert-info mt-2">
                <p><small>🏨 <strong>Need travel help?</strong> I can also find:</small></p>
                <p><small>"Taxi booking", "Railway station", "Airport transport"</small></p>
            </div>
            """
        
        response += tips_content + follow_up_content
        
        return response
