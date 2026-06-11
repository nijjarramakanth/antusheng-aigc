
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aigc_education.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ======================
# 数据库模型
# ======================
class Prompt(db.Model):
    __tablename__ = 'prompts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    video_file = db.Column(db.String(200), default='')
    tags = db.Column(db.JSON, default=[])

# ======================
# 路由
# ======================
@app.route('/library')
def library():
    return render_template('prompt_library.html')

@app.route('/api/prompts')
def api_prompts():
    prompts = Prompt.query.order_by(Prompt.id.desc()).all()
    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "category": p.category,
            "video_file": p.video_file,
            "tags": p.tags or []
        } for p in prompts
    ])

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/videos', exist_ok=True)
    db.create_all()
    app.run(debug=True)
