from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
from . import user_bp

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_users():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if current_user.role != 'teacher':
        return jsonify({'error': 'Only teachers can view all users'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    
    if current_user_id != user_id:
        return jsonify({'error': 'Cannot update other users'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'avatar' in data:
        user.avatar = data['avatar']
    if 'bio' in data:
        user.bio = data['bio']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200
