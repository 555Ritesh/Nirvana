# Nirvana Music App - Complete Setup Guide

This guide provides detailed steps to set up and run the Nirvana Music Application on your machine.

## System Requirements

- Windows, macOS, or Linux operating system
- Python 3.10 or higher
- MySQL 8.0 or higher
- Git (optional)
- 4GB RAM or more recommended
- Internet connection (for Spotify API access)

## Step 1: Download the Project

Either download the ZIP file from the repository or clone it using Git:

```bash
git clone <repository-url>
cd recommendation_FaceExpression
```

## Step 2: Set Up Python Environment

### Install Python

If you don't have Python installed:
1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH" option

### Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

You should see (venv) at the beginning of your command prompt when activated.

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This might take a few minutes as it installs all the necessary libraries.

## Step 4: Set Up MySQL

### Install MySQL

If not already installed:
1. Download MySQL from [mysql.com](https://dev.mysql.com/downloads/mysql/)
2. Follow the installation instructions for your OS
3. Remember the root password you set during installation

### Create the Database and Tables

1. Open a terminal/command prompt
2. Run the database setup script:

   **Windows PowerShell:**
   ```
   Get-Content database_setup.sql | mysql -u root -p
   ```

   **Windows Command Prompt:**
   ```
   mysql -u root -p < database_setup.sql
   ```

   **macOS/Linux:**
   ```
   mysql -u root -p < database_setup.sql
   ```

3. Enter your MySQL root password when prompted
4. Verify the database was created:
   ```
   mysql -u root -p -e "SHOW DATABASES;"
   ```
   
   You should see `nirvana_music` in the list.

## Step 5: Configure the Application

1. Open the `config.env` file in a text editor
2. Update the MySQL connection details:
   ```
   DB_HOST=localhost
   DB_NAME=nirvana_music
   DB_USER=root
   DB_PASSWORD=your_actual_mysql_password
   DB_PORT=3306
   ```
   Replace `your_actual_mysql_password` with your MySQL root password

3. For improved security in production, update these keys:
   ```
   SECRET_KEY=generate_a_random_string_here
   JWT_SECRET_KEY=generate_another_random_string_here
   ```

## Step 6: Run the Application

```bash
python app.py
```

The application should start and be available at `http://localhost:5001` in your web browser.

## Step 7: Create an Account and Log In

1. Visit `http://localhost:5001` in your browser
2. You'll be redirected to the login page
3. Click on "Sign Up" to create a new account
4. Fill out the registration form with your details
5. After registration, log in with your email and password

## Common Issues and Troubleshooting

### Database Connection Error

**Symptom:** "Error connecting to MySQL database: Access denied for user..."

**Solutions:**
- Verify the MySQL password in `config.env` is correct
- Make sure MySQL server is running
- Check if the user has appropriate privileges

```bash
# Grant privileges to MySQL user
mysql -u root -p
GRANT ALL PRIVILEGES ON nirvana_music.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
exit;
```

### Package Installation Issues

**Symptom:** Errors when installing packages from requirements.txt

**Solutions:**
- Update pip: `python -m pip install --upgrade pip`
- Install packages individually to identify problematic ones
- Check Python version compatibility (Python 3.10+ recommended)

### Model Loading Error

**Symptom:** "Error loading model" or recommendation features not working

**Solution:**
- This is usually due to compatibility issues with scikit-learn and numpy
- Try: `pip install numpy==1.23.5 scikit-learn==1.2.2 --force-reinstall`
- Application will still function with random recommendations if model can't be loaded

### Facial Recognition Not Working

**Symptom:** Camera opens but mood detection fails

**Solutions:**
- Install additional packages: `pip install deepface tensorflow`
- Uncomment deepface implementation in app.py
- Make sure your camera is properly connected and accessible

## Using the Application

### Main Features:

1. **Mood-based Music Recommendations**
   - Select a mood from the dropdown
   - Click "Get Recommendations"
   - Use camera detection for automatic mood sensing

2. **Song Search**
   - Use the search bar to find specific songs
   - Results show song details and preview options

3. **User Dashboard**
   - Access via the "Dashboard" link in the navigation bar
   - View saved songs, liked songs, and listening history
   - Manage your profile settings

4. **Save and Like Songs**
   - Click the save button (💾) to save songs for later
   - Use the heart button (♡/❤️) to like your favorite songs

## Next Steps

After successful setup, you might want to:
- Customize the application by modifying the HTML/CSS
- Add your own music datasets for better recommendations
- Implement additional features mentioned in the README
- Deploy the application to a web server for broader access

For any further assistance, please refer to the documentation or contact the development team. 