# backend_local/app/services.py

from typing import List
import json

from .crud_db import list_attractions_db, get_attraction_db
from .crud import get_posts_for
from .ai_services import summarize_pros_cons, generate_itinerary
from .models import RecommendRequest, ItineraryRequest, Attraction
from .db import SessionLocal

def recommend(req: RecommendRequest) -> List[Attraction]:
    """
    查询候选景点，并可根据偏好进行二次过滤或排序（TODO）。
    """
    db = SessionLocal()
    try:
        # 从数据库中拉取所有符合目的地的景点
        cands = list_attractions_db(db, req.destination)
        # TODO: 按 req.preferences 做打分或二次筛选
        return cands
    finally:
        db.close()

def detail(attraction_id: str) -> Attraction:
    """
    读取单个景点基础信息并调用 AI 对爬取的评论做优缺点总结。
    """
    db = SessionLocal()
    try:
        base = get_attraction_db(db, attraction_id)
    finally:
        db.close()

    if base is None:
        raise ValueError(f"Attraction {attraction_id} not found")

    # 从 JSON/Excel/爬虫中拿原始评论
    posts = get_posts_for(attraction_id)
    # 由 AI 服务补全 pros/cons、source_posts
    return summarize_pros_cons(base, posts)

def build_itinerary(req: ItineraryRequest) -> List[dict]:
    """
    根据用户选中的景点与偏好，调用 AI 生成结构化行程方案。
    """
    # 先从数据库读取所有景点
    db = SessionLocal()
    try:
        all_attractions = list_attractions_db(db, "")
    finally:
        db.close()

    # 过滤出用户已选的景点对象
    selected = [a for a in all_attractions if a.id in req.selected_ids]
    if not selected:
        return []

    # 调用 AI 生成行程
    itinerary = generate_itinerary(selected, req.days, req.preferences)
    # 确保返回值为 List[dict]
    if isinstance(itinerary, str):
        try:
            itinerary = json.loads(itinerary)
        except json.JSONDecodeError:
            itinerary = []
    return itinerary
