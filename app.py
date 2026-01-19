
# app.py
import os
import pymysql
from flask import Flask, render_template, session, redirect, url_for
from config import get_db_connection
from routes.product_routes import product_bp
from routes.user_routes import user_bp
from routes.cart_routes import cart_bp
from datetime import datetime


UPLOAD_FOLDER = os.path.join("static", "images")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.secret_key = os.getenv("SECRET_KEY", "supersecret")
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

    # Register blueprints
    app.register_blueprint(product_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(cart_bp)

    @app.context_processor
   
    def inject_globals():
        if "user_id" in session:
            user = {
                "id": session.get("user_id"),
                "username": session.get("username"),
                "email": session.get("email"),   # make sure email is stored in session
                "is_admin": session.get("is_admin", 0)
            }
            return dict(logged_user=user)
        return dict(logged_user=None)


    @app.route("/")
    def index():
        db = get_db_connection()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
        products = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template("index.html", products=products)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
