from replit.object_storage import Client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Client()

def save_to_storage(file_data, key):
    try:
        # Read the file data
        data = file_data.read()
        # Upload to object storage
        client.upload_from_bytes(key, data)
        logger.info(f"Successfully saved file to object storage: {key}")
        return True
    except Exception as e:
        logger.error(f"Error saving to object storage: {str(e)}")
        return False

def get_from_storage(key):
    try:
        # Download from object storage
        data = client.download_as_bytes(key)
        if data is None:
            logger.warning(f"No data found for key: {key}")
            return None
        logger.info(f"Successfully retrieved file from object storage: {key}")
        return data
    except Exception as e:
        logger.error(f"Error retrieving from object storage: {str(e)}")
        return None

def delete_from_storage(key):
    """Delete file from object storage"""
    try:
        client.delete(key)
        logger.info(f"Successfully deleted file from object storage: {key}")
        return True
    except Exception as e:
        logger.error(f"Error deleting from object storage: {str(e)}")
        return False

def generate_storage_key(user_id, project_id, filename):
    # Create a unique key for each file in the format: user_<id>/project_<id>/<filename>
    return f"user_{user_id}/project_{project_id}/{filename}"
