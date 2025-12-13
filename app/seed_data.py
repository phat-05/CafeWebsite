import random
from app import app, database
from models import Category, Product

# Ảnh mặc định
DEFAULT_IMAGE = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRtoeck-tuXcEZoyQD_uTfrNfxdimBsNCiUog&s"

# DỮ LIỆU SẢN PHẨM
PRODUCT_DATA = {
    "Cà phê": [
        "Cà phê đen nóng", "Cà phê đen đá", "Cà phê sữa nóng", "Cà phê sữa đá",
        "Bạc xỉu", "Latte", "Cappuccino", "Espresso",
        "Americano", "Mocha", "Cold Brew", "Cold Brew sữa"
    ],
    "Trà": [
        "Trà đào cam sả", "Trà đào", "Trà vải", "Trà chanh",
        "Trà tắc", "Trà gừng", "Trà lài", "Trà hoa cúc",
        "Trà sen vàng", "Trà sữa truyền thống", "Trà sữa trân châu"
    ],
    "Đá xay": [
        "Matcha đá xay", "Chocolate đá xay", "Oreo đá xay",
        "Caramel đá xay", "Mocha đá xay", "Cookie đá xay"
    ],
    "Nước ép": [
        "Nước cam ép", "Nước táo ép", "Nước dưa hấu ép",
        "Nước cà rốt ép", "Nước thơm ép", "Nước ổi ép"
    ],
    "Sinh tố": [
        "Sinh tố bơ", "Sinh tố dâu", "Sinh tố xoài",
        "Sinh tố chuối", "Sinh tố sapoche", "Sinh tố mãng cầu"
    ],
    "Bánh ngọt": [
        "Bánh tiramisu", "Bánh cheesecake", "Bánh su kem",
        "Bánh muffin socola", "Bánh bông lan trứng muối",
        "Bánh croissant", "Bánh donut", "Bánh macaron"
    ]
}


def seed_data():
    with app.app_context():
        print("🚀 Bắt đầu sinh dữ liệu...")

        database.session.query(Product).delete()
        database.session.query(Category).delete()
        database.session.commit()

        categories = {}

        # 1️⃣ Tạo category
        for cate_name in PRODUCT_DATA.keys():
            cate = Category(
                name=cate_name,
                description=f"Các sản phẩm thuộc danh mục {cate_name}"
            )
            database.session.add(cate)
            categories[cate_name] = cate

        database.session.commit()
        print(f"✔ Đã tạo {len(categories)} danh mục")

        # 2️⃣ Tạo product (~100 sản phẩm)
        for cate_name, product_names in PRODUCT_DATA.items():
            cate = categories[cate_name]

            for i in range(1, 4):  # nhân 3 lần
                for name in product_names:
                    product = Product(
                        name=f"{name} ({i})" if i > 1 else name,
                        unit="Cái" if cate_name == "Bánh ngọt" else "Ly",
                        price=random.randint(25000, 70000),
                        image=DEFAULT_IMAGE,
                        category_id=cate.id
                    )
                    database.session.add(product)

        database.session.commit()
        print("✅ Seed xong ~100 sản phẩm + ảnh mặc định")


if __name__ == "__main__":
    seed_data()
