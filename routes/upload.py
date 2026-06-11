import os, uuid
from flask import request, jsonify, send_from_directory, current_app, Blueprint
from flask_jwt_extended import jwt_required

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')

ALLOWED = {'png','jpg','jpeg','gif','webp','mp4','mov','avi','mkv','webm'}

def allowed(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED

@upload_bp.route('/', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': '未选择文件'}), 400
    if not allowed(file.filename):
        return jsonify({'error': '只支持图片和视频文件'}), 400
    ext = file.filename.rsplit('.',1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(current_app.root_path, 'uploads')
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, filename))
    return jsonify({'url': f'/api/upload/files/{filename}'}), 200

@upload_bp.route('/files/<filename>', methods=['GET'])
def serve_file(filename):
    folder = os.path.join(current_app.root_path, 'uploads')
    return send_from_directory(folder, filename)
