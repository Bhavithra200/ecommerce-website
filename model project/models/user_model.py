# models/user_model.py
import pymysql  # Make sure pymysql is imported
from config import get_db_connection

def create_user(username, hashed_password, email, is_admin=0):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, email, is_admin) VALUES (%s, %s, %s, %s)",
            (username, hashed_password, email, is_admin)
        )
        db.commit()
        last_id = cursor.lastrowid
    except Exception as e:
        print("Error creating user:", e)  # Optional: print error for debugging
        db.rollback()
        last_id = None
    finally:
        cursor.close()
        db.close()
    return last_id

def find_user_by_username(username):
    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)  # Use DictCursor for dict result
    try:
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
    finally:
        cursor.close()
        db.close()
    return user

def find_user_by_id(user_id):
    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
    finally:
        cursor.close()
        db.close()
    return user
