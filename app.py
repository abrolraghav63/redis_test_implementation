from flask import Flask, render_template, request, jsonify
import redis
import mysql.connector
from mysql.connector import Error
import json
import time

app = Flask(__name__)

# Redis configuration
redis_client = redis.Redis(host='node02', port=6379, db=0, decode_responses=True)

# MySQL configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Change this to your MySQL password
    'database': 'user_database'
}

def get_mysql_connection():
    """Create a MySQL database connection"""
    try:
        connection = mysql.connector.connect(**mysql_config)
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def get_user_data(name):
    """
    Retrieve user data from Redis first, then MySQL if not found
    Returns: dict with name, profession, age, country or None if not found
    """
    # Try Redis first
    cached_data = redis_client.get(name)
    if cached_data:
        return json.loads(cached_data)
    
    # If not in Redis, check MySQL
    connection = get_mysql_connection()
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT name, profession, age, country FROM users WHERE name = %s"
        cursor.execute(query, (name,))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            # Store in Redis for future requests
            redis_client.set(name, json.dumps(user))
            return user
        return None
    except Error as e:
        print(f"Error retrieving data from MySQL: {e}")
        return None
    finally:
        connection.close()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_user():
    """
    API endpoint to search for user data
    Expects JSON: {"name": "user_name"}
    Returns: JSON with user data, response time (in ms), and error message
    """
    start_time = time.time()
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        return jsonify({
            'error': 'Name is required',
            'response_time_ms': round(response_time, 2)
        }), 400
    
    user_data = get_user_data(name)
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    if user_data:
        return jsonify({
            'success': True,
            'data': user_data,
            'response_time_ms': round(response_time, 2)
        })
    else:
        return jsonify({
            'success': False,
            'error': 'User not found',
            'response_time_ms': round(response_time, 2)
        }), 404

@app.route('/api/search/<name>', methods=['GET'])
def search_user_get(name):
    """
    Alternative GET endpoint for API calls
    Returns: JSON with user data, response time (in ms), or error message
    """
    start_time = time.time()
    
    if not name or not name.strip():
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        return jsonify({
            'error': 'Name is required',
            'response_time_ms': round(response_time, 2)
        }), 400
    
    user_data = get_user_data(name)
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    if user_data:
        return jsonify({
            'success': True,
            'data': user_data,
            'response_time_ms': round(response_time, 2)
        })
    else:
        return jsonify({
            'success': False,
            'error': 'User not found',
            'response_time_ms': round(response_time, 2)
        }), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
