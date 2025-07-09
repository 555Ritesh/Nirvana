# Nirvana - Music Recommendation with User Authentication

Nirvana is a music recommendation application that suggests songs based on mood detection through facial expressions. This enhanced version includes user authentication, song liking/saving, and a personalized dashboard.

## Features

- User authentication (signup, login, logout)
- Personalized dashboard with saved and liked songs
- Song recommendations based on facial expression mood detection
- Song search functionality using Spotify API
- Ability to save and like songs
- Listening history tracking
- Responsive UI for all devices

## Detailed Setup Instructions

### Prerequisites

- Python 3.10 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd recommendation_FaceExpression
```

### 2. Set Up Virtual Environment (Optional but Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

1. Make sure MySQL is installed and running
2. Create a MySQL user or use the existing root user
3. Set up the database using the provided SQL script:

   ```bash
   # On Windows PowerShell
   Get-Content database_setup.sql | mysql -u root -p
   
   # On macOS/Linux or Windows command prompt
   mysql -u root -p < database_setup.sql
   ```

   Enter your MySQL root password when prompted.

4. Verify the database was created:

   ```bash
   mysql -u root -p -e "SHOW DATABASES;"
   ```

   You should see "nirvana_music" in the list.

### 5. Configuration

1. Open `config.env` file and update the MySQL credentials:

   ```
   DB_HOST=localhost
   DB_NAME=nirvana_music
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_PORT=3306
   ```

   Replace `your_mysql_password` with your actual MySQL password.

2. Update Spotify API credentials if needed:

   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   ```

3. Generate and set secure keys for JWT and sessions:

   ```
   SECRET_KEY=your_secret_key
   JWT_SECRET_KEY=your_jwt_secret_key
   ```

### 6. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5001`

### 7. First-time Access

1. Open your browser and go to `http://localhost:5001`
2. You'll be redirected to the login page
3. Click "Sign Up" to create a new account
4. After successful registration, log in with your credentials

## Facial Emotion Detection (Optional)

The application includes a feature to detect mood from facial expressions. However, this requires additional setup:

1. Uncomment the deepface and tensorflow packages in requirements.txt
2. Install these additional packages:
   ```bash
   pip install deepface tensorflow
   ```
3. Edit the app.py file to uncomment the deepface implementation in the detect-mood endpoint

## Troubleshooting

- **Database connection issues**: 
  - Check your MySQL credentials in `config.env`
  - Make sure MySQL server is running
  - Verify the user has permissions to access the database
  
- **Login problems**: 
  - Make sure the database is properly set up with `database_setup.sql`
  - Check that you have tables: users, saved_songs, liked_songs, etc.
  
- **Spotify API issues**: 
  - Verify your Spotify API credentials
  - Make sure you have internet connectivity

- **Model loading issues**:
  - If the recommendation model fails to load, the application will still run but with random recommendations

## User Flow

1. When a user first visits the site, they're directed to the login page
2. After successful login, they can:
   - Search for songs
   - Get mood-based recommendations (manually or via facial expression)
   - Like/save songs
   - View their dashboard with saved/liked songs and history

## 📦 Download Trained Model (.pkl)

The trained Random Forest model (`random_forest_model1.pkl`) is too large to upload directly to GitHub.

👉 You can download it from Google Drive:

🔗 [Click here to download random_forest_model1.pkl (ZIP)](https://drive.google.com/file/d/1qOc8kVBfICRKHK8LcxBEd9DKJDGTY-Gu)

📌 **Instructions:**
1. Download the `.zip` file from the link.
2. Extract it to get `random_forest_model1.pkl`.
3. Place it inside the project root directory (same folder as `app.py`) before running the project.


## License

This project is licensed under the MIT License. 
