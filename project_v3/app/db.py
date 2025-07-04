# backend_local/app/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 1) 读取 .env 中的 DATABASE_URL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# 2) 创建 SQLAlchemy 引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

# 3) 会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 4) ORM 基类
Base = declarative_base()

def get_db():
    """
    FastAPI 依赖，用于在路由中获取一个数据库会话，
    并保证使用后关闭。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
