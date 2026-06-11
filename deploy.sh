#!/bin/bash

echo "🚀 开始一键初始化 + 导入流程..."

cd "$(dirname "$0")"

DB="aigc_education.db"

# =========================
# 1️⃣ 初始化数据库表
# =========================
echo "📦 初始化数据库表..."

python3 - <<'EOF'
from app import create_app
from models import db

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ 数据库表已创建/确认存在")
EOF

# =========================
# 2️⃣ 添加 video_file 字段（如果没有）
# =========================
echo "📌 检查 video_file 字段..."

python3 - <<'EOF'
import sqlite3

conn = sqlite3.connect("aigc_education.db")
c = conn.cursor()

c.execute("PRAGMA table_info(prompts)")
cols = [i[1] for i in c.fetchall()]

if "video_file" not in cols:
    print("⚡ 添加 video_file 字段")
    c.execute("ALTER TABLE prompts ADD COLUMN video_file TEXT DEFAULT ''")
    conn.commit()
else:
    print("✅ video_file 已存在")

conn.close()
EOF

# =========================
# 3️⃣ 导入 / 更新数据
# =========================
echo "📥 导入 prompts.json ..."

python3 - <<'EOF'
import json
from app import create_app
from models import db, Prompt

app = create_app()

with app.app_context():

    with open("prompts.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    added = 0
    updated = 0

    for item in data:
        title = item.get("title","")

        obj = Prompt.query.filter_by(title=title).first()

        if obj:
            obj.content = item.get("content","")
            obj.category = item.get("category","通用")
            obj.difficulty = item.get("difficulty","beginner")
            obj.example_output = item.get("example_output","")
            obj.use_case = item.get("use_case","")
            obj.tags = item.get("tags",[])
            obj.ai_platform = item.get("ai_platform","gemini")
            obj.created_by = item.get("created_by","admin")

            if hasattr(obj, "video_file"):
                obj.video_file = item.get("video_file","")

            updated += 1

        else:
            obj = Prompt(
                title=title,
                content=item.get("content",""),
                category=item.get("category","通用"),
                difficulty=item.get("difficulty","beginner"),
                example_output=item.get("example_output",""),
                use_case=item.get("use_case",""),
                tags=item.get("tags",[]),
                ai_platform=item.get("ai_platform","gemini"),
                created_by=item.get("created_by","admin")
            )

            if hasattr(obj, "video_file"):
                obj.video_file = item.get("video_file","")

            db.session.add(obj)
            added += 1

    db.session.commit()

    print(f"✅ 完成：新增 {added} 条 / 更新 {updated} 条")
EOF

echo "🎉 全部完成！系统已就绪"
