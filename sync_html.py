import os
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from app import app, db, Prompt

# ======================
# 配置
# ======================
PUBLIC_URL = "https://xiaolaimedia.feishu.cn/wiki/S3MewfMp8iyuRYkLqmKclItOnwg"  # 你的公开分享链接
SAVE_DIR = "static/videos"
os.makedirs(SAVE_DIR, exist_ok=True)

# ======================
# 拉取 HTML
# ======================
r = requests.get(PUBLIC_URL)
if r.status_code != 200:
    raise Exception(f"无法访问文档，状态码: {r.status_code}")

soup = BeautifulSoup(r.text, "html.parser")

# ======================
# 解析提示词 + 视频
# ======================
prompts = []

for block in soup.find_all(["p", "div"]):
    text = block.get_text(strip=True)
    if not text:
        continue
    # 假设每条提示词标题是 # 开头
    if text.startswith("#"):
        prompts.append({"title": text[1:].strip(), "content": "", "video_file": ""})
        current = prompts[-1]
    else:
        # 简单判断是不是视频链接
        if re.search(r"(http.*(mp4|video|drive|file))", text):
            if prompts:
                prompts[-1]["video_file"] = text
        else:
            if prompts:
                prompts[-1]["content"] += text + "\n"

print(f"✅ 解析完成 {len(prompts)} 条提示词")

# ======================
# 保存 JSON
# ======================
with open("prompts.json", "w", encoding="utf-8") as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)

# ======================
# 下载视频
# ======================
for p in prompts:
    video_url = p.get("video_file")
    if not video_url:
        continue
    try:
        local_name = os.path.join(SAVE_DIR, os.path.basename(video_url))
        r = requests.get(video_url, stream=True)
        with open(local_name, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print(f"✅ 下载视频: {local_name}")
    except Exception as e:
        print(f"⚠️ 下载失败 {video_url}: {e}")

# ======================
# 导入数据库
# ======================
with app.app_context():
    count = 0
    for p in prompts:
        if not p.get("title") or not p.get("content"):
            continue
        if Prompt.query.filter_by(title=p["title"]).first():
            continue
        db.session.add(Prompt(
            title=p["title"],
            content=p["content"],
            video_file=p.get("video_file", ""),
            category="feishu",
            created_by="admin",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ))
        count += 1
    db.session.commit()

print(f"🎉 完成入库 {count} 条提示词")
