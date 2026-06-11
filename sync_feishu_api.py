import os
import json
import requests
from datetime import datetime
from app import app, db, Prompt

APP_ID = "cli_aaa32f7e6538dccd"
APP_SECRET = "GrzG1ipFXaBlKxZ3qP06UfVjgZiL3vAW"

WIKI_TOKEN = "S3MewfMp8iyuRYkLqmKclItOnwg"
SPACE_ID = "7618057410762198211"

SAVE_DIR = "static/videos"
os.makedirs(SAVE_DIR, exist_ok=True)

# =========================
# safe request
# =========================
def safe_json(r, name="api"):
    try:
        return r.json()
    except Exception:
        print(f"\n❌ {name} 非JSON")
        print("STATUS:", r.status_code)
        print("TEXT:", r.text[:300])
        return None

# =========================
# 1. token
# =========================
def get_token():
    r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}
    )
    data = safe_json(r, "token")
    if not data or data.get("code") != 0:
        raise Exception(f"token失败: {data}")
    return data["tenant_access_token"]

token = get_token()
headers = {"Authorization": f"Bearer {token}"}
print("✅ token ok")

# =========================
# 2. 获取 wiki tree
# =========================
tree_url = f"https://open.feishu.cn/open-apis/wiki/v2/tree/get_node/?wiki_token={WIKI_TOKEN}"

r = requests.get(tree_url, headers=headers)
tree = safe_json(r, "wiki tree")

if not tree or "data" not in tree:
    raise Exception("wiki tree失败")

nodes = tree["data"].get("nodes", [])
if not nodes:
    raise Exception("没有nodes")

node_id = nodes[0]["node_id"]
print("📌 node_id:", node_id)

# =========================
# 3. 获取 content（关键API）
# =========================
content_url = f"https://open.feishu.cn/open-apis/wiki/v2/nodes/{node_id}/content"

r = requests.get(content_url, headers=headers)

# ⚠️ content 可能不是json
content = r.text

if "<html" in content.lower():
    print("❌ 返回HTML（权限或API错误）")
    print(content[:300])
    exit()

print("✅ content 获取成功")

# =========================
# 4. 解析提示词
# =========================
lines = [l.strip() for l in content.split("\n") if l.strip()]
prompts = []

cur = None

for line in lines:
    if line.startswith("#"):
        if cur:
            prompts.append(cur)
        cur = {"title": line[1:].strip(), "content": "", "video_file": ""}
    else:
        if not cur:
            cur = {"title": "未命名", "content": "", "video_file": ""}

        if "http" in line and ("mp4" in line or "video" in line):
            cur["video_file"] = line
        else:
            cur["content"] += line + "\n"

if cur:
    prompts.append(cur)

print(f"✅ prompts: {len(prompts)}")

# =========================
# 5. 保存
# =========================
with open("prompts.json", "w", encoding="utf-8") as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)

# =========================
# 6. 下载视频
# =========================
for p in prompts:
    url = p.get("video_file")
    if not url or "http" not in url:
        continue
    try:
        name = os.path.join(SAVE_DIR, url.split("/")[-1])
        r = requests.get(url, stream=True)
        with open(name, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print("⬇️ video:", name)
    except Exception as e:
        print("⚠️ video fail:", e)

# =========================
# 7. 入库
# =========================
with app.app_context():
    count = 0

    for p in prompts:
        if not p["title"] or not p["content"]:
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

print(f"🎉 完成入库 {count} 条")
