import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Project, Document, Output
from utils.file_handler import save_uploaded_file, get_file_content, process_outline
from utils.pdf_processor import process_pdfs
from utils.gpt4_processor import generate_narrative
from sqlalchemy.exc import SQLAlchemyError
from io import BytesIO
import markdown

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static/dist')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise ValueError("DATABASE_URL environment variable is not set")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create database tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except SQLAlchemyError as e:
        logger.error(f"Error loading user: {e}")
        return None

# API Routes
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({
            'success': True,
            'user': {'username': user.username}
        })
    return jsonify({'success': False}), 401

@app.route('/api/logout')
@login_required
def api_logout():
    logout_user()
    return jsonify({'success': True})

@app.route('/api/check_auth')
def check_auth():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {'username': current_user.username}
        })
    return jsonify({'authenticated': False}), 401

@app.route('/api/projects')
@login_required
def api_projects():
    active_projects = Project.query.filter_by(user_id=current_user.id, archived=False).all()
    archived_projects = Project.query.filter_by(user_id=current_user.id, archived=True).all()
    
    def project_to_dict(project):
        return {
            'id': project.id,
            'name': project.name,
            'created_at': project.created_at.isoformat(),
            'archived': project.archived,
            'documents': [{
                'id': doc.id,
                'filename': doc.filename,
                'file_type': doc.file_type
            } for doc in project.documents],
            'has_output': bool(project.output)
        }
    
    return jsonify({
        'active_projects': [project_to_dict(p) for p in active_projects],
        'archived_projects': [project_to_dict(p) for p in archived_projects]
    })

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
