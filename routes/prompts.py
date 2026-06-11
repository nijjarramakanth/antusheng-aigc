from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Prompt
from . import prompt_bp

def prompt_to_dict(p):
    return {
        'id': p.id,
        'title': p.title,
        'content': p.content,
        'category': p.category,
        'difficulty': p.difficulty,
        'video_file': p.video_file or '',
        'video_url': f'/api/upload/files/{p.video_file}' if p.video_file else '',
        'ai_platform': p.ai_platform,
        'tags': p.tags or [],
        'views': p.views,
        'rating': p.rating
    }

@prompt_bp.route('/', methods=['GET'])
def get_prompts():
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    search = request.args.get('search')
    
    query = Prompt.query
    if category:
        query = query.filter_by(category=category)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if search:
        query = query.filter(
            Prompt.title.contains(search) | Prompt.content.contains(search)
        )
    
    prompts = query.all()
    return jsonify({
        'total': len(prompts),
        'prompts': [prompt_to_dict(p) for p in prompts]
    }), 200

@prompt_bp.route('/<int:prompt_id>', methods=['GET'])
def get_prompt(prompt_id):
    p = Prompt.query.get(prompt_id)
    if not p:
        return jsonify({'error': 'Prompt not found'}), 404
    p.views += 1
    db.session.commit()
    return jsonify(prompt_to_dict(p)), 200

@prompt_bp.route('/categories', methods=['GET'])
def get_prompt_categories():
    cats = db.session.query(Prompt.category).distinct().all()
    return jsonify({'categories': [c[0] for c in cats]}), 200

@prompt_bp.route('/stats', methods=['GET'])
def get_prompt_stats():
    total = Prompt.query.count()
    return jsonify({'total_prompts': total}), 200

@prompt_bp.route('/<int:prompt_id>/video', methods=['PUT'])
@jwt_required()
def update_prompt_video(prompt_id):
    p = Prompt.query.get(prompt_id)
    if not p:
        return jsonify({'error': 'Prompt not found'}), 404
    data = request.get_json()
    p.video_file = data.get('video_file', '')
    db.session.commit()
    return jsonify({'message': 'Updated', 'video_file': p.video_file}), 200

