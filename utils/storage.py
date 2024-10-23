import logging
import os
from replit import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_to_storage(file_data, key):
    """Save file data to Replit Database"""
    try:
        # Store file data using Replit db
        content = file_data.read()
        db[key] = content
        logger.info(f"Successfully saved file to storage with key: {key}")
        return True
    except Exception as e:
        logger.error(f"Error saving to storage: {str(e)}")
        return False

def get_from_storage(key):
    """Retrieve file data from Replit Database"""
    try:
        # Get file data from Replit db
        data = db.get(key)
        if data is None:
            logger.warning(f"No data found for key: {key}")
            return None
        logger.info(f"Successfully retrieved file from storage with key: {key}")
        return data
    except Exception as e:
        logger.error(f"Error retrieving from storage: {str(e)}")
        return None

def delete_from_storage(key):
    """Delete file from Replit Database"""
    try:
        if key in db:
            del db[key]
            logger.info(f"Successfully deleted file from storage with key: {key}")
            return True
        logger.warning(f"No file found to delete for key: {key}")
        return False
    except Exception as e:
        logger.error(f"Error deleting from storage: {str(e)}")
        return False

def generate_storage_key(user_id, project_id, filename):
    """Generate a unique key for storing files"""
    return f"users/{user_id}/projects/{project_id}/{filename}"
