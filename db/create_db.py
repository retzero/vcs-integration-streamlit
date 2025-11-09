import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

# Database connection parameters
db_params = {
    "dbname":  os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def create_database():
    # Connect to the default 'postgres' database to create a new database
    conn = psycopg2.connect(dbname="postgres", **{k: v for k, v in db_params.items() if k != "dbname"})
    conn.autocommit = True
    cur = conn.cursor()
    
    # Create the new database
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_params["dbname"])))
    
    cur.close()
    conn.close()

def create_user_table(conn, cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hash_password TEXT NOT NULL
        );
    """)
    conn.commit()

def create_vcs_server_table(conn, cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vcs_server (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            url VARCHAR(255)
        );
    """)
    conn.commit()

def create_repository_table(conn, cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS repository (
            id SERIAL PRIMARY KEY,
            origin_server VARCHAR(1023) NOT NULL,
            repository_path VARCHAR(1023) NOT NULL,
            size_in_bytes BIGINT,
            committer_emails VARCHAR(1023),
            last_commit_date DATE,
            target_server VARCHAR(1023),
            UNIQUE (origin_server, repository_path)
        );
    """)
    conn.commit()

def create_superuser(conn, cur):

    hhashed_password = bcrypt.hashpw(os.getenv("admin_password").encode(), bcrypt.gensalt()).decode('utf-8')
    cur.execute(f"""
        INSERT INTO users (email, hash_password) VALUES('{os.getenv("admin_username")}', '{hhashed_password}');
    """)
    conn.commit()


def create_table():
    # Connect to the new database
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    create_user_table(conn, cur)
    create_vcs_server_table(conn, cur)
    create_repository_table(conn, cur)
    create_superuser(conn, cur)

    cur.close()
    conn.close()


if __name__ == "__main__":
    try:
        create_database()
        print("Database created successfully.")
    except psycopg2.Error as e:
        print(f"Error creating database: {e}")

    try:
        create_table()
        print("Table created successfully.")
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
