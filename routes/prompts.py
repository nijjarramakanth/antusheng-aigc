from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Prompt, User
from prompts_library import (
    get_all_prompts, 
    get_prompts_by_category, 
    get_prompts_by_difficulty,
    search_prompts,
    get_categories,
    get_tags
)
from . import prompt_bp

@prompt_bp.route('/', methods=['GET'])
def get_prompts():
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    search = request.args.get('search')
    
    if search:
        prompts = search_prompts(search)
    elif category:
        prompts = get_prompts_by_category(category)
    elif difficulty:
        prompts = get_prompts_by_difficulty(difficulty)
    else:
        prompts = get_all_prompts()
    
    return jsonify({
        'total': len(prompts),
        'prompts': prompts
    }), 200

@prompt_bp.route('/categories', methods=['GET'])
def get_prompt_categories():
    return jsonify({
        'categories': get_categories()
    }), 200

@prompt_bp.route('/tags', methods=['GET'])
def get_prompt_tags():
    return jsonify({
        'tags': get_tags()
    }), 200

@prompt_bp.route('/<int:prompt_id>', methods=['GET'])
def get_prompt(prompt_id):
    prompts = get_all_prompts()
    
    if 0 <= prompt_id < len(prompts):
        return jsonify(prompts[prompt_id]), 200
    
    return jsonify({'error': 'Prompt not found'}), 404

@prompt_bp.route('/category/<category>', methods=['GET'])
def get_category_prompts(category):
    prompts = get_prompts_by_category(category)
    
    return jsonify({
        'category': category,
        'total': len(prompts),
        'prompts': prompts
    }), 200

@prompt_bp.route('/difficulty/<difficulty>', methods=['GET'])
def get_difficulty_prompts(difficulty):
    prompts = get_prompts_by_difficulty(difficulty)
    
    return jsonify({
        'difficulty': difficulty,
        'total': len(prompts),
        'prompts': prompts
    }), 200

@prompt_bp.route('/search', methods=['GET'])
def search_prompt_library():
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Missing search query'}), 400
    
    prompts = search_prompts(query)
    
    return jsonify({
        'query': query,
        'total': len(prompts),
        'prompts': prompts
    }), 200

@prompt_bp.route('/stats', methods=['GET'])
def get_prompt_stats():
    all_prompts = get_all_prompts()
    
    stats = {
        'total_prompts': len(all_prompts),
        'categories': get_categories(),
        'by_category': {
            cat: len(get_prompts_by_category(cat)) 
            for cat in get_categories()
        },
        'by_difficulty': {
            diff: len(get_prompts_by_difficulty(diff))
            for diff in ['beginner', 'intermediate', 'advanced']
        }
    }
    
    return jsonify(stats), 200
