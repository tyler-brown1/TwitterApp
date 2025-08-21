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
    add_user(cursor, 'mailo')
    add_post(cursor, 1, 'First post')
    add_post(cursor, 2, 'Second post')
    add_post(cursor, 1, 'Third post')
    add_post(cursor, 2, 'Fourth post')
    #print_users(cursor)
    
    close_connections(conn, cursor)

def close_connections(conn, cursor):
    cursor.close()
    conn.close()

def erase_tables(cursor):
    cursor.execute("DROP TABLE IF EXISTS comments;")
    cursor.execute("DROP TABLE IF EXISTS posts;")
    cursor.execute("DROP TABLE IF EXISTS users;")
    print("Tables erased")
        
def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(10) UNIQUE NOT NULL CHECK (LENGTH(username) >= 4),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("'users' created")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            content VARCHAR(300) NOT NULL,
            image_url VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts (created_at);")
    print("'posts' created")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            post_id INTEGER,
            content VARCHAR(150) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE SET NULL
        );
    """)
    print("'comments' created")
    
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