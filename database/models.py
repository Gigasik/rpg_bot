from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50))
    balance = Column(Integer, default=100)

class Character(Base):
    __tablename__ = "characters"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    level = Column(Integer, default=1)
    health = Column(Integer, default=100)

class Market(Base):
    __tablename__ = "market"
    item_id = Column(Integer, primary_key=True)
    name = Column(String(50), default="Меч")
    base_price = Column(Integer, default=50)
    supply = Column(Integer, default=100)
