import os
import PyPDF2
from utils.gpt4_processor import summarize_text

def process_pdfs():
    input_folder = 'inputs'
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
    
    for pdf_file in pdf_files:
        file_path = os.path.join(input_folder, pdf_file)
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
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
