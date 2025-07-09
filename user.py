from db import execute_query

def save_song(user_id, track_id, song_name, artist_name, album_image_url=None):
    """Save a song to a user's saved songs list."""
    query = """
    INSERT INTO saved_songs (user_id, track_id, song_name, artist_name, album_image_url) 
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE saved_at = CURRENT_TIMESTAMP
    """
    params = (user_id, track_id, song_name, artist_name, album_image_url)
    result = execute_query(query, params)
    return result is not None

def unsave_song(user_id, track_id):
    """Remove a song from a user's saved songs list."""
    query = "DELETE FROM saved_songs WHERE user_id = %s AND track_id = %s"
    params = (user_id, track_id)
    execute_query(query, params)
    return True

def like_song(user_id, track_id, song_name, artist_name, album_image_url=None):
    """Like a song."""
    query = """
    INSERT INTO liked_songs (user_id, track_id, song_name, artist_name, album_image_url) 
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE liked_at = CURRENT_TIMESTAMP
    """
    params = (user_id, track_id, song_name, artist_name, album_image_url)
    result = execute_query(query, params)
    return result is not None

def unlike_song(user_id, track_id):
    """Unlike a song."""
    query = "DELETE FROM liked_songs WHERE user_id = %s AND track_id = %s"
    params = (user_id, track_id)
    execute_query(query, params)
    return True

def add_to_history(user_id, track_id, song_name, artist_name, album_image_url=None):
    """Add a song to the user's listening history."""
    query = """
    INSERT INTO listening_history (user_id, track_id, song_name, artist_name, album_image_url) 
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (user_id, track_id, song_name, artist_name, album_image_url)
    result = execute_query(query, params)
    return result is not None

def get_saved_songs(user_id, limit=50, offset=0):
    """Get all saved songs for a user."""
    query = """
    SELECT * FROM saved_songs 
    WHERE user_id = %s 
    ORDER BY saved_at DESC
    LIMIT %s OFFSET %s
    """
    params = (user_id, limit, offset)
    return execute_query(query, params, fetch=True) or []

def get_liked_songs(user_id, limit=50, offset=0):
    """Get all liked songs for a user."""
    query = """
    SELECT * FROM liked_songs 
    WHERE user_id = %s 
    ORDER BY liked_at DESC
    LIMIT %s OFFSET %s
    """
    params = (user_id, limit, offset)
    return execute_query(query, params, fetch=True) or []

def get_listening_history(user_id, limit=50, offset=0):
    """Get listening history for a user."""
    query = """
    SELECT * FROM listening_history 
    WHERE user_id = %s 
    ORDER BY played_at DESC
    LIMIT %s OFFSET %s
    """
    params = (user_id, limit, offset)
    return execute_query(query, params, fetch=True) or []

def is_song_saved(user_id, track_id):
    """Check if a song is saved by the user."""
    query = "SELECT * FROM saved_songs WHERE user_id = %s AND track_id = %s"
    params = (user_id, track_id)
    result = execute_query(query, params, fetch=True)
    return bool(result)

def is_song_liked(user_id, track_id):
    """Check if a song is liked by the user."""
    query = "SELECT * FROM liked_songs WHERE user_id = %s AND track_id = %s"
    params = (user_id, track_id)
    result = execute_query(query, params, fetch=True)
    return bool(result)

def get_user_profile(user_id):
    """Get a user's profile information."""
    query = "SELECT user_id, username, email, created_at FROM users WHERE user_id = %s"
    params = (user_id,)
    users = execute_query(query, params, fetch=True)
    if users and len(users) > 0:
        user = users[0]
        
        # Count saved and liked songs
        saved_count_query = "SELECT COUNT(*) as count FROM saved_songs WHERE user_id = %s"
        liked_count_query = "SELECT COUNT(*) as count FROM liked_songs WHERE user_id = %s"
        
        saved_count = execute_query(saved_count_query, (user_id,), fetch=True)
        liked_count = execute_query(liked_count_query, (user_id,), fetch=True)
        
        user['saved_songs_count'] = saved_count[0]['count'] if saved_count else 0
        user['liked_songs_count'] = liked_count[0]['count'] if liked_count else 0
        
        return user
    return None 