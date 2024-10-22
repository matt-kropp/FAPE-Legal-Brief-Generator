import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User
from utils.file_handler import process_outline, save_uploaded_file
from utils.pdf_processor import process_pdfs
from utils.gpt4_processor import generate_narrative
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'inputs'
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
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

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
            
            user = User(username=username, email=email)
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

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        files = request.files.getlist('file')
        
        if not files or files[0].filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_uploaded_file(file, filename)
            else:
                flash(f'Invalid file: {file.filename}')
                return redirect(request.url)
        
        try:
            process_outline()
            process_pdfs()
            generate_narrative()
            flash('Files processed successfully!')
        except Exception as e:
            logger.error(f"Error processing files: {e}")
            flash(f'Error processing files: {str(e)}')
        
        return redirect(url_for('index'))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
