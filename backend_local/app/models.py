# app/models.py

from pydantic import BaseModel
from typing import List, Optional

# --------------------
# 景点与外部爬取帖子模型
# --------------------

class Attraction(BaseModel):
    id: str
    name: str
    description: Optional[str]
    lat: float
    lon: float
    tags: List[str]
    images: List[str] = []        # 小程序展示时作为封面图
    address: Optional[str] = None # 详情页显示的地址
    pros: List[str] = []
    cons: List[str] = []
    source_posts: List[str] = []   # 原始爬取的评论来源链接

class SourcePost(BaseModel):
    """
    用于存储爬虫抓取的小红书/携程等点评内容
    """
    post_id: str
    attraction_id: str
    content: str
    url: Optional[str]
    tags: List[str]
    likes: int
    sentiment: float

# --------------------
# 请求与行程模型
# --------------------

class RecommendRequest(BaseModel):
    destination: str
    days: int
    preferences: List[str]

class ItineraryRequest(BaseModel):
    selected_ids: List[str]
    days: int
    preferences: List[str]

# --------------------
# 社交化用户与互动模型
# --------------------

class User(BaseModel):
    id: str                # UUID
    username: str          # 登录账号
    nickname: str          # 昵称
    avatar: Optional[str] = None
    bio: Optional[str]    = ""

class Post(BaseModel):
    """
    社交平台上的用户帖子（UGC）
    """
    id: str
    user_id: str
    content: str
    images: List[str] = []  # 可为空
    created_at: str         # ISO 时间字符串

class Comment(BaseModel):
    id: str
    post_id: str
    user_id: str
    content: str
    created_at: str

class Like(BaseModel):
    user_id: str
    post_id: str

class Follow(BaseModel):
    user_id: str
    target_user_id: str

class ItineraryRecord(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    selected_ids: List[str]
    days: int
    preferences: List[str]
    itinerary: List[dict]
    created_at: str
