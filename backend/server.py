# For docker runniung, change conn.host and turn off debug
from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "admin"
DB_PASSWORD = "secret"
DB_NAME = "mydb"

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    dbname=DB_NAME
)
conn.autocommit = True

def parse_user(obj):
    return {"id": obj[0], "username": obj[1]}

# Fetching 1 user also includes username
def parse_post(obj):
    res = {
        "id": obj[0], 
        "user_id": obj[1], 
        "content": obj[2], 
        "image_url": obj[3], 
        "created_at": obj[4]
    }
    if len(obj) == 6:
        res["username"] = obj[5]
    return res

# Get all users
@app.route('/api/users', methods=['GET'])
def get_users():
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users;")
    data = cursor.fetchall()
    cursor.close()
    return jsonify({'users': list(map(parse_user, data))}), 200

# Get user by username
@app.route('/api/user/<username>', methods=['GET'])
def get_user(username):
    username = username
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username FROM users
        WHERE username = %s
    """, (username,))
    res = cursor.fetchone()
    cursor.close()
    if res is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": parse_user(res)}), 200

# Add a new user
@app.route('/api/user', methods=['POST'])
def add_user():
    if 'username' not in request.json:
        return jsonify({"error": "No username"}), 400
    username = request.json['username'].lower()
    if len(username)<4 or len(username)>10:
        return jsonify({"error": "Username must be between 4 and 12 characters"}), 400
    if not username.isalnum():
        return jsonify({"error": "Username must be alphanumeric"}), 400
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO users (username)
        VALUES (%s)
        RETURNING id;             
        """, (username,))
        return jsonify({"msg": f"User: '{username}' created"})
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": f"Username taken"}), 400
    finally:
        cursor.close()

@app.route('/api/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT posts.id, user_id, content, image_url, created_at, username FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.id = %s
    """, (post_id,))
    res = cursor.fetchone()
    cursor.close()
    if res is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({'post': parse_post(res)}), 200

@app.route('/api/posts', methods=['GET'])
def get_posts():
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, content, image_url, created_at FROM posts;")
    data = cursor.fetchall()
    cursor.close()
    return jsonify({'posts': list(map(parse_post, data))}), 200

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5001, debug=True)
    finally:
        conn.close()