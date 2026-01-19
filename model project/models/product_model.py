# models/product_model.py
import pymysql
from config import get_db_connection

def get_all_products():
    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    db.close()
    return products

def get_product_by_id(product_id):
    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    db.close()
    return product

def create_product(name, description, price, stock, image_filename):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO products (name, description, price, stock, image) VALUES (%s, %s, %s, %s, %s)",
        (name, description, price, stock, image_filename)
    )
    db.commit()
    last_id = cursor.lastrowid
    cursor.close()
    db.close()
    return last_id

def update_product(product_id, name, description, price, stock, image_filename=None):
    db = get_db_connection()
    cursor = db.cursor()
    if image_filename:
        cursor.execute(
            "UPDATE products SET name=%s, description=%s, price=%s, stock=%s, image=%s WHERE id=%s",
            (name, description, price, stock, image_filename, product_id)
        )
    else:
        cursor.execute(
            "UPDATE products SET name=%s, description=%s, price=%s, stock=%s WHERE id=%s",
            (name, description, price, stock, product_id)
        )
    db.commit()
    cursor.close()
    db.close()

def delete_product(product_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    db.commit()
    cursor.close()
    db.close()