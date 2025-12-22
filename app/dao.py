import hashlib
from datetime import datetime, timedelta

from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError
from app import database, app
from app.models import Category, Product, Account, Customer, OrderDetail, Configuration, Order, OrderStatus, Ingredient, Recipe

def load_categories():
    return Category.query.all()

def load_products(category_id=None, keyword=None, sort=None):
    query = Product.query
    if keyword:
        query = query.filter(Product.name.ilike(f"%{keyword}%"))
    if category_id:
        query = query.filter(Product.category_id.__eq__(category_id))
    if sort:
        if sort == "giá thấp trước":
            query = query.order_by(Product.price)
        elif sort == "giá cao trước":
            query = query.order_by(desc(Product.price))

    products = query.all()
    products = [p for p in products if p.is_remaining()]

    return products

def get_user_by_id(id):
    return Account.query.get(int(id))

def authenticate(username, password):
    password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()
    return Account.query.filter_by(user_name=username.strip(), password=password).first()

def is_user_name_valid(username):
    return Account.query.filter_by(user_name=username.strip()).first() is None

def add_customer(name, phone, email, address, username, password):
    try:
        if not is_user_name_valid(username):
            return {
                "result": None,
                "message": "Tên người dùng đẫ tồn tại!"

            }

        password_hash = hashlib.md5(password.strip().encode('utf-8')).hexdigest()

        new_account = Account(user_name=username, password=password_hash)
        database.session.add(new_account)
        database.session.flush()

        new_customer = Customer(
            name=name,
            phone=phone,
            email=email,
            address=address,
            account_id=new_account.id
        )

        database.session.add(new_customer)
        database.session.commit()

        return {
            "result": new_customer,
            "message": "Đăng ký thành công!"
        }

    except SQLAlchemyError as ex:
        database.session.rollback()
        return {
            "result": None,
            "message": "Đăng ký không thành công! Vui lòng thử lại sau."
        }

def get_configs():
    configs = {}
    conf = Configuration.query.all()
    for config in conf:
        configs[config.key] = {
            "key": config.key,
            "value": config.value,
            "description": config.description,
        }
    return configs

def add_order_detail(order_id, product_id, amount, note):
    try:
        order_detail = OrderDetail(order_id=order_id, product_id=product_id, amount=amount, note=note)
        database.session.add(order_detail)

        return {
            "result": order_detail,
            "message": f"Thêm thành công: order: {order_id}, product_id: {product_id}, amount: {amount}, note: {note}"
        }
    except SQLAlchemyError as ex:
        database.session.rollback()
        return {
            "result": None,
            "message": f"Thêm chi tiết đơn hàng không thành công!: {ex}"
        }


def add_order(cart, total_price, customer=None, staff=None):
    try:
        new_order = Order(
            created_date=datetime.now(),
            total_price=total_price
        )

        if customer:
            new_order.customer_id = customer.id
        if staff:
            new_order.staff_id = staff.id

        database.session.add(new_order)

        for c in cart.values():
            amount = int(c['quantity'])
            product_id = int(c['id'])

            new_order_detail = OrderDetail(
                order=new_order,
                product_id=product_id,
                amount=amount
            )

            if 'note' in c:
                new_order_detail.add_note(c['note'])

            database.session.add(new_order_detail)

        database.session.commit()

        return {
            "result": new_order,
            "message": "Đặt hàng thành công!"
        }
    except SQLAlchemyError as ex:
        database.session.rollback()
        print(f"Lỗi đặt hàng: {ex}")
        return {
            "result": None,
            "message": "Đặt hàng không thành công! Vui lòng thử lại sau."
        }

def get_uncompleted_orders(customer_id=None):
    query = Order.query.filter(Order.status == OrderStatus.IN_PROGRESS)
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    return query.order_by(desc(Order.created_date)).all()

def update_ingredient(order_id):
    order = Order.query.get(order_id)
    for detail in order.order_details:
        product_id = detail.product_id
        quantity_sold = detail.amount
        recipes = Recipe.query.filter_by(product_id=product_id).all()
        for recipe in recipes:
            total_amount_needed = recipe.amount * quantity_sold
            ingredient = Ingredient.query.get(recipe.ingredient_id)
            if ingredient:
                ingredient.remaining = ingredient.remaining - total_amount_needed
                database.session.add(ingredient)

def confirm_order(order_id):
    try:
        order = Order.query.get(order_id)
        if order:
            order.status = OrderStatus.COMPLETED
            update_ingredient(order.id)
            database.session.commit()
            return True
    except SQLAlchemyError:
        database.session.rollback()
    return False

def load_low_stock_ingredients(warning_level=5):
    return Ingredient.query.filter(Ingredient.remaining <= warning_level).all()



#_________________________________


def stats_revenue(time_type='Tháng',year=datetime.today().year, month=datetime.today().month):
    if time_type == 'Tháng':
        return database.session.query(func.extract('day', Order.created_date), func.sum(Order.total_price)).filter(
            Order.status == OrderStatus.COMPLETED,
            func.extract('year', Order.created_date) == year,
            func.extract('month', Order.created_date) == month
        ).group_by(
            func.extract('day', Order.created_date),
        ).order_by(
            func.extract('day', Order.created_date),
        ).all()

    if time_type == 'Năm':
        return database.session.query(func.extract('month', Order.created_date), func.sum(Order.total_price)).filter(
            Order.status == OrderStatus.COMPLETED,
            func.extract('year', Order.created_date) == year
        ).group_by(
            func.extract('month', Order.created_date),
        ).order_by(
            func.extract('month', Order.created_date),
        ).all()

    return None

def load_best_sell_products(year = None, month = None, number = None):
    query = database.session.query(
        Product,
        func.sum(OrderDetail.amount)
    ).join(
        OrderDetail,
        Product.id == OrderDetail.product_id
    ).join(
        Order,
        OrderDetail.order_id == Order.id
    ).filter(
        Order.status == OrderStatus.COMPLETED,
    )


    if year:
        query = query.filter(func.extract('year', Order.created_date) == year)
    if month:
        query = query.filter(func.extract('month', Order.created_date) == month)

    query = query.group_by(
        Product.id,
        Product.name
    ).order_by(
        func.sum(OrderDetail.amount).desc()
    )

    if number:
        query = query.limit(number)

    return query.all()

def stats_revenue_by_day(day=datetime.today()):
    return database.session.query(
        func.sum(Order.total_price),
    ).filter(
        Order.status == OrderStatus.COMPLETED,
        func.date(Order.created_date) == day.date()
    ).group_by(
        func.date(Order.created_date)
    ).scalar() or 0

def get_total_order_by_day(day=datetime.today()):
    return database.session.query(
        func.count(Order.id)
    ).filter(
        func.date(Order.created_date) == day.date()
    ).scalar() or 0


########################################################################################################################
def stats_products(year=2024, month=1):
    return database.session.query(
        Product.name,
        func.sum(OrderDetail.amount)
    ).join(
        OrderDetail, OrderDetail.product_id == Product.id
    ).join(
        Order, OrderDetail.order_id == Order.id
    ).filter(
        Order.status == OrderStatus.COMPLETED,
        func.extract('year', Order.created_date) == year,
        func.extract('month', Order.created_date) == month
    ).group_by(
        Product.name
    ).order_by(
        func.sum(OrderDetail.amount).desc()
    ).limit(5).all()

#_________________________________
if __name__ == '__main__':
    with app.app_context():
        #print(load_best_sell_products(2025, 12))
        print(stats_revenue_by_day())