# backend_local/app/models_orm.py

import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .db import Base

class AttractionORM(Base):
    __tablename__ = "attractions"
    id          = Column(String, primary_key=True, index=True)
    name        = Column(String, index=True)
    description = Column(Text)
    lat         = Column(Float)
    lon         = Column(Float)
    tags        = Column(Text)   # 存 JSON 列表
    images      = Column(Text)   # 存 JSON 列表
    address     = Column(String)

class UserORM(Base):
    __tablename__ = "users"
    id       = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    nickname = Column(String)
    avatar   = Column(String)
    bio      = Column(Text)

class PostORM(Base):
    __tablename__ = "posts"
    id         = Column(String, primary_key=True, index=True)
    user_id    = Column(String, ForeignKey("users.id"))
    content    = Column(Text)
    images     = Column(Text)      # JSON 列表
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    author     = relationship("UserORM")

class CommentORM(Base):
    __tablename__ = "comments"
    id         = Column(String, primary_key=True, index=True)
    post_id    = Column(String, ForeignKey("posts.id"))
    user_id    = Column(String, ForeignKey("users.id"))
    content    = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class LikeORM(Base):
    __tablename__ = "likes"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    post_id = Column(String, ForeignKey("posts.id"), primary_key=True)

class FollowORM(Base):
    __tablename__ = "follows"
    user_id        = Column(String, ForeignKey("users.id"), primary_key=True)
    target_user_id = Column(String, ForeignKey("users.id"), primary_key=True)

class ItineraryORM(Base):
    __tablename__ = "itineraries"
    id           = Column(String, primary_key=True, index=True)
    user_id      = Column(String, ForeignKey("users.id"))
    title        = Column(String)
    selected_ids = Column(Text)      # JSON 列表
    days         = Column(String)
    preferences  = Column(Text)      # JSON 列表
    itinerary    = Column(Text)      # JSON
    created_at   = Column(DateTime, default=datetime.datetime.utcnow)
    # 可选：添加关系以便级联查询
    items        = relationship("ItineraryItemORM", back_populates="itinerary")

class ItineraryItemORM(Base):
    __tablename__ = "itinerary_items"
    id            = Column(String, primary_key=True, index=True)
    itinerary_id  = Column(String, ForeignKey("itineraries.id"), index=True)
    day           = Column(Integer, index=True)
    position      = Column(Integer, index=True)
    attraction_id = Column(String, index=True)

    # 与主表建立双向关系
    itinerary     = relationship("ItineraryORM", back_populates="items")
