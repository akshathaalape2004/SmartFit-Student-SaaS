# backend/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    
    # Profile Metrics with fallback values
    age = Column(Integer, default=22)
    weight_kg = Column(Float, default=70.0)
    height_cm = Column(Float, default=175.0)
    gender = Column(String, default="Male")
    goal = Column(String, default="weight_loss")
    diet_preference = Column(String, default="Vegetarian")
    budget = Column(String, default="Low")

    posts = relationship("ForumPost", back_populates="author")
    progress_logs = relationship("ProgressLog", back_populates="user")


class ProgressLog(Base):
    __tablename__ = "progress_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    water_ml = Column(Integer, default=0)
    calories_consumed = Column(Integer, default=0)
    timestamp = Column(String)

    user = relationship("User", back_populates="progress_logs")


class ForumPost(Base):
    __tablename__ = "forum_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username = Column(String, index=True)
    content = Column(String)
    category = Column(String, default="General")
    timestamp = Column(String)
    
    author = relationship("User", back_populates="posts")