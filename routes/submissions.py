from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Submission, Assignment, User
from datetime import datetime
from . import submission_bp

@submission_bp.route('/', methods=['GET'])
@jwt_required()
def get_submissions():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role == 'student':
        submissions = Submission.query.filter_by(student_id=user_id).all()
    else:
        submissions = Submission.query.join(Assignment).filter(
            Assignment.teacher_id == user_id
        ).all()
    
    return jsonify([submission.to_dict() for submission in submissions]), 200

@submission_bp.route('/', methods=['POST'])
@jwt_required()
def create_submission():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'student':
        return jsonify({'error': 'Only students can submit assignments'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('assignment_id') or not data.get('content'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    assignment = Assignment.query.get(data['assignment_id'])
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    existing = Submission.query.filter_by(
        assignment_id=data['assignment_id'],
        student_id=user_id
    ).first()
    
    if existing:
        return jsonify({'error': 'You have already submitted this assignment'}), 409
    
    try:
        submission = Submission(
            assignment_id=data['assignment_id'],
            student_id=user_id,
            content=data['content'],
            prompt_used=data.get('prompt_used', ''),
            file_url=data.get('file_url', ''),
            status='submitted'
        )
        
        db.session.add(submission)
        db.session.commit()
        
        return jsonify({
            'message': 'Submission created successfully',
            'submission': submission.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@submission_bp.route('/<int:submission_id>', methods=['GET'])
@jwt_required()
def get_submission(submission_id):
    user_id = get_jwt_identity()
    submission = Submission.query.get(submission_id)
    
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404
    
    user = User.query.get(user_id)
    if user.role == 'student' and submission.student_id != user_id:
        return jsonify({'error': 'Cannot view other students submissions'}), 403
    
    if user.role == 'teacher':
        assignment = Assignment.query.get(submission.assignment_id)
        if assignment.teacher_id != user_id:
            return jsonify({'error': 'Cannot view submissions for other teachers assignments'}), 403
    
    return jsonify(submission.to_dict()), 200

@submission_bp.route('/<int:submission_id>', methods=['PUT'])
@jwt_required()
def update_submission(submission_id):
    user_id = get_jwt_identity()
    submission = Submission.query.get(submission_id)
    
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404
    
    if submission.student_id != user_id:
        return jsonify({'error': 'Cannot update other students submissions'}), 403
    
    if submission.status in ['reviewed', 'graded']:
        return jsonify({'error': 'Cannot update graded submissions'}), 403
    
    data = request.get_json()
    
    if 'content' in data:
        submission.content = data['content']
    if 'prompt_used' in data:
        submission.prompt_used = data['prompt_used']
    
    submission.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Submission updated successfully',
        'submission': submission.to_dict()
    }), 200

@submission_bp.route('/assignment/<int:assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment_submissions(assignment_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'teacher':
        return jsonify({'error': 'Only teachers can view all submissions'}), 403
    
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    if assignment.teacher_id != user_id:
        return jsonify({'error': 'Cannot view submissions for other teachers assignments'}), 403
    
    submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
    
    return jsonify({
        'assignment': assignment.to_dict(),
        'submissions': [submission.to_dict() for submission in submissions],
        'total': len(submissions),
        'reviewed': sum(1 for s in submissions if s.status != 'submitted')
    }), 200
