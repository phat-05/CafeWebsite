from flask import abort, redirect, request, flash
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme
from flask_login import current_user, logout_user
from markupsafe import Markup
from pymysql import IntegrityError

from app import database, app, dao
from app.models import Category, Product, Ingredient, Recipe, Order, Customer, Staff, Position, OrderStatus, UserRole, Configuration

from sqlalchemy import func
from datetime import datetime
class AdminView(ModelView):
    page_size = 10
    edit_modal = True
    create_modal = True
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        abort(403)

class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self) -> str:
        low_stock = dao.load_low_stock_ingredients(5)
        low_stock_count = len(low_stock)
        stats_day = dao.stats_revenue_by_day()
        total_order = dao.get_total_order_by_day()
        uncompleted_order = len(dao.get_uncompleted_orders())
        return self.render("admin/index.html", low_stock_count=low_stock_count, stats_day=stats_day,
                           total_order=total_order, uncompleted_order=uncompleted_order)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        abort(403)


class MyLogOutView(BaseView):
    @expose("/")
    def index(self) -> str:
        logout_user()
        return redirect("/login")

class MyHomeView(BaseView):
    @expose("/")
    def index(self) -> str:
        return redirect("/")


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
    can_create = False
    can_delete = False
    form_columns = ["name", "category", "unit", "price", "image"]

    def format_image(view, context, model, name):
        if not model.image:
            return ""
        return Markup(f'<img src="{model.image}" width="25" height="25" style=" object-fit:cover;">')

    column_formatters = {
        'price': lambda v, c, m, n: "{:,.0f} VNĐ".format(m.price),
        'image': format_image
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


    def delete_model(self, model):
        try:
            if model.products:
                raise Exception()
            self.session.delete(model)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            flash(f'Lỗi: Không thể xoá danh mục "{model.name}" vì vẫn còn các món ăn thuộc nhóm này. Hãy xoá hoặc chuyển danh mục cho các món đó trước!', 'error')
            return False

#done
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
    form_excluded_columns = ["received_date", "recipes"]
    can_export = True
    can_create = False
    can_delete = False


    def format_remaining(view, context, model, name):
        qty = model.remaining
        if qty < 5:
            return Markup(f'''
                <span class="text-danger fw-bold">{qty}</span>
                <i class="fa fa-exclamation-triangle text-danger mx-1"></i>
            ''')
        return qty

    column_formatters = {
        'remaining': format_remaining
    }

    @expose('/')
    def index_view(self):
        low_stock = dao.load_low_stock_ingredients(5)
        low_stock_count = len(low_stock)

        if low_stock_count > 0:
            flash(f'CẢNH BÁO: Có {low_stock_count} nguyên liệu sắp hết hàng! ({", ".join([item.name for item in low_stock])})', 'danger')

        return super(IngredientView, self).index_view()

#done
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
    form_columns = ["product", "ingredient", "amount"]
    column_searchable_list = ["product.name", "ingredient.name"]
    can_export = True
    can_delete = False
    can_edit = False
    can_create = False

#dône
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
    form_columns = ['status']
    can_create = False
    can_delete = False
    can_export = True

    column_filters = ["customer.name", "staff.name", "created_date", "total_price", "status"]
    column_searchable_list = ["customer.name", "staff.name"]
    column_default_sort = ("created_date", True)

    def format_status(view, context, model, name):
        return {
            OrderStatus.IN_PROGRESS: "Đang Xử lý",
            OrderStatus.COMPLETED: "Hoàn thành",
        }.get(model.status, str(model.status))

    column_formatters = {
        'status': format_status,
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
            (Position.MANAGER.name, "Quản lý"),
            (Position.STAFF.name, "Nhân viên"),
            (Position.CASHIER.name, "Thu ngân"),
        ]
    }

    def format_position(view, context, model, name):
        return {
            Position.MANAGER: "Quản lý",
            Position.STAFF: "Nhân viên",
            Position.CASHIER: "Thu ngân"
        }.get(model.position, str(model.position))

    column_formatters = {
        'position': format_position,
        'salary': lambda v, c, m, n: "{:,.0f} VNĐ".format(m.salary)
    }

    can_export = True
    can_edit = False
    can_create = False
    can_delete = False
    column_filters = ["name", "phone", "email", "position"]
    column_searchable_list = ["name", "phone", "email", "position"]
    form_columns = ["name", "phone", "email", "position", "salary", "account"]

#done
class ConfigurationView(AdminView):
    column_list = ( "description", "value")
    column_labels = {
        "description": "Mô tả",
        "value": "Giá trị"
    }

    form_columns = ["value"]
    can_create = False
    can_delete = False

    def get_count_query(self):
        return self.session.query(func.count('*')).filter(self.model.key == 'SERVICE_FEE')

class ImportStockView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        ingredients = Ingredient.query.all()

        if request.method == 'POST':
            try:
                # Lấy danh sách các giá trị từ form (dạng mảng)
                ing_ids = request.form.getlist('ingredient_id[]')
                quantities = request.form.getlist('quantity[]')
                dates = request.form.getlist('received_date[]')

                # Kiểm tra nếu danh sách rỗng
                if not ing_ids:
                    flash("Vui lòng thêm ít nhất một dòng nguyên liệu!", "error")
                else:
                    count_success = 0
                    # Duyệt qua từng dòng được gửi lên
                    for i in range(len(ing_ids)):
                        p_id = ing_ids[i]
                        qty_str = quantities[i]
                        date_str = dates[i]

                        # Bỏ qua nếu dữ liệu dòng đó trống
                        if not p_id or not qty_str:
                            continue

                        qty_float = float(qty_str)
                        ing = Ingredient.query.get(p_id)

                        if ing:
                            # 1. Cập nhật tồn kho
                            ing.remaining += qty_float

                            # 2. Cập nhật ngày nhập (nếu có nhập ngày)
                            if date_str:
                                try:
                                    # Chuyển chuỗi 'YYYY-MM-DD' thành đối tượng datetime
                                    dt_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                    ing.received_date = dt_obj
                                except ValueError:
                                    pass # Nếu ngày lỗi thì giữ nguyên ngày cũ hoặc dùng ngày hiện tại

                            database.session.add(ing)
                            count_success += 1

                    database.session.commit()
                    flash(f"Đã nhập kho thành công {count_success} dòng nguyên liệu!", "success")

            except ValueError:
                flash("Lỗi: Số lượng phải là số!", "error")
            except Exception as e:
                database.session.rollback()
                flash(f"Lỗi hệ thống: {str(e)}", "error")

            return self.render('admin/import_stock.html', ingredients=ingredients)

        return self.render('admin/import_stock.html', ingredients=ingredients)

admin = Admin(
    app=app,
    name="Trang quản trị - Hailan Cafe",
    index_view=MyAdminIndexView(),
    theme=Bootstrap4Theme(swatch='lux', fluid=True)
)

admin.add_view(CategoryView(
    model=Category,
    session=database.session,
    name="🏷️ Danh mục",
    category="Quản lý"
))

admin.add_view(ProductView(
    model=Product,
    session=database.session,
    name="🍹 Sản phẩm",
    category="Quản lý"
))

admin.add_view(CustomerView(
    model=Customer,
    session=database.session,
    name="🙋🏻‍♂️ Khách hàng",
    category="Quản lý"
))

admin.add_view(StaffView(
    model=Staff,
    session=database.session,
    name="👨🏻‍🍳 Nhân viên",
    category="Quản lý"
))

admin.add_view(IngredientView(
    model=Ingredient,
    session=database.session,
    name="🌿 Nguyên liệu",
    category="Quản lý"
))

admin.add_view(RecipeView(
    model=Recipe,
    session=database.session,
    name="📋 Công thức",
    category="Quản lý"
))

admin.add_view(OrderView(
    model=Order,
    session=database.session,
    name="🧾 Đơn hàng",
    category="Quản lý"
))

admin.add_view(StatisticalView(
    name="📶 Thống kê",
    menu_icon_type='fa-solid',
    menu_icon_value='fa-chart-pie'
))

admin.add_view(ConfigurationView(
    model=Configuration,
    session=database.session,
    name="🛠️ Phí dịch vụ",
    category="Quản lý",
))

admin.add_view(ImportStockView(
    name="📥 Nhập kho nhanh"
))

admin.add_view(MyHomeView(name="🏠 Về trang chủ"))

admin.add_view(MyLogOutView(
    name="➜] Đăng xuất"
))
