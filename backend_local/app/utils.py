from typing import List
import math

def safe_str(value):
    """
    将输入值安全转换为字串，处理 None 或 NaN 等非法情况。

    参数:
        value: 任意值，可能是 None、NaN 或其他类型。

    返回:
        str: 若为 NaN 或 None，回传空字串 ""；否则回传其字串形式。
    """
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return str(value)


# 示例：把行程草稿转换成 GeoJSON
def to_geojson(items: List[dict]) -> dict:
    features = []
    for itm in items:
        co = itm["attraction"]
        features.append({
            "type": "Feature",
            "properties": {"day": itm["day"], "name": co["name"]},
            "geometry": {"type": "Point", "coordinates": [co["lon"], co["lat"]]}
        })
    return {"type": "FeatureCollection", "features": features}