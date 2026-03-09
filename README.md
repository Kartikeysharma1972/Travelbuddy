---
title: TravelBuddy
emoji: ✈️
colorFrom: purple
colorTo: blue
sdk: docker
app_file: app.py
pinned: false
---

# TravelBuddy 🌍✈️

A smart AI-powered travel planning assistant that helps users discover destinations and plan their perfect trips with personalized recommendations.

## 🚀 Features

- **Smart Destination Detection** - Understands English, Hindi, and Hinglish
- **ChatGPT-like Interface** - Sidebar with chat history (remembers up to 3 sessions)
- **Personalized Recommendations** - Based on your salary/budget
- **Hotel & Package Suggestions** - Real-time travel package recommendations
- **Multi-language Support** - Works with phrases like "goa jana hai", "kashmir trip", etc.
- **Lightning Fast** - Optimized with multiple free AI APIs

## 🆕 NEW: Real-Time Local Guide

**Click the "Real-Time Guide" button** to activate your personal travel assistant!

### Features:
- 📍 **GPS Location Tracking** - Knows exactly where you are
- 🏨 **Nearby Hotels** - Compares prices, ratings, distance
- 🍽️ **Restaurants & Cafes** - Real reviews, open/closed status
- 🎯 **Tourist Attractions** - Discover places around you
- 🛍️ **Shopping Areas** - Find markets & malls
- 💬 **Hindi/Hinglish Support** - "Hotel dikhao", "Khane ka kya hai"
- 🔗 **Direct Booking** - Links to Booking.com, Zomato, Google Maps

<<<<<<< HEAD

=======
>>>>>>> 3681c442669d59b9b4438aceda57eb007753dfe5

## ⚡ Performance

- **With GROQ API**: Response in 1-2 seconds (super fast!)
- **With Gemini API**: Response in 2-3 seconds (fast)
- **Regex-based detection**: Instant for 100+ popular destinations

## 🗣️ Usage Examples

The bot understands multiple languages and styles:

**English:**
- "I want to go to Goa"
- "Plan a trip to Manali"
- "Show me Kashmir packages"

**Hindi/Hinglish:**
- "kashmir jana hai"
- "mujhe manali ghumna hai"
- "goa trip planning"

**Just destination:**
- "Shimla"
- "Dubai"
- "Kerala"


<<<<<<< HEAD
=======



## 🛠️ Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **AI Models**: 
  - GROQ (Llama 3.1) - Ultra fast
  - Google Gemini 1.5 Flash - High quality
  - Mistral 7B (OpenRouter) - Backup
- **Storage**: JSON (chat history), CSV (user data)
>>>>>>> 3681c442669d59b9b4438aceda57eb007753dfe5

## 📱 Features in Detail

### 1. Smart Chat Interface
- ChatGPT-like sidebar with session history
- Persistent chat sessions (up to 3 per user)
- Real-time message updates
- Mobile responsive

### 2. Intelligent Destination Understanding
- Recognizes 100+ popular destinations instantly
- Understands Hindi, English, and Hinglish
- Works with natural phrases like "jana hai", "trip to", etc.

### 3. Personalized Recommendations
- Budget calculation based on salary
- Custom travel packages
- Hotel suggestions
- Local attractions and activities

### 4. Multi-API Fallback System
- Tries fastest API first (GROQ)
- Automatic fallback to backup APIs
- Always provides results (pre-written content as final fallback)

## 🚀 Deployment

### Docker (Included)
```bash
docker build -t travelbuddy .
docker run -p 5000:5000 travelbuddy
```

### Heroku / Railway / Render
1. Add environment variables in platform settings
2. Deploy from GitHub repository
3. Done!

## 📊 Performance Metrics

- **Response Time**: 1-3 seconds (with GROQ/Gemini)
- **Regex Detection**: Instant (0ms) for popular destinations
- **Uptime**: 99.9% (with multiple API fallbacks)
- **Free Tier Limits**: 14,400 requests/day (GROQ)

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- GROQ for blazing fast inference
- Google Gemini for high-quality AI responses
- OpenRouter for API access
- Bootstrap for UI components

---

## LIVE DEMO 
[https://travelbuddy-an5m.onrender.com]
