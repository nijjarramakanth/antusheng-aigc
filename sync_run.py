import os
import json
import requests

APP_ID = "cli_aaa32f7e6538dccd"
APP_SECRET = "GrzG1ipFXaBlKxZ3qP06UfVjgZiL3vAW"
WIKI_TOKEN = "S3MewfMp8iyuRYkLqmKclItOnwg"

def safe_json(r, name="api"):
    try:
        return r.json()
    except Exception:
        print(f"\n❌ {name} 返回不是JSON")
        print("STATUS:", r.status_code)
        print("TEXT:\n", r.text[:500])
        return None

# 1️⃣ token
r = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}
)

data = safe_json(r, "token")

if not data or data.get("code") != 0:
    print("❌ token失败：", data)
    exit()

token = data["tenant_access_token"]
print("✅ token ok")

headers = {"Authorization": f"Bearer {token}"}

# 2️⃣ wiki tree（安全版）
url = f"https://open.feishu.cn/open-apis/wiki/v2/tree/get_node/?wiki_token={WIKI_TOKEN}"
r = requests.get(url, headers=headers)

tree = safe_json(r, "wiki tree")
if not tree:
    exit()

if "data" not in tree:
    print("❌ wiki返回异常：", tree)
    exit()

nodes = tree["data"].get("nodes", [])
if not nodes:
    print("❌ 没有nodes，检查wiki权限或token")
    exit()

node_id = nodes[0].get("node_id")
print("📌 node_id:", node_id)

# 3️⃣ content
url = f"https://open.feishu.cn/open-apis/wiki/v2/nodes/{node_id}/content"
r = requests.get(url, headers=headers)

content = r.text

if "<html" in content.lower():
    print("❌ 返回HTML（权限/路径错误）")
    print(content[:300])
    exit()

print("✅ content 获取成功")
print("\n===== 内容预览 =====\n")
print(content[:500])

print("\n🎉 完成（已成功连通飞书API）")

