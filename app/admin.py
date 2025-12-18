from flask import abort, redirect
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme
from flask_login import current_user, logout_user
from markupsafe import Markup

from app import database, app
from app.models import Category, Product, Ingredient, Recipe, Order, Customer, Staff, Position, OrderStatus, UserRole


class AdminView(ModelView):
    page_size = 6
    edit_modal = True
    create_modal = True
    can_view_details = True
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        abort(403)

class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self) -> str:
        return self.render("admin/index.html")

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        abort(403)


class MyLogOutView(BaseView):
    @expose("/")
    def index(self) -> str:
        logout_user()
        return redirect("/login")


class StatisticalView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/statistic.html')

class ProductView(AdminView):
    column_list = ("id", "image", "name", "category", "unit", "recipes", "price")
    column_labels = {
        "id": "Mã sản phẩm",
        "image": "Hình ảnh",
        "name": "Tên sản phẩm",
        "category": "Loại",
        "unit": "Đơn vị",
        "price": "Giá bán",
        "category.name": "Loại sản phẩm",
        "recipes": "Nguyên liệu"
    }
    column_searchable_list = ["name"]
    column_filters = ["id", "name", "category.name", "unit", "price"]
    can_export = True
    form_columns = ["name", "category", "unit", "price", "image"]

    def _format_image(view, context, model, name):
        if not model.image:
            return ""
        return Markup(f'<img src="{model.image}" width="25" height="25" style=" object-fit:cover;">')

    column_formatters = {
        'price': lambda v, c, m, n: "{:,.0f} VNĐ".format(m.price),
        'image': _format_image
    }

class CategoryView(AdminView):
    column_list = ("id", "name")
    column_labels = {
        "id": "Mã danh mục",
        "name": "Tên danh mục"
    }
    column_searchable_list = ["id", "name"]
    can_export = True
    form_columns = ["name", "products"]

class IngredientView(AdminView):
    column_list = ("id", "name", "remaining", "received_date", "unit")
    column_labels = {
        "id": "Mã nguyên liệu",
        "name": "Tên nguyên liệu",
        "remaining": "Số lượng trong kho",
        "received_date": "Ngày nhập mới nhất",
        "unit": "Đơn vị"
    }
    column_searchable_list = ["name"]
    column_filters = ["id", "name", "remaining", "received_date", "unit"]
    form_excluded_columns = ["remaining", "received_date", "recipes"]
    can_export = True

class RecipeView(AdminView):
    column_list = ("id", "product", "ingredient", "amount")
    column_labels = {
        "id": "Mã công thức",
        "product": "Sản phẩm",
        "ingredient": "Nguyên liệu",
        "amount": "Số lượng",
        "product.name": "Tên sản phẩm",
        "ingredient.name": "Tên nguyên liệu"
    }
    column_filters = ["id", "product.name", "ingredient.name"]
    column_searchable_list = ["product.name", "ingredient.name"]
    can_export = True

class OrderView(AdminView):
    column_list = ("id", "customer", "staff", "created_date", "order_details", "total_price", "status")
    column_labels = {
        "id": "Mã Đơn hàng",
        "customer": "Khách hàng",
        "staff": "Nhân viên lập",
        "created_date": "Ngày lập",
        "order_details": "Chi tiết sản phẩm",
        "total_price": "Tổng tiền",
        "status": "Trạng thái",
        "customer.name": "Tên khách hàng",
        "staff.name": "Tên nhân viên"
    }
    can_edit = False
    can_create = False
    can_delete = False
    can_export = True

    column_filters = ["customer.name", "staff.name", "created_date", "total_price", "status"]
    column_searchable_list = ["customer.name", "staff.name"]

    def _format_status(view, context, model, name):
        return {
            OrderStatus.IN_PROGRESS: "Đang Xử lý",
            OrderStatus.COMPLETED: "Hoàn thành",
        }.get(model.status, str(model.status))

    column_formatters = {
        'status': _format_status,
        'total_price': lambda v, c, m, n: "{:,.0f} VNĐ".format(m.total_price)
    }

class CustomerView(AdminView):
    column_list = ("id", "name", "phone", "email", "address")
    column_labels = {
        "id": "Mã Khách Hàng",
        "name": "Họ và Tên",
        "phone": "SĐT",
        "email": "Email",
        "address": "Địa chỉ",
    }
    can_export = False
    can_delete = False
    can_create = False
    can_edit = False
    column_searchable_list = ["name", "phone"]

class StaffView(AdminView):
    column_list = ("id", "name", "phone", "email", "position", "salary")
    column_labels = {
        "id": "Mã Nhân Viên",
        "name": "Họ và Tên",
        "phone": "SĐT",
        "email": "Email",
        "position": "Chức vụ",
        "salary": "Lương"
    }

    form_choices = {
        "position": [
            (Position.MANAGER, "Quản lý"),
            (Position.STAFF, "Nhân viên"),
            (Position.CASHIER, "Thu ngân"),
        ]
    }

    def _format_position(view, context, model, name):
        return {
            Position.MANAGER: "Quản lý",
            Position.STAFF: "Nhân viên",
            Position.CASHIER: "Thu ngân"
        }.get(model.position, str(model.position))

    column_formatters = {
        'position': _format_position,
        'salary': lambda v, c, m, n: "{:,.0f} VNĐ".format(m.salary)
    }

    can_export = True
    column_filters = ["name", "phone", "email", "position"]
    column_searchable_list = ["name", "phone", "email", "position"]
    form_columns = ["name", "phone", "email", "position", "salary"]


admin = Admin(
    app=app,
    name="Trang quản trị - Hailan Cafe",
    index_view=MyAdminIndexView(),
    theme=Bootstrap4Theme(swatch='lux', fluid=True)
)

admin.add_view(CategoryView(
    model=Category,
    session=database.session,
    name="Danh mục",
    category="Quản lý",
    menu_icon_type='fa',
    menu_icon_value='fa-tags')
)

admin.add_view(ProductView(
    model=Product,
    session=database.session,
    name="Sản phẩm",
    category="Quản lý",
    menu_icon_type='fa',
    menu_icon_value='fa-coffee')
)

admin.add_view(CustomerView(
    model=Customer,
    session=database.session,
    name="Khách hàng",
    category="Quản lý",
    menu_icon_type='fa',
    menu_icon_value='fa-user')
)

admin.add_view(StaffView(
    model=Staff,
    session=database.session,
    name="Nhân viên",
    category="Quản lý",
    menu_icon_type='fa',
    menu_icon_value='fa-users')
)

admin.add_view(IngredientView(
    model=Ingredient,
    session=database.session,
    name="Nguyên liệu",
    category="Quản lý",
    menu_icon_type='fa',
    menu_icon_value='fa-boxes-stacked')
)

admin.add_view(RecipeView(
    model=Recipe,
    session=database.session,
    name="Công thức",
    category="Quản lý",
    menu_icon_type='fa',
    menu_icon_value='fa-ruler')
)

admin.add_view(OrderView(
    model=Order,
    session=database.session,
    name="Đơn hàng",
    category="Quản lý",
    menu_icon_type='fa',
    menu_icon_value='fa-file-invoice-dollar')
)

admin.add_view(StatisticalView(name="Thống kê", endpoint=''))
admin.add_view(MyLogOutView(name="Đăng xuất"))
