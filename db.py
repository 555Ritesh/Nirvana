import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables from config.env
load_dotenv('config.env')

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'nirvana_music'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'user'),
    'port': os.getenv('DB_PORT', '3306')
}

# Print current configuration for debugging
print(f"DB Config: {DB_CONFIG}")

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def execute_query(query, params=None, fetch=False, many=False):
    """Execute a SQL query with parameters and optionally fetch results"""
    connection = get_db_connection()
    result = None
    
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            if many:
                cursor.executemany(query, params)
            else:
                cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.lastrowid
            
    except Error as e:
        print(f"Error executing query: {e}")
        print(f"Query was: {query}")
        if params:
            print(f"Params were: {params}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return result 