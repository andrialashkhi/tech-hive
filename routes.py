from functools import wraps

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from ext import app, db, login_manager
from forms import (RegisterForm, LoginForm, OrderForm, ProductForm, EditProductForm,
                    NewsletterForm, OrderStatusForm)
from models import Product, User, Order, Subscriber, CATEGORIES, ORDER_STATUSES


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def moderator_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_moderator:
            flash("You don't have permission to do that.", "danger")
            return redirect(url_for('products'))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_globals():
    is_mod = current_user.is_authenticated and current_user.is_moderator
    return {"newsletter_form": NewsletterForm(), "categories": CATEGORIES, "is_moderator": is_mod}


@app.route('/')
def home():
    featured = Product.query.filter_by(featured=True).limit(3).all()
    if len(featured) < 3:
        featured = Product.query.order_by(Product.id.desc()).limit(3).all()
    stats = {
        "products": Product.query.count(),
        "categories": len(CATEGORIES),
        "orders": Order.query.count(),
    }
    return render_template("Index.html", active='home', featured=featured, stats=stats)


@app.route('/products')
def products():
    query = Product.query
    search = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category and category in CATEGORIES:
        query = query.filter_by(category=category)

    products_list = query.order_by(Product.featured.desc(), Product.id.desc()).all()
    return render_template("Products.html", active='products', products=products_list,
                            search=search, selected_category=category)


@app.route('/product/add', methods=["GET", "POST"])
@login_required
@moderator_required
def add_product():
    form = ProductForm()

    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            image=form.image.data,
            category=form.category.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            featured=form.featured.data,
        )

        db.session.add(product)
        db.session.commit()
        flash(f'"{product.name}" was added to the catalog.', "success")
        return redirect(url_for('products'))

    return render_template("ProductForm.html", form=form, title="Add Product")


@app.route('/product/edit/<int:product_id>', methods=["GET", "POST"])
@login_required
@moderator_required
def edit_product(product_id):
    product = db.get_or_404(Product, product_id)
    form = EditProductForm()

    if form.validate_on_submit():
        product.name = form.name.data
        product.category = form.category.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.featured = form.featured.data

        if form.image.data:
            product.image = form.image.data

        db.session.commit()
        flash(f'"{product.name}" was updated.', "success")
        return redirect(url_for('product_detail', product_id=product.id))

    if not form.is_submitted():
        form.name.data = product.name
        form.category.data = product.category
        form.description.data = product.description
        form.price.data = product.price
        form.stock.data = product.stock
        form.featured.data = product.featured

    return render_template("ProductForm.html", form=form, product=product, title="Edit Product")


@app.route('/product/delete/<int:product_id>', methods=["POST"])
@login_required
@moderator_required
def delete_product(product_id):
    product = db.get_or_404(Product, product_id)
    name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'"{name}" was removed from the catalog.', "success")
    return redirect(url_for('products'))


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    selected_product = db.get_or_404(Product, product_id)
    related = Product.query.filter(
        Product.category == selected_product.category,
        Product.id != selected_product.id
    ).limit(3).all()
    return render_template("ProductDetail.html", product=selected_product, related=related)


@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('products'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            password_hash=generate_password_hash(form.password.data),
            birthday=form.birthday.data,
            role="user"
        )

        db.session.add(user)
        db.session.commit()

        flash(f"Welcome to the Hive, {user.username}! You can now log in.", "success")
        return redirect(url_for('login'))
    return render_template("Register.html", form=form)


@app.route('/order', methods=["GET", "POST"])
def order():
    form = OrderForm()
    products_list = Product.query.filter(Product.stock > 0).order_by(Product.name).all()
    form.product.choices = [(p.id, f"{p.name} — {p.price:.2f} GEL") for p in products_list]

    if current_user.is_authenticated and request.method == "GET":
        form.full_name.data = current_user.username

    if not products_list:
        flash("Every product is currently out of stock — check back soon.", "warning")
        return render_template("order.html", form=form, active='order', products_list=products_list)

    if form.validate_on_submit():
        product = db.get_or_404(Product, form.product.data)

        if form.quantity.data > product.stock:
            flash(f"Only {product.stock} unit(s) of {product.name} left in stock.", "danger")
            return render_template("order.html", form=form, active='order', products_list=products_list)

        order_item = Order(
            full_name=form.full_name.data,
            product_id=product.id,
            quantity=form.quantity.data,
            user_id=current_user.id if current_user.is_authenticated else None,
        )
        product.stock -= form.quantity.data

        db.session.add(order_item)
        db.session.commit()

        flash(f"Order placed! {form.quantity.data} × {product.name} is on its way.", "success")
        return redirect(url_for('my_orders') if current_user.is_authenticated else url_for('order'))

    return render_template("order.html", form=form, active='order', products_list=products_list)


@app.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("MyOrders.html", orders=orders, active='my-orders')


@app.route('/manage/orders', methods=["GET"])
@login_required
@moderator_required
def manage_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    status_form = OrderStatusForm()
    status_form.status.choices = [(s, s) for s in ORDER_STATUSES]
    return render_template("ManageOrders.html", orders=orders, status_form=status_form, active='manage-orders')


@app.route('/manage/orders/<int:order_id>/status', methods=["POST"])
@login_required
@moderator_required
def update_order_status(order_id):
    order_item = db.get_or_404(Order, order_id)
    status_form = OrderStatusForm()
    status_form.status.choices = [(s, s) for s in ORDER_STATUSES]

    if status_form.validate_on_submit() and status_form.status.data in ORDER_STATUSES:
        order_item.status = status_form.status.data
        db.session.commit()
        flash(f"Order #{order_item.id} marked as {order_item.status}.", "success")

    return redirect(url_for('manage_orders'))


@app.route('/newsletter', methods=["POST"])
def newsletter_signup():
    form = NewsletterForm()
    if form.validate_on_submit():
        existing = Subscriber.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash("You're already on the list — thanks for the love!", "info")
        else:
            db.session.add(Subscriber(email=form.email.data.lower()))
            db.session.commit()
            flash("You're in! Watch your inbox for Hive drops.", "success")
    else:
        flash("Enter a valid email to subscribe.", "danger")

    return redirect(request.referrer or url_for('home'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('products'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.username}.", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('products'))

        flash("Invalid email or password.", "danger")

    return render_template("Login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for('products'))


@app.errorhandler(404)
def not_found(_e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(_e):
    return render_template("500.html"), 500
