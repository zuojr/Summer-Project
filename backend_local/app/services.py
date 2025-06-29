from typing import List
from .crud import list_attractions, get_posts_for
from .ai_services import summarize_pros_cons, generate_itinerary
from .models import RecommendRequest, ItineraryRequest, Attraction

# 推荐候选景点
def recommend(req: RecommendRequest) -> List[Attraction]:
    cands = list_attractions(req.destination)
    # TODO: 根据 prefs 做二次过滤或打分排序
    return cands

# 生成景点详情（含优缺点）
def detail(attraction_id: str) -> Attraction:
    base = next(a for a in list_attractions("") if a.id == attraction_id)
    posts = get_posts_for(attraction_id)
    return summarize_pros_cons(base, posts)

# 基于选点生成行程草稿
def build_itinerary(req: ItineraryRequest) -> List[dict]:
    all_at = list_attractions("")
    selected = [a for a in all_at if a.id in req.selected_ids]
    return generate_itinerary(selected, req.days, req.preferences)