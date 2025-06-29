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