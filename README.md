# Summer-Project

## 快速启动
1. 打开 Codespaces（或本地）
2. 安装依赖：
   ```bash
   pip install --no-cache-dir -r requirements.txt
3. 启动服务：
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
4. 在浏览器访问：
文档： http://localhost:8000/docs
推荐： GET  /attractions?destination=北京&days=2&preferences=文化,美食
详情： GET  /attractions/{id}
行程： POST /itinerary (JSON body)

## 协作开发
1. Fork 或 Clone 仓库
2. 点击 **Code → Open with Codespaces**
3. 等待容器启动并安装依赖
4. 运行 Uvicorn 并联调前端，即可开始协作开发

## 后端接口
| 方法   | 路径                                         | 参数示例／位置                                                                             | 功能说明             | 返回模型                               |                  |
| ---- | ------------------------------------------ | ----------------------------------------------------------------------------------- | ---------------- | ---------------------------------- | ---------------- |
| GET  | `/`                                        | —                                                                                   | 健康检查，返回服务状态      | `{ status, message }`              |                  |
| GET  | `/attractions`                             | `?destination=北京&days=2&preferences=文化&preferences=美食`<br>（Query）                   | 搜索/推荐景点列表        | `List<Attraction>`                 |                  |
| GET  | `/attractions/{id}`                        | `id`（Path）                                                                          | 单个景点详情，含优缺点与来源链接 | `Attraction`                       |                  |
| POST | `/itinerary`                               | `{ selected_ids: ["id1","id2"], days:2, preferences:["文化","美食"] }`<br>（JSON Body）   | 基于选中景点生成行程草稿     | `List<{ day, attraction, notes }>` |                  |
| POST | `/users`                                   | `?username=xxx&nickname=yyy`<br>（Query） 或 Body（可根据前端实际改）                            | 用户注册             | `User`                             |                  |
| GET  | `/users/{user_id}`                         | `user_id`（Path）                                                                     | 获取用户资料           | `User`                             |                  |
| POST | `/posts`                                   | `{ user_id:"uid", content:"文字", images:["url1","url2"] }`<br>（JSON Body）            | 创建一条用户帖子         | `Post`                             |                  |
| GET  | `/posts`                                   | —                                                                                   | 拉取所有用户帖子列表       | `List<Post>`                       |                  |
| POST | `/posts/{post_id}/comments`                | `{ user_id:"uid", content:"评论内容" }`<br>（JSON Body），`post_id`（Path）                  | 在某贴下添加评论         | `Comment`                          |                  |
| GET  | `/posts/{post_id}/comments`                | `post_id`（Path）                                                                     | 获取某贴的所有评论        | `List<Comment>`                    |                  |
| POST | `/posts/{post_id}/like`                    | `?user_id=uid`<br>（Query） 或 JSON Body                                               | 对帖子点赞／取消点赞       | \`{ result: "added"                | "deleted" }\`    |
| GET  | `/posts/{post_id}/likes`                   | `post_id`（Path）                                                                     | 查询某贴的点赞总数        | `{ count: number }`                |                  |
| POST | `/users/{user_id}/follow/{target_user_id}` | `user_id`、`target_user_id`（Path）                                                    | 关注／取关某用户         | \`{ result: "followed"             | "unfollowed" }\` |
| POST | `/users/{user_id}/itineraries`             | `{ selected_ids: [...], days:2, preferences:[...] }`<br>（JSON Body），`user_id`（Path） | 保存当前行程到“我的行程”    | `ItineraryRecord`                  |                  |
| GET  | `/users/{user_id}/itineraries`             | `user_id`（Path）                                                                     | 拉取某用户所有保存的行程     | `List<ItineraryRecord>`            |                  |

---

**字段说明：**

* **Attraction**：`{ id, name, description, lat, lon, tags[], images[], address, pros[], cons[], source_posts[] }`
* **User**：`{ id, username, nickname, avatar?, bio }`
* **Post**：`{ id, user_id, content, images[], created_at }`
* **Comment**：`{ id, post_id, user_id, content, created_at }`
* **ItineraryRecord**：`{ id, user_id, title?, selected_ids[], days, preferences[], itinerary[], created_at }`

* 搜索页/推荐页：`GET /attractions`
* 详情页：`GET /attractions/{id}`
* 滑卡推荐：`POST /itinerary`
* 用户社交：`/users`、`/posts`、`/comments`、`/like`、`/follow`
* 我的行程：`/users/{user_id}/itineraries`

确保在小程序或网页端，按上表填写正确的 Path、Query 或 JSON Body，就能获得相应的 JSON 数据并渲染 UI。

