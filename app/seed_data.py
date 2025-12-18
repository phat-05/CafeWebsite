import random
import hashlib  # <--- Import thư viện hashlib
from datetime import datetime, timedelta
from faker import Faker
from app import app, database
# Import models
from models import (
    Account, UserRole, Customer, Staff, Position,
    Category, Product, Ingredient, Recipe,
    Order, OrderStatus, OrderDetail, Configuration
)

# Cấu hình Faker
fake = Faker('vi_VN')


# Hàm mã hóa MD5 helper để code gọn hơn
def hash_md5(password):
    return hashlib.md5(password.strip().encode('utf-8')).hexdigest()


def seed_database():
    print("--- BẮT ĐẦU SINH DỮ LIỆU LỚN (MD5 VERSION) ---")
    conf1 = Configuration(key='SERVICE_FEE', value='0.05')
    conf2 = Configuration(key='MAX_NUM_OF_ORDERS_ITEMS', value='10')
    conf3 = Configuration(key='INGREDIENT_WARNING_LEVEL', value='5')
    database.session.add_all([conf1, conf2, conf3])
    # ---------------------------------------------------------
    # 1. TẠO DANH MỤC & NGUYÊN LIỆU
    # ---------------------------------------------------------
    categories_list = ["Cà phê", "Trà sữa", "Trà trái cây", "Đá xay", "Sinh tố", "Sữa chua", "Bánh ngọt", "Snack"]
    db_categories = {}

    for name in categories_list:
        cat = Category(name=name)
        database.session.add(cat)
        db_categories[name] = cat

    ing_names = ["Hạt Arabica", "Hạt Robusta", "Sữa tươi", "Sữa đặc", "Đường đen", "Trân châu đen", "Trân châu trắng",
                 "Bột Matcha", "Bột Chocolate", "Kem Cheese", "Dâu tây", "Xoài", "Đào", "Vải", "Bột mì", "Trứng gà"]
    db_ingredients = []
    for name in ing_names:
        ing = Ingredient(
            name=name,
            unit="kg" if "Hạt" in name or "Bột" in name else "lít",
            remaining=random.uniform(50.0, 200.0),
            received_date=fake.date_time_this_year()
        )
        database.session.add(ing)
        db_ingredients.append(ing)

    database.session.commit()
    print("-> Đã xong danh mục và nguyên liệu.")

    # ---------------------------------------------------------
    # 2. TẠO > 150 SẢN PHẨM
    # ---------------------------------------------------------
    product_prefixes = {
        "Cà phê": ["Cà phê đen", "Cà phê sữa", "Bạc xỉu", "Latte", "Cappuccino", "Espresso", "Americano", "Mocha"],
        "Trà sữa": ["Trà sữa truyền thống", "Trà sữa Oolong", "Trà sữa Thái xanh", "Trà sữa Thái đỏ", "Hồng trà sữa"],
        "Trà trái cây": ["Trà lài", "Trà sen", "Trà đào", "Trà vải", "Lục trà"],
        "Đá xay": ["Cookie đá xay", "Matcha đá xay", "Chocolate đá xay", "Cà phê đá xay"],
        "Sinh tố": ["Sinh tố"],
        "Sữa chua": ["Sữa chua đánh đá", "Sữa chua dẻo"],
        "Bánh ngọt": ["Bánh Mousse", "Bánh Tiramisu", "Bánh Cheesecake", "Croissant"],
        "Snack": ["Khoai tây chiên", "Gà viên vui vẻ"]
    }

    flavors = ["", "Trân châu đường đen", "Kem Cheese", "Sương sáo", "Hạt dẻ", "Hạnh nhân", "Caramel", "Muối biển",
               "Dâu tây", "Xoài", "Việt quất", "Chanh dây", "Bạc hà", "Khoai môn", "Đậu đỏ"]

    db_products = []

    print("-> Đang sinh sản phẩm...")
    count_prod = 0
    for cat_name, prefixes in product_prefixes.items():
        category_obj = db_categories.get(cat_name)
        if not category_obj: continue

        for prefix in prefixes:
            selected_flavors = random.sample(flavors, k=random.randint(3, 8))

            for flav in selected_flavors:
                full_name = f"{prefix} {flav}".strip()
                base_price = 25000
                if "Bánh" in cat_name: base_price = 35000
                if "Trà sữa" in cat_name: base_price = 30000

                prod = Product(
                    name=full_name,
                    unit="Cái" if "Bánh" in cat_name or "Snack" in cat_name else "Ly",
                    price=base_price + random.choice([0, 5000, 10000, 15000]),
                    image=f"https://placehold.co/400x400/orange/white?text={full_name.replace(' ', '+')}",
                    category_id=category_obj.id
                )
                database.session.add(prod)
                db_products.append(prod)
                count_prod += 1

    database.session.commit()

    for prod in db_products:
        ings = random.sample(db_ingredients, k=random.randint(1, 2))
        for ing in ings:
            rec = Recipe(amount=0.1, ingredient_id=ing.id, product_id=prod.id)
            database.session.add(rec)

    database.session.commit()
    print(f"-> Đã tạo xong {count_prod} sản phẩm.")

    # ---------------------------------------------------------
    # 3. TẠO ADMIN, STAFF, KHÁCH HÀNG (Dùng MD5)
    # ---------------------------------------------------------
    # Admin
    admin = Account(
        user_name="admin",
        password=hash_md5("123"),  # <--- Đã sửa thành MD5
        user_role=UserRole.ADMIN,
        status=True
    )
    database.session.add(admin)

    # Staff (20 người)
    db_staffs = []
    for i in range(20):
        acc = Account(
            user_name=f"staff{i}",
            password=hash_md5("123"),  # <--- Đã sửa thành MD5
            user_role=UserRole.STAFF,
            status=True
        )
        database.session.add(acc)
        database.session.flush()

        st = Staff(name=fake.name(), phone=fake.phone_number(), email=fake.email(),
                   position=random.choice(list(Position)), salary=8000000, account_id=acc.id)
        database.session.add(st)
        db_staffs.append(st)

    # Customer (300 người)
    db_customers = []
    print("-> Đang tạo 300 khách hàng...")
    for i in range(300):
        acc = Account(
            user_name=f"user{i}",
            password=hash_md5("123"),  # <--- Đã sửa thành MD5
            user_role=UserRole.CUSTOMER,
            status=True
        )
        database.session.add(acc)
        database.session.flush()

        cus = Customer(name=fake.name(), phone=fake.phone_number(), email=fake.email(), address=fake.address(),
                       account_id=acc.id)
        database.session.add(cus)
        db_customers.append(cus)

    database.session.commit()
    print("-> Đã xong Users (Password: 123456).")

    # ---------------------------------------------------------
    # 4. TẠO 2500 ĐƠN HÀNG
    # ---------------------------------------------------------
    print("-> Đang sinh 2500 đơn hàng...")

    TOTAL_ORDERS = 2500
    batch_size = 100

    for i in range(TOTAL_ORDERS):
        created_date = fake.date_time_between(start_date='-1y', end_date='now')

        cus = random.choice(db_customers)
        st = random.choice(db_staffs) if random.random() > 0.2 else None

        order = Order(
            created_date=created_date,
            status=random.choice(
                [OrderStatus.COMPLETED, OrderStatus.COMPLETED, OrderStatus.COMPLETED, OrderStatus.IN_PROGRESS]),
            customer_id=cus.id,
            staff_id=st.id if st else None,
            total_price=0
        )
        database.session.add(order)
        database.session.flush()

        items_count = random.randint(1, 6)
        selected_prods = random.sample(db_products, k=items_count)

        current_total = 0
        for prod in selected_prods:
            qty = random.randint(1, 3)
            detail = OrderDetail(
                amount=qty,
                note=random.choice(["", "Ít ngọt", "Nhiều đá", "Mang về"]) if random.random() > 0.7 else "",
                order_id=order.id,
                product_id=prod.id
            )
            database.session.add(detail)
            current_total += prod.price * qty

        order.total_price = current_total

        if i % batch_size == 0:
            database.session.commit()
            print(f"   ...Đã tạo {i}/{TOTAL_ORDERS} đơn")

    database.session.commit()
    print("--- HOÀN TẤT TOÀN BỘ DỮ LIỆU ---")


if __name__ == '__main__':
    with app.app_context():
        # Xóa hết dữ liệu cũ để tránh lỗi trùng lặp (nếu cần)
        database.drop_all()
        database.create_all()

        seed_database()