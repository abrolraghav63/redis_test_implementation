# Redis & MySQL User Search Application

## Project Overview
This application provides a web interface and REST API to search for user information. The system uses Redis for caching and MySQL as the primary database. When a user is searched, the application first checks Redis (fast), and if not found, queries MySQL and caches the result in Redis.

---

## Part 1: Code Structure

### Files Created:
- `app.py` - Flask backend application with API endpoints
- `templates/index.html` - Web interface
- `requirements.txt` - Python dependencies

### How It Works:
1. User enters a name in the web interface
2. Application checks Redis cache first
3. If found in Redis, return immediately
4. If not in Redis, query MySQL database
5. If found in MySQL, cache in Redis and return
6. If not found anywhere, return error message

---

## Part 2: MySQL Setup on VM

### Step 1: Install MySQL Server

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install mysql-server -y
```

**On macOS (using Homebrew):**
```bash
brew install mysql
brew services start mysql
```

**On CentOS/RHEL:**
```bash
sudo yum install mysql-server -y
sudo systemctl start mysqld
```

### Step 2: Secure MySQL Installation

```bash
mysql_secure_installation
```

Follow the prompts:
- Set root password: yes
- Remove anonymous users: yes
- Disable remote root login: yes
- Remove test database: yes
- Reload privilege tables: yes

### Step 3: Create Database and User

```bash
# Connect to MySQL
mysql -u root -p

# Execute these SQL commands:
CREATE DATABASE user_database;
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'app_password';
GRANT ALL PRIVILEGES ON user_database.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 4: Create Users Table

```bash
mysql -u root -p user_database
```

Then execute:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    profession VARCHAR(100),
    age INT,
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_name ON users(name);
```

### Step 5: Load Dummy Data

```sql
-- Insert sample data
INSERT INTO users (name, profession, age, country) VALUES
('John Doe', 'Software Engineer', 28, 'USA'),
('Jane Smith', 'Data Scientist', 32, 'Canada'),
('Michael Johnson', 'Product Manager', 35, 'UK'),
('Sarah Williams', 'UX Designer', 26, 'Australia'),
('Ahmed Hassan', 'DevOps Engineer', 30, 'UAE'),
('Maria Garcia', 'Full Stack Developer', 29, 'Spain'),
('Raj Patel', 'Cloud Architect', 34, 'India'),
('Emily Chen', 'Machine Learning Engineer', 27, 'China'),
('Tom Anderson', 'Security Analyst', 31, 'Canada'),
('Lisa Thompson', 'Business Analyst', 28, 'USA');
```

### Step 6: Verify Data

```sql
SELECT * FROM users;
EXIT;
```

---

## Part 3: Redis Setup on VM

### Step 1: Install Redis Server

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server -y
```

**On macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**On CentOS/RHEL:**
```bash
sudo yum install redis -y
sudo systemctl start redis
```

### Step 2: Start Redis Service

**Ubuntu/Debian:**
```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server  # Start on boot
```

**macOS:**
```bash
brew services start redis
```

**CentOS/RHEL:**
```bash
sudo systemctl start redis
sudo systemctl enable redis  # Start on boot
```

### Step 3: Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

### Step 4: Optional - Redis Configuration

Edit `/etc/redis/redis.conf` for production:

```bash
# Access control
requirepass your_secure_password

# Max memory policy (optional)
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence (optional)
save 900 1
save 300 10
save 60 10000
```

Then restart Redis:
```bash
sudo systemctl restart redis-server
```

### Step 5: Test Redis Connection

```bash
redis-cli
> SET test_key "Hello Redis"
> GET test_key
> DEL test_key
> EXIT
```

---

## Part 4: Python Application Setup

### Step 1: Clone/Navigate to Project

```bash
cd /path/to/Redis_test
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Database Credentials

Edit `app.py` and update the MySQL connection configuration:

```python
mysql_config = {
    'host': 'localhost',
    'user': 'app_user',  # Your MySQL user
    'password': 'app_password',  # Your MySQL password
    'database': 'user_database'
}
```

### Step 5: Run the Application

```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

### Step 6: Access the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

---

## Part 5: API Endpoints

### POST Request (JSON)

**Endpoint:** `http://localhost:5000/api/search`

**Method:** POST

**Request:**
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe"}'
```

**Success Response:**
```json
{
  "success": true,
  "data": {
    "name": "John Doe",
    "profession": "Software Engineer",
    "age": 28,
    "country": "USA"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "User not found"
}
```

---

### GET Request

**Endpoint:** `http://localhost:5000/api/search/<name>`

**Method:** GET

**Request:**
```bash
curl http://localhost:5000/api/search/John%20Doe
```

**Response:** Same as POST endpoint

**Example with different users:**
```bash
# Search for Jane Smith
curl http://localhost:5000/api/search/Jane%20Smith

# Search for Raj Patel
curl http://localhost:5000/api/search/Raj%20Patel
```

---

## Part 6: Testing the Application

### Using Web Interface:
1. Open `http://localhost:5000`
2. Enter a user name (e.g., "John Doe")
3. Click "Search" or press Enter
4. View results

### Using curl/Postman:

**Test 1 - First search (hits MySQL, then caches in Redis):**
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe"}'
```

**Test 2 - Same search again (hits Redis cache):**
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe"}'
```

**Test 3 - Non-existent user:**
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"name": "Non Existent"}'
```

**Test 4 - GET request:**
```bash
curl http://localhost:5000/api/search/Jane%20Smith
```

---

## Part 7: Troubleshooting

### Issue: "Connection refused" for MySQL
- Check MySQL is running: `sudo systemctl status mysql`
- Verify credentials in `app.py`
- Check user permissions: `mysql -u app_user -p`

### Issue: "Connection refused" for Redis
- Check Redis is running: `redis-cli ping`
- Verify Redis port (default 6379)
- Check firewall settings

### Issue: "ModuleNotFoundError"
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

### View Redis Cache
```bash
redis-cli
> KEYS *
> GET "John Doe"
```

### Clear Redis Cache
```bash
redis-cli
> FLUSHALL
> EXIT
```

---

## Part 8: Production Considerations

1. **Security:**
   - Use environment variables for passwords
   - Enable Redis authentication
   - Use SSL/TLS for connections
   - Implement rate limiting

2. **Performance:**
   - Set Redis expiration time (TTL)
   - Use connection pooling
   - Enable database indexing

3. **Monitoring:**
   - Log all queries
   - Monitor cache hit/miss ratio
   - Set up alerts for failures

4. **Scaling:**
   - Use Redis Cluster for high availability
   - Implement MySQL replication
   - Use load balancers

---

## Summary

Your application is now ready to use! The system efficiently handles user searches with Redis caching and MySQL as the primary data source. The web interface provides an intuitive way to search users, while the REST API allows programmatic access.





===========================================================================

Test result -

bob@node01 ~ ➜  curl -X POST http://localhost:5000/api/search   -H "Content-Type: application/json"   -d '{"name": "Jane Smith"}'
{
  "data": {
    "age": 32,
    "country": "Canada",
    "name": "Jane Smith",
    "profession": "Data Scientist"
  },
  "response_time_ms": 5.4,
  "success": true
}

bob@node01 ~ ➜  curl -X POST http://localhost:5000/api/search   -H "Content-Type: application/json"   -d '{"name": "Jane Smith"}'
{
  "data": {
    "age": 32,
    "country": "Canada",
    "name": "Jane Smith",
    "profession": "Data Scientist"
  },
  "response_time_ms": 0.47,
  "success": true
}