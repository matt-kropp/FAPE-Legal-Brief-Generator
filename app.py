import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Project, Document, Output
from utils.file_handler import save_uploaded_file, get_file_content, process_outline
from utils.pdf_processor import process_pdfs
from utils.gpt4_processor import generate_narrative
from sqlalchemy.exc import SQLAlchemyError
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
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

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except SQLAlchemyError as e:
        logger.error(f"Error loading user: {e}")
        return None

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered')
                return redirect(url_for('register'))
            
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user registered: {username}")
            
            flash('Registration successful')
            return redirect(url_for('login'))
        except SQLAlchemyError as e:
            logger.error(f"Database error during registration: {e}")
            db.session.rollback()
            flash('An error occurred during registration')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            user = User.query.filter_by(username=request.form['username']).first()
            if user and user.check_password(request.form['password']):
                login_user(user)
                logger.info(f"User logged in: {user.username}")
                return redirect(url_for('index'))
            flash('Invalid username or password')
        except SQLAlchemyError as e:
            logger.error(f"Database error during login: {e}")
            flash('An error occurred during login')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    current_project = None
    has_outline = False
    has_documents = False
    
    if 'current_project_id' in session:
        current_project = Project.query.get(session['current_project_id'])
        if current_project and not current_project.archived:
            has_outline = any(doc.file_type == 'outline' for doc in current_project.documents)
            has_documents = any(doc.file_type == 'supporting' for doc in current_project.documents)
            session['has_outline'] = has_outline
            session['has_documents'] = has_documents
    
    return render_template('index.html', 
                         current_project=current_project,
                         has_outline=has_outline,
                         has_documents=has_documents)

@app.route('/projects')
@login_required
def projects():
    active_projects = Project.query.filter_by(user_id=current_user.id, archived=False).all()
    archived_projects = Project.query.filter_by(user_id=current_user.id, archived=True).all()
    return render_template('projects.html', active_projects=active_projects, archived_projects=archived_projects)

@app.route('/archive_project/<int:project_id>', methods=['POST'])
@login_required
def archive_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('projects'))
    
    try:
        project.archived = True
        db.session.commit()
        if 'current_project_id' in session and session['current_project_id'] == project_id:
            session.pop('current_project_id')
        flash('Project archived successfully')
    except SQLAlchemyError as e:
        logger.error(f"Error archiving project: {e}")
        db.session.rollback()
        flash('Error archiving project')
    
    return redirect(url_for('projects'))

@app.route('/unarchive_project/<int:project_id>', methods=['POST'])
@login_required
def unarchive_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('projects'))
    
    try:
        project.archived = False
        db.session.commit()
        flash('Project unarchived successfully')
    except SQLAlchemyError as e:
        logger.error(f"Error unarchiving project: {e}")
        db.session.rollback()
        flash('Error unarchiving project')
    
    return redirect(url_for('projects'))

@app.route('/create_project', methods=['POST'])
@login_required
def create_project():
    try:
        project_name = request.form['project_name']
        project = Project()
        project.name = project_name
        project.user_id = current_user.id
        project.archived = False
        db.session.add(project)
        db.session.commit()
        session['current_project_id'] = project.id
        flash('Project created successfully')
    except SQLAlchemyError as e:
        logger.error(f"Error creating project: {e}")
        db.session.rollback()
        flash('Error creating project')
    return redirect(url_for('index'))

@app.route('/select_project/<int:project_id>')
@login_required
def select_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('projects'))
    if project.archived:
        flash('Cannot select archived project')
        return redirect(url_for('projects'))
    session['current_project_id'] = project_id
    return redirect(url_for('index'))

@app.route('/upload_outline/<int:project_id>', methods=['POST'])
@login_required
def upload_outline(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id or project.archived:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    if 'outline' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['outline']
    if not file or file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if allowed_file(file.filename) and file.filename.endswith('.txt'):
        filename = secure_filename(file.filename)
        if save_uploaded_file(file, filename, current_user.id, project_id):
            document = Document()
            document.project_id = project_id
            document.filename = filename
            document.file_type = 'outline'
            db.session.add(document)
            db.session.commit()
            flash('Outline uploaded successfully')
        else:
            flash('Error uploading outline')
    else:
        flash('Invalid file type')
    
    return redirect(url_for('index'))

@app.route('/upload_documents/<int:project_id>', methods=['POST'])
@login_required
def upload_documents(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id or project.archived:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    if 'documents' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    files = request.files.getlist('documents')
    if not files or files[0].filename == '':
        flash('No selected files')
        return redirect(url_for('index'))
    
    for file in files:
        if file and allowed_file(file.filename) and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            if save_uploaded_file(file, filename, current_user.id, project_id):
                document = Document()
                document.project_id = project_id
                document.filename = filename
                document.file_type = 'supporting'
                db.session.add(document)
                db.session.commit()
                flash(f'{filename} uploaded successfully')
            else:
                flash(f'Error uploading {filename}')
        else:
            flash(f'Invalid file type: {file.filename}')
    
    return redirect(url_for('index'))

@app.route('/process/<int:project_id>', methods=['POST'])
@login_required
def process_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id or project.archived:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    try:
        # Get outline document
        outline_doc = Document.query.filter_by(
            project_id=project_id,
            file_type='outline'
        ).first()
        
        if not outline_doc:
            flash('Outline document not found')
            return redirect(url_for('index'))
        
        # Process outline
        outline_content = get_file_content(current_user.id, project_id, outline_doc.filename)
        if not outline_content:
            flash('Error reading outline content')
            return redirect(url_for('index'))
        
        timeline_content = process_outline(current_user.id, project_id, outline_content)
        
        # Process supporting documents
        supporting_docs = Document.query.filter_by(
            project_id=project_id,
            file_type='supporting'
        ).all()
        
        pdf_contents = []
        for doc in supporting_docs:
            content = get_file_content(current_user.id, project_id, doc.filename)
            if content:
                pdf_contents.append(content)
        
        # Generate narrative
        narrative_content = generate_narrative(timeline_content, pdf_contents)
        
        # Save or update output
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
        flash('Project processed successfully')
    except Exception as e:
        logger.error(f"Error processing project: {e}")
        db.session.rollback()
        flash('Error processing project')
    
    return redirect(url_for('index'))

@app.route('/view/timeline/<int:project_id>')
@login_required
def view_timeline(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('projects'))
    
    output = Output.query.filter_by(project_id=project_id).first()
    if not output or not output.timeline_content:
        flash('Timeline not found')
        return redirect(url_for('projects'))
    
    return render_template('timeline.html', 
                         project=project,
                         timeline_content=output.timeline_content)

@app.route('/view/narrative/<int:project_id>')
@login_required
def view_narrative(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('projects'))
    
    output = Output.query.filter_by(project_id=project_id).first()
    if not output or not output.narrative_content:
        flash('Narrative not found')
        return redirect(url_for('projects'))
    
    return render_template('narrative.html',
                         project=project,
                         narrative_content=output.narrative_content)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
