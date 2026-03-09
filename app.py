from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pandas as pd
import os
import json
import random
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from travel_assistant import TravelAssistant
from dotenv import load_dotenv
from flask_session import Session

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_default_secret_key")

# Configure Flask-Session for persistent sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

# Chat sessions file
CHAT_SESSIONS_FILE = 'chat_sessions.json'

# Initialize chat sessions storage
if not os.path.exists(CHAT_SESSIONS_FILE):
    with open(CHAT_SESSIONS_FILE, 'w') as f:
        json.dump({}, f)

def load_chat_sessions():
    """Load chat sessions from file"""
    try:
        with open(CHAT_SESSIONS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_chat_sessions(sessions):
    """Save chat sessions to file"""
    with open(CHAT_SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f, indent=2)

def get_user_sessions(user_id):
    """Get all sessions for a user, limited to 3 most recent"""
    sessions = load_chat_sessions()
    user_id_str = str(user_id)
    
    if user_id_str not in sessions:
        return []
    
    # Sort by timestamp and limit to 3
    user_sessions = sessions[user_id_str]
    sorted_sessions = sorted(user_sessions, key=lambda x: x['created_at'], reverse=True)[:3]
    return sorted_sessions

def create_new_session(user_id):
    """Create a new chat session for user"""
    sessions = load_chat_sessions()
    user_id_str = str(user_id)
    
    if user_id_str not in sessions:
        sessions[user_id_str] = []
    
    # Create new session
    new_session = {
        'session_id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'created_at': datetime.now().isoformat(),
        'title': 'New Chat',
        'messages': [],
        'assistant_state': {
            'conversation_state': 'initial',
            'location': None
        }
    }
    
    sessions[user_id_str].append(new_session)
    
    # Keep only 3 most recent sessions
    sessions[user_id_str] = sorted(sessions[user_id_str], key=lambda x: x['created_at'], reverse=True)[:3]
    
    save_chat_sessions(sessions)
    return new_session['session_id']

def save_session_data(user_id, session_id, messages, assistant_state):
    """Save session data"""
    sessions = load_chat_sessions()
    user_id_str = str(user_id)
    
    if user_id_str not in sessions:
        return
    
    # Find and update the session
    for session in sessions[user_id_str]:
        if session['session_id'] == session_id:
            session['messages'] = messages
            session['assistant_state'] = assistant_state
            
            # Update title based on first user message
            if messages and session['title'] == 'New Chat':
                first_user_msg = next((m['message'] for m in messages if m['sender'] == 'user'), None)
                if first_user_msg:
                    session['title'] = first_user_msg[:50] + ('...' if len(first_user_msg) > 50 else '')
            break
    
    save_chat_sessions(sessions)

def get_session_data(user_id, session_id):
    """Get session data"""
    sessions = load_chat_sessions()
    user_id_str = str(user_id)
    
    if user_id_str not in sessions:
        return None
    
    for session in sessions[user_id_str]:
        if session['session_id'] == session_id:
            return session
    
    return None

def delete_session(user_id, session_id):
    """Delete a session"""
    sessions = load_chat_sessions()
    user_id_str = str(user_id)
    
    if user_id_str not in sessions:
        return
    
    sessions[user_id_str] = [s for s in sessions[user_id_str] if s['session_id'] != session_id]
    save_chat_sessions(sessions)

# Load user database
if not os.path.exists('user_database.csv'):
    # If running for the first time, create the CSV with a sample user
    data = {
        'id': [1],
        'name': ['Harshit Sharma'],
        'age': [28],
        'email': ['harshit@example.com'],
        'password': [generate_password_hash('password123')],
        'salary': [75000]
    }
    df = pd.DataFrame(data)
    df.to_csv('user_database.csv', index=False)
else:
    # Load existing database
    df = pd.read_csv('user_database.csv')

# Helper function to get latest user data
def get_user_df():
    """Reload user database from CSV to get latest data"""
    if os.path.exists('user_database.csv'):
        return pd.read_csv('user_database.csv')
    return df

# Home route
@app.route('/')
def home():
    user_df = get_user_df()
    if 'user_id' in session:
        # Get user name from session
        user_data = user_df[user_df['id'] == session['user_id']]
        if not user_data.empty:
            user_name = user_data.iloc[0]['name']
            return render_template('home.html', logged_in=True, user_name=user_name)
    return render_template('home.html', logged_in=False)

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    user_df = get_user_df()
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        email = request.form['email']
        password = request.form['password']
        salary = int(request.form['salary'])
        
        # Check if email already exists
        if not user_df[user_df['email'] == email].empty:
            flash('Email already exists!')
            return redirect(url_for('signup'))
        
        # Create new user
        new_id = int(user_df['id'].max() + 1) if not user_df.empty else 1
        new_user = {
            'id': new_id,
            'name': name,
            'age': age,
            'email': email,
            'password': generate_password_hash(password),
            'salary': salary
        }
        
        # Add to DataFrame and save
        user_df.loc[len(user_df)] = new_user
        user_df.to_csv('user_database.csv', index=False)
        
        flash('Account created successfully! Please login.')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    user_df = get_user_df()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Find user
        user_data = user_df[user_df['email'] == email]
        
        if not user_data.empty:
            user = user_data.iloc[0]
            if check_password_hash(user['password'], password):
                # Convert numpy int64 to Python int
                session['user_id'] = int(user['id'])
                flash('Logged in successfully!')
                return redirect(url_for('chat'))
        
        flash('Invalid email or password!')
    
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('current_session_id', None)
    flash('Logged out successfully!')
    return redirect(url_for('home'))

# New chat route
@app.route('/new_chat')
def new_chat():
    if 'user_id' not in session:
        flash('Please login to access the chat!')
        return redirect(url_for('login'))
    
    # Create new session
    session_id = create_new_session(session['user_id'])
    session['current_session_id'] = session_id
    
    return redirect(url_for('chat'))

# Load session route
@app.route('/load_session/<session_id>')
def load_session(session_id):
    if 'user_id' not in session:
        flash('Please login to access the chat!')
        return redirect(url_for('login'))
    
    # Verify session belongs to user
    session_data = get_session_data(session['user_id'], session_id)
    if session_data:
        session['current_session_id'] = session_id
    else:
        flash('Session not found!')
    
    return redirect(url_for('chat'))

# Delete session route
@app.route('/delete_session/<session_id>')
def delete_session_route(session_id):
    if 'user_id' not in session:
        flash('Please login to access the chat!')
        return redirect(url_for('login'))
    
    # Delete the session
    delete_session(session['user_id'], session_id)
    
    # If current session was deleted, clear it
    if session.get('current_session_id') == session_id:
        session.pop('current_session_id', None)
    
    flash('Chat session deleted successfully!')
    return redirect(url_for('chat'))

# Chat route
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    user_df = get_user_df()
    if 'user_id' not in session:
        flash('Please login to access the chat!')
        return redirect(url_for('login'))
    
    user_data = user_df[user_df['id'] == session['user_id']]
    if user_data.empty:
        flash('User not found!')
        return redirect(url_for('logout'))
    
    user_name = user_data.iloc[0]['name']
    user_salary = int(user_data.iloc[0]['salary'])
    
    # Get or create current session
    if 'current_session_id' not in session:
        session_id = create_new_session(session['user_id'])
        session['current_session_id'] = session_id
    else:
        session_id = session['current_session_id']
    
    # Load session data
    session_data = get_session_data(session['user_id'], session_id)
    if not session_data:
        # Session not found, create new one
        session_id = create_new_session(session['user_id'])
        session['current_session_id'] = session_id
        session_data = get_session_data(session['user_id'], session_id)
    
    chat_history = session_data['messages']
    assistant_state = session_data['assistant_state']
    
    # Initialize travel assistant
    user_info = {
        'name': user_name,
        'salary': user_salary
    }
    
    assistant = TravelAssistant(user_info)
    assistant.conversation_state = assistant_state.get('conversation_state', 'initial')
    assistant.location = assistant_state.get('location')
    assistant.realtime_mode = assistant_state.get('realtime_mode', False)
    assistant.current_lat = assistant_state.get('current_lat')
    assistant.current_lon = assistant_state.get('current_lon')
    assistant.current_city = assistant_state.get('current_city')
    
    if request.method == 'POST':
        user_message = request.form.get('message', '')
        user_lat = request.form.get('lat')
        user_lon = request.form.get('lon')
        # Check if user is explicitly requesting realtime guide mode
        enable_realtime = request.form.get('enable_realtime', 'false').lower() == 'true'
        
        # Convert lat/lon to float if provided
        if user_lat and user_lon:
            try:
                assistant.current_lat = float(user_lat)
                assistant.current_lon = float(user_lon)
                print(f"[LOCATION UPDATE] User at {assistant.current_lat}, {assistant.current_lon}")
            except ValueError:
                print("[ERROR] Invalid lat/lon values")
        
        # Add user message to chat history
        chat_history.append({'sender': 'user', 'message': user_message})
        
        # Process the message and get response (with location if available)
        # force_realtime=True will activate realtime mode for this message
        bot_response = assistant.process_message(
            user_message,
            lat=assistant.current_lat,
            lon=assistant.current_lon,
            force_realtime=enable_realtime
        )
        
        # Add bot response to chat history
        chat_history.append({'sender': 'bot', 'message': bot_response})
        
        # Save session data with all state
        save_session_data(
            session['user_id'], 
            session_id, 
            chat_history,
            {
                'conversation_state': assistant.conversation_state,
                'location': assistant.location,
                'realtime_mode': assistant.realtime_mode,
                'current_lat': assistant.current_lat,
                'current_lon': assistant.current_lon,
                'current_city': assistant.current_city
            }
        )
        
        # For AJAX requests, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'success',
                'message': bot_response
            })
    
    # Get all user sessions for sidebar
    user_sessions = get_user_sessions(session['user_id'])
    
    return render_template('chat.html', 
                         chat_history=chat_history, 
                         user_name=user_name,
                         user_sessions=user_sessions,
                         current_session_id=session_id)

# Generate user database with 500 entries
@app.route('/generate_users', methods=['GET'])
def generate_users():
    # Check if it's localhost
    if request.remote_addr != '127.0.0.1':
        return "Unauthorized", 403
        
    from faker import Faker
    import random
    
    # Set seed for reproducibility
    random.seed(42)
    fake = Faker('en_IN')  # Using Indian locale

    # Function to generate Indian names
    def generate_indian_name():
        first_names = [
            "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Ayaan", "Atharva", 
            "Ishaan", "Shaurya", "Advait", "Rudra", "Kabir", "Dhruv", "Krishna", "Krish",
            "Sahil", "Arnav", "Dhiraj", "Vedant", "Shivam", "Siddharth", "Pranav", "Yash",
            "Aanya", "Aadhya", "Ananya", "Saanvi", "Pari", "Myra", "Diya", "Sara",
            "Siya", "Aarohi", "Anvi", "Divya", "Anika", "Ishita", "Prisha", "Riya",
            "Shreya", "Tanvi", "Vanya", "Neha", "Nisha", "Tara", "Kiara", "Mahi",
            "Harshit", "Rahul", "Amit", "Rohit", "Vikas", "Sanjay", "Rajesh", "Deepak",
            "Ajay", "Vijay", "Ravi", "Rajiv", "Amar", "Naveen", "Preeti", "Pooja",
            "Rekha", "Sunita", "Anita", "Kavita", "Meena", "Usha", "Anjali", "Jyoti"
        ]
        
        last_names = [
            "Sharma", "Verma", "Patel", "Singh", "Kumar", "Yadav", "Gupta", "Joshi",
            "Thakur", "Shah", "Pandey", "Chopra", "Desai", "Bose", "Das", "Kaur",
            "Mishra", "Reddy", "Kapoor", "Iyer", "Jain", "Malhotra", "Mehta", "Nair",
            "Agarwal", "Khanna", "Bansal", "Bhatia", "Chawla", "Dubey", "Garg", "Mehra",
            "Raj", "Bajaj", "Chauhan", "Dalal", "Sarin", "Bhatt", "Ahuja", "Arora",
            "Srivastava", "Chauhan", "Patil", "Wadhwa", "Menon", "Dutta", "Kohli", "Pillai"
        ]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    # Generate 500 user records
    num_users = 500
    user_data = {
        'id': list(range(1, num_users + 1)),  # Use Python list instead of numpy array
        'name': [generate_indian_name() for _ in range(num_users)],
        'age': [random.randint(18, 65) for _ in range(num_users)],  # Python random instead of numpy
        'email': [fake.email() for _ in range(num_users)],
        'password': [generate_password_hash('password' + str(i)) for i in range(1, num_users + 1)],
        'salary': [random.randint(10000, 300001) for _ in range(num_users)]  # Python random
    }

    # Create DataFrame and save to CSV
    df_new = pd.DataFrame(user_data)
    df_new.to_csv('user_database.csv', index=False)
    
    global df
    df = df_new
    
    return f"Generated {num_users} user records and saved to user_database.csv"

if __name__ == '__main__':
    port = int(os.getenv('PORT', 7860))
    app.run(debug=False, host='0.0.0.0', port=port)