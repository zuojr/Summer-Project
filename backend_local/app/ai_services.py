from typing import List, Dict
import requests
import json
from .models import Attraction, Post

# AI 优缺点归纳
def summarize_pros_cons(attraction: Attraction, posts: List[Post]) -> Attraction:
    # 取正向评论前3条当 pros，负向前3条当 cons
    pros = [p.content[:50]+"…" for p in sorted(posts, key=lambda x: -x.sentiment)[:3]]
    cons = [p.content[:50]+"…" for p in sorted(posts, key=lambda x: x.sentiment)[:3]]
    attraction.pros = pros
    attraction.cons = cons
    attraction.source_posts = [p.url for p in posts if p.url][:5]
    return attraction

# AI 行程生成（已移除重复定义）

import requests
import json
from typing import List, Dict
from app.config import BAIDU_API_URL, BAIDU_APP_ID, BAIDU_AUTH_TOKEN  # 导入配置

class BaiduAIService:
    def __init__(self):
        self.url = BAIDU_API_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": BAIDU_AUTH_TOKEN
        }
        self.app_id = BAIDU_APP_ID

    def generate_itinerary(
        self, 
        city: str, 
        selected_attractions: List[str], 
        excluded_attractions: List[str], 
        days: int, 
        prefs: List[str]
    ) -> Dict:
        """
        调用百度AI生成行程
        :return: 结构化的行程数据
        """
        prompt = self._build_prompt(city, selected_attractions, excluded_attractions, days, prefs)
        payload = self._build_payload(prompt)
        
        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8")
            )
            response.raise_for_status()
            return self._parse_response(response.json())
            
        except requests.RequestException as e:
            return {"error": f"API请求失败: {str(e)}", "status": "api_error"}
        except Exception as e:
            return {"error": f"处理响应失败: {str(e)}", "status": "processing_error"}

    def _build_prompt(self, city, selected, excluded, days, prefs) -> str:
        """构建提示词"""
        return f"""
        我计划去{city}旅行{days}天，请帮我生成详细的行程规划。
        必去景点：{", ".join(selected)}
        不去的景点：{", ".join(excluded) or '无'}
        我的偏好：{", ".join(prefs) or '无特殊偏好'}
        
        请按以下格式返回：
        [
            {{
                "day": 1,
                "time_slot": "上午",
                "attraction": "故宫博物院",
                "duration": 3,
                "description": "参观故宫三大殿...",
                "transport": "地铁1号线天安门东站",
                "notes": "建议提前预约门票"
            }},
            ...
        ]
        """

    def _build_payload(self, prompt) -> Dict:
        """构建请求体"""
        return {
            "app_id": self.app_id,
            "query": prompt,
            "temperature": 0.7,
            "max_tokens": 2000
        }

    def _parse_response(self, response) -> Dict:
        """解析AI返回的行程数据"""
        try:
            # 假设AI返回的是结构化数据
            itinerary_items = json.loads(response.get("result", "[]"))
            
            # 提取每日行程摘要
            daily_summary = {}
            for item in itinerary_items:
                day = item.get("day")
                if day not in daily_summary:
                    daily_summary[day] = []
                daily_summary[day].append(f"{item.get('time_slot')}: {item.get('attraction')}")
            
            return {
                "items": itinerary_items,
                "summary": daily_summary,
                "status": "success"
            }
        except json.JSONDecodeError:
            # 如果AI返回的不是JSON格式，进行简单解析
            return {
                "raw_response": response.get("result", ""),
                "status": "parsing_failed",
                "error": "无法解析AI返回的行程数据，请检查提示词格式"
            }
        except Exception as e:
            return {
                "raw_response": response.get("result", ""),
                "status": "unknown_error",
                "error": f"解析行程数据时发生未知错误: {str(e)}"
            }
