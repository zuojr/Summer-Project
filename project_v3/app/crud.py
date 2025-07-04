# app/crud.py

import os
import pandas as pd
from .models import Attraction, Post

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# 读取并重命名列
ATTR_FILE = os.path.join(DATA_DIR, "beijing.csv")
DF = pd.read_csv(
    ATTR_FILE,
    dtype=str,
    encoding="gb18030",
    engine="python"
)

DF.rename(columns={
  "景区id":       "id",
  "景区名称":     "name",
  "介绍":         "description",
  "景区纬度":     "lat",
  "景区经度":     "lon",
  "景区标签列表": "tags",
  "景区展示图片": "images",    # 对应模型 images
  "景区地址":     "address",   # 对应模型 address
}, inplace=True)

# 解析 tags/images 列并转换坐标
DF["tags"]   = DF["tags"].fillna("").apply(lambda s: [t for t in s.split(",") if t])
DF["images"] = DF["images"].fillna("").apply(lambda s: [u for u in s.split(",") if u])
DF["lat"]    = DF["lat"].astype(float)
DF["lon"]    = DF["lon"].astype(float)

DF_ATTRACTIONS = DF

# 加载社媒和携程评论，保持不变
POST_FILE  = os.path.join(DATA_DIR, "xiaohongshu_posts.xlsx")
DF_POSTS   = pd.read_excel(POST_FILE, engine="openpyxl")
CTRIP_FILE = os.path.join(DATA_DIR, "ctrip_comments.xlsx")
DF_CTRIP   = pd.read_excel(CTRIP_FILE, engine="openpyxl")

def list_attractions(dest: str):
    df = DF_ATTRACTIONS.copy()
    if dest:
        df = df[df["name"].str.contains(dest)]
    return [
        Attraction(
            id     = r["id"],
            name   = r["name"],
            description = r.get("description"),
            lat    = r["lat"],
            lon    = r["lon"],
            tags   = r["tags"],
            images = r["images"],     # 返回图片列表
            address= r.get("address"),# 返回地址
            pros   = [],
            cons   = [],
            source_posts=[]
        )
        for _, r in df.iterrows()
    ]

# get_posts_for 保持不变...
def get_posts_for(attraction_id: str):
    """
    返回某景点的所有评论（合并小红书 + 携程），映射成 Post 对象
    """
    posts = []
    # 小红书
    df1 = DF_POSTS[DF_POSTS["attraction_id"] == attraction_id]
    for r in df1.to_dict(orient="records"):
        posts.append(Post(
            post_id=str(r["post_id"]),
            attraction_id=attraction_id,
            content=r["content"],
            url=r.get("url"),
            tags=r.get("tags", "").split(","),
            likes=int(r.get("likes", 0)),
            sentiment=float(r.get("sentiment_score", 0))
        ))
    # 携程
    df2 = DF_CTRIP[DF_CTRIP["attraction_id"] == attraction_id]
    for r in df2.to_dict(orient="records"):
        posts.append(Post(
            post_id=str(r.get("ctrip_comment_id", "")),
            attraction_id=attraction_id,
            content=r.get("comment", ""),
            url=None,
            tags=[],
            likes=0,
            sentiment=0.0
        ))
    return posts
