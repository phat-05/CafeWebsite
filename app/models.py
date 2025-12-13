from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from app import database, app


class Base(database.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    def __str__(self):
        return self.name

class Category(Base):
    description = Column(Text)
    products = relationship("Product", backref="category", lazy=True)


class Product(Base):
    unit = Column(String(20), nullable=False)
    price = Column(Float, default=0)
    image = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        database.create_all()


        database.session.commit()