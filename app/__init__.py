from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
app = Flask(__name__)

app.secret_key = "abcqjoaduhoslkjh"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/cafedb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["MAX_POPULAR_PRODUCTS_DISPLAY"] = 20

database = SQLAlchemy(app=app)
login = LoginManager(app=app)