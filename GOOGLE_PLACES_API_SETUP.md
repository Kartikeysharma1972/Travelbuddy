# 🗺️ Google Places API Setup Guide (100% FREE!)

## ✅ What You'll Get

- **40,000 FREE requests per month** (enough for 1000+ users!)
- **Real hotel, restaurant, cafe data**
- **Actual photos, ratings, reviews**
- **Open/closed status**
- **Accurate addresses & distances**

**Cost for local testing: ₹0 (FREE!)** 🎉

---

## 📋 Step-by-Step Setup (Takes 5 Minutes)

### Step 1: Create Google Cloud Account

1. **Go to**: [Google Cloud Console](https://console.cloud.google.com/)
2. **Sign in** with your Gmail account
3. If first time:
   - Click **"Try for Free"** or **"Get Started"**
   - You'll get **$300 FREE credits** (valid for 90 days)
   - **No credit card required** for Places API!

---

### Step 2: Create a New Project

1. Once logged in, click the **project dropdown** at the top
   - It says "Select a project" or shows current project name
   
2. Click **"NEW PROJECT"** button (top right of popup)

3. **Fill in project details:**
   ```
   Project name: TravelBuddy
   Organization: No organization
   Location: No organization
   ```

4. Click **"CREATE"**

5. Wait 10-20 seconds for project creation

6. You'll see notification: "Project TravelBuddy created"

---

### Step 3: Enable Places API

1. **Open the Navigation Menu** (☰ hamburger icon, top left)

2. Go to: **APIs & Services** → **Library**
   - Or use this direct link: [API Library](https://console.cloud.google.com/apis/library)

3. In the search bar, type: **"Places API"**

4. Click on **"Places API"** (by Google Maps Platform)

5. Click the blue **"ENABLE"** button

6. Wait for it to enable (5-10 seconds)

7. You'll see: "API enabled" ✅

**IMPORTANT**: Also enable these (same process):
- Search "Geocoding API" → Enable
- Search "Geolocation API" → Enable

---

### Step 4: Create API Key

1. After enabling, you'll see **"Credentials"** option

2. Click **"CREATE CREDENTIALS"** button (top of page)

3. Select **"API key"** from dropdown

4. A popup appears: **"API key created"**
   ```
   Your API key:
   AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567
   ```

5. **COPY THIS KEY** immediately! (You'll need it)

6. Click **"CLOSE"** (don't click restrict yet)

---

### Step 5: Restrict API Key (Security - IMPORTANT!)

1. Go to: **APIs & Services** → **Credentials**

2. Find your API key in the list (under "API Keys" section)

3. Click the **pencil icon** (Edit) next to your key

4. **Application restrictions:**
   - Select: **"HTTP referrers (web sites)"**
   - Click **"ADD AN ITEM"**
   - Enter: `http://localhost:5000/*`
   - Click **"ADD AN ITEM"** again
   - Enter: `http://127.0.0.1:5000/*`
   - (Later when deploying, add your domain)

5. **API restrictions:**
   - Select: **"Restrict key"**
   - Check these APIs:
     - ✅ Places API
     - ✅ Geocoding API
     - ✅ Geolocation API

6. Click **"SAVE"** at bottom

7. Wait 5 minutes for changes to apply

---

### Step 6: Add to Your Project

1. Open your project folder: `travelbuddy`

2. Open `.env` file in text editor

3. Add this line (or update if exists):
   ```env
   GOOGLE_PLACES_API_KEY=AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567
   ```
   *(Replace with YOUR actual key)*

4. **FULL `.env` example:**
   ```env
   # Existing keys
   GROQ_API_KEY=your_groq_key
   GEMINI_API_KEY=your_gemini_key
   OPENROUTER_API_KEY=your_openrouter_key
   SERPAPI_API_KEY=your_serpapi_key
   SECRET_KEY=your_secret_key
   
   # NEW: Add this line
   GOOGLE_PLACES_API_KEY=AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567
   ```

5. **Save** the file

---

### Step 7: Test It!

1. **Restart your Flask app:**
   ```bash
   # Stop the app (Ctrl+C)
   python app.py
   ```

2. **Open browser:**
   ```
   http://localhost:5000
   ```

3. **Login and go to Chat**

4. **Click "Real-Time Guide" button** (new button at top!)

5. **Grant location permission**

6. **Type:** `"hotels nearby"`

7. **Check console** (terminal):
   ```
   [API SUCCESS] Found 6 hotels
   ```
   ✅ If you see this = **WORKING WITH REAL DATA!**
   
   ❌ If you see `[WARNING] No Google Places API key` = Check .env file

8. **You should see:**
   - Real hotel names from your area
   - Actual addresses
   - Real ratings & review counts
   - Actual photos
   - Distance from your location

---

## 🎯 How to Verify It's Working

### ✅ Signs of Real Data:
- Hotel names match your actual location
- Addresses are real and nearby
- Photos look professional
- Review counts in thousands
- Distance makes sense (0.5 km, 2.3 km, etc.)

### ❌ Signs of Dummy Data:
- Generic names like "Grand Plaza Hotel"
- Fake addresses
- Stock photos from Unsplash
- Round numbers (500, 1000 reviews)
- Says `[WARNING] No API key` in console

---

## 💰 Billing & Free Tier

### Free Tier Limits (Monthly):
| API | Free Requests | Cost After |
|-----|---------------|------------|
| **Places Nearby Search** | 40,000 | $17 per 1,000 |
| **Place Details** | 40,000 | $17 per 1,000 |
| **Place Photos** | Unlimited | Free |
| **Geocoding** | 40,000 | $5 per 1,000 |

### For Your Use Case (2 Users Testing):
```
Estimated usage per day: 50 queries
With caching (60% reduction): 20 API calls/day
Per month: 600 API calls
Free tier limit: 40,000 calls

Result: 100% FREE! ✅
```

### If You Scale to 100 Users:
```
100 users × 10 queries/day = 1,000 queries
With caching: 400 API calls/day
Per month: 12,000 calls
Free tier limit: 40,000 calls

Result: Still 100% FREE! ✅
```

### If You Scale to 1000 Users:
```
1000 users × 5 queries/day = 5,000 queries
With caching: 2,000 API calls/day
Per month: 60,000 calls
Free tier: 40,000 (FREE)
Extra: 20,000 calls × $0.017 = $340

Result: ~$340/month
BUT with better caching: Can stay under free tier!
```

---

## 🔐 Security Best Practices

### ✅ DO:
1. **Restrict API key** to specific APIs
2. **Add HTTP referrer restrictions** (localhost, your domain)
3. **Use environment variables** (.env file)
4. **Add .env to .gitignore** (don't commit keys!)
5. **Rotate keys** if accidentally exposed
6. **Monitor usage** in Google Cloud Console

### ❌ DON'T:
1. **Don't share API keys** in public repos
2. **Don't hardcode** keys in code
3. **Don't skip restrictions** (anyone can steal!)
4. **Don't use same key** for multiple projects
5. **Don't forget to enable billing** (for alerts)

---

## 📊 Monitor Your Usage

### Check Usage Dashboard:

1. Go to: [Google Cloud Console](https://console.cloud.google.com/)

2. Navigate: **APIs & Services** → **Dashboard**

3. Click on **"Places API"**

4. You'll see:
   - Requests per day (graph)
   - Total requests this month
   - Errors (if any)
   - Quota remaining

5. **Set up alerts:**
   - Click **"Quotas"** in left menu
   - Set alert at 80% of free tier (32,000 requests)
   - Get email when approaching limit

---

## 🐛 Troubleshooting

### Issue 1: "API key not valid"
**Solutions:**
- Wait 5-10 minutes after creating key
- Check if Places API is enabled
- Verify API key copied correctly (no spaces)
- Check restrictions (should allow localhost)

### Issue 2: "This API project is not authorized"
**Solutions:**
- Make sure you enabled Places API
- Check API restrictions (should include Places API)
- Wait a few minutes after enabling

### Issue 3: Still showing dummy data
**Solutions:**
- Check console logs for errors
- Verify .env file has correct key
- Make sure you restarted Flask app
- Check if key has correct restrictions

### Issue 4: "REQUEST_DENIED"
**Solutions:**
- Enable billing (even with $0 cost)
- Verify all 3 APIs enabled (Places, Geocoding, Geolocation)
- Check HTTP referrer restrictions

---

## 🎨 What You'll See After Setup

### Before (Dummy Data):
```
Grand Plaza Hotel
Budget Inn
Luxury Suites
(Generic names, fake addresses)
```

### After (Real Data):
```
The Oberoi Jaipur
Fairmont Jaipur
Radisson Blu Jaipur
(Real hotels with actual ratings!)
```

### Real Features You'll Get:
- ✅ Actual hotel/restaurant names
- ✅ Real addresses with landmarks
- ✅ Accurate ratings (4.3, 4.7, etc.)
- ✅ Real review counts (1,234 reviews)
- ✅ Professional photos
- ✅ Open/closed status (LIVE)
- ✅ Correct distances
- ✅ Real phone numbers
- ✅ Actual websites

---

## 🚀 Quick Test Commands

After setup, test with these:

```bash
# 1. Hotels
"Show hotels nearby"
→ Should show real hotels from your area

# 2. Restaurants
"Restaurants near me"
→ Should show real restaurants

# 3. Cafes
"Coffee shops"
→ Should show actual cafes

# 4. Distance test
"Show closest hotels"
→ Distances should be accurate

# 5. Rating test
"Best rated restaurants"
→ Should show real ratings (4.x)
```

---

## 📱 Alternative: Use Without API Key

If you don't want to setup API key **right now**, the app works with **dummy data**:

### Pros:
- ✅ No setup needed
- ✅ Test all features
- ✅ Show to friends/demo
- ✅ Perfect for development

### Cons:
- ❌ Fake hotel names
- ❌ Generic addresses
- ❌ Stock photos
- ❌ Not useful for real travel

### When to Add API Key:
- When showing to investors
- When deploying for real users
- When need accurate data
- When ready for production

---

## 🎯 Summary

### Setup Checklist:
```bash
☐ 1. Created Google Cloud account
☐ 2. Created "TravelBuddy" project
☐ 3. Enabled Places API
☐ 4. Enabled Geocoding API
☐ 5. Enabled Geolocation API
☐ 6. Created API key
☐ 7. Copied API key
☐ 8. Added restrictions (localhost)
☐ 9. Added to .env file
☐ 10. Restarted Flask app
☐ 11. Tested with "hotels nearby"
☐ 12. Saw real data! ✅
```

### Time Required:
- Google Cloud setup: **2 minutes**
- Enable APIs: **1 minute**
- Create & restrict key: **2 minutes**
- Add to project & test: **1 minute**
- **Total: ~5 minutes** ⏱️

### Cost:
- Setup: **₹0**
- For testing (2 users): **₹0**
- For 100 users: **₹0**
- For 1000 users: **₹340/month** (but can optimize!)

---

## 🎉 Next Steps

After successful setup:

1. **Test all place types:**
   - Hotels
   - Restaurants
   - Cafes
   - Tourist attractions
   - Shopping malls

2. **Test Hindi commands:**
   - "Hotel dikhao"
   - "Khana kaha milega"
   - "Cafe paas mein"

3. **Check caching:**
   - Search same thing twice
   - Second time should be instant
   - Console should show `[CACHE HIT]`

4. **Monitor usage:**
   - Check Google Cloud dashboard daily
   - Set up quota alerts
   - Optimize if approaching limit

---

## 📞 Need Help?

### Resources:
- [Google Places API Docs](https://developers.google.com/maps/documentation/places/web-service/overview)
- [API Key Best Practices](https://developers.google.com/maps/api-security-best-practices)
- [Pricing Calculator](https://mapsplatform.google.com/pricing/)

### Common Issues:
- Check console logs: `F12` → Console
- Check terminal logs: Look for `[API SUCCESS]` or errors
- Verify .env file is in project root
- Make sure Flask app restarted

---

**Congratulations! You now have REAL travel data! 🎊🗺️**

Start testing: Click "Real-Time Guide" button → Grant location → "hotels nearby" 🚀


