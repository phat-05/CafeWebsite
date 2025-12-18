import json

from flask import render_template, request, redirect, jsonify, session
from flask_login import login_user, logout_user, current_user
from sqlalchemy.util import ordered_column_set

from app import app, dao, login, database, utils
from app.decorator import anonymous_required, login_required, customer_required, customer_or_serving_staff_required, \
    cashier_required
from app.models import UserRole, Position


@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)
@app.route('/')
def index():
    with open("./static/data/banner.json") as f:
        banners = json.load(f)
    popular_products = dao.get_popular_products(app.config["MAX_POPULAR_PRODUCTS_DISPLAY"])
    return render_template("index.html", banners=banners, popular_products=popular_products)

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    cates = dao.load_categories()
    category_id = request.args.get("category_id")
    keyword = request.args.get("kw")
    sort = request.args.get("sort")
    products = dao.load_products(category_id=category_id, keyword=keyword,sort=sort)
    return render_template("menu.html", cates=cates, products=products, category_id=category_id
                           , keyword=keyword, sort=sort)

@app.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login_my_user():
    message = None
    if request.method.__eq__("POST"):
        username = request.form.get("username")
        password = request.form.get("password")

        user = dao.authenticate(username, password)

        if user:
            login_user(user)
            if (current_user.user_role == UserRole.ADMIN):
                return redirect("/admin")
            if (current_user.user_role == UserRole.STAFF and current_user.staff.position == Position.CASHIER):
                return redirect("/staff/pay-confirm")
            return redirect("/")
        else:
            message = "Tài khoản hoặc mật khẩu không đúng!"


    return render_template("login.html", message=message)

@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    person = None
    message = None
    done = False
    if current_user.user_role == UserRole.CUSTOMER:
        person = current_user.customer
    else:
        person = current_user.staff

    if request.method.__eq__("POST"):
        try:
            person.name = request.form.get("name")
            person.phone = request.form.get("phone")
            person.email = request.form.get("email")
            if current_user.user_role == UserRole.CUSTOMER:
                person.address = request.form.get("address")

            database.session.commit()
            message = "Thay đổi thông tin thành công!"
            done = True
        except:
            database.session.rollback()
            message = "Đã xảy ra lỗi trong khi thay đổi dữ liệu! Vui lòng thử lại sau."
    return render_template("profile.html", person=person, message=message, done=done)


@app.route("/register", methods=['GET', 'POST'])
@anonymous_required
def register():
    message = None
    if request.method.__eq__("POST"):
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if password.__eq__(confirm):
            name = request.form.get('name')
            username = request.form.get("username")
            phone = request.form.get("phone")
            email = request.form.get("email")
            address = request.form.get("address")

            result = dao.add_customer(
                name=name,
                phone=phone,
                email=email,
                address=address,
                username=username,
                password=password
            )

            if result["result"]:
                return redirect("/login")
            else:
                message = result["message"]

        else:
            message = "Mật khẩu không khớp!"

        print(message)

    return render_template("register.html", message=message)

@app.errorhandler(403)
def forbidden(e):
    return render_template("forbidden.html"), 403


@app.route("/api/carts", methods=["POST"])
@customer_or_serving_staff_required
def add_to_cart():
    cart = session.get('cart')
    if not cart:
        cart = {}

    current_quantity = 0
    for p in cart.values():
        current_quantity += p["quantity"]

    if current_quantity >= 10:
        return jsonify(
            {'message': 'Giỏ hàng đã đầy! Xin vui lòng đặt hàng hoặc xoá bớt sản phẩm để thêm sản phẩm mới.'})

    id = str(request.json.get('id'))

    if id not in cart:
        name = request.json.get("name")
        price = str(request.json.get("price"))
        image = request.json.get("image")
        cart[id] = {
            "id": id,
            "name": name,
            "image": image,
            "price": price,
            "note": '',
            "quantity": 1
        }
    else:
        cart[id]["quantity"] += 1

    session['cart'] = cart
    return jsonify(utils.stats_cart(cart=cart, configs=dao.get_configs()))


@app.route("/api/carts/<id>", methods=["PUT"])
@customer_or_serving_staff_required
def update_cart(id):
    cart = session.get('cart')

    if cart and id in cart:
        if 'quantity' in request.json:
            quantity = request.json.get("quantity")
            cart[id]["quantity"] = int(quantity)

        if 'note' in request.json:
            note = request.json.get("note")
            cart[id]["note"] = note.strip()

    session['cart'] = cart
    print(cart)
    return jsonify(utils.stats_cart(cart=cart, configs=dao.get_configs()))


@app.route("/api/carts/<id>", methods=["DELETE"])
@customer_or_serving_staff_required
def delete_cart(id):
    cart = session.get('cart')
    if cart and id in cart:
        del cart[id]

    session['cart'] = cart
    if cart:
        return jsonify(utils.stats_cart(cart=cart, configs=dao.get_configs()))
    else:
        return jsonify({'flag': True})

@app.route('/api/order', methods=['POST'])
@customer_or_serving_staff_required
def order():
    cart = session.get('cart')

    if not cart:
        return jsonify({'message': 'Giỏ hàng trống!'})

    customer = None
    stats_cart = utils.stats_cart(cart=cart, configs=dao.get_configs())

    if current_user.customer:
        customer = current_user.customer

    result = dao.add_order(cart=cart, customer=customer, total_price=stats_cart['total_price'])

    if result['result']:
        del session['cart']
        return jsonify({'message': result['message']})

    return jsonify({'message': "Đặt hàng không thành công! Vui lòng thử lại sau"})

@app.route('/cart')
@customer_required
def cart():
    return render_template("cart.html")

@app.route('/staff/pay-confirm')
@cashier_required
def pay_confirm():
    orders = dao.get_uncompleted_orders()
    return render_template("staff/pay-confirm.html", orders=orders)

@app.route('/about-us')
def about():
    return render_template("about-us.html")


@app.context_processor
def common_attributes():
    atributes = {}

    atributes['configs'] = dao.get_configs()
    atributes['stats_cart'] = utils.stats_cart(session.get('cart'), configs=dao.get_configs())

    if current_user.is_authenticated:
        atributes['is_customer'] = current_user.customer

    if 'cart' in session:
        current_quantity = 0
        for p in session['cart'].values():
            current_quantity += p["quantity"]
        atributes['current_quantity'] = current_quantity

    return atributes

if __name__ == '__main__':
    from app import admin
    app.run(debug=True, port=8080)
