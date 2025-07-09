from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
import pandas as pd
import random
import joblib
import requests
import base64
from decouple import config
import os

import numpy as np
import cv2
from deepface import DeepFace


# optional
# to open the app in the browser in mobile or any other device
from flask_cors import CORS

# Import our custom modules
from db import execute_query
from auth import register_user, login_user, logout_user, get_current_user, token_required
from user import (
    save_song, unsave_song, like_song, unlike_song, 
    get_saved_songs, get_liked_songs, get_listening_history,
    is_song_liked, is_song_saved, get_user_profile, add_to_history
)

app = Flask(__name__, 
            static_url_path='/static',
            static_folder='static',
            template_folder='templates')
CORS(app)

# JWT and session configuration
app.config['SECRET_KEY'] = config('SECRET_KEY', default='your_very_secure_secret_key_change_this_in_production')

# Spotify API credentials (should be in .env file)
SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID', default='2ab8b140e3ec4f018f8bd9f4aa686302')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET', default='62c215c84e914ebea35c58b31a59e2f6')

# Define mock model behavior
USE_MODEL = False
try:
    # Try loading the model if it exists
    model = joblib.load("random_forest_model1.pkl")
    USE_MODEL = True
    print("Model loaded successfully!")
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    print("Using random recommendations as fallback.")

# Labels: {'sad': 0, 'happy': 1, 'energetic': 2, 'calm': 3}
mood_to_labels = {
    "sad": [3],        
    "neutral": [3, 1],  
    "happy": [1, 2],    
    "calm": [3],       
    "energetic": [1, 2]
}

def load_dataset(language):
    if language == "hindi":
        return pd.read_csv("HindiSongs_WithTrack_ID.csv")
    elif language == "marathi":
        return pd.read_csv("MarathiSongs_with_Track_ID.csv")
    elif language == "english":
        return pd.read_csv("EnglishSongs_with_Track_ID.csv")
    else:
        return None

# Get current user from cookie
def get_current_user_from_request():
    token = request.cookies.get('token')
    if token:
        return get_current_user(token)
    return None

# Custom decorator to check if user is logged in
def login_required(f):
    def decorated(*args, **kwargs):
        user = get_current_user_from_request()
        if user is None:
            return redirect(url_for('login'))
        return f(user, *args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

# ===== AUTHENTICATION ROUTES =====

@app.route("/", methods=["GET"])
def home():
    user = get_current_user_from_request()
    if user is None:
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route("/login", methods=["GET"])
def login():
    user = get_current_user_from_request()
    if user:
        return redirect(url_for('home'))
    return render_template("login.html")

@app.route("/signup", methods=["GET"])
def signup():
    user = get_current_user_from_request()
    if user:
        return redirect(url_for('home'))
    return render_template("signup.html")

@app.route("/logout", methods=["GET"])
def logout():
    user = get_current_user_from_request()
    if user:
        logout_user(user['session_id'])
    response = make_response(redirect(url_for('login')))
    response.set_cookie('token', '', expires=0)
    return response

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard(user):
    # Get user profile and song lists
    user_profile = get_user_profile(user['user_id'])
    
    # Get saved and liked songs
    saved_songs = get_saved_songs(user['user_id'], limit=20)
    liked_songs = get_liked_songs(user['user_id'], limit=20)
    history = get_listening_history(user['user_id'], limit=20)
    
    # Check liked/saved status for all songs
    for song in saved_songs:
        song['is_liked'] = is_song_liked(user['user_id'], song['track_id'])
    
    for song in liked_songs:
        song['is_saved'] = is_song_saved(user['user_id'], song['track_id'])
    
    for song in history:
        song['is_liked'] = is_song_liked(user['user_id'], song['track_id'])
        song['is_saved'] = is_song_saved(user['user_id'], song['track_id'])
    
    return render_template(
        "dashboard.html", 
        user=user_profile, 
        saved_songs=saved_songs, 
        liked_songs=liked_songs,
        history=history
    )

# ===== API ROUTES =====

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    
    print(f"Registration attempt with data: {data}")
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    try:
        result = register_user(data['username'], data['email'], data['password'])
        print(f"Registration result: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"Exception during registration: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'})

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    result = login_user(data['email'], data['password'])
    return jsonify(result)

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    user = get_current_user_from_request()
    if user:
        result = logout_user(user['session_id'])
        return jsonify(result)
    return jsonify({'success': False, 'message': 'Not logged in'})

@app.route('/api/songs/save', methods=['POST'])
def api_save_song():
    user = get_current_user_from_request()
    if not user:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    if not data or not data.get('track_id') or not data.get('song_name') or not data.get('artist_name'):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    # Check if song is already saved, if yes, unsave it
    if is_song_saved(user['user_id'], data['track_id']):
        unsave_song(user['user_id'], data['track_id'])
        return jsonify({'success': True, 'saved': False, 'message': 'Song removed from saved songs'})
    
    # Otherwise save the song
    success = save_song(
        user['user_id'], 
        data['track_id'], 
        data['song_name'], 
        data['artist_name'], 
        data.get('album_image_url')
    )
    
    if success:
        return jsonify({'success': True, 'saved': True, 'message': 'Song saved successfully'})
    return jsonify({'success': False, 'message': 'Failed to save song'})

@app.route('/api/songs/like', methods=['POST'])
def api_like_song():
    user = get_current_user_from_request()
    if not user:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    if not data or not data.get('track_id') or not data.get('song_name') or not data.get('artist_name'):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    # Check if song is already liked, if yes, unlike it
    if is_song_liked(user['user_id'], data['track_id']):
        unlike_song(user['user_id'], data['track_id'])
        return jsonify({'success': True, 'liked': False, 'message': 'Song removed from liked songs'})
    
    # Otherwise like the song
    success = like_song(
        user['user_id'], 
        data['track_id'], 
        data['song_name'], 
        data['artist_name'], 
        data.get('album_image_url')
    )
    
    if success:
        return jsonify({'success': True, 'liked': True, 'message': 'Song liked successfully'})
    return jsonify({'success': False, 'message': 'Failed to like song'})

@app.route('/api/songs/history', methods=['POST'])
def api_add_to_history():
    user = get_current_user_from_request()
    if not user:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    if not data or not data.get('track_id') or not data.get('song_name') or not data.get('artist_name'):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    success = add_to_history(
        user['user_id'], 
        data['track_id'], 
        data['song_name'], 
        data['artist_name'],
        data.get('album_image_url')
    )
    
    if success:
        return jsonify({'success': True, 'message': 'Added to history'})
    return jsonify({'success': False, 'message': 'Failed to add to history'})

# ===== EXISTING ROUTES =====

@app.route('/get-spotify-token', methods=['GET'])
def get_spotify_token():
    try:
        auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

        response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers={
                'Authorization': f'Basic {auth_base64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={'grant_type': 'client_credentials'}
        )
        
        if response.status_code == 200:
            return jsonify({'access_token': response.json().get('access_token')})
        else:
            return jsonify({'error': 'Failed to get Spotify token'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/recommend", methods=["GET"])
def recommend():
    mood = request.args.get("mood", "").lower()
    language = request.args.get("language", "").lower()
    limit = request.args.get("limit", 10, type=int)
    
    # Cap the limit at 10 to prevent excessive results
    if limit > 10:
        limit = 10

    if mood not in mood_to_labels:
        return jsonify({"error": "Invalid mood selection."}), 400

    df = load_dataset(language)
    if df is None:
        return jsonify({"error": "Invalid language selection."}), 400

    features = ['duration', 'danceability', 'energy', 'loudness', 
                'speechiness', 'acousticness', 'liveness', 'valence', 'tempo']
    
    # Check if all expected features exist in the dataset
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        print(f"Warning: Missing features in dataset: {missing_features}")
        # Use only available features
        features = [f for f in features if f in df.columns]
    
    if not features or not USE_MODEL:
        # If no features or model not loaded, return random recommendations
        sampled_songs = df.sample(n=min(limit, len(df)))
        result = sampled_songs[['song_name', 'singer', 'track_id']].head(limit).to_dict(orient='records')
    else:
        try:
            sampled_songs = df.sample(n=min(100, len(df)))
            sampled_songs['predicted_label'] = model.predict(sampled_songs[features])
            recommended_songs = sampled_songs[sampled_songs['predicted_label'].isin(mood_to_labels[mood])]

            if recommended_songs.empty:
                # Fallback to random if no matches for this mood
                recommended_songs = df.sample(n=min(limit, len(df)))
                
            result = recommended_songs[['song_name', 'singer', 'track_id']].head(limit).to_dict(orient='records')
        except Exception as e:
            print(f"Error predicting with model: {e}")
            # Fallback to random recommendations
            sampled_songs = df.sample(n=min(limit, len(df)))
            result = sampled_songs[['song_name', 'singer', 'track_id']].head(limit).to_dict(orient='records')
    
    # Add liked/saved status if user is logged in
    user = get_current_user_from_request()
    if user:
        for song in result:
            song['is_liked'] = is_song_liked(user['user_id'], song['track_id'])
            song['is_saved'] = is_song_saved(user['user_id'], song['track_id'])
    
    return jsonify(result)

@app.route("/detect-mood", methods=["POST"])
def detect_mood():
    try:
        
        data = request.get_json(force=True)  # Ensures it parses even if header is missing
        img_data = data["image"].split(",")[1]
        image_bytes = base64.b64decode(img_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        analysis = DeepFace.analyze(img, actions=["emotion"], enforce_detection=False)

        dominant_emotion = analysis[0]["dominant_emotion"]
        print("Detected emotion from DeepFace:", dominant_emotion)  #  Debug line

        # Map emotions to mood categories
        if dominant_emotion in ["sad", "fear", "disgust", "angry"]:
            mood = "sad"
        elif dominant_emotion in ["happy", "surprise"]:
            mood = "happy"
        else:
            mood = "neutral"

        return jsonify({"mood": mood})  #  Proper JSON response

    except Exception as e:
        print("Error during mood detection:", str(e))  #  Debug line
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
