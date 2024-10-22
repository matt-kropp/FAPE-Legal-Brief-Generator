import os

def process_outline():
    input_folder = 'inputs'
    outline_file = os.path.join(input_folder, 'outline.txt')
    
    if not os.path.exists(outline_file):
        raise FileNotFoundError("outline.txt not found in the inputs folder")
    
    try:
        with open(outline_file, 'r') as outline, open('timeline.md', 'w') as timeline:
            timeline.write("# Timeline of Events\n\n")
            for line in outline:
                timeline.write(f"- {line.strip()}\n")
    except Exception as e:
        print(f"Error processing outline: {str(e)}")

def save_uploaded_file(file, filename):
    if not os.path.exists('inputs'):
        os.makedirs('inputs')
    file.save(os.path.join('inputs', filename))
