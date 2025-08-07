from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# Модели пользователей
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50))
    balance = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

# Модели персонажей
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

# Модели ресурсов
class Resource(Base):
    __tablename__ = "resources"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    wood = Column(Integer, default=0)
    stone = Column(Integer, default=0)
    food = Column(Integer, default=0)
    last_collection = Column(DateTime, default=datetime.utcnow)

# Модели построек
class Building(Base):
    __tablename__ = "buildings"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    gold_mine_level = Column(Integer, default=1)
    farm_level = Column(Integer, default=1)
    lumber_mill_level = Column(Integer, default=1)
    stone_quarry_level = Column(Integer, default=1)
    last_collection = Column(DateTime, default=datetime.utcnow)
    last_upgrade = Column(DateTime, default=datetime.utcnow)

# Модели для рынка
class MarketItem(Base):
    __tablename__ = "market_items"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200))
    base_price = Column(Integer, default=50)
    current_price = Column(Integer, default=50)
    supply = Column(Integer, default=100)
    demand = Column(Integer, default=50)
    price_change = Column(Float, default=0.0)
    last_update = Column(DateTime, default=datetime.utcnow)

# Модели транзакций
class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey("users.user_id"))
    seller_id = Column(Integer, ForeignKey("users.user_id"))
    item_id = Column(Integer, ForeignKey("market_items.id"))
    quantity = Column(Integer, default=1)
    price = Column(Integer)
    transaction_type = Column(String(20), default="market")  # market, player
    timestamp = Column(DateTime, default=datetime.utcnow)

# Модели для крафта
class CraftingRecipe(Base):
    __tablename__ = "crafting_recipes"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    output_item = Column(String(50), nullable=False)
    output_quantity = Column(Integer, default=1)
    gold_cost = Column(Integer, default=0)
    wood_cost = Column(Integer, default=0)
    stone_cost = Column(Integer, default=0)
    food_cost = Column(Integer, default=0)
    required_level = Column(Integer, default=1)

# Модели для заданий
class DailyQuest(Base):
    __tablename__ = "daily_quests"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    quest_type = Column(String(50), nullable=False)
    target = Column(Integer, default=1)
    progress = Column(Integer, default=0)
    reward_gold = Column(Integer, default=10)
    reward_exp = Column(Integer, default=20)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
