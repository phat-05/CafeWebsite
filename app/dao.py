from app.models import Category

#hàm trả về tất cả danh mục đang lưu trong csdl
def load_categories():
    return Category.query.all()