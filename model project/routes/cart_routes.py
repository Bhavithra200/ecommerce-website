# routes/cart_routes.py
from flask import Blueprint, request, redirect, url_for, flash, render_template, session
from models.product_model import get_product_by_id
from config import get_db_connection
import pymysql
from datetime import datetime
import random
import string



cart_bp = Blueprint("cart_bp", __name__, template_folder="../templates", url_prefix="/cart")

def add_to_cart_db(user_id, product_id, quantity):
    db = get_db_connection()
    cursor = db.cursor()
    # check if exists
    cursor.execute("SELECT id, quantity FROM cart WHERE user_id=%s AND product_id=%s", (user_id, product_id))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE cart SET quantity = quantity + %s WHERE id=%s", (quantity, row[0]))
    else:
        cursor.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
            (user_id, product_id, quantity)
        )
    db.commit()
    cursor.close()
    db.close()

@cart_bp.route("/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    if "user_id" not in session:
        flash("Please login to add to cart", "warning")
        return redirect(url_for("user_bp.login", next=url_for("cart_bp.add_to_cart", product_id=product_id)))

    qty = int(request.form.get("quantity", 1))
    user_id = session["user_id"]

    product = get_product_by_id(product_id)
    if not product:
        flash("Product not found", "warning")
        return redirect(url_for("index"))

    if product['stock'] < qty:
        flash("Not enough stock", "danger")
        return redirect(url_for("product_bp.view_product", product_id=product_id))

    add_to_cart_db(user_id, product_id, qty)
    flash("Added to cart", "success")
    return redirect(url_for("cart_bp.view_cart"))

@cart_bp.route("/")
def view_cart():
    if "user_id" not in session:
        flash("Please login to view cart", "warning")
        return redirect(url_for("user_bp.login", next=url_for("cart_bp.view_cart")))

    user_id = session["user_id"]
    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT c.id as cart_id, p.id as product_id, p.name, p.price, p.image, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id=%s
    """, (user_id,))
    items = cursor.fetchall()
    cursor.close()
    db.close()

    total = sum(float(item["price"]) * item["quantity"] for item in items) if items else 0.0
    return render_template("cart.html", items=items, total=total)

@cart_bp.route("/update/<int:cart_id>", methods=["POST"])
def update_cart(cart_id):
    qty = int(request.form.get("quantity", 1))
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE cart SET quantity=%s WHERE id=%s", (qty, cart_id))
    db.commit()
    cursor.close()
    db.close()
    flash("Cart updated", "success")
    return redirect(url_for("cart_bp.view_cart"))

@cart_bp.route("/remove/<int:cart_id>", methods=["POST"])
def remove_from_cart(cart_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM cart WHERE id=%s", (cart_id,))
    db.commit()
    cursor.close()
    db.close()
    flash("Removed from cart", "info")
    return redirect(url_for("cart_bp.view_cart"))

@cart_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "user_id" not in session:
        flash("Please login to checkout", "warning")
        return redirect(url_for("user_bp.login", next=url_for("cart_bp.checkout")))

    user_id = session["user_id"]
    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Fetch user's cart items from DB
    cursor.execute("""
        SELECT c.id as cart_id, p.id as product_id, p.name, p.price, p.stock, p.image, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id=%s
    """, (user_id,))
    items = cursor.fetchall()

    if not items:
        flash("No items to checkout.", "info")
        cursor.close()
        db.close()
        return redirect(url_for("cart_bp.view_cart"))

    if request.method == "POST":
        # Check stock availability
        for item in items:
            if item['stock'] < item['quantity']:
                flash(f"Not enough stock for {item['name']}", "danger")
                return redirect(url_for("cart_bp.view_cart"))

        # Deduct stock
        for item in items:
            cursor.execute(
                "UPDATE products SET stock = stock - %s WHERE id=%s",
                (item['quantity'], item['product_id'])
            )

        # Clear DB cart
        cursor.execute("DELETE FROM cart WHERE user_id=%s", (user_id,))
        db.commit()
        cursor.close()
        db.close()

        # Clear session cart
        session.pop('cart', None)

        # Pass order info to order confirmation page
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        order_time = datetime.now()
        total = sum(item["price"] * item["quantity"] for item in items)

        return render_template("order_success.html", items=items, total=total, order_time=order_time,order_id=order_id)

    # GET request: show checkout page
    total = sum(item["price"] * item["quantity"] for item in items)
    cursor.close()
    db.close()
    return render_template("checkout.html", items=items, total=total)




@cart_bp.route('/buy_now', methods=['POST'])
def buy_now():
    if "user_id" not in session:
        flash("Please login to buy now", "warning")
        return redirect(url_for("user_bp.login", next=url_for("product_bp.view_product")))

    user_id = session["user_id"]
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 1))

    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Check if product exists and has enough stock
    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()
    if not product:
        flash("Product not found", "danger")
        cursor.close()
        db.close()
        return redirect(url_for("index"))

    if product['stock'] < quantity:
        flash("Not enough stock", "danger")
        cursor.close()
        db.close()
        return redirect(url_for("product_bp.view_product", product_id=product_id))

    # Check if product already in user's cart
    cursor.execute("SELECT id, quantity FROM cart WHERE user_id=%s AND product_id=%s", (user_id, product_id))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE cart SET quantity = quantity + %s WHERE id=%s", (quantity, row['id']))
    else:
        cursor.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
            (user_id, product_id, quantity)
        )

    db.commit()
    cursor.close()
    db.close()

    flash(f"{product['name']} added to cart successfully!", "success")
    return redirect(url_for('cart_bp.checkout'))
