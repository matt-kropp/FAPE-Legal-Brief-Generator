from replit import db
import os
import base64

def save_to_storage(file_data, key):
    """Save file data to Replit Object Storage"""
    try:
        # Convert file data to base64 for storage
        encoded_data = base64.b64encode(file_data.read()).decode('utf-8')
        db[key] = encoded_data
        return True
    except Exception as e:
        print(f"Error saving to storage: {e}")
        return False

def get_from_storage(key):
    """Retrieve file data from Replit Object Storage"""
    try:
        encoded_data = db.get(key)
        if encoded_data:
            return base64.b64decode(encoded_data.encode('utf-8'))
        return None
    except Exception as e:
        print(f"Error retrieving from storage: {e}")
        return None

def delete_from_storage(key):
    """Delete file from Replit Object Storage"""
    try:
        if key in db:
            del db[key]
            return True
        return False
    except Exception as e:
        print(f"Error deleting from storage: {e}")
        return False

def generate_storage_key(user_id, project_id, filename):
    """Generate a unique key for storing files"""
    return f"user_{user_id}/project_{project_id}/{filename}"
