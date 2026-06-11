
# ===== Prompt Library =====
from flask import render_template, jsonify
from models import Prompt

@app.route('/library')
def library():
    return render_template('prompt_library.html')

@app.route('/api/prompts')
def api_prompts():
    prompts = Prompt.query.order_by(Prompt.id.desc()).all()
    return jsonify([
        {
            "id":p.id,
            "title":p.title,
            "content":p.content,
            "category":p.category,
            "video_file":p.video_file,
            "tags":p.tags or []
        } for p in prompts
    ])
