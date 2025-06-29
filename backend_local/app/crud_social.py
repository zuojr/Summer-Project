import json, uuid, datetime
from pathlib import Path
from fastapi import HTTPException
from .models import User, Post, Comment, Like, Follow, ItineraryRecord

BASE = Path(__file__).parent.parent / "data" / "social"

def _load(name):
    f = BASE / f"{name}.json"
    return json.loads(f.read_text(encoding="utf-8"))

def _save(name, arr):
    f = BASE / f"{name}.json"
    f.write_text(json.dumps(arr, ensure_ascii=False, indent=2), encoding="utf-8")

# --- User ---
def create_user(username, nickname):
    users = _load("users")
    if any(u["username"] == username for u in users):
        raise HTTPException(400, "用户名已存在")
    u = User(
       id=str(uuid.uuid4()),
       username=username,
       nickname=nickname,
       avatar=None,
       bio="",
    )
    users.append(u.dict())
    _save("users", users)
    return u

def get_user(user_id):
    users = _load("users")
    for u in users:
        if u["id"] == user_id:
            return User(**u)
    raise HTTPException(404, "用户不存在")

# --- Post ---
def create_post(user_id, content, images):
    posts = _load("posts")
    p = Post(
      id=str(uuid.uuid4()),
      user_id=user_id,
      content=content,
      images=images or [],
      created_at=datetime.datetime.utcnow().isoformat()
    )
    posts.append(p.dict())
    _save("posts", posts)
    return p

def list_posts():
    return [Post(**p) for p in _load("posts")]

# --- Comment ---
def add_comment(post_id, user_id, content):
    comments = _load("comments")
    c = Comment(
      id=str(uuid.uuid4()),
      post_id=post_id,
      user_id=user_id,
      content=content,
      created_at=datetime.datetime.utcnow().isoformat()
    )
    comments.append(c.dict())
    _save("comments", comments)
    return c

def list_comments(post_id):
    return [Comment(**c) for c in _load("comments") if c["post_id"]==post_id]

# --- Like ---
def toggle_like(user_id, post_id):
    likes = _load("likes")
    exists = next((l for l in likes if l["user_id"]==user_id and l["post_id"]==post_id), None)
    if exists:
        likes = [l for l in likes if not (l["user_id"]==user_id and l["post_id"]==post_id)]
        action = "deleted"
    else:
        likes.append(Like(user_id=user_id, post_id=post_id).dict())
        action = "added"
    _save("likes", likes)
    return {"result": action}

def count_likes(post_id):
    return sum(1 for l in _load("likes") if l["post_id"]==post_id)

# --- Follow ---
def toggle_follow(user_id, target_user_id):
    fs = _load("follows")
    exists = next((f for f in fs if f["user_id"]==user_id and f["target_user_id"]==target_user_id), None)
    if exists:
        fs = [f for f in fs if not (f["user_id"]==user_id and f["target_user_id"]==target_user_id)]
        action = "unfollowed"
    else:
        fs.append(Follow(user_id=user_id, target_user_id=target_user_id).dict())
        action = "followed"
    _save("follows", fs)
    return {"result": action}

# --- Itineraries ---
def save_itinerary(user_id, title, selected_ids, days, preferences, itinerary):
    its = _load("itineraries")
    rec = ItineraryRecord(
      id=str(uuid.uuid4()),
      user_id=user_id,
      title=title,
      selected_ids=selected_ids,
      days=days,
      preferences=preferences,
      itinerary=itinerary,
      created_at=datetime.datetime.utcnow().isoformat()
    )
    its.append(rec.dict())
    _save("itineraries", its)
    return rec

def list_user_itineraries(user_id):
    return [ItineraryRecord(**i) for i in _load("itineraries") if i["user_id"]==user_id]
