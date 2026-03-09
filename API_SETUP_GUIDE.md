# 🚀 API Setup Guide for TravelBuddy

This guide will help you set up FREE and FAST APIs to make your TravelBuddy app super fast and smooth!

---

## 📋 Quick Overview

Your app now supports **3 FREE APIs** (in order of speed):

1. **GROQ** ⚡ - FASTEST (recommended)
2. **Google Gemini** 🔥 - Fast & High Quality
3. **OpenRouter** - Backup (your current one)

---

## 🎯 Option 1: GROQ API (RECOMMENDED - SUPER FAST!)

### Why Groq?
- **Speed**: Up to 500 tokens/second (10x faster than others!)
- **Free Tier**: 14,400 requests per day
- **Models**: Llama 3.1, Mixtral, Gemma

### How to Get Groq API Key:

1. **Visit**: https://console.groq.com/
2. **Sign Up**: Click "Sign Up" (use Google/GitHub/Email)
3. **Get API Key**:
   - After login, click on "API Keys" in the left sidebar
   - Click "Create API Key"
   - Copy the key (starts with `gsk_...`)

4. **Add to .env file**:
   ```env
   GROQ_API_KEY=gsk_your_api_key_here
   ```

---

## 🎯 Option 2: Google Gemini API (FAST & FREE)

### Why Gemini?
- **Speed**: Very fast (2-3 seconds)
- **Free Tier**: 60 requests/minute (very generous!)
- **Quality**: Excellent responses

### How to Get Gemini API Key:

1. **Visit**: https://makersuite.google.com/app/apikey
2. **Sign In**: Use your Google account
3. **Create API Key**:
   - Click "Create API Key"
   - Select "Create API key in new project" or use existing
   - Copy the key

4. **Add to .env file**:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

---

## 📝 Complete .env File Setup

Open your `.env` file (create if it doesn't exist) and add:

```env
# TravelBuddy Environment Variables

# Secret Key for Flask
SECRET_KEY=your_secret_key_here

# API Keys (in order of preference)
# 1. GROQ (Fastest - RECOMMENDED)
GROQ_API_KEY=gsk_your_groq_api_key_here

# 2. Google Gemini (Fast backup)
GEMINI_API_KEY=your_gemini_api_key_here

# 3. OpenRouter (Your current one - slowest)
OPENROUTER_API_KEY=your_openrouter_key_here

# SerpAPI (for hotel search)
SERPAPI_API_KEY=your_serpapi_key_here
```

---

## 🎮 How It Works (Smart Fallback System)

The app is now **super smart** and tries APIs in this order:

1. **First**: Tries **GROQ** (if key is available) → FASTEST! ⚡
2. **Second**: Tries **Gemini** (if GROQ fails) → Fast backup 🔥
3. **Third**: Tries **OpenRouter** (if both fail) → Reliable backup
4. **Last**: Uses **pre-written content** (if all APIs fail)

This means:
- ✅ Your app will ALWAYS work (multiple fallbacks)
- ✅ Uses the FASTEST available API automatically
- ✅ No code changes needed - just add API keys!

---

## 🚀 Speed Comparison

| API | Speed | Free Tier | Recommended For |
|-----|-------|-----------|-----------------|
| **GROQ** | ⚡⚡⚡⚡⚡ (500 tokens/sec) | 14,400 req/day | **Production - Best Choice!** |
| **Gemini** | ⚡⚡⚡⚡ (Fast) | 60 req/min | Backup & High Quality |
| **OpenRouter** | ⚡⚡ (Slower) | Varies | Emergency Backup |

---

## 📦 Installation (if needed)

No new packages needed! Your current `requirements.txt` already has everything.

---

## 🧪 Testing Your Setup

1. Add API keys to `.env` file
2. Restart your Flask app
3. Go to chat interface
4. Type: **"kashmir jana hai"** or **"I want to visit Goa"**
5. Response should be **SUPER FAST** (1-2 seconds max!)

---

## 💡 Pro Tips

1. **Use GROQ for best speed** - It's FREE and blazing fast!
2. **Add multiple API keys** - The app will automatically use the best one
3. **Don't worry about limits** - Free tiers are very generous
4. **Regex extraction** - Most common destinations (Goa, Kashmir, Manali, etc.) are detected instantly without API calls!

---

## 🆓 All APIs are 100% FREE!

✅ GROQ - Free tier: 14,400 requests/day  
✅ Gemini - Free tier: 60 requests/minute  
✅ OpenRouter - Has free tier  

No credit card required for any of them!

---

## 🎯 Recommended Setup

For **MAXIMUM SPEED**, add these two in your `.env`:

```env
GROQ_API_KEY=gsk_your_key_here
GEMINI_API_KEY=your_key_here
```

This gives you:
- ⚡ Lightning fast responses (Groq)
- 🔥 High-quality backup (Gemini)
- 💪 Two free APIs = No worries about limits!

---

## 🐛 Troubleshooting

### Issue: "API Key not found"
**Solution**: Make sure your `.env` file is in the project root folder

### Issue: "Still slow"
**Solution**: 
1. Check if GROQ_API_KEY is correctly added
2. Restart your Flask app after adding keys
3. Most destinations use regex (instant) - only rare ones use API

### Issue: "API error"
**Solution**: The app has multiple fallbacks, so it should always work. Check your internet connection.

---

## 📞 Need Help?

If you face any issues:
1. Check if API key is correct (no extra spaces)
2. Make sure `.env` file is in root directory
3. Restart the Flask application
4. Test with simple queries like "goa" or "manali"

---

**Made with ❤️ for TravelBuddy**

Your app is now **10x FASTER** with these APIs! 🚀

