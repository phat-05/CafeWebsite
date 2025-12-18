import hashlib
from datetime import datetime

from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError

from app import database
from app.models import Category, Product, Account, Customer, OrderDetail, Configuration, Order, OrderStatus


#hàm trả về tất cả danh mục đang lưu trong csdl
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

        # elif sort == "mới nhất trước":
        #     query = query.order_by(Product.created_date)

    return query.all()

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

def get_popular_products(number = 8):
    return database.session.query(Product, func.sum(OrderDetail.amount)) \
        .join(OrderDetail, Product.id == OrderDetail.product_id) \
        .group_by(Product.id) \
        .order_by(func.sum(OrderDetail.amount).desc()) \
        .limit(number).all()

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


def add_order(cart, total_price, customer, staff=None):
    try:
        customer_id = customer.id
        created_date = datetime.now()
        new_order = None
        if staff:
            staff_id = staff.id
            new_order = Order(customer_id=customer_id, staff_id=staff_id , created_date=created_date, total_price=total_price)
        else:
            new_order = Order(customer_id=customer_id, created_date=created_date, total_price=total_price)

        database.session.add(new_order)
        for c in cart.values():
            new_order_detail = OrderDetail(order=new_order, product_id=c['id'], amount=c['quantity'], note=c['note'] or '')
            database.session.add(new_order_detail)

        database.session.commit()

        return {
            "result": new_order,
            "message": "Đặt hàng thành công!"
        }
    except SQLAlchemyError as ex:
        return {
            "result": None,
            "message": "Tạo đơn hàng không thành công!"
        }

def get_uncompleted_orders(customer_id=None):
    query = Order.query.filter(Order.status == OrderStatus.IN_PROGRESS)
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    return query.order_by(desc(Order.created_date)).all()


def confirm_order(order_id):
    try:
        order = Order.query.get(order_id)
        if order:
            order.status = OrderStatus.COMPLETED
            database.session.commit()
            return True
    except Exception as ex:
        database.session.rollback()
        print(ex)
    return False