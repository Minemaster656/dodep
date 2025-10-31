from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    deleted = Column(Integer, default=0)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    last_seen_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    session_uuid = Column(String)
    avatar = Column(String, default='🤑')
    avatarcolor1 = Column(String, default='slate-600')
    avatarcolor2 = Column(String, default='slate-900')
    avatargradientvar = Column(Integer, default=0)
    color1 = Column(String, default='neutral-50')
    color2 = Column(String, default='neutral-700')
    about = Column(Text)
    top3_wins = Column(String, default='0 0 : 0 0 : 0 0')
    balance = Column(Float, default=100)
    debt = Column(Float, default=0)
    top_balance = Column(Float, default=0)
    top_debt = Column(Float, default=0)
    works_count = Column(Integer, default=0)
    casino_count = Column(Integer, default=0)


class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    target = Column(Integer, ForeignKey('users.id'), nullable=False)
    sender = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # 'bet', 'win', 'work', 'debt_change', 'transfer'
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    activity_type = Column(String)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())


class FavActivity(Base):
    __tablename__ = 'fav_activities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    activity_type = Column(String)
    weight = Column(Integer, default=0)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())


class Relationship(Base):
    __tablename__ = 'relationships'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    requester_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    STATE = Column(Integer, default=0)  # -1:BLOCK 0:REQUEST_FRIENDS 1:FRIENDS
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat())
