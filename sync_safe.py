import os
import json
import re
import requests
from datetime import datetime
from tqdm import tqdm

# 导入你项目里的 Flask 对象
from app import app, db, Prompt

# ======================
# 配置
# ======================
APP_ID = "cli_aaa32f7e6538dccd"
APP_SECRET = "GrzG1ipFXaBlKxZ3qP06UfVjgZiL3vAW"
WIKI_TOKEN = "S3MewfMp8iyuRYkLqmKclItOnwg"

SAVE_DIR = "static/videos"
os.makedirs(SAVE_DIR, exist_ok=True)

# ======================
# 获取 tenant token
# ======================
def get_token():
    r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}
    )
    data = r.json()
    if data.get("code") != 0:
        raise Exception(f"获取 token 失败: {data}")
    return data["tenant_access_token"]

token = get_token()
headers = {"Authorization": f"Bearer {token}"}
print("✅ token ok")

# ======================
# 拉取 wiki 内容
# ======================
tree_url = f"https://open.feishu.cn/open-apis/wiki/v2/tree/get_node/?wiki_token={WIKI_TOKEN}&space_id=7618057410762198211&expand_shortcut=true&with_deleted=true"
r = requests.get(tree_url, headers=headers)
data = r.json()

if "data" not in data:
    raise Exception(f"获取 wiki 树失败: {data}")

# 假设第一层 node_id 就是我们需要的
node_id = data["data"]["nodes"][0]["node_id"]
content_url = f"https://open.feishu.cn/open-apis/wiki/v2/nodes/{node_id}/content"
r = requests.get(content_url, headers=headers)
content = r.text

# ======================
# 解析提示词
# ======================
lines = [l.strip() for l in content.split("\n") if l.strip()]
prompts = []
current = None

def flush():
    global current
    if current and current.get("title"):
        prompts.append(current)
    current = None

for line in lines:
    if line.startswith("#"):
        flush()
        current = {"title": line.replace("#", "").strip(), "content": "", "video_file": ""}
    else:
        if not current:
            current = {"title": "未命名", "content": "", "video_file": ""}
        if re.search(r"(http|mp4|video|drive|file)", line):
            current["video_file"] = line
        else:
            current["content"] += line + "\n"

flush()
print(f"✅ 解析完成 {len(prompts)} 条提示词")

# ======================
# 保存 JSON
# ======================
with open("prompts.json", "w", encoding="utf-8") as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)

# ======================
# 下载视频
# ======================
for p in tqdm(prompts, desc="下载视频"):
    file_token = p.get("video_file", "")
    if not file_token or "http" in file_token:
        continue
    try:
        url = f"https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/download"
        r = requests.get(url, headers=headers, stream=True)
        path = os.path.join(SAVE_DIR, f"{file_token}.mp4")
        with open(path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    except:
        continue

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
