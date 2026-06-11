"""
提示词批量导入脚本
使用方法：python import_prompts.py
"""
import json
import os
import sys

# 确保在项目目录下运行
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Prompt

def import_prompts():
    app = create_app()
    
    with app.app_context():
        # 读取提示词数据
        json_path = os.path.join(os.path.dirname(__file__), 'prompts.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            prompts_data = json.load(f)
        
        print(f"准备导入 {len(prompts_data)} 条提示词...")
        
        success = 0
        skip = 0
        
        for item in prompts_data:
            # 检查是否已存在
            existing = Prompt.query.filter_by(title=item['title']).first()
            if existing:
                skip += 1
                continue
            
            prompt = Prompt(
                title=item['title'],
                content=item['content'],
                category=item.get('category', 'video_generation'),
                video_file=item.get('video_file', ''),
                difficulty='intermediate',
                is_public=True
            )
            db.session.add(prompt)
            success += 1
        
        db.session.commit()
        print(f"✅ 导入完成：成功 {success} 条，跳过重复 {skip} 条")

if __name__ == '__main__':
    import_prompts()
