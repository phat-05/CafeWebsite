import random
import hashlib
from datetime import datetime
from faker import Faker
from app import app, database
from models import *

fake = Faker('vi_VN')


def hash_md5(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()


def seed_database():
    print("=== SEED DATABASE (DATA THỰC TẾ) ===")

    # ---------------- CONFIG ----------------
    database.session.add_all([
        Configuration(
            key='SERVICE_FEE',
            value='0.05',
            description='Phí dịch vụ (%) cộng vào tổng hoá đơn'
        ),
        Configuration(
            key='MAX_NUM_OF_ORDERS_ITEMS',
            value='10',
            description='Số lượng sản phẩm tối đa trong một hoá đơn'
        ),
        Configuration(
            key='INGREDIENT_WARNING_LEVEL',
            value='5',
            description='Mức tồn kho nguyên liệu tối thiểu để cảnh báo'
        )
    ])

    # ---------------- CATEGORY ----------------
    categories = {
        "Cà phê": [],
        "Trà sữa": [],
        "Trà trái cây": [],
        "Đá xay": [],
        "Bánh ngọt": []
    }

    db_categories = {}
    for name in categories:
        cat = Category(name=name)
        database.session.add(cat)
        db_categories[name] = cat

    database.session.commit()

    # ---------------- INGREDIENT ----------------
    ingredients = [
        "Hạt Arabica", "Hạt Robusta", "Sữa tươi", "Sữa đặc",
        "Trân châu", "Bột matcha", "Chocolate", "Kem cheese"
    ]

    db_ings = []
    for name in ingredients:
        ing = Ingredient(
            name=name,
            unit="kg",
            remaining=random.uniform(20, 100),
            received_date=datetime.now()
        )
        database.session.add(ing)
        db_ings.append(ing)

    database.session.commit()

    # ---------------- PRODUCT (ẢNH THẬT) ----------------
    products_data = [
        ("Cà phê sữa đá", 30000, "Cà phê",
         "https://res.cloudinary.com/demo/image/upload/sample.jpg"),
        ("Bạc xỉu", 32000, "Cà phê",
         "https://res.cloudinary.com/demo/image/upload/sample.jpg"),
        ("Trà sữa trân châu", 35000, "Trà sữa",
         "https://res.cloudinary.com/demo/image/upload/sample.jpg"),
        ("Trà đào cam sả", 40000, "Trà trái cây",
         "https://res.cloudinary.com/demo/image/upload/sample.jpg"),
        ("Matcha đá xay", 45000, "Đá xay",
         "https://res.cloudinary.com/demo/image/upload/sample.jpg"),
        ("Bánh tiramisu", 45000, "Bánh ngọt",
         "https://res.cloudinary.com/demo/image/upload/sample.jpg"),
    ]

    db_products = []
    for name, price, cate, img in products_data:
        prod = Product(
            name=name,
            unit="Ly" if cate != "Bánh ngọt" else "Cái",
            price=price,
            image=img,
            category_id=db_categories[cate].id
        )
        database.session.add(prod)
        db_products.append(prod)

    database.session.commit()

    # recipe
    for prod in db_products:
        for ing in random.sample(db_ings, k=2):
            database.session.add(
                Recipe(amount=0.1, ingredient_id=ing.id, product_id=prod.id)
            )

    database.session.commit()

    # ---------------- ACCOUNT ----------------
    # ADMIN = QUẢN LÝ
    admin_acc = Account(
        user_name="admin",
        password=hash_md5("123"),
        user_role=UserRole.ADMIN,
        status=True
    )
    database.session.add(admin_acc)
    database.session.flush()

    admin_staff = Staff(
        name="Quản lý quán",
        phone="0900000000",
        email="admin@coffee.com",
        position=Position.MANAGER,
        salary=15000000,
        account_id=admin_acc.id
    )
    database.session.add(admin_staff)

    # STAFF
    staffs = []
    for i in range(5):
        acc = Account(
            user_name=f"staff{i}",
            password=hash_md5("123"),
            user_role=UserRole.STAFF,
            status=True
        )
        database.session.add(acc)
        database.session.flush()

        st = Staff(
            name=fake.name(),
            phone=fake.phone_number(),
            email=fake.email(),
            position=Position.STAFF,
            salary=8000000,
            account_id=acc.id
        )
        database.session.add(st)
        staffs.append(st)

    # CUSTOMER
    customers = []
    for i in range(20):
        acc = Account(
            user_name=f"user{i}",
            password=hash_md5("123"),
            user_role=UserRole.CUSTOMER,
            status=True
        )
        database.session.add(acc)
        database.session.flush()

        cus = Customer(
            name=fake.name(),
            phone=fake.phone_number(),
            email=fake.email(),
            address=fake.address(),
            account_id=acc.id
        )
        database.session.add(cus)
        customers.append(cus)

    database.session.commit()

    # ---------------- ORDER ----------------
    for _ in range(50):
        cus = random.choice(customers)
        st = random.choice(staffs)

        order = Order(
            created_date=datetime.now(),
            status=random.choice([OrderStatus.COMPLETED, OrderStatus.IN_PROGRESS]),
            customer_id=cus.id,
            staff_id=st.id
        )
        database.session.add(order)
        database.session.flush()

        total = 0
        for prod in random.sample(db_products, k=random.randint(1, 3)):
            qty = random.randint(1, 2)
            database.session.add(
                OrderDetail(
                    amount=qty,
                    note=random.choice(["", "Ít đá", "Ít ngọt"]),
                    order_id=order.id,
                    product_id=prod.id
                )
            )
            total += prod.price * qty

        order.total_price = total * 1.05  # có phí dịch vụ

    database.session.commit()
    print("=== SEED HOÀN TẤT ===")


if __name__ == "__main__":
    with app.app_context():
        database.drop_all()
        database.create_all()
        seed_database()
