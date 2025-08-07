from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50))
    balance = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

class Character(Base):
    __tablename__ = "characters"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    level = Column(Integer, default=1)
    health = Column(Integer, default=100)
    strength = Column(Integer, default=10)
    armor = Column(Integer, default=5)
    experience = Column(Integer, default=0)
    gold = Column(Integer, default=100)
    last_fight = Column(DateTime, default=datetime.utcnow)

class Resource(Base):
    __tablename__ = "resources"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    wood = Column(Integer, default=0)
    stone = Column(Integer, default=0)
    food = Column(Integer, default=0)
    last_collection = Column(DateTime, default=datetime.utcnow)

class Building(Base):
    __tablename__ = "buildings"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    gold_mine_level = Column(Integer, default=1)
    farm_level = Column(Integer, default=1)
    lumber_mill_level = Column(Integer, default=1)
    stone_quarry_level = Column(Integer, default=1)
    last_collection = Column(DateTime, default=datetime.utcnow)
    last_upgrade = Column(DateTime, default=datetime.utcnow)

class Market(Base):
    __tablename__ = "market"
    item_id = Column(Integer, primary_key=True)
    name = Column(String(50), default="Меч")
    base_price = Column(Integer, default=50)
    supply = Column(Integer, default=100)
