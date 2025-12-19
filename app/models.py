from datetime import datetime
from enum import Enum as MyEnum

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Enum, Boolean, DateTime, Null
from sqlalchemy.ext.orderinglist import count_from_1
from sqlalchemy.orm import relationship

from app import database, app


# enum loại tài khoản
class UserRole(MyEnum):
    ADMIN = 1
    STAFF = 2
    CUSTOMER = 3


# enum loại nhân viên
class Position(MyEnum):
    MANAGER = 1
    STAFF = 2
    CASHIER = 3

# enum trạng thái đơn hàng
class OrderStatus(MyEnum):
    IN_PROGRESS = 1
    COMPLETED = 2


# class Base chứa các cột chung để các lớp khác kế thừa
class Base(database.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


# class Người(id, tên, số điện thoại, email) chứa các thuộc tính chung của Nhân viên và Khách hàng
class Person(Base):
    __abstract__ = True
    name = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(50))

    def __str__(self):
        return self.name

# class Khách hàng có thêm thuộc tính đia chỉ
class Customer(Person):
    __tablename__ = 'customers'
    address = Column(String(255), nullable=False)

    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    orders = relationship("Order", backref="customer", lazy=True)


# class Nhân viên có thêm thuộc tính Chức vụ và Lương
class Staff(Person):
    __tablename__ = 'staffs'
    position = Column(Enum(Position), nullable=False, default=Position.STAFF)
    salary = Column(Float, nullable=False, default=0)

    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    orders = relationship("Order", backref="staff", lazy=True)


# class Tài Khoản(id, tên đăng nhập, mật khaẩu, trạng thái(True = active, False = inactive)
class Account(Base, UserMixin):
    __tablename__ = 'accounts'
    user_name = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=False, default='https://static.vecteezy.com/system/resources/previews/046/010/545/non_2x/user-icon-simple-design-free-vector.jpg')
    user_role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    status = Column(Boolean, nullable=False, default=True)

    customer = relationship("Customer", backref="account", lazy=True, uselist=False)
    staff = relationship("Staff", backref="account", lazy=True, uselist=False)

    def __str__(self):
        return self.user_name

    def is_customer(self):
        return self.user_role == UserRole.CUSTOMER

    def is_staff(self):
        return self.user_role == UserRole.STAFF and self.staff.position == Position.STAFF

    def is_admin(self):
        return self.user_role == UserRole.ADMIN

    def is_cashier(self):
        return self.user_role == UserRole.STAFF and self.staff.position == Position.CASHIER


# class Nguyên liệu(id, tên, đơn vị, số lượng hiện tại, ngày nhập)
class Ingredient(Base):
    __tablename__ = 'ingredients'
    name = Column(String(100), nullable=False)
    unit = Column(String(20), nullable=False)
    remaining = Column(Float, nullable=False, default=0)
    received_date = Column(DateTime, nullable=False, default=datetime.now)

    def __str__(self):
        return self.name

# class Công thức(id, nguyên liệu, sản phẩm, số lượng cần)
class Recipe(Base):
    __tablename__ = 'recipes'
    amount = Column(Float, nullable=False, default=1)

    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    ingredient = relationship("Ingredient", backref="recipes", lazy=True)
    product = relationship("Product", backref="recipes", lazy=True)

    def __str__(self):
        return f"{self.ingredient.name} ({self.amount}{self.ingredient.unit})"

# class Đơn hàng(id, khách hàng, nhân viên, ngày tạo, tổng tiền, trạng thái)
class Order(Base):
    __tablename__ = 'orders'
    created_date = Column(DateTime, nullable=False, default=datetime.now)
    total_price = Column(Float, nullable=False, default=0)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.IN_PROGRESS)

    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    staff_id = Column(Integer, ForeignKey('staffs.id'), nullable=True)
    order_details = relationship("OrderDetail", backref="order", lazy=True)

    def __str__(self):
        return f"{self.id}_{self.created_date.strftime("%Y-%m-%d").__str__()}"

# class Chi tiết đơn hàng(id, đơn hàng, sản phẩm, số lượng, ghi chú)
class OrderDetail(Base):
    __tablename__ = 'order_details'
    amount = Column(Integer, nullable=False, default=1)
    note = Column(Text, nullable=False, default='')

    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product = relationship("Product", backref="order_details", lazy=True)

    def __str__(self):
        return f"{self.product.name} x {self.amount}"

#class Danh mục(id, tên)
class Category(Base):
    __tablename__ = 'categories'
    name = Column(String(100), nullable=False)
    products = relationship("Product", backref="category", lazy=True)

    def __str__(self):
        return self.name

#class Sản Phẩm(id, tên, đơn vị, giá, ảnh minh hoạ, loại danh mục)
class Product(Base):
    __tablename__ = 'products'
    name = Column(String(100), nullable=False)
    unit = Column(String(20), nullable=False)
    price = Column(Float, default=0)
    image = Column(String(255), default='https://res.cloudinary.com/dphz3ewhr/image/upload/v1765821427/cup-hot_ow2zbf.svg')

    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    def __str__(self):
        return self.name

class Configuration(Base):
    __tablename__ = 'configuration'
    key = database.Column(database.String(50), unique=True, nullable=False)
    value = database.Column(database.String(255), nullable=False)
    description = database.Column(database.String(255))

    def __str__(self):
        return self.key + ": " + self.value
if __name__ == '__main__':
    with app.app_context():
        database.create_all()
        database.session.commit()
        print("Database created successfully!")