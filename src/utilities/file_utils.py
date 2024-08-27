import shutil 
from utilities.logger import logger
import os 

# Remove a Directory by checking path
def remove_directory(directory_path: str):
    """
    Removes the specified directory.

    Parameters:
        directory_path (str): The path of the directory to be removed.

    Raises:
        OSError: If an error occurs during the directory removal process.

    Returns:
        None
    """
    if os.path.exists(directory_path):
        try:
            shutil.rmtree(directory_path)
        except OSError as e:
            logger.error(f"Error: {e} - {directory_path}")
    else:
        logger.error(f"Directory not found - {directory_path}")


# Create a Directory by checking path
def create_directory(directory_path: str):
    """
    Create the specified directory.

    Parameters:
        directory_path (str): The path of the directory to be created.

    Raises:
        OSError: If an error occurs during the directory creation process.

    Returns:
        None
    """
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
        except OSError as e:
            logger.error(f"Error: {e} - {directory_path}")
    else:
        logger.error(f"Directory already exists - {directory_path}")