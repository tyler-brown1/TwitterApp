import psycopg2
from psycopg2.extras import execute_batch

DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "admin"
DB_PASSWORD = "secret"
DB_NAME = "mydb"


def main():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    erase_tables(cursor)
    create_tables(cursor)
    add_user(cursor, 'tyler')
    add_post(cursor, 1, 'First post')
    #print_users(cursor)
    
    close_connections(conn, cursor)

def close_connections(conn, cursor):
    cursor.close()
    conn.close()

def erase_tables(cursor):
    cursor.execute("DROP TABLE IF EXISTS posts;")
    cursor.execute("DROP TABLE IF EXISTS users;")
    print("Tables erased")
        
def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(10) UNIQUE NOT NULL CHECK (LENGTH(username) >= 4)
        );
    """)
    print("'users' created")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            content VARCHAR(300) NOT NULL,
            image_url VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            INDEX (created_at)
        );
    """)
    print("'posts' created")
    
def print_users(cursor):
    cursor.execute("SELECT * FROM users;")
    rows =  cursor.fetchall()
    for row in rows:
        print(row)

def add_user(cursor, username):
    cursor.execute("""
        INSERT INTO users (username)
        VALUES (%s)
        RETURNING id;
    """, (username,))
    print(f"Added user: '{username} ")
    
def add_post(cursor, user_id, content):
    cursor.execute("""
        INSERT INTO posts (user_id, content)
        VALUES (%s, %s)
        RETURNING id;
    """, (user_id, content))
    print(f"Created post #{cursor.fetchone()[0]}")

def get_user(cursor, username):
    cursor.execute("""
        SELECT * FROM users 
        WHERE username = %s
    """, (username,))
    return cursor.fetchone()

def test_query(cursor):
    cursor.execute("""
        SELECT * FROM users
        WHERE age >= 25
        ORDER BY age ASC
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    
if __name__ == "__main__":
    main()