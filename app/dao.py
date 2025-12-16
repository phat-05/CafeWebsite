import hashlib
from idlelib.configdialog import changes

from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.testing.pickleable import User

from app import database
from app.models import Category, Product, Account, Customer, UserRole, OrderDetail


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