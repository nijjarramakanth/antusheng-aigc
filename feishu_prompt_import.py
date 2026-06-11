import os
import json
import requests
from tqdm import tqdm

# ======================
# 🔑 飞书 App 信息
# ======================
APP_ID = "cli_aaa32f7e6538dccd"
APP_SECRET = "GrzG1ipFXaBlKxZ3qP06UfVjgZiL3vAW"

# 你的文档 URL
DOC_URL = "https://xiaolaimedia.feishu.cn/wiki/S3MewfMp8iyuRYkLqmKclItOnwg"

SAVE_DIR = "static/videos"
os.makedirs(SAVE_DIR, exist_ok=True)

# ======================
# 1️⃣ 获取 tenant_access_token
# ======================
token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
resp = requests.post(token_url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
data = resp.json()

if data.get("code") != 0:
    raise Exception(f"❌ token 获取失败：{data}")

token = data["tenant_access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ token 获取成功")

# ======================
# 2️⃣ 获取文档 ID
# ======================
doc_token = DOC_URL.rstrip("/").split("/")[-1]

# ======================
# 3️⃣ 获取文档内容
# ======================
url = f"https://open.feishu.cn/open-apis/wiki/v2/nodes/{doc_token}/content"
r = requests.get(url, headers=headers)
doc_data = r.json()

if doc_data.get("code") != 0:
    raise Exception(f"❌ 文档读取失败：{doc_data}")

content = doc_data.get("data", {}).get("content", "")

# ======================
# 4️⃣ 解析提示词（标题→内容→视频）
# ======================
lines = [l.strip() for l in content.split("\n") if l.strip()]
prompts = []
i = 0
while i < len(lines):
    title = lines[i]
    content_text = lines[i+1] if i+1 < len(lines) else ""
    video_file = lines[i+2] if i+2 < len(lines) else ""
    prompts.append({"title": title, "content": content_text, "video_file": video_file})
    i += 3

print(f"✅ 解析到 {len(prompts)} 条提示词")

# ======================
# 5️⃣ 保存 JSON
# ======================
with open("prompts.json", "w", encoding="utf-8") as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)

print("✅ prompts.json 已生成")

# ======================
# 6️⃣ 下载视频（如果 video_file 是文件 token）
# ======================
for p in tqdm(prompts):
    file_token = p.get("video_file")
    if not file_token or "." in file_token:
        continue
    download_url = f"https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/download"
    r = requests.get(download_url, headers=headers, stream=True)
    path = os.path.join(SAVE_DIR, f"{file_token}.mp4")
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)

print("🎉 全部完成：JSON + 视频下载完成")
