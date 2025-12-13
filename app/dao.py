from sqlalchemy import null

from app.models import Category, Product


#hàm trả về tất cả danh mục đang lưu trong csdl
def load_categories():
    return Category.query.all()

def load_products(category_id=None, keyword=None):
    query = Product.query
    if keyword:
        query = query.filter(Product.name.ilike(f"%{keyword}%"))
    if category_id:
        query = query.filter(Product.category_id.__eq__(category_id))

    return query.all()