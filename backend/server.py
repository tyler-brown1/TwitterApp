# For docker running, change conn.host and turn off debug
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
    return {"id": obj[0], "username": obj[1], "created_at": obj[2]}

# Fetching 1 user also includes username
def parse_post(obj):
    res = {
        "id": obj[0], 
        "user_id": obj[1], 
        "content": obj[2], 
        "image_url": obj[3], 
        "created_at": obj[4],
        'username': obj[5]
    }
    return res

# Get all users
@app.route('/api/users', methods=['GET'])
def get_users():
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, created_at FROM users;")
    data = cursor.fetchall()
    cursor.close()
    return jsonify({'users': list(map(parse_user, data))}), 200

# Get user by username
@app.route('/api/user/username/<username>', methods=['GET'])
def get_user(username):
    username = username
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, created_at FROM users
        WHERE username = %s
    """, (username,))
    res = cursor.fetchone()
    cursor.close()
    if res is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": parse_user(res)}), 200

# Get user by username
@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_id(user_id):
    user_id = user_id
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, created_at FROM users
        WHERE id = %s
    """, (user_id,))
    res = cursor.fetchone()
    cursor.close()
    if res is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": parse_user(res)}), 200

# Add a new user
@app.route('/api/user', methods=['POST'])
def add_user():
    if 'username' not in request.json:
        return jsonify({"error": "Missing field"}), 400
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
        """, (username,))
        return jsonify({"msg": f"User: '{username}' created"})
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": f"Username taken"}), 400
    finally:
        cursor.close()

@app.route('/api/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    if cursor.rowcount == 0:
        cursor.close()
        return jsonify({"error": "Post not found"}), 404
    cursor.close()
    return jsonify({"msg": f"User #{user_id} deleted"}), 200

# Get post by ID
@app.route('/api/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT posts.id, user_id, content, image_url, posts.created_at, username FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.id = %s
    """, (post_id,))
    res = cursor.fetchone()
    cursor.close()
    if res is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({'post': parse_post(res)}), 200

@app.route('/api/post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    if cursor.rowcount == 0:
        cursor.close()
        return jsonify({"error": "Post not found"}), 404
    cursor.close()
    return jsonify({"msg": f"Post #{post_id} deleted"}), 200
    
# Get all posts using pagination
@app.route('/api/feed/new', methods=['GET'])
def get_new():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)
    offset = (page - 1) * limit
    cursor = conn.cursor()
    cursor.execute("""
        SELECT posts.id, user_id, content, image_url, posts.created_at, username FROM posts
        LEFT JOIN users ON posts.user_id = users.id
        ORDER BY created_at DESC
        LiMIT %s OFFSET %s;
    """, (limit, offset))
    data = cursor.fetchall()
    cursor.close()
    return jsonify({'posts': list(map(parse_post, data))}), 200

# Add a new post
@app.route('/api/post', methods=['POST'])
def add_post():
    if 'content' not in request.json or 'user_id' not in request.json:
        return jsonify({"error": "Missing field"}), 400
    if not isinstance(request.json['user_id'], int) or request.json['user_id'] <= 0:
        return jsonify({"error": "Invalid user_id"}), 400
    if len(request.json['content']) > 300 or len(request.json['content']) == 0:
        return jsonify({"error": "Content length error"}), 400
    content = request.json['content']
    user_id = int(request.json['user_id'])
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO posts (user_id, content)
        VALUES (%s, %s)
        """, (user_id, content,))
        return jsonify({"msg": f"Post created"})
    except psycopg2.errors.ForeignKeyViolation:
        return jsonify({"error": f"user_id does not exist"}), 400
    finally:
        cursor.close()
    
if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5001, debug=True)
    finally:
        conn.close()