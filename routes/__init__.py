from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
user_bp = Blueprint('users', __name__, url_prefix='/api/users')
assignment_bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')
submission_bp = Blueprint('submissions', __name__, url_prefix='/api/submissions')
prompt_bp = Blueprint('prompts', __name__, url_prefix='/api/prompts')
feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

# Import route handlers
from .auth import *
from .users import *
from .assignments import *
from .submissions import *
from .prompts import *
from .feedback import *

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')
from .upload import *
