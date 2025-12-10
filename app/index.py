import json
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    with open("./static/data/banner.json") as f:
        banners = json.load(f)
    return render_template("index.html", banners=banners)

@app.route('/menu')
def menu():
    return render_template("menu.html")

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
