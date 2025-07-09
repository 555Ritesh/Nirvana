import bcrypt
import jwt
import datetime
import uuid
from functools import wraps
from flask import request, jsonify, session, redirect, url_for
import os
from dotenv import load_dotenv
from db import execute_query

# Load environment variables
load_dotenv('config.env')

# JWT configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key_change_this_in_production')
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

def hash_password(password):
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(hashed_password, user_password):
    """Check hashed password against user input."""
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(username, email, password):
    """Register a new user in the database."""
    # Check if username or email already exists
    query = "SELECT * FROM users WHERE username = %s OR email = %s"
    params = (username, email)
    existing_user = execute_query(query, params, fetch=True)
    
    if existing_user:
        return {'success': False, 'message': 'Username or email already exists.'}
    
    # Hash the password and insert the new user
    hashed_password = hash_password(password)
    insert_query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    insert_params = (username, email, hashed_password)
    user_id = execute_query(insert_query, insert_params)
    
    if user_id:
        return {'success': True, 'user_id': user_id, 'message': 'User registered successfully.'}
    else:
        return {'success': False, 'message': 'Failed to register user.'}

def login_user(email, password):
    """Authenticate a user and return a JWT token."""
    query = "SELECT * FROM users WHERE email = %s"
    params = (email,)
    users = execute_query(query, params, fetch=True)
    
    if not users or len(users) == 0:
        return {'success': False, 'message': 'Invalid email or password.'}
    
    user = users[0]
    
    if check_password(user['password'], password):
        # Create session
        session_id = str(uuid.uuid4())
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        
        # Store session in database
        session_query = "INSERT INTO user_sessions (session_id, user_id, expires_at) VALUES (%s, %s, %s)"
        session_params = (session_id, user['user_id'], expires_at)
        execute_query(session_query, session_params)
        
        # Create JWT token
        payload = {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'session_id': session_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES)
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        
        return {
            'success': True,
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email']
            },
            'message': 'Logged in successfully.'
        }
    else:
        return {'success': False, 'message': 'Invalid email or password.'}

def logout_user(session_id):
    """Log out a user by removing their session."""
    query = "DELETE FROM user_sessions WHERE session_id = %s"
    params = (session_id,)
    execute_query(query, params)
    return {'success': True, 'message': 'Logged out successfully.'}

def get_current_user(token):
    """Get the current user from a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        
        # Check if the session is still valid
        session_query = "SELECT * FROM user_sessions WHERE session_id = %s AND expires_at > NOW()"
        session_params = (payload['session_id'],)
        sessions = execute_query(session_query, session_params, fetch=True)
        
        if not sessions or len(sessions) == 0:
            return None
        
        return {
            'user_id': payload['user_id'],
            'username': payload['username'],
            'email': payload['email'],
            'session_id': payload['session_id']
        }
    except:
        return None

def token_required(f):
    """Decorator for routes that require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        elif 'token' in request.cookies:
            token = request.cookies.get('token')
            
        if not token:
            return redirect(url_for('login'))
        
        current_user = get_current_user(token)
        if current_user is None:
            return redirect(url_for('login'))
            
        return f(current_user, *args, **kwargs)
    
    return decorated 