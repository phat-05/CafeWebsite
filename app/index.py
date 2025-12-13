import json
from flask import render_template, request

from app import app,dao

@app.route('/')
def index():
    with open("./static/data/banner.json") as f:
        banners = json.load(f)
    return render_template("index.html", banners=banners)

#index
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    cates = dao.load_categories()
    category_id = request.args.get("category_id")
    keyword = request.args.get("kw")
    products = dao.load_products(category_id=category_id, keyword=keyword)
    return render_template("menu.html", cates=cates, products=products, category_id=category_id
                           , keyword=keyword)

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/cart')
def cart():
    return render_template("cart.html")

@app.route('/about-us')
def about():
    return render_template("about-us.html")

if __name__ == '__main__':
    app.run(debug=True, port=8080)
