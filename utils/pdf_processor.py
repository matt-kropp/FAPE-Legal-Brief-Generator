import os
import PyPDF2
from io import BytesIO
from utils.gpt4_processor import summarize_text

def extract_text_from_pdf(pdf_content):
    """Extract text from PDF content"""
    try:
        # Create a BytesIO object from the PDF content
        pdf_file = BytesIO(pdf_content)
        # Create PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        # Extract text from each page
        for page in pdf_reader.pages:
            try:
                text += page.extract_text() + "\n"
            except Exception as e:
                print(f"Error extracting text from page: {e}")
                continue
        return text
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""

def process_pdfs():
    input_folder = 'inputs'
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
    
    for pdf_file in pdf_files:
        file_path = os.path.join(input_folder, pdf_file)
        
        try:
            with open(file_path, 'rb') as file:
                pdf_content = file.read()
                text = extract_text_from_pdf(pdf_content)
                summary = summarize_text(text)
                update_timeline(pdf_file, summary)
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")

def update_timeline(pdf_file, summary):
    timeline_path = 'timeline.md'
    
    with open(timeline_path, 'a') as timeline:
        timeline.write(f"\n## Events from {pdf_file}\n")
        timeline.write(summary)
        timeline.write(f"\n[Reference: {pdf_file}]\n")
