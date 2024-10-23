from utils.storage import save_to_storage, get_from_storage, generate_storage_key
import os

def save_uploaded_file(file, filename, user_id, project_id):
    """Save uploaded file to Replit Object Storage"""
    storage_key = generate_storage_key(user_id, project_id, filename)
    return save_to_storage(file, storage_key)

def get_file_content(user_id, project_id, filename):
    """Get file content from Replit Object Storage"""
    storage_key = generate_storage_key(user_id, project_id, filename)
    return get_from_storage(storage_key)

def process_outline(user_id, project_id, outline_content):
    """Process outline content and return timeline content"""
    try:
        timeline_content = "# Timeline of Events\n\n"
        for line in outline_content.decode('utf-8').splitlines():
            if line.strip():
                timeline_content += f"- {line.strip()}\n"
        return timeline_content
    except Exception as e:
        print(f"Error processing outline: {e}")
        return None
