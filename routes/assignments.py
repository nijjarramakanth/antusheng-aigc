from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Assignment, User
from datetime import datetime
from . import assignment_bp

@assignment_bp.route('/', methods=['GET'])
@jwt_required()
def get_assignments():
    assignments = Assignment.query.all()
    return jsonify([assignment.to_dict() for assignment in assignments]), 200

@assignment_bp.route('/', methods=['POST'])
@jwt_required()
def create_assignment():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'teacher':
        return jsonify({'error': 'Only teachers can create assignments'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('description'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        assignment = Assignment(
            title=data['title'],
            description=data['description'],
            teacher_id=user_id,
            prompt_category=data.get('prompt_category', ''),
            suggested_prompts=data.get('suggested_prompts', []),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            is_published=data.get('is_published', True)
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        return jsonify({
            'message': 'Assignment created successfully',
            'assignment': assignment.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assignment_bp.route('/<int:assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment(assignment_id):
    assignment = Assignment.query.get(assignment_id)
    
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    return jsonify(assignment.to_dict()), 200

@assignment_bp.route('/<int:assignment_id>', methods=['PUT'])
@jwt_required()
def update_assignment(assignment_id):
    user_id = get_jwt_identity()
    assignment = Assignment.query.get(assignment_id)
    
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    if str(assignment.teacher_id) != str(user_id):
        return jsonify({'error': 'Cannot update other teachers assignments'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        assignment.title = data['title']
    if 'description' in data:
        assignment.description = data['description']
    if 'due_date' in data:
        assignment.due_date = datetime.fromisoformat(data['due_date'])
    if 'is_published' in data:
        assignment.is_published = data['is_published']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Assignment updated successfully',
        'assignment': assignment.to_dict()
    }), 200

@assignment_bp.route('/<int:assignment_id>', methods=['DELETE'])
@jwt_required()
def delete_assignment(assignment_id):
    user_id = get_jwt_identity()
    assignment = Assignment.query.get(assignment_id)
    
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    if str(assignment.teacher_id) != str(user_id):
        return jsonify({'error': 'Cannot delete other teachers assignments'}), 403
    
    db.session.delete(assignment)
    db.session.commit()
    
    return jsonify({'message': 'Assignment deleted successfully'}), 200
