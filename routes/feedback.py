from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Feedback, Submission, Assignment, User
from datetime import datetime
from . import feedback_bp

@feedback_bp.route('/', methods=['POST'])
@jwt_required()
def create_feedback():
    """Create feedback on submission (teacher only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'teacher':
        return jsonify({'error': 'Only teachers can create feedback'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('submission_id'):
        return jsonify({'error': 'Missing submission_id'}), 400
    
    # Get submission
    submission = Submission.query.get(data['submission_id'])
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404
    
    # Verify teacher owns the assignment
    assignment = Assignment.query.get(submission.assignment_id)
    if assignment.teacher_id != user_id:
        return jsonify({'error': 'Cannot grade submissions for other teachers assignments'}), 403
    
    # Check if feedback already exists
    existing_feedback = Feedback.query.filter_by(submission_id=data['submission_id']).first()
    if existing_feedback:
        return jsonify({'error': 'Feedback already exists for this submission'}), 409
    
    try:
        feedback = Feedback(
            submission_id=data['submission_id'],
            teacher_id=user_id,
            score=data.get('score', 0),
            comments=data.get('comments', ''),
            ai_suggestions=data.get('ai_suggestions', '')
        )
        
        # Update submission status
        submission.status = 'graded'
        submission.updated_at = datetime.utcnow()
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'message': 'Feedback created successfully',
            'feedback': feedback.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/<int:feedback_id>', methods=['GET'])
@jwt_required()
def get_feedback(feedback_id):
    """Get specific feedback"""
    user_id = get_jwt_identity()
    feedback = Feedback.query.get(feedback_id)
    
    if not feedback:
        return jsonify({'error': 'Feedback not found'}), 404
    
    # Check permissions
    user = User.query.get(user_id)
    if user.role == 'student' and feedback.submission.student_id != user_id:
        return jsonify({'error': 'Cannot view other students feedback'}), 403
    
    if user.role == 'teacher' and feedback.teacher_id != user_id:
        return jsonify({'error': 'Cannot view other teachers feedback'}), 403
    
    return jsonify(feedback.to_dict()), 200

@feedback_bp.route('/<int:feedback_id>', methods=['PUT'])
@jwt_required()
def update_feedback(feedback_id):
    """Update feedback (teacher only)"""
    user_id = get_jwt_identity()
    feedback = Feedback.query.get(feedback_id)
    
    if not feedback:
        return jsonify({'error': 'Feedback not found'}), 404
    
    if feedback.teacher_id != user_id:
        return jsonify({'error': 'Cannot update other teachers feedback'}), 403
    
    data = request.get_json()
    
    if 'score' in data:
        feedback.score = data['score']
    if 'comments' in data:
        feedback.comments = data['comments']
    if 'ai_suggestions' in data:
        feedback.ai_suggestions = data['ai_suggestions']
    
    feedback.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Feedback updated successfully',
        'feedback': feedback.to_dict()
    }), 200

@feedback_bp.route('/submission/<int:submission_id>', methods=['GET'])
@jwt_required()
def get_submission_feedback(submission_id):
    """Get feedback for specific submission"""
    feedback = Feedback.query.filter_by(submission_id=submission_id).first()
    
    if not feedback:
        return jsonify({'error': 'No feedback found for this submission'}), 404
    
    return jsonify(feedback.to_dict()), 200

@feedback_bp.route('/stats/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_feedback_stats(teacher_id):
    """Get feedback statistics for a teacher"""
    # Get all assignments from this teacher
    assignments = Assignment.query.filter_by(teacher_id=teacher_id).all()
    assignment_ids = [a.id for a in assignments]
    
    # Get all submissions for these assignments
    submissions = Submission.query.filter(Submission.assignment_id.in_(assignment_ids)).all()
    
    # Count feedback stats
    total_submissions = len(submissions)
    graded = sum(1 for s in submissions if s.status == 'graded')
    pending = total_submissions - graded
    
    # Get average score
    feedbacks = Feedback.query.filter_by(teacher_id=teacher_id).all()
    avg_score = sum(f.score for f in feedbacks) / len(feedbacks) if feedbacks else 0
    
    return jsonify({
        'total_submissions': total_submissions,
        'graded': graded,
        'pending': pending,
        'average_score': round(avg_score, 2),
        'total_feedback': len(feedbacks)
    }), 200
