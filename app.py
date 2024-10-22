import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from utils.file_handler import process_outline, save_uploaded_file
from utils.pdf_processor import process_pdfs
from utils.gpt4_processor import generate_narrative

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'inputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
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
            flash(f'Error processing files: {str(e)}')
        
        return redirect(url_for('index'))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
