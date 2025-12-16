import random
from datetime import datetime, timedelta
import hashlib
from faker import Faker
from app import app, database
from app.models import (
    Account, UserRole, Customer, Staff, Position,
    Category, Product, Ingredient, Recipe, Order, OrderDetail, OrderStatus
)

fake = Faker('vi_VN')
DEFAULT_PASS = hashlib.md5("123456".encode('utf-8')).hexdigest()

# CẤU HÌNH SỐ LƯỢNG
NUM_CUSTOMERS = 200
NUM_ORDERS = 3000
DAYS_HISTORY = 60

# --- 1. DỮ LIỆU NGUYÊN LIỆU (KHO) ---
INGREDIENTS_DATA = [
    # Cà phê
    ("Hạt Arabica Cầu Đất", "kg", 500), ("Hạt Robusta Buôn Ma Thuột", "kg", 500),
    # Sữa & Kem
    ("Sữa Tươi Thanh Trùng", "lít", 1000), ("Sữa Đặc Ngôi Sao", "hộp", 800),
    ("Kem Béo Rich's", "hộp", 300), ("Kem Cheese", "hộp", 200), ("Whipping Cream", "lít", 100),
    ("Sữa Chua Vinamilk", "hộp", 500),
    # Trà
    ("Trà Đen Túi Lọc", "gói", 500), ("Trà Lài", "kg", 200), ("Trà Oolong", "kg", 200),
    ("Bột Matcha Nhật", "kg", 50),
    # Hương liệu & Topping
    ("Syrup Caramel", "chai", 50), ("Syrup Vanilla", "chai", 50), ("Syrup Hạt Dẻ", "chai", 50),
    ("Trân Châu Đen", "kg", 200), ("Trân Châu Trắng", "kg", 200), ("Thạch Đào", "hộp", 100),
    ("Vải Ngâm", "hộp", 100), ("Đào Ngâm", "hộp", 100),
    # Trái cây tươi
    ("Cam Vàng", "kg", 100), ("Sả Cây", "kg", 50), ("Chanh Dây", "kg", 50),
    ("Xoài Cát", "kg", 80), ("Bơ Sáp", "kg", 80), ("Dâu Tây", "kg", 40),
    # Làm bánh
    ("Bột Mì", "kg", 200), ("Trứng Gà", "quả", 1000), ("Bơ Lạt", "kg", 100), ("Phô Mai", "kg", 100),
    # Vật dụng
    ("Ly Nhựa Mang Đi", "cái", 10000), ("Ống Hút", "cái", 10000)
]

# --- 2. DỮ LIỆU MENU (60+ MÓN) ---
# Cấu trúc: Tên Category, List các món (Tên, Giá, Link ảnh)
MENU_DATA = {
    "Cà Phê Phin Việt Nam": [
        ("Phin Đen Đá", 29000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/PHIN-SUA-DA.png"),
        ("Phin Sữa Đá", 29000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/PHIN-SUA-DA.png"),
        ("Bạc Xỉu Đá", 35000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/BAC-XIU.png"),
        ("Cà Phê Trứng Hà Nội", 45000, "https://toplist.vn/images/800px/ca-phe-trung-244242.jpg"),
        ("Cà Phê Cốt Dừa", 45000, "https://congcaphe.com/media/252b47e8-e54e-4e4b-b0b3-f7243914a486.jpg"),
        ("Cà Phê Muối Huế", 39000,
         "https://product.hstatic.net/1000075078/product/ca-phe-muoi_924250268574421b9201083984d72023_master.jpg"),
    ],
    "Espresso & Coffee": [
        ("Espresso", 35000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/ESPRESSO.png"),
        ("Americano", 39000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/AMERICANO.png"),
        ("Cappuccino", 45000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/CAPPUCCINO.png"),
        ("Latte", 45000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/LATTE.png"),
        ("Mocha", 49000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/MOCHA.png"),
        ("Caramel Macchiato", 55000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/CARAMEL-MACCHIATO.png"),
        ("Hazelnut Latte", 49000,
         "https://starbucks-cdn-01.s3.ap-southeast-1.amazonaws.com/Category/Beverage/Hazelnut+Latte.jpg"),
        ("Cold Brew Truyền Thống", 45000,
         "https://product.hstatic.net/1000360860/product/cold_brew_truyen_thong_351586a10058444a8069d2732959685e_master.jpg"),
    ],
    "Trà Trái Cây & Nhiệt Đới": [
        ("Trà Sen Vàng", 45000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/TRA-SEN-VANG.png"),
        ("Trà Thạch Đào", 45000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/TRA-THACH-DAO.png"),
        ("Trà Thanh Đào", 45000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/TRA-THANH-DAO.png"),
        ("Trà Vải Lài", 42000, "https://phuclong.com.vn/uploads/dish/879619179d63c2-tra-vai-lai.png"),
        ("Trà Ổi Hồng", 42000, "https://phuclong.com.vn/uploads/dish/0b3780d38384c9-tra-oi-hong.png"),
        ("Trà Đào Cam Sả", 45000,
         "https://tocotocotea.com/wp-content/uploads/2021/01/Tra-dao-buoi-hong-tran-chau-baby-1.png"),
        ("Trà Xoài Chanh Dây", 45000, "https://tocotocotea.com/wp-content/uploads/2021/01/Tra-xoai-buoi-hong-1.png"),
        ("Trà Dâu Tằm Pha Lê", 42000,
         "https://tocotocotea.com/wp-content/uploads/2021/01/Tra-dau-tam-pha-le-Tuyet.png"),
    ],
    "Trà Sữa & Macchiato": [
        ("Trà Sữa Truyền Thống", 35000, "https://tocotocotea.com/wp-content/uploads/2021/01/Tra-sua-truyen-thong.png"),
        ("Trà Sữa Trân Châu Đường Đen", 45000,
         "https://tocotocotea.com/wp-content/uploads/2021/01/Sua-tuoi-tran-chau-duong-den-1.png"),
        ("Trà Sữa Oolong", 39000, "https://phuclong.com.vn/uploads/dish/2a688975871143-tra-sua-oolong.png"),
        ("Trà Sữa Thái Xanh", 35000, "https://image.cooky.vn/recipe/g/2017/04/18/cooky-recipe-cover-r14574.jpg"),
        ("Trà Sữa Matcha", 42000, "https://tocotocotea.com/wp-content/uploads/2021/01/Tra-sua-matcha-1.png"),
        ("Trà Sữa Khoai Môn", 42000, "https://tocotocotea.com/wp-content/uploads/2021/01/Tra-sua-khoai-mon.png"),
        ("Hồng Trà Macchiato", 39000, "https://tocotocotea.com/wp-content/uploads/2021/01/Hong-tra-kem-pho-mai.png"),
        ("Lục Trà Macchiato", 39000, "https://tocotocotea.com/wp-content/uploads/2021/01/Luc-tra-kem-pho-mai.png"),
    ],
    "Đá Xay (Freeze)": [
        ("Freeze Trà Xanh", 55000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/FREEZE-TRA-XANH.png"),
        ("Freeze Chocolate", 55000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/FREEZE-CHOCO.png"),
        ("Caramel Phin Freeze", 55000,
         "https://highlandscoffee.com.vn/vnt_upload/product/05_2018/CARAMEL-PHIN-FREEZE.png"),
        ("Classic Phin Freeze", 55000,
         "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/CLASSIC-PHIN-FREEZE.png"),
        ("Cookies & Cream", 55000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/COOKIES-CREAM.png"),
        ("Chanh Đá Xay", 45000, "https://phuclong.com.vn/uploads/dish/6e43118949755b-chanh-da-xay.png"),
    ],
    "Sinh Tố & Sữa Chua": [
        ("Sinh Tố Bơ", 49000,
         "https://product.hstatic.net/1000075078/product/sinh-to-bo_9e43257793544a4ab56461f68740523f_master.jpg"),
        ("Sinh Tố Xoài", 45000,
         "https://product.hstatic.net/1000075078/product/sinh-to-xoai_14169992644246069772322307525287_master.jpg"),
        ("Sinh Tố Dâu", 49000,
         "https://product.hstatic.net/1000075078/product/sinh-to-dau_1f834645224346768341613146115354_master.jpg"),
        ("Sữa Chua Trân Châu", 35000,
         "https://tocotocotea.com/wp-content/uploads/2021/01/Sua-chua-tran-chau-hoang-kim.png"),
        ("Sữa Chua Nếp Cẩm", 35000, "https://media.cooky.vn/recipe/v500/recipe23126-636952726354673894.jpg"),
        ("Sữa Chua Dâu Tây", 39000, "https://tocotocotea.com/wp-content/uploads/2021/01/Sua-chua-dau-tam-hat-dieu.png"),
    ],
    "Bánh Ngọt & Bakery": [
        ("Bánh Mì Que Pate", 15000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/BANH-MI-QUE.png"),
        ("Bánh Mì Que Phô Mai", 19000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/BANH-MI-QUE.png"),
        ("Mousse Cacao", 35000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/MOUSSE-CACAO.png"),
        ("Mousse Đào", 35000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/MOUSSE-DAO.png"),
        ("Phô Mai Cà Phê", 35000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/PHO-MAI-CA-PHE.png"),
        ("Tiramisu", 39000, "https://highlandscoffee.com.vn/vnt_upload/product/03_2018/TIRAMISU.png"),
        ("Croissant Trứng Muối", 35000, "https://phuclong.com.vn/uploads/dish/0793108c487399-croissant-trung-muoi.png"),
        ("Bánh Su Kem", 25000, "https://phuclong.com.vn/uploads/dish/5f85055890875c-banh-su-kem.png"),
    ],
    "Ăn Vặt (Snacks)": [
        ("Khô Gà Lá Chanh", 45000, "https://product.hstatic.net/200000407127/product/kho-ga-la-chanh-500g_800x800.jpg"),
        ("Hạt Điều Rang Muối", 45000,
         "https://product.hstatic.net/200000407127/product/hat-dieu-rang-muoi_800x800.jpg"),
        ("Khoai Tây Chiên", 35000,
         "https://cdn.tgdd.vn/Files/2019/10/24/1211756/cach-lam-khoai-tay-chien-bang-noi-chien-khong-dau-gion-rum-nhu-kfc-202201191024328225.jpg"),
        ("Xúc Xích Nướng", 25000,
         "https://cpfoods.vn/upload/news/xuc-xich-cp-heo-tiem-tuyet-dinh-thom-ngon-bo-duong-1.jpg"),
    ]
}


def generate_static_data():
    """Tạo Menu khủng và Kho"""
    print("🔄 Đang khởi tạo Menu và Kho Nguyên Liệu...")

    # 1. Categories
    cats_db = {}
    for cat_name in MENU_DATA.keys():
        c = Category(name=cat_name)
        database.session.add(c)
        database.session.flush()  # Để lấy ID ngay
        cats_db[cat_name] = c

    # 2. Ingredients
    ings_db = []
    for name, unit, qty in INGREDIENTS_DATA:
        ing = Ingredient(
            name=name, unit=unit, remaining=qty,
            received_date=datetime.now() - timedelta(days=random.randint(1, 60))
        )
        database.session.add(ing)
        ings_db.append(ing)
    database.session.commit()

    # 3. Products & Recipes (Tự động gán nguyên liệu ngẫu nhiên để có data)
    all_products = []
    print("   -> Đang lên thực đơn...")

    for cat_name, items in MENU_DATA.items():
        cat_obj = cats_db[cat_name]

        for p_name, p_price, p_img in items:
            prod = Product(
                name=p_name, unit="Ly" if "Bánh" not in cat_name else "Cái",
                price=p_price, image=p_img, category_id=cat_obj.id
            )
            database.session.add(prod)
            database.session.flush()
            all_products.append(prod)

            # Tự động tạo công thức (Recipe) giả lập
            # Mỗi món lấy ngẫu nhiên 2-4 nguyên liệu để trừ kho cho vui
            num_ing = random.randint(2, 4)
            selected_ings = random.sample(ings_db, num_ing)
            for ing in selected_ings:
                # Logic đơn giản: Đồ uống dùng ít nguyên liệu, bánh dùng nhiều
                amt = random.uniform(0.01, 0.2)
                rec = Recipe(
                    product_id=prod.id,
                    ingredient_id=ing.id,
                    amount=round(amt, 3)
                )
                database.session.add(rec)

    database.session.commit()
    return all_products, ings_db


def generate_staff():
    """Tạo đội ngũ nhân viên"""
    print("🔄 Đang tuyển dụng nhân sự...")

    # 1 Admin
    admin_acc = Account(user_name="admin", password=DEFAULT_PASS, user_role=UserRole.ADMIN)
    database.session.add(admin_acc)

    staff_objs = []
    positions = [Position.MANAGER, Position.CASHIER, Position.STAFF]

    for i in range(25):  # 25 Nhân viên
        username = f"staff{i + 1}"
        acc = Account(user_name=username, password=DEFAULT_PASS, user_role=UserRole.STAFF)
        database.session.add(acc)
        database.session.flush()

        pos = random.choice(positions)
        salary = 15000000 if pos == Position.MANAGER else (8000000 if pos == Position.CASHIER else 6000000)

        staff = Staff(
            name=fake.name(), phone=fake.phone_number(), email=fake.email(),
            position=pos, salary=salary, account_id=acc.id
        )
        database.session.add(staff)
        staff_objs.append(staff)

    database.session.commit()
    return staff_objs


def generate_customers():
    """Tạo khách hàng"""
    print(f"🔄 Đang tạo hồ sơ {NUM_CUSTOMERS} khách hàng thân thiết...")

    cust_objs = []
    for i in range(NUM_CUSTOMERS):
        username = f"user{i + 1}"
        acc = Account(user_name=username, password=DEFAULT_PASS, user_role=UserRole.CUSTOMER)
        database.session.add(acc)
        database.session.flush()

        cust = Customer(
            name=fake.name(), phone=fake.phone_number(), email=fake.email(),
            address=fake.address(), account_id=acc.id
        )
        database.session.add(cust)
        cust_objs.append(cust)

    database.session.commit()
    return cust_objs


def generate_orders(customers, staffs, products):
    """Tạo 3000 đơn hàng lịch sử"""
    print(f"🔄 Đang vận hành hệ thống ({NUM_ORDERS} đơn hàng)... Vui lòng đợi!")

    def random_time(date_base):
        # Giờ cao điểm: 7h-9h, 12h, 19h
        hour = random.choices(
            [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
            weights=[15, 15, 10, 5, 5, 15, 10, 5, 5, 5, 5, 10, 15, 10, 5], k=1
        )[0]
        return date_base.replace(hour=hour, minute=random.randint(0, 59))

    start_date = datetime.now() - timedelta(days=DAYS_HISTORY)
    count = 0

    for _ in range(NUM_ORDERS):
        day_offset = random.randint(0, DAYS_HISTORY)
        current_date = start_date + timedelta(days=day_offset)
        order_time = random_time(current_date)

        # Tạo Order
        order = Order(
            created_date=order_time, total_price=0, status=OrderStatus.COMPLETED,
            customer_id=random.choice(customers).id,
            staff_id=random.choice(staffs).id
        )
        database.session.add(order)
        database.session.flush()

        # Random 1-6 món/đơn
        num_items = random.randint(1, 6)
        selected_prods = random.choices(products, k=num_items)

        current_total = 0
        for prod in selected_prods:
            qty = random.randint(1, 3)
            note = random.choice(["", "", "Ít đá", "Nhiều sữa", "Mang về", "Không đường"])

            detail = OrderDetail(
                amount=qty, note=note, order_id=order.id, product_id=prod.id
            )
            database.session.add(detail)
            current_total += (prod.price * qty)

        order.total_price = current_total

        count += 1
        if count % 500 == 0:
            print(f"   -> Đã xử lý {count}/{NUM_ORDERS} đơn...")
            database.session.commit()

    database.session.commit()


if __name__ == '__main__':
    with app.app_context():
        print("⚠ Đang reset Database...")
        database.drop_all()
        database.create_all()

        products, ingredients = generate_static_data()
        staffs = generate_staff()
        customers = generate_customers()
        generate_orders(customers, staffs, products)

        print("\n" + "=" * 50)
        print("✅ DỮ LIỆU KHỔNG LỒ ĐÃ ĐƯỢC TẠO XONG!")
        print(f" - Món ăn: {len(products)} món (Đủ thể loại)")
        print(f" - Khách hàng: {len(customers)}")
        print(f" - Đơn hàng: {NUM_ORDERS}")
        print(f" - Admin: admin / 123456")
        print("=" * 50)