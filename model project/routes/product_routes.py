# routes/product_routes.py
import os
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app, session
from werkzeug.utils import secure_filename
from models.product_model import get_product_by_id, create_product, update_product, delete_product, get_all_products

product_bp = Blueprint("product_bp", __name__, template_folder="../templates", url_prefix="/products")

def allowed_file(filename):
    if not filename:
        return False
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', set())

@product_bp.route("/<int:product_id>")
def view_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash("Product not found", "warning")
        return redirect(url_for('index'))
    return render_template("product.html", product=product)

# Admin - product list & create/update/delete
@product_bp.route("/admin")
def admin_list():
    if not session.get("is_admin"):
        flash("Admin required", "danger")
        return redirect(url_for("index"))
    products = get_all_products()
    return render_template("admin.html", products=products)

@product_bp.route("/admin/create", methods=["GET","POST"])
def admin_create():
    if not session.get("is_admin"):
        flash("Admin required", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price") or 0
        stock = request.form.get("stock") or 0
        file = request.files.get("image")

        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

        product_id = create_product(name, description, float(price), int(stock), filename)
        flash("Product created", "success")
        return redirect(url_for("product_bp.admin_list"))

    return render_template("product_form.html", action="Create", product=None)

@product_bp.route("/admin/edit/<int:product_id>", methods=["GET","POST"])
def admin_edit(product_id):
    if not session.get("is_admin"):
        flash("Admin required", "danger")
        return redirect(url_for("index"))

    product = get_product_by_id(product_id)
    if not product:
        flash("Product not found", "warning")
        return redirect(url_for("product_bp.admin_list"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price") or 0
        stock = request.form.get("stock") or 0
        file = request.files.get("image")
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        update_product(product_id, name, description, float(price), int(stock), image_filename=filename)
        flash("Product updated", "success")
        return redirect(url_for("product_bp.admin_list"))

    return render_template("product_form.html", action="Edit", product=product)

@product_bp.route("/admin/delete/<int:product_id>", methods=["POST"])
def admin_delete(product_id):
    if not session.get("is_admin"):
        flash("Admin required", "danger")
        return redirect(url_for("index"))

    delete_product(product_id)
    flash("Product deleted", "info")
    return redirect(url_for("product_bp.admin_list"))

@product_bp.route('/')
def index():
    return render_template('index.html')