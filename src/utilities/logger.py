import logging
import sys

# Prevent Python from generating .pyc files
sys.dont_write_bytecode = True


def setup_logger(log_file="app.log", log_level=logging.DEBUG):
    # Create or get the logger
    logger = logging.getLogger("my_logger")

    # Avoid adding handlers multiple times
    if not logger.hasHandlers():
        logger.setLevel(log_level)

        # Create a file handler and set the log level
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # Create a console handler and set the log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Create a formatter and set it for the handlers
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Initialize the logger
logger = setup_logger()

if __name__ == "__main__":
    # Example usage
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
