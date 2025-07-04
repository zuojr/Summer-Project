# backend_local/app/main.py

from fastapi import FastAPI, Query, Body, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
from typing import List, Optional
from sqlalchemy.orm import Session

# 导入数据库引擎与依赖
from .db import get_db, Base, engine

# 导入 Pydantic 模型
from .models import (
    Attraction,
    RecommendRequest,
    ItineraryRequest,
    User,
    Post,
    Comment,
    ItineraryRecord,
    ItineraryItem,
    ItineraryDetail,
)

# 业务逻辑
from .services import recommend, detail, build_itinerary

# ORM CRUD
from .crud_db import (
    create_user_db,
    get_user_db,
    create_post_db,
    list_posts_db,
    add_comment_db,
    list_comments_db,
    toggle_like_db,
    count_likes_db,
    toggle_follow_db,
    save_itinerary_db,
    list_user_itineraries_db,
    list_itinerary_items,
    update_item_positions,
    add_itinerary_item,
    delete_itinerary_item,
)

app = FastAPI(title="Local Travel Prototype")

# 启动时自动创建所有表
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- 景点推荐 / 行程 ----
@app.get(
    "/attractions",
    response_model=List[Attraction],
    summary="查询候选景点"
)
def api_recommend(
    destination: Optional[str] = Query(None, description="目的地关键词"),
    days: int = Query(1, gt=0, description="行程天数"),
    preferences: List[str] = Query([], description="偏好标签列表")
):
    req = RecommendRequest(destination=destination or "", days=days, preferences=preferences)
    return recommend(req)

@app.get(
    "/attractions/{id}",
    response_model=Attraction,
    summary="查询景点详情（含优缺点）"
)
def api_detail(id: str):
    return detail(id)

@app.post(
    "/itinerary",
    response_model=List[dict],
    summary="生成行程草稿"
)
def api_itinerary(req: ItineraryRequest):
    return build_itinerary(req)

@app.get("/", include_in_schema=False)
def health_check():
    return {"status": "ok", "message": "Travel API is running"}

# ---- 用户注册 & 查询 ----
@app.post(
    "/users",
    response_model=User,
    summary="注册新用户"
)
def api_signup(
    username: str = Body(...),
    nickname: str = Body(...),
    db: Session = Depends(get_db)
):
    return create_user_db(db, username, nickname)

@app.get(
    "/users/{user_id}",
    response_model=User,
    summary="查询用户信息"
)
def api_get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    user = get_user_db(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ---- 帖子 / 评论 / 点赞 ----
@app.post(
    "/posts",
    response_model=Post,
    summary="发布新帖子"
)
def api_create_post(
    user_id: str = Body(...),
    content: str = Body(...),
    images: List[str] = Body([], description="可选，图片 URL 列表"),
    db: Session = Depends(get_db)
):
    return create_post_db(db, user_id, content, images)

@app.get(
    "/posts",
    response_model=List[Post],
    summary="获取所有帖子"
)
def api_list_posts(
    db: Session = Depends(get_db)
):
    return list_posts_db(db)

@app.post(
    "/posts/{post_id}/comments",
    response_model=Comment,
    summary="对帖子添加评论"
)
def api_add_comment(
    post_id: str,
    user_id: str = Body(...),
    content: str = Body(...),
    db: Session = Depends(get_db)
):
    return add_comment_db(db, post_id, user_id, content)

@app.get(
    "/posts/{post_id}/comments",
    response_model=List[Comment],
    summary="获取帖子评论列表"
)
def api_list_comments(
    post_id: str,
    db: Session = Depends(get_db)
):
    return list_comments_db(db, post_id)

@app.post(
    "/posts/{post_id}/like",
    summary="点赞／取消点赞"
)
def api_toggle_like(
    post_id: str,
    user_id: str = Body(...),
    db: Session = Depends(get_db)
):
    return toggle_like_db(db, user_id, post_id)

@app.get(
    "/posts/{post_id}/likes",
    summary="查询点赞数量"
)
def api_count_likes(
    post_id: str,
    db: Session = Depends(get_db)
):
    return {"count": count_likes_db(db, post_id)}

# ---- 关注 ----
@app.post(
    "/users/{user_id}/follow/{target_user_id}",
    summary="关注／取关用户"
)
def api_toggle_follow(
    user_id: str,
    target_user_id: str,
    db: Session = Depends(get_db)
):
    return toggle_follow_db(db, user_id, target_user_id)

# ---- 我的行程：保存 & 列表 ----
@app.post(
    "/users/{user_id}/itineraries",
    response_model=ItineraryRecord,
    summary="保存行程到我的收藏"
)
def api_save_itinerary(
    user_id: str,
    title: Optional[str] = Body(None, description="行程标题，可空"),
    selected_ids: List[str] = Body(..., description="已选景点 ID 列表"),
    days: int = Body(..., gt=0, description="行程天数"),
    preferences: List[str] = Body(..., description="行程偏好标签"),
    db: Session = Depends(get_db)
):
    itinerary = build_itinerary(
        ItineraryRequest(selected_ids=selected_ids, days=days, preferences=preferences)
    )
    return save_itinerary_db(
        db, user_id, title, selected_ids, days, preferences, itinerary
    )

@app.get(
    "/users/{user_id}/itineraries",
    response_model=List[ItineraryRecord],
    summary="获取我的行程列表"
)
def api_list_user_itineraries(
    user_id: str,
    db: Session = Depends(get_db)
):
    return list_user_itineraries_db(db, user_id)

# ---- 行程明细编辑 ----
@app.get(
    "/itineraries/{itinerary_id}/items",
    response_model=ItineraryDetail,
    summary="获取行程明细（按 day+position 排序）"
)
def api_list_items(
    itinerary_id: str,
    db: Session = Depends(get_db)
):
    return ItineraryDetail(
        itinerary_id=itinerary_id,
        items=list_itinerary_items(db, itinerary_id)
    )

@app.patch(
    "/itineraries/{itinerary_id}/items",
    summary="批量更新行程项顺序"
)
def api_update_positions(
    itinerary_id: str,
    updates: List[dict] = Body(..., example=[{"id":"...","new_position":2}]),
    db: Session = Depends(get_db)
):
    return update_item_positions(db, updates)

@app.post(
    "/itineraries/{itinerary_id}/items",
    response_model=ItineraryItem,
    summary="向行程中添加一个景点"
)
def api_add_item(
    itinerary_id: str,
    day: int = Body(..., ge=1),
    position: int = Body(..., ge=0),
    attraction_id: str = Body(...),
    db: Session = Depends(get_db)
):
    return add_itinerary_item(db, itinerary_id, day, position, attraction_id)

@app.delete(
    "/itineraries/items/{item_id}",
    summary="删除行程中的一个景点"
)
def api_delete_item(
    item_id: str,
    db: Session = Depends(get_db)
):
    return delete_itinerary_item(db, item_id)

