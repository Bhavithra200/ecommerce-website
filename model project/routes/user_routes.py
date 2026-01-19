# routes/user_routes.py
import pymysql
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import create_user, find_user_by_username
from config import get_db_connection

user_bp = Blueprint(
    "user_bp",
    __name__,
    template_folder="../templates",
    url_prefix="/user"
)

@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        email = request.form.get("email", "").strip()

        if not username or not password or not email:
            flash("Please fill all fields", "warning")
            return redirect(url_for("user_bp.register"))

        if find_user_by_username(username):
            flash("Username already taken", "danger")
            return redirect(url_for("user_bp.register"))

        hashed_password = generate_password_hash(password)
        user_id = create_user(username, hashed_password, email)

        if user_id:
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("user_bp.login"))
        else:
            flash("Registration failed. Try again.", "danger")
            return redirect(url_for("user_bp.register"))

    return render_template("register.html")


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            flash("Email is required", "warning")
            return render_template('login.html')

        user = check_user_by_email(email)

        if user:
            # Store all required info in session for navbar
            session['user_id'] = user['id']
            session['username'] = user.get('username')
            session['email'] = user.get('email')
            session['is_admin'] = user.get('is_admin', 0)

            flash(f"Welcome {user['email']}!", "success")
            return redirect(url_for("index"))  # redirect to home page
        else:
            flash("User not found. Please register first.", "info")
            return redirect(url_for("user_bp.register"))

    return render_template('login.html')


def check_user_by_email(email):
    """Check if email exists in DB"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    conn.close()
    return user


@user_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("index"))  # redirect to index
