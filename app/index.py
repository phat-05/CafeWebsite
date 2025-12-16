import json
from os import name

from flask import abort

from flask import render_template, request, redirect
from flask_login import login_user, logout_user, current_user
from pycparser.ply.yacc import resultlimit

from app import app, dao, login, database
from app.decorator import anonymous_required, login_required
from app.models import UserRole


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
            else:
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

@app.route('/cart')
def cart():
    return render_template("cart.html")

@app.route('/about-us')
def about():
    return render_template("about-us.html")

if __name__ == '__main__':
    from app import admin
    app.run(debug=True, port=8080)
