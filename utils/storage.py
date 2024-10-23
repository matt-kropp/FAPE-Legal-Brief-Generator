import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def save_to_storage(file_data, key):
    try:
        directory = os.path.dirname(key)
        ensure_directory_exists(directory)
        with open(key, 'wb') as f:
            f.write(file_data.read())
        logger.info(f"Successfully saved file to storage: {key}")
        return True
    except Exception as e:
        logger.error(f"Error saving to storage: {str(e)}")
        return False

def get_from_storage(key):
    try:
        if not os.path.exists(key):
            logger.warning(f"No file found: {key}")
            return None
        with open(key, 'rb') as f:
            data = f.read()
        logger.info(f"Successfully retrieved file: {key}")
        return data
    except Exception as e:
        logger.error(f"Error retrieving from storage: {str(e)}")
        return None

def delete_from_storage(key):
    """Delete file from storage"""
    try:
        if os.path.exists(key):
            os.remove(key)
            logger.info(f"Successfully deleted file: {key}")
            return True
        logger.warning(f"No file found to delete: {key}")
        return False
    except Exception as e:
        logger.error(f"Error deleting from storage: {str(e)}")
        return False

def generate_storage_key(user_id, project_id, filename):
    return os.path.join('storage', str(user_id), str(project_id), filename)
