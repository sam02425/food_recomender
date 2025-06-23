from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    orders = relationship('Order', back_populates='user')

class MenuItem(Base):
    __tablename__ = 'menu_items'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text)
    calories = Column(Integer)
    category = Column(String, nullable=False)  # e.g. protein, sauce, base, veggie

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    total = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order')

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'))
    quantity = Column(Integer, default=1)
    order = relationship('Order', back_populates='items')
    menu_item = relationship('MenuItem')