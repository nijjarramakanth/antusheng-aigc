import os
import json
import re
import requests
from datetime import datetime
from tqdm import tqdm

# 引入 Flask 数据库对象
from app import db, Prompt

# ======================
# 配置
# ======================
APP_ID = "cli_aaa32f7e6538dccd"
APP_SECRET = "GrzG1ipFXaBlKxZ3qP06UfVjgZiL3vAW"
WIKI_TOKEN = "S3MewfMp8iyuRYkLqmKclItOnwg"

SAVE_DIR = "static/videos"
os.makedirs(SAVE_DIR, exist_ok=True)

# ======================
# 1. 获取 token
# ======================
def get_token():
    r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}
    )
    data = r.json()
    if data.get("code") != 0:
        raise Exception(f"token获取失败: {data}")
    return data["tenant_access_token"]

token = get_token()
headers = {"Authorization": f"Bearer {token}"}
print("✅ token ok")

# ======================
# 2. 拉取文档内容
# ======================
url = f"https://open.feishu.cn/open-apis/doc/v2/{WIKI_TOKEN}/raw_content"
r = requests.get(url, headers=headers)
raw = r.text
if not raw:
    raise Exception("❌ 文档内容为空")

lines = [l.strip() for l in raw.split("\n") if l.strip()]

# ======================
# 3. 解析提示词
# ======================
prompts = []
current = None

def flush():
    global current
    if current and current.get("title") and current.get("content"):
        prompts.append(current)
    current = None

for line in lines:
    # 新标题
    if line.startswith("#"):
        flush()
        current = {"title": line.replace("#", "").strip(), "content": "", "video_file": ""}
        continue

    # 初始化 current
    if current is None:
        current = {"title": "未命名提示词", "content": "", "video_file": ""}

    # 视频识别
    if re.search(r"(http|file|mp4|video|drive)", line):
        current["video_file"] = line
    else:
        current["content"] += line + "\n"

flush()

print(f"✅ 解析完成: {len(prompts)} 条提示词")

# ======================
# 4. 保存 JSON
# ======================
with open("prompts.json", "w", encoding="utf-8") as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)

# ======================
# 5. 下载视频
# ======================
for p in tqdm(prompts):
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
# 6. 导入数据库
# ======================
count = 0
for p in prompts:
    if not p["title"] or not p["content"]:
        continue

    exists = Prompt.query.filter_by(title=p["title"]).first()
    if exists:
        continue

    obj = Prompt(
        title=p["title"],
        content=p["content"],
        video_file=p.get("video_file", ""),
        category="feishu",
        created_by="admin",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(obj)
    count += 1

db.session.commit()
print(f"🎉 完成：新增入库 {count} 条提示词")
