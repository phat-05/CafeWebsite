import calendar
import json

from flask import render_template, request, redirect, jsonify, session
from flask_login import login_user, logout_user, current_user

from app import app, dao, login, database, utils
from app.decorator import anonymous_required, login_required, customer_required, cashier_required, \
    serving_staff_required, admin_required
from app.models import UserRole


@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)
@app.route('/')
def index():
    with open("./static/data/banner.json") as f:
        banners = json.load(f)
    popular_products = dao.load_best_sell_products(number=app.config["MAX_POPULAR_PRODUCTS_DISPLAY"])
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
            if (current_user.is_admin()):
                return redirect("/admin")
            if (current_user.is_cashier()):
                return redirect("/staff/pay-confirm")
            if (current_user.is_staff()):
                return redirect("/staff/create-order")
            return redirect("/")
        else:
            message = "Tài khoản hoặc mật khẩu không đúng!"


    return render_template("login.html", message=message)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
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
@customer_required
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
@customer_required
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
    return jsonify(utils.stats_cart(cart=cart, configs=dao.get_configs()))


@app.route("/api/carts/<id>", methods=["DELETE"])
@customer_required
def delete_cart(id):
    cart = session.get('cart')
    if cart and id in cart:
        del cart[id]

    session['cart'] = cart

    return jsonify(utils.stats_cart(cart=cart, configs=dao.get_configs()))

@app.route('/api/order', methods=['POST'])
@customer_required
def customer_order():
    customer = None
    staff = None
    if 'cart' in session:
        if not session['cart']:
            return jsonify({'message': 'Giỏ hàng trống!'})
        order = session.get('cart')
        if current_user.customer:
            customer = current_user.customer

    order_stats = utils.stats_cart(cart=order, configs=dao.get_configs())
    result = dao.add_order(cart=order, customer=customer, staff=staff, total_price=order_stats['total_price'])

    if result['result']:
        if 'cart' in session:
            del session['cart']
        return jsonify({'message': result['message']})

    return (jsonify({'message': result['message']}))


@app.route('/api/staff/order', methods=['POST'])
@serving_staff_required
def staff_order():
    customer = None
    staff = None
    if request.json:
        order = request.json
        if current_user.staff:
            staff = current_user.staff

    order_stats = utils.stats_cart(cart=order, configs=dao.get_configs())

    result = dao.add_order(cart=order, customer=customer, staff=staff, total_price=order_stats['total_price'])

    if result['result']:
        if 'cart' in session:
            del session['cart']
        return jsonify({'message': result['message']})

    return jsonify({'message': result['message']})


@app.route('/cart')
@customer_required
def cart():
    return render_template("cart.html")

@app.route('/api/configs')
@login_required
def my_configs():
    return jsonify(dao.get_configs())

@app.route('/staff/pay-confirm')
@cashier_required
def pay_confirm():
    orders = dao.get_uncompleted_orders()
    return render_template("staff/pay-confirm.html", orders=orders)

@app.route('/staff/create-order')
@serving_staff_required
def create_order():
    cates = dao.load_categories()
    products = dao.load_products()
    return render_template("staff/order.html", cates=cates, products=products)


@app.route('/api/staff/pay/<int:id>', methods=['POST'])
@cashier_required
def pay_order(id):
    print(id)
    if dao.confirm_order(id):
        return jsonify({'code': 200,'message': 'Thanh toán thành công!'})
    return jsonify({'message': 'Thanh toán thất bại!'})


########################################################################################################################
############################################### THỐNG KÊ ###############################################################
@app.route('/api/revenue', methods=['POST'])
@admin_required
def revenue_api():
    time_type = request.json.get('type')
    month = request.json.get('month')
    year = request.json.get('year')

    if month:
        year = int(month.split('-')[0])
        month = int(month.split('-')[1])

    if year:
        year = int(year)

    print(month, year)

    data = dao.stats_revenue(time_type, year, month)

    labels = []
    values = []

    if time_type == 'Tháng':
        _, num_days = calendar.monthrange(year, month)

        stats_map = {int(item[0]): float(item[1]) for item in data}

        for day in range(1, num_days + 1):
            labels.append(f"Ngày {day}")
            values.append(stats_map.get(day, 0))

    if time_type == 'Năm':
        stats_map = {int(item[0]): float(item[1]) for item in data}
        for m in range(1, 13):
            labels.append(f"Tháng {m}")
            values.append(stats_map.get(m, 0))
    print({'labels': labels, 'values': values})
    return jsonify({'labels': labels, 'values': values})


@app.route('/api/best-sell', methods=['POST'])
def best_sell_api():
    month = request.json.get('month')
    year = None
    if month:
        year = int(month.split('-')[0])
        month = int(month.split('-')[1])

    data = dao.load_best_sell_products(year, month)

    labels = [item[0].name for item in data]
    values = [item[1] for item in data]

    total = sum(values)
    if total > 0:
        values = [v / total * 100 for v in values]
    else:
        values = [0] * len(values)

    return jsonify({'labels': labels, 'values': values})


# __________________________________
@app.route('/about-us')
def about():
    return render_template("about-us.html")

@app.context_processor
def common_attributes():
    atributes = {}

    atributes['configs'] = dao.get_configs()
    atributes['stats_cart'] = utils.stats_cart(session.get('cart'), configs=dao.get_configs())

    if 'cart' in session:
        current_quantity = 0
        for p in session['cart'].values():
            current_quantity += p["quantity"]
        atributes['current_quantity'] = current_quantity

    return atributes

if __name__ == '__main__':
    from app import admin
    app.run(debug=True, port=8080)
