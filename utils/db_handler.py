import streamlit as st
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

def verify_duplicate_user(email):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
    count = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return count > 0


def authenticate_user(email, password):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    # Retrieve the stored hashed password for the user
    cur.execute("SELECT hash_password FROM users WHERE email = %s", (email,))
    stored_hashed_password = cur.fetchone()
    
    cur.close()
    conn.close()

    # Check if a user with the given email was found
    if stored_hashed_password is None:
        return False
    
    stored_hashed_password = stored_hashed_password[0]  # Extract the hash from the tuple

    # Compare the provided password with the stored hashed password
    return bcrypt.checkpw(password.encode(), stored_hashed_password.encode())

    

def save_user(email, password, extra_input_params):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    # Hash the password before saving
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
    
    # Base columns and values
    columns = ['email', 'hash_password']
    values = [email, hashed_password]

    # Add extra input params to the columns and values lists
    for key in extra_input_params.keys():
        columns.append(key)
        values.append(st.session_state[f'{key}'])
    
    # Dynamically build the SQL query
    columns_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(values))
    
    query = sql.SQL("INSERT INTO users ({}) VALUES ({})").format(
        sql.SQL(columns_str),
        sql.SQL(placeholders)
    )
    
    # Execute the query
    cur.execute(query, values)

    conn.commit()
    cur.close()
    conn.close()
    

def get_users():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return users


def get_repos():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM repository")
    repos = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()
    
    return columns, repos


def get_target_servers():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    cur.execute("SELECT name FROM target_server")
    records = cur.fetchall()

    cur.close()
    conn.close()
    
    return records


def create_target_server(server_name: str):

    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    try:
        cur.execute(f"INSERT INTO target_server (name) VALUES ('{server_name}')")
        conn.commit()
    except Exception as err:
        conn.rollback()

    cur.close()
    conn.close()


def delete_repository_table(origin_server: str):
    if not origin_server:
        return

    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    cur.execute(f"DELETE FROM repository WHERE origin_server='{origin_server}'")
    conn.commit()

    cur.close()
    conn.close()
