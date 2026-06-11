from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    """User model for students and teachers"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'teacher'
    avatar = db.Column(db.String(255), default='')
    bio = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    assignments_created = db.relationship('Assignment', backref='creator', foreign_keys='Assignment.teacher_id')
    submissions = db.relationship('Submission', backref='student')
    feedbacks = db.relationship('Feedback', backref='teacher')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'avatar': self.avatar,
            'bio': self.bio,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class Assignment(db.Model):
    """Assignment model for tasks posted by teachers"""
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prompt_category = db.Column(db.String(100), default='')
    suggested_prompts = db.Column(db.JSON, default=[])
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)
    
    # Relationships
    submissions = db.relationship('Submission', backref='assignment', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'prompt_category': self.prompt_category,
            'suggested_prompts': self.suggested_prompts,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'is_published': self.is_published
        }

class Submission(db.Model):
    """Submission model for student work"""
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    prompt_used = db.Column(db.Text, default='')
    file_url = db.Column(db.String(255), default='')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='submitted')
    
    # Relationships
    feedback = db.relationship('Feedback', backref='submission', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'content': self.content,
            'prompt_used': self.prompt_used,
            'file_url': self.file_url,
            'submitted_at': self.submitted_at.isoformat(),
            'status': self.status,
            'score': self.feedback.score if self.feedback else None,
            'comments': self.feedback.comments if self.feedback else None,
            'ai_suggestions': self.feedback.ai_suggestions if self.feedback else None
        }

class Feedback(db.Model):
    """Feedback model for teacher reviews"""
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    comments = db.Column(db.Text, default='')
    ai_suggestions = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'teacher_id': self.teacher_id,
            'score': self.score,
            'comments': self.comments,
            'ai_suggestions': self.ai_suggestions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Prompt(db.Model):
    """Prompt library for AIGC training"""
    __tablename__ = 'prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), default='beginner')
    example_output = db.Column(db.Text, default='')
    use_case = db.Column(db.Text, default='')
    tags = db.Column(db.JSON, default=[])
    ai_platform = db.Column(db.String(100), default='gemini')
    created_by = db.Column(db.String(100), default='admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    video_file = db.Column(db.String(300), default='')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'difficulty': self.difficulty,
            'example_output': self.example_output,
            'use_case': self.use_case,
            'tags': self.tags,
            'ai_platform': self.ai_platform,
            'created_by': self.created_by,
            'views': self.views,
            'rating': self.rating,
            'created_at': self.created_at.isoformat()
        }

class LearningPath(db.Model):
    """Learning path for structured learning"""
    __tablename__ = 'learning_paths'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    level = db.Column(db.String(20), default='beginner')
    skills = db.Column(db.JSON, default=[])
    prompts = db.Column(db.JSON, default=[])
    duration_weeks = db.Column(db.Integer, default=4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'level': self.level,
            'skills': self.skills,
            'prompts': self.prompts,
            'duration_weeks': self.duration_weeks
        }
