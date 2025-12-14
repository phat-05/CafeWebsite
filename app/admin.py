from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import database, app
from app.models import Category, Product

admin = Admin(app=app, name="Trang quản trị - Hailan Cafe")
admin.add_view(ModelView(Category, database.session))
admin.add_view(ModelView(Product, database.session))

