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
    
    #erase_tables(cursor)
    #create_tables(cursor)
    print_users(cursor)
    
    close_connections(conn, cursor)

def close_connections(conn, cursor):
    cursor.close()
    conn.close()

def erase_tables(cursor):
    cursor.execute("DROP TABLE IF EXISTS users;")
    print("'users' dropped")
    
def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(10) UNIQUE NOT NULL CHECK (LENGTH(username) >= 4)
        );
    """)
    print("'users' created")
    
def print_users(cursor):
    cursor.execute("SELECT * FROM users;")
    rows =  cursor.fetchall()
    for row in rows:
        print(row)

def add_user(cursor, username):
    cursor.execute("""
        INSERT INTO users (username)
        VALUES (%s)
    """, (username,))
    print(f"Added user: '{username} ")

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