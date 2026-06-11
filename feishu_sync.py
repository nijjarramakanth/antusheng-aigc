import os
import json
import requests
from tqdm import tqdm

APP_ID = "cli_aaa32f7e6538dccd"
APP_SECRET = "GrzG1ipFXaBlKxZ3qP06UfVjgZiL3vAW"

WIKI_TOKEN = "S3MewfMp8iyuRYkLqmKclItOnwg"
SPACE_ID = "7618057410762198211"

SAVE_DIR = "static/videos"
os.makedirs(SAVE_DIR, exist_ok=True)

# ======================
# 1. token
# ======================
resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}
)

data = resp.json()
if data.get("code") != 0:
    raise Exception(data)

token = data["tenant_access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("✅ token ok")

# ======================
# 2. 正确获取 wiki nodes（替代 tree）
# ======================
url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/{SPACE_ID}/nodes"

r = requests.get(url, headers=headers, params={
    "wiki_token": WIKI_TOKEN
})

text = r.text
text = text.lstrip(")]}',\n")

try:
    data = json.loads(text)
except Exception:
    raise Exception("❌ API返回不是JSON:\n" + text[:300])

if data.get("code") != 0:
    raise Exception(data)

nodes = data["data"]["items"]

print(f"✅ nodes数量: {len(nodes)}")

# ======================
# 3. 解析
# ======================
prompts = []

for i, node in enumerate(nodes):
    title = node.get("title", f"p_{i}")
    obj_token = node.get("obj_token")

    if not obj_token:
        continue

    content_url = f"https://open.feishu.cn/open-apis/doc/v2/{obj_token}/raw_content"
    r = requests.get(content_url, headers=headers)

    content = r.text
    lines = [x.strip() for x in content.split("\n") if x.strip()]

    if not lines:
        continue

    prompts.append({
        "title": title,
        "content": lines[0],
        "video_file": lines[-1] if len(lines) > 1 else ""
    })

# ======================
# 4. 保存
# ======================
with open("prompts.json", "w", encoding="utf-8") as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)

print("✅ prompts.json 完成:", len(prompts))

# ======================
# 5. 下载视频
# ======================
for p in tqdm(prompts):
    file_token = p["video_file"]

    if not file_token or "." in file_token:
        continue

    url = f"https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/download"

    r = requests.get(url, headers=headers, stream=True)

    path = os.path.join(SAVE_DIR, f"{file_token}.mp4")

    with open(path, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

print("🎉 完成")
