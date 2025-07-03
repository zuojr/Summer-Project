# app/main.py

from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import os


from .models import (
    Attraction,
    RecommendRequest,
    ItineraryRequest,
    User,
    Post,
    Comment,
    Like,
    Follow,
    ItineraryRecord,
)
from .services import recommend, detail, build_itinerary
from .crud_social import (
    create_user, get_user,
    create_post, list_posts,
    add_comment, list_comments,
    toggle_like, count_likes,
    toggle_follow,
    save_itinerary, list_user_itineraries
)


# 手动挂载 FastAPI 的 Static 目录
app = FastAPI(title="Local Travel Prototype")

# 取得 static 文件夹的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请锁定域名
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 景点推荐 / 行程接口 ---
@app.get("/attractions", response_model=List[Attraction])
def api_recommend(
    destination: Optional[str] = Query(None, description="目的地关键词"),
    days: int = Query(1, gt=0, description="行程天数"),
    preferences: List[str] = Query([], description="偏好标签列表")
):
    req = RecommendRequest(destination=destination or "", days=days, preferences=preferences)
    return recommend(req)

@app.get("/attractions/{id}", response_model=Attraction)
def api_detail(id: str):
    return detail(id)

@app.post("/itinerary", response_model=List[dict])
def api_itinerary(req: ItineraryRequest):
    return build_itinerary(req)

@app.get("/", include_in_schema=False)
def health_check():
    return {"status": "ok", "message": "Travel API is running"}

# --- 用户注册 & 查询 ---
@app.post("/users", response_model=User)
def api_signup(username: str, nickname: str):
    return create_user(username, nickname)

@app.get("/users/{user_id}", response_model=User)
def api_get_user(user_id: str):
    return get_user(user_id)

# --- 帖子 & 评论 & 点赞 ---
@app.post("/posts", response_model=Post)
def api_create_post(user_id: str, content: str, images: List[str] = Body([])):
    return create_post(user_id, content, images)

@app.get("/posts", response_model=List[Post])
def api_list_posts():
    return list_posts()

@app.post("/posts/{post_id}/comments", response_model=Comment)
def api_add_comment(post_id: str, user_id: str, content: str):
    return add_comment(post_id, user_id, content)

@app.get("/posts/{post_id}/comments", response_model=List[Comment])
def api_list_comments(post_id: str):
    return list_comments(post_id)

@app.post("/posts/{post_id}/like")
def api_toggle_like(post_id: str, user_id: str):
    return toggle_like(user_id, post_id)

@app.get("/posts/{post_id}/likes")
def api_count_likes(post_id: str):
    return {"count": count_likes(post_id)}

# --- 关注 ---
@app.post("/users/{user_id}/follow/{target_user_id}")
def api_toggle_follow(user_id: str, target_user_id: str):
    return toggle_follow(user_id, target_user_id)

# --- 保存 & 列出“我的行程” ---
@app.post("/users/{user_id}/itineraries", response_model=ItineraryRecord)
def api_save_itinerary(
    user_id: str,
    title: Optional[str] = Body(None),
    selected_ids: List[str] = Body(...),
    days: int = Body(...),
    preferences: List[str] = Body(...)
):
    itinerary = build_itinerary(ItineraryRequest(
        selected_ids=selected_ids, days=days, preferences=preferences
    ))
    return save_itinerary(user_id, title, selected_ids, days, preferences, itinerary)

@app.get("/users/{user_id}/itineraries", response_model=List[ItineraryRecord])
def api_list_user_itineraries(user_id: str):
    return list_user_itineraries(user_id)
