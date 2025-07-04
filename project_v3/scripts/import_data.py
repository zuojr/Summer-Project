# backend_local/scripts/import_data.py

import os
import sys
import json
import uuid
import datetime
import pandas as pd

# 将项目根目录（backend_local）加入 sys.path，确保可以导入 app 模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, "..")))

from app.db import SessionLocal, Base, engine
from app.models_orm import AttractionORM, PostORM, CommentORM

# 确保所有表已创建
Base.metadata.create_all(bind=engine)


def import_attractions(csv_path: str):
    # 尝试多种编码读取 CSV，解决 GBK/UTF-8 编码冲突
    try:
        df = pd.read_csv(csv_path, dtype=str, encoding='utf-8').fillna("")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, dtype=str, encoding='gb18030').fillna("")
    db = SessionLocal()
    for _, row in df.iterrows():
        tags = [t.strip() for t in row.get("景区标签列表", "").split(",") if t.strip()]
        imgs = [u.strip() for u in row.get("景区展示图片", "").split(",") if u.strip()]
        try:
            lat = float(row.get("景区纬度", "0"))
            lon = float(row.get("景区经度", "0"))
        except ValueError:
            continue  # 无效坐标跳过
        orm = AttractionORM(
            id=row.get("景区id", str(uuid.uuid4())),
            name=row.get("景区名称", ""),
            description=row.get("介绍", ""),
            lat=lat,
            lon=lon,
            tags=json.dumps(tags, ensure_ascii=False),
            images=json.dumps(imgs, ensure_ascii=False),
            address=row.get("景区地址", ""),
        )
        db.merge(orm)
    db.commit()
    db.close()
    print("✅ Attractions imported.")


def import_xhs_posts(xlsx_path: str):
    df = pd.read_excel(xlsx_path).fillna("")
    db = SessionLocal()
    for _, row in df.iterrows():
        pid = str(uuid.uuid4())
        orm = PostORM(
            id=pid,
            user_id=row.get("用户ID", ""),
            content=row.get("内容", ""),
            images=json.dumps(row.get("图片URLs", "").split(","), ensure_ascii=False),
            created_at=datetime.datetime.utcnow()
        )
        db.add(orm)
    db.commit()
    db.close()
    print("✅ 小红书帖子导入完成。")


def import_ctrip_comments(xlsx_path: str):
    df = pd.read_excel(xlsx_path).fillna("")
    db = SessionLocal()
    for _, row in df.iterrows():
        cid = str(uuid.uuid4())
        orm = CommentORM(
            id=cid,
            post_id=row.get("关联PostID", ""),
            user_id=row.get("评论用户ID", ""),
            content=row.get("评论内容", ""),
            created_at=datetime.datetime.utcnow()
        )
        db.add(orm)
    db.commit()
    db.close()
    print("✅ 携程评论导入完成。")


if __name__ == "__main__":
    base = os.path.abspath(os.path.join(current_dir, "..", "data"))
    import_attractions(os.path.join(base, "beijing.csv"))
    import_xhs_posts(os.path.join(base, "xiaohongshu_posts.xlsx"))
    import_ctrip_comments(os.path.join(base, "ctrip_comments.xlsx"))
    print("✅ 数据导入完成。")