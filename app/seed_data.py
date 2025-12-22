import random
import hashlib
from datetime import datetime, timedelta
from faker import Faker

from app import app, database
from models import *

fake = Faker("vi_VN")


def hash_md5(password):
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def seed_database():
    print("=== SEED DATABASE: 3000 ORDERS ===")

    # ================= CONFIG =================
    database.session.query(Configuration).delete()

    configs = [
        Configuration(key="SERVICE_FEE", value="0.05", description="Phí dịch vụ 5%"),
        Configuration(key="MAX_NUM_OF_ORDERS_ITEMS", value="10"),
        Configuration(key="INGREDIENT_WARNING_LEVEL", value="5"),
    ]
    database.session.add_all(configs)

    # ================= CATEGORY =================
    categories = []
    for name in ["Cà phê", "Trà sữa", "Đá xay", "Bánh ngọt"]:
        c = Category(name=name)
        database.session.add(c)
        categories.append(c)

    # ================= INGREDIENT =================
    ingredients = []
    for name in ["Cafe hạt", "Sữa tươi", "Đường", "Trà đen", "Matcha"]:
        ing = Ingredient(
            name=name,
            unit="kg",
            remaining=100,
            received_date=datetime.now()
        )
        database.session.add(ing)
        ingredients.append(ing)

    database.session.commit()

    # ================= ACCOUNT + STAFF =================
    staffs = []

    admin_acc = Account(
        user_name="admin",
        password=hash_md5("123"),
        user_role=UserRole.ADMIN
    )
    database.session.add(admin_acc)
    database.session.flush()

    database.session.add(
        Staff(
            name="Admin",
            phone="0909999999",
            email="admin@cafe.com",
            position=Position.MANAGER,
            salary=20000000,
            account_id=admin_acc.id
        )
    )

    for i in range(10):
        acc = Account(
            user_name=f"staff{i}",
            password=hash_md5("123"),
            user_role=UserRole.STAFF
        )
        database.session.add(acc)
        database.session.flush()

        st = Staff(
            name=fake.name(),
            phone=fake.phone_number(),
            email=fake.email(),
            position=random.choice([Position.STAFF, Position.CASHIER]),
            salary=8000000,
            account_id=acc.id
        )
        database.session.add(st)
        staffs.append(st)

    # ================= CUSTOMER =================
    customers = []
    for i in range(10):
        acc = Account(
            user_name=f"user{i}",
            password=hash_md5("123"),
            user_role=UserRole.CUSTOMER
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

    # ================= PRODUCT =================
    products = []
    for i in range(100):  # nhiều món
        cate = random.choice(categories) if random.random() > 0.25 else None

        p = Product(
            name=f"Món số {i}",
            unit="Ly",
            price=random.randint(20000, 70000),
            category_id=cate.id if cate else None
        )
        database.session.add(p)
        products.append(p)

    database.session.commit()

    # ================= ORDER =================
    print("→ Đang tạo 3000 đơn hàng...")

    for i in range(3000):
        order = Order(
            created_date=datetime.now() - timedelta(days=random.randint(0, 365)),
            status=random.choice([OrderStatus.COMPLETED, OrderStatus.IN_PROGRESS]),
            customer_id=random.choice(customers).id,
            staff_id=random.choice(staffs).id
        )
        database.session.add(order)
        database.session.flush()

        total = 0
        for prod in random.sample(products, random.randint(1, 5)):
            qty = random.randint(1, 3)
            database.session.add(
                OrderDetail(
                    order_id=order.id,
                    product_id=prod.id,
                    amount=qty,
                    note=random.choice(["", "Ít đá", "Ít đường", "Mang về"])
                )
            )
            total += prod.price * qty

        order.total_price = total * 1.05

        if i % 500 == 0 and i > 0:
            database.session.commit()
            print(f"  ✓ {i} orders")

    database.session.commit()
    print("=== SEED THÀNH CÔNG ===")


if __name__ == "__main__":
    with app.app_context():
        database.drop_all()
        database.create_all()
        seed_database()
