from typing import List
from .models import Attraction, Post

# AI 优缺点归纳（Mock）
# 取正向评论前3条当 pros，负向前3条当 cons
def summarize_pros_cons(attraction: Attraction, posts: List[Post]) -> Attraction:
    pros = [p.content[:50]+"…" for p in sorted(posts, key=lambda x: -x.sentiment)[:3]]
    cons = [p.content[:50]+"…" for p in sorted(posts, key=lambda x: x.sentiment)[:3]]
    attraction.pros = pros
    attraction.cons = cons
    attraction.source_posts = [p.url for p in posts if p.url][:5]
    return attraction

# AI 行程生成（Mock）
def generate_itinerary(selected: List[Attraction], days: int, prefs: List[str]):
    items = []
    for idx, a in enumerate(selected):
        day = (idx % days) + 1
        items.append({
            "day": day,
            "attraction": a.dict(),
            "notes": f"第{day}天游览{a.name}，建议上午出发。"
        })
    return items