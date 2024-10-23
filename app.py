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

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        user = User()
        user.username = data['username']
        user.email = data['email']
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/projects', methods=['GET', 'POST'])
@login_required
def api_projects():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data or 'name' not in data:
                return jsonify({'success': False, 'message': 'Project name is required'}), 400
            
            project = Project(
                name=data['name'],
                user_id=current_user.id
            )
            db.session.add(project)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'created_at': project.created_at.isoformat(),
                    'archived': project.archived,
                    'documents': [],
                    'has_output': False
                }
            })
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Error creating project'}), 500

    # GET request
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

@app.route('/api/projects/<int:project_id>/archive', methods=['POST'])
@login_required
def api_archive_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        project.archived = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/projects/<int:project_id>/unarchive', methods=['POST'])
@login_required
def api_unarchive_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        project.archived = False
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/projects/<int:project_id>/upload_outline', methods=['POST'])
@login_required
def api_upload_outline(project_id):
    if 'outline' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    
    file = request.files['outline']
    if not file.filename:
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    try:
        project = Project.query.get_or_404(project_id)
        if project.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        filename = secure_filename(file.filename)
        save_uploaded_file(file, filename, current_user.id, project_id)
        
        document = Document(
            project_id=project_id,
            filename=filename,
            file_type='outline'
        )
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'document': {
                'id': document.id,
                'filename': document.filename,
                'file_type': document.file_type
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/projects/<int:project_id>/upload_documents', methods=['POST'])
@login_required
def api_upload_documents(project_id):
    if 'documents' not in request.files:
        return jsonify({'success': False, 'message': 'No files uploaded'}), 400
    
    try:
        project = Project.query.get_or_404(project_id)
        if project.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        documents = []
        files = request.files.getlist('documents')
        
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                save_uploaded_file(file, filename, current_user.id, project_id)
                
                document = Document(
                    project_id=project_id,
                    filename=filename,
                    file_type='supporting'
                )
                db.session.add(document)
                documents.append({
                    'filename': filename,
                    'file_type': 'supporting'
                })
        
        db.session.commit()
        return jsonify({
            'success': True,
            'documents': documents
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/current_project')
@login_required
def api_current_project():
    if not current_user.projects:
        return jsonify({'project': None})
    
    project = current_user.projects[-1]  # Get the most recent project
    return jsonify({
        'project': {
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
    })

@app.route('/api/projects/<int:project_id>/process', methods=['POST'])
@login_required
def api_process_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
            
        # Get outline content
        outline_doc = Document.query.filter_by(
            project_id=project_id,
            file_type='outline'
        ).first()
        if not outline_doc:
            return jsonify({'success': False, 'message': 'Outline document not found'}), 404
            
        outline_content = get_file_content(current_user.id, project_id, outline_doc.filename)
        if not outline_content:
            return jsonify({'success': False, 'message': 'Could not read outline content'}), 500
            
        # Process outline to create timeline
        timeline_content = process_outline(outline_content)
        if not timeline_content:
            return jsonify({'success': False, 'message': 'Error processing outline'}), 500
            
        # Get supporting documents content
        supporting_docs = Document.query.filter_by(
            project_id=project_id,
            file_type='supporting'
        ).all()
        
        pdf_contents = []
        for doc in supporting_docs:
            content = get_file_content(current_user.id, project_id, doc.filename)
            if content:
                pdf_contents.append(content)
                
        if not pdf_contents:
            return jsonify({'success': False, 'message': 'No readable supporting documents found'}), 500
                
        # Generate narrative using GPT-4
        narrative_content = generate_narrative(timeline_content, pdf_contents)
        if not narrative_content:
            return jsonify({'success': False, 'message': 'Error generating narrative'}), 500
        
        # Save output
        output = Output.query.filter_by(project_id=project_id).first()
        if output:
            output.timeline_content = timeline_content
            output.narrative_content = narrative_content
        else:
            output = Output(
                project_id=project_id,
                timeline_content=timeline_content,
                narrative_content=narrative_content
            )
            db.session.add(output)
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'output': {
                'timeline_content': timeline_content,
                'narrative_content': narrative_content
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing project: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
