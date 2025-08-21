from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

DB_HOST = "postgres"
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

@app.route('/api/users', methods=['GET'])
def get_users():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users;")
    data = cursor.fetchall()
    cursor.close()
    return jsonify({'users': data}), 200

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
    obj = {"id": res[0], "username": res[1]}
    return jsonify({"user": obj}), 200

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
        """, (username,))
        return jsonify({"msg": f"User: '{username}' created"})
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": f"Username taken"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5001)
    finally:
        conn.close()