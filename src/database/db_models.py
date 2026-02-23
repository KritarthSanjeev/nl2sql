from sqlalchemy import Integer, String, Float, ForeignKey, Column, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

#market place db four tables 1) Users, 2) Products, 3) Orders, 4) OrderItems

orm_obj = declarative_base() # ORM mapping used to create tables using metadata

class User(orm_obj):
    __tablename__ = "users"
    __table_args__ = {"comment": "Stores both buyer and seller information"}

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    user_type = Column(String,comment="Role of User: Buyer or Seller")


class Product(orm_obj):
    __tablename__ = "products"
    __table_args__ = {"comment": "Contains the information of the products"}

    product_id = Column(Integer,primary_key = True)
    seller_id = Column(Integer, ForeignKey("users.user_id"))
    name = Column(String, nullable = False)
    description = Column(Text)
    price = Column(Float, nullable = False)
    stock_count = Column(Integer, default = 0)
    category = Column(String, comment="Eg Electronics, Groceries, Healthcare etc ... ")

class Orders(orm_obj):
    __tablename__ = "orders"
    __table_args__ = {"comment": "All the information regarding the Order or Order details"}

    order_id = Column(Integer,primary_key=True)
    buyer_id = Column(Integer,ForeignKey("users.user_id"))
    order_status = Column(String, nullable=False)
    total_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class OrderItems(orm_obj):
    __tablename__ = "orderitems"
    __table_args__ = {"comment":"Information regarding the Items that have been ordered Ex price, quantity"}

    item_id = Column(Integer,primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer)
    price_at_purchase = Column(Float)