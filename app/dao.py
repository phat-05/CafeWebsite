from sqlalchemy import null, desc

from app.models import Category, Product


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